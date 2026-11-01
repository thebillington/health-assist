import BackgroundTasks
import Foundation
import HealthKit
import UIKit
import os
import AppleHealthSyncCore

/// Handles HealthKit background delivery and the weekly BGTask fallback.
///
/// HealthKit observer queries wake the app when health data changes. The
/// weekly BGTask is a best-effort fallback for weeks where HealthKit does not
/// deliver an update. iOS decides the exact execution time; neither path is a
/// guaranteed cron schedule.
@MainActor
final class BackgroundSyncManager {
    static let shared = BackgroundSyncManager()
    static let weeklyTaskIdentifier = "uk.rebecchi.applehealthsync.weekly-sync"

    private let health = HealthKitManager()
    private let settings = SettingsStore()
    private let client = WebhookClient()
    private lazy var historyExporter = HistoryExporter(
        health: health,
        settings: settings,
        client: client
    )
    private let logger = Logger(
        subsystem: "uk.rebecchi.applehealthsync",
        category: "background"
    )
    private let store = HKHealthStore()

    private var observerQueries: [HKObserverQuery] = []
    private var observedTypes: [HKSampleType] = []
    private var configuredSignature: String?
    private var syncing = false

    private init() {}

    /// Register HealthKit observers and make sure a weekly task is queued.
    func start(includeExtras: Bool, force: Bool = false) {
        #if targetEnvironment(simulator)
        return
        #else
        guard health.isAvailable else { return }

        let signature = includeExtras ? "all" : "canonical"
        if force || configuredSignature != signature {
            stopObservers()
            registerObservers(includeExtras: includeExtras)
            configuredSignature = signature
        }

        scheduleWeekly()
        #endif
    }

    /// Called by the SwiftUI background task handler.
    func performWeeklySync() async {
        #if targetEnvironment(simulator)
        return
        #else
        await syncFromBackground(reason: "weekly")
        scheduleWeekly()
        #endif
    }

    private func registerObservers(includeExtras: Bool) {
        let metrics = includeExtras
            ? MetricCatalog.canonical + MetricCatalog.extras
            : MetricCatalog.canonical

        var sampleTypes: [HKSampleType] = []
        var seen = Set<String>()

        for metric in metrics {
            guard let type = HKObjectType.quantityType(forIdentifier: metric.identifier) else {
                continue
            }
            if seen.insert(type.identifier).inserted {
                sampleTypes.append(type)
            }
        }

        if let sleep = HKObjectType.categoryType(forIdentifier: .sleepAnalysis),
           seen.insert(sleep.identifier).inserted {
            sampleTypes.append(sleep)
        }
        if let stand = HKObjectType.categoryType(forIdentifier: .appleStandHour),
           seen.insert(stand.identifier).inserted {
            sampleTypes.append(stand)
        }

        for type in sampleTypes {
            let query = HKObserverQuery(sampleType: type, predicate: nil) {
                [weak self] _, completionHandler, error in
                // HealthKit requires this to be called before doing work.
                completionHandler()

                guard error == nil, let self else { return }
                Task { @MainActor [weak self] in
                    await self?.syncFromBackground(reason: "healthkit")
                }
            }

            store.execute(query)
            observerQueries.append(query)
            observedTypes.append(type)

            store.enableBackgroundDelivery(for: type, frequency: .hourly) {
                [weak self] _, error in
                if let error {
                    self?.logger.debug(
                        "Could not enable background delivery: \(error.localizedDescription, privacy: .public)"
                    )
                }
            }
        }

        logger.info("Registered \(sampleTypes.count, privacy: .public) HealthKit observers")
    }

    private func stopObservers() {
        for query in observerQueries {
            store.stop(query)
        }
        observerQueries.removeAll()

        for type in observedTypes {
            store.disableBackgroundDelivery(for: type) { _, _ in }
        }
        observedTypes.removeAll()
    }

    private func syncFromBackground(reason: String) async {
        guard !syncing else { return }

        guard let url = WebhookClient.validateURL(settings.webhookURL) else {
            logger.debug("Background sync skipped: no webhook URL configured")
            return
        }

        guard health.isAvailable else { return }

        syncing = true
        defer { syncing = false }

        let backgroundTask = UIApplication.shared.beginBackgroundTask(
            withName: "AppleHealthSyncBackgroundSync"
        )
        defer {
            if backgroundTask != .invalid {
                UIApplication.shared.endBackgroundTask(backgroundTask)
            }
        }

        if settings.historyFullExportComplete,
           let lastHistoryExport = settings.lastHistoryExport,
           Date().timeIntervalSince(lastHistoryExport) > 60 * 60 {
            do {
                try await historyExporter.export(includeExtras: settings.includeExtras) { _ in }
            } catch {
                logger.error(
                    "Background history export failed: \(error.localizedDescription, privacy: .public)"
                )
            }
        }

        let readings = await health.fetchMetrics(includeExtras: settings.includeExtras)
        guard !readings.isEmpty else {
            logger.debug("Background sync skipped: no health data")
            return
        }

        let deviceName = UIDevice.current.name.trimmingCharacters(in: .whitespacesAndNewlines)
        let payload = HealthPayload(
            deviceID: settings.deviceID,
            deviceName: deviceName.isEmpty ? "iPhone" : deviceName,
            readings: readings
        )

        do {
            let response = try await client.send(
                payload: payload,
                url: url,
                secret: settings.secret
            )
            settings.lastBackgroundSync = Date()
            logger.info(
                "Background sync (\(reason, privacy: .public)) sent \(readings.count) metrics; accepted \(response.accepted), ignored \(response.ignored)"
            )
        } catch {
            logger.error(
                "Background sync failed: \(error.localizedDescription, privacy: .public)"
            )
        }
    }

    private func scheduleWeekly() {
        let request = BGAppRefreshTaskRequest(identifier: Self.weeklyTaskIdentifier)
        request.earliestBeginDate = Calendar.current.date(
            byAdding: .day,
            value: 7,
            to: Date()
        )

        do {
            try BGTaskScheduler.shared.submit(request)
            logger.info("Weekly background sync scheduled")
        } catch {
            logger.error(
                "Could not schedule weekly background sync: \(error.localizedDescription, privacy: .public)"
            )
        }
    }
}
