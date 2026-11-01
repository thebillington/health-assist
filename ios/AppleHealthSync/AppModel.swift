import Foundation
import HealthKit
import UIKit
import AppleHealthSyncCore

@MainActor
final class AppModel: ObservableObject {
    @Published var webhookURL: String
    @Published var secret: String
    @Published var includeExtras: Bool
    @Published var syncOnOpen: Bool

    @Published private(set) var healthStatus = "Checking…"
    @Published private(set) var statusMessage = "Not synced yet."
    @Published private(set) var isSyncing = false
    @Published private(set) var isRequestingAccess = false
    @Published private(set) var lastSync: Date?
    @Published private(set) var lastBackgroundSync: Date?
    @Published private(set) var readings: [MetricReading] = []

    private let settings: SettingsStore
    private let health = HealthKitManager()
    private let client = WebhookClient()
    private var lastAutoSync: Date?
    private let autoTestPayload: Bool
    private let environmentOverrides: Bool

    init(settings: SettingsStore = SettingsStore()) {
        let environment = ProcessInfo.processInfo.environment
        self.settings = settings
        self.webhookURL = environment["AHS_WEBHOOK_URL"] ?? settings.webhookURL
        self.secret = environment["AHS_SECRET"] ?? settings.secret
        self.includeExtras = settings.includeExtras
        self.syncOnOpen = settings.syncOnOpen
        self.autoTestPayload = environment["AHS_AUTO_TEST_PAYLOAD"] == "1"
        self.environmentOverrides = environment["AHS_WEBHOOK_URL"] != nil
            || environment["AHS_SECRET"] != nil
        self.lastBackgroundSync = settings.lastBackgroundSync
    }

    func saveSettings() {
        #if targetEnvironment(simulator)
        // Simulator automation uses throwaway settings; never overwrite the
        // developer's real configuration from an env-driven test run.
        guard !environmentOverrides else { return }
        #endif
        settings.webhookURL = webhookURL
        settings.secret = secret
        settings.includeExtras = includeExtras
        settings.syncOnOpen = syncOnOpen
    }

    func prepare() async {
        #if !targetEnvironment(simulator)
        if environmentOverrides, !autoTestPayload {
            saveSettings()
        }
        #endif

        BackgroundSyncManager.shared.start(includeExtras: includeExtras)
        refreshBackgroundSyncDate()

        if autoTestPayload {
            healthStatus = "Simulator test mode"
            await sendTestPayload()
            return
        }

        await refreshHealthStatus()
        await syncOnLaunchIfNeeded()
    }

    func refreshHealthStatus() async {
        #if targetEnvironment(simulator)
        healthStatus = "Simulator (test payload only)"
        return
        #endif

        guard health.isAvailable else {
            healthStatus = "Unavailable"
            return
        }

        let status = await health.authorizationRequestStatus(includeExtras: includeExtras)
        switch status {
        case .unnecessary:
            healthStatus = "Access requested"
        case .shouldRequest:
            healthStatus = "Not requested"
        case .unknown:
            healthStatus = "Unknown"
        @unknown default:
            healthStatus = "Unknown"
        }
    }

    func requestHealthAccess() async {
        #if targetEnvironment(simulator)
        statusMessage = "HealthKit access is only available on a physical iPhone. Use Send a Test Payload in the simulator."
        return
        #endif

        guard !isRequestingAccess else { return }
        isRequestingAccess = true
        defer { isRequestingAccess = false }

        do {
            try await health.requestAuthorization(includeExtras: includeExtras)
            BackgroundSyncManager.shared.start(includeExtras: includeExtras, force: true)
            await refreshHealthStatus()
            statusMessage = "Health access updated. Tap Sync Now to send data."
        } catch {
            statusMessage = error.localizedDescription
        }
    }

    func updateBackgroundDelivery() {
        BackgroundSyncManager.shared.start(includeExtras: includeExtras, force: true)
    }

    func refreshBackgroundSyncDate() {
        lastBackgroundSync = settings.lastBackgroundSync
    }

    func syncOnLaunchIfNeeded() async {
        #if targetEnvironment(simulator)
        return
        #endif

        guard syncOnOpen, !isSyncing else { return }
        guard !webhookURL.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            return
        }
        guard WebhookClient.validateURL(webhookURL) != nil else { return }
        guard health.isAvailable else { return }
        guard await health.authorizationRequestStatus(includeExtras: includeExtras) == .unnecessary else {
            return
        }
        if let lastAutoSync, Date().timeIntervalSince(lastAutoSync) < 60 {
            return
        }

        lastAutoSync = Date()
        await sync()
    }

    func sync() async {
        #if targetEnvironment(simulator)
        statusMessage = "HealthKit sync is only available on a physical iPhone. Use Send a Test Payload in the simulator."
        return
        #endif

        guard !isSyncing else { return }
        saveSettings()

        guard let url = WebhookClient.validateURL(webhookURL) else {
            statusMessage = WebhookError.invalidURL.localizedDescription
            return
        }

        isSyncing = true
        defer { isSyncing = false }

        do {
            guard health.isAvailable else { throw HealthKitError.unavailable }

            try await health.requestAuthorization(includeExtras: includeExtras)
            await refreshHealthStatus()

            let fetched = await health.fetchMetrics(includeExtras: includeExtras)
            guard !fetched.isEmpty else {
                statusMessage = "No health data was returned. Check Health permissions, or add sample data to Apple Health."
                return
            }

            let payload = HealthPayload(
                deviceID: settings.deviceID,
                deviceName: deviceName,
                readings: fetched
            )
            let response = try await client.send(
                payload: payload,
                url: url,
                secret: secret
            )

            readings = fetched
            lastSync = Date()
            statusMessage = "Sent \(fetched.count) metrics. Home Assistant accepted \(response.accepted) and ignored \(response.ignored)."
        } catch {
            statusMessage = error.localizedDescription
        }
    }

    /// Send deterministic sample values. This works without HealthKit, which
    /// makes it useful for testing the integration from the iOS simulator.
    func sendTestPayload() async {
        guard !isSyncing else { return }
        saveSettings()

        guard let url = WebhookClient.validateURL(webhookURL) else {
            statusMessage = WebhookError.invalidURL.localizedDescription
            return
        }

        isSyncing = true
        defer { isSyncing = false }

        let testReadings = [
            MetricReading(key: "weight", name: "Weight", value: 72.4, unit: "kg", canonical: true),
            MetricReading(key: "body_fat", name: "Body fat", value: 18.5, unit: "%", canonical: true),
            MetricReading(key: "steps", name: "Steps", value: 8_432, unit: "steps", canonical: true),
            MetricReading(key: "heart_rate", name: "Heart rate", value: 62, unit: "bpm", canonical: true),
            MetricReading(key: "sleep_total", name: "Sleep total", value: 7.5, unit: "h", canonical: true),
            MetricReading(
                key: "blood_glucose",
                name: "Blood Glucose",
                value: 5.4,
                unit: "mmol/L",
                canonical: false
            ),
        ]

        do {
            let payload = HealthPayload(
                deviceID: settings.deviceID,
                deviceName: deviceName,
                readings: testReadings
            )
            let response = try await client.send(
                payload: payload,
                url: url,
                secret: secret
            )

            readings = testReadings
            lastSync = Date()
            statusMessage = "Test payload sent. Home Assistant accepted \(response.accepted) and ignored \(response.ignored)."
        } catch {
            statusMessage = error.localizedDescription
        }
    }

    private var deviceName: String {
        let name = UIDevice.current.name.trimmingCharacters(in: .whitespacesAndNewlines)
        return name.isEmpty ? "iPhone" : name
    }
}
