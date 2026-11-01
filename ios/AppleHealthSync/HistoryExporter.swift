import Foundation
import UIKit
import AppleHealthSyncCore

/// Exports the complete HealthKit history in resumable, chunked webhook
/// requests. Each metric has its own checkpoint so an interrupted first export
/// resumes where it stopped instead of starting over.
@MainActor
final class HistoryExporter {
    // Apple Health launched in 2014. Querying from here covers the full data set
    // without needing a per-metric earliest-sample lookup first.
    static let earliestHistory: Date = {
        Calendar.current.date(
            from: DateComponents(year: 2014, month: 1, day: 1)
        ) ?? Date(timeIntervalSince1970: 0)
    }()

    private static let sleepNames: [(key: String, name: String)] = [
        ("sleep_total", "Sleep total"),
        ("sleep_deep", "Deep sleep"),
        ("sleep_rem", "REM sleep"),
        ("sleep_core", "Core sleep"),
        ("sleep_awake", "Awake time"),
    ]

    private let health: HealthKitManager
    private let settings: SettingsStore
    private let client: WebhookClient
    private let chunkSize = 1_000

    init(health: HealthKitManager, settings: SettingsStore, client: WebhookClient) {
        self.health = health
        self.settings = settings
        self.client = client
    }

    func export(
        includeExtras: Bool,
        progress: @escaping (String) -> Void
    ) async throws {
        guard let url = WebhookClient.validateURL(settings.webhookURL) else {
            throw WebhookError.invalidURL
        }

        let now = Date()
        let deviceName = UIDevice.current.name.trimmingCharacters(in: .whitespacesAndNewlines)
        let name = deviceName.isEmpty ? "iPhone" : deviceName
        let metrics = includeExtras
            ? MetricCatalog.canonical + MetricCatalog.extras
            : MetricCatalog.canonical
        let totalSteps = metrics.count + 2 // quantity metrics + sleep + stand
        var step = 0

        for metric in metrics {
            step += 1
            progress("Exporting history: \(metric.name) (\(step)/\(totalSteps))")

            let start = settings.historyCheckpoint(for: metric.key)
                ?? Self.earliestHistory
            guard start < now else { continue }

            let entries: [HistoryEntry]
            do {
                entries = try await health.quantityHistory(
                    for: metric,
                    from: start,
                    to: now
                )
            } catch {
                #if DEBUG
                print("AHS history query failed for \(metric.key): \(error)")
                #endif
                continue
            }

            #if DEBUG
            print("AHS history \(metric.key): \(entries.count) entries")
            #endif
            try await send(
                key: metric.key,
                name: metric.name,
                unit: metric.payloadUnit,
                entries: entries,
                from: start,
                to: now,
                url: url,
                deviceName: name,
                progress: progress
            )
        }

        step += 1
        progress("Exporting history: Sleep (\(step)/\(totalSteps))")
        try await exportSleep(
            to: now,
            url: url,
            deviceName: name,
            progress: progress
        )

        step += 1
        progress("Exporting history: Stand hours (\(step)/\(totalSteps))")
        let standStart = settings.historyCheckpoint(for: "stand_hours")
            ?? Self.earliestHistory
        if standStart < now {
            let entries: [HistoryEntry]?
            do {
                entries = try await health.standHistory(from: standStart, to: now)
            } catch {
                #if DEBUG
                print("AHS stand history query failed: \(error)")
                #endif
                entries = nil
            }
            if let entries {
                try await send(
                    key: "stand_hours",
                    name: "Stand hours",
                    unit: "h",
                    entries: entries,
                    from: standStart,
                    to: now,
                    url: url,
                    deviceName: name,
                    progress: progress
                )
            }
        }

        settings.historyFullExportComplete = true
        settings.lastHistoryExport = Date()
        #if DEBUG
        print("AHS history export complete")
        #endif
    }

    private func exportSleep(
        to now: Date,
        url: URL,
        deviceName: String,
        progress: @escaping (String) -> Void
    ) async throws {
        let starts = Self.sleepNames.map {
            settings.historyCheckpoint(for: $0.key) ?? Self.earliestHistory
        }
        guard let start = starts.min(), start < now else { return }

        let history: [String: [HistoryEntry]]
        do {
            history = try await health.sleepHistory(from: start, to: now)
        } catch {
            #if DEBUG
            print("AHS sleep history query failed: \(error)")
            #endif
            return
        }

        for (key, name) in Self.sleepNames {
            let keyStart = settings.historyCheckpoint(for: key) ?? Self.earliestHistory
            let entries = (history[key] ?? []).filter { $0.timestamp >= keyStart }
            try await send(
                key: key,
                name: name,
                unit: "h",
                entries: entries,
                from: keyStart,
                to: now,
                url: url,
                deviceName: deviceName,
                progress: progress
            )
        }
    }

    private func send(
        key: String,
        name: String,
        unit: String?,
        entries: [HistoryEntry],
        from start: Date,
        to now: Date,
        url: URL,
        deviceName: String,
        progress: @escaping (String) -> Void
    ) async throws {
        let filtered = entries.filter { $0.timestamp >= start }
        guard !filtered.isEmpty else {
            // Do not advance the checkpoint: the metric may simply have no data
            // yet, or read permission may have been granted after the first
            // export. Retrying from the same checkpoint is cheap and avoids
            // silently losing history.
            return
        }

        let total = filtered.count
        var sent = 0

        for chunk in filtered.chunked(into: chunkSize) {
            let payload = HistoryPayload(
                deviceID: settings.deviceID,
                deviceName: deviceName,
                history: [key: chunk]
            )
            _ = try await client.send(
                history: payload,
                url: url,
                secret: settings.secret
            )

            sent += chunk.count
            #if DEBUG
            print("AHS history sent \(key): \(sent)/\(total)")
            #endif
            progress("Exporting \(name): \(sent)/\(total)")

            if let latest = chunk.map(\.timestamp).max() {
                // Keep a small overlap so late-arriving HealthKit samples are
                // not missed. Duplicates are upserts on the HA side.
                let overlap: TimeInterval = key.hasPrefix("sleep") || key == "stand_hours"
                    ? 86_400
                    : 3_600
                let checkpoint = latest.addingTimeInterval(-overlap)
                settings.setHistoryCheckpoint(max(checkpoint, start), for: key)
            }
        }
    }
}

private extension Array {
    func chunked(into size: Int) -> [[Element]] {
        guard size > 0, !isEmpty else { return [] }
        return stride(from: 0, to: count, by: size).map {
            Array(self[$0 ..< Swift.min($0 + size, count)])
        }
    }
}
