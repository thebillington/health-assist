import Foundation
import Security

final class SettingsStore {
    private let defaults = UserDefaults.standard

    private let includeExtrasKey = "includeExtras"
    private let syncOnOpenKey = "syncOnOpen"
    private let deviceIDKey = "deviceID"
    private let lastBackgroundSyncKey = "lastBackgroundSync"
    private let historyCompleteKey = "historyFullExportComplete"
    private let lastHistoryExportKey = "lastHistoryExport"
    private let historyCheckpointsKey = "historyCheckpoints"

    private let keychainService = "uk.rebecchi.applehealthsync"
    private let urlAccount = "webhook-url"
    private let secretAccount = "webhook-secret"

    var webhookURL: String {
        get { readKeychain(account: urlAccount) }
        set { writeKeychain(newValue, account: urlAccount) }
    }

    var includeExtras: Bool {
        get { defaults.object(forKey: includeExtrasKey) as? Bool ?? true }
        set { defaults.set(newValue, forKey: includeExtrasKey) }
    }

    var syncOnOpen: Bool {
        get { defaults.object(forKey: syncOnOpenKey) as? Bool ?? true }
        set { defaults.set(newValue, forKey: syncOnOpenKey) }
    }

    var lastBackgroundSync: Date? {
        get { defaults.object(forKey: lastBackgroundSyncKey) as? Date }
        set { defaults.set(newValue, forKey: lastBackgroundSyncKey) }
    }

    var historyFullExportComplete: Bool {
        get { defaults.bool(forKey: historyCompleteKey) }
        set { defaults.set(newValue, forKey: historyCompleteKey) }
    }

    var lastHistoryExport: Date? {
        get { defaults.object(forKey: lastHistoryExportKey) as? Date }
        set {
            if let newValue {
                defaults.set(newValue, forKey: lastHistoryExportKey)
            } else {
                defaults.removeObject(forKey: lastHistoryExportKey)
            }
        }
    }

    func historyCheckpoint(for key: String) -> Date? {
        let checkpoints = defaults.dictionary(forKey: historyCheckpointsKey) ?? [:]
        guard let timestamp = checkpoints[key] as? Double else { return nil }
        return Date(timeIntervalSince1970: timestamp)
    }

    func setHistoryCheckpoint(_ date: Date?, for key: String) {
        var checkpoints = defaults.dictionary(forKey: historyCheckpointsKey) ?? [:]
        if let date {
            checkpoints[key] = date.timeIntervalSince1970
        } else {
            checkpoints.removeValue(forKey: key)
        }
        defaults.set(checkpoints, forKey: historyCheckpointsKey)
    }

    func resetHistoryCheckpoints() {
        defaults.removeObject(forKey: historyCheckpointsKey)
        defaults.removeObject(forKey: historyCompleteKey)
        defaults.removeObject(forKey: lastHistoryExportKey)
    }

    var deviceID: String {
        if let existing = defaults.string(forKey: deviceIDKey), !existing.isEmpty {
            return existing
        }
        let identifier = UUID().uuidString.lowercased()
        defaults.set(identifier, forKey: deviceIDKey)
        return identifier
    }

    var secret: String {
        get { readKeychain(account: secretAccount) }
        set { writeKeychain(newValue, account: secretAccount) }
    }

    private func keychainQuery(account: String) -> [String: Any] {
        [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: keychainService,
            kSecAttrAccount as String: account,
        ]
    }

    private func readKeychain(account: String) -> String {
        var query = keychainQuery(account: account)
        query[kSecReturnData as String] = true
        query[kSecMatchLimit as String] = kSecMatchLimitOne

        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        guard status == errSecSuccess,
              let data = result as? Data,
              let value = String(data: data, encoding: .utf8) else {
            return ""
        }
        return value
    }

    private func writeKeychain(_ value: String, account: String) {
        let query = keychainQuery(account: account)
        SecItemDelete(query as CFDictionary)

        let trimmed = value.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }

        var attributes = query
        attributes[kSecValueData as String] = Data(trimmed.utf8)
        attributes[kSecAttrAccessible as String] = kSecAttrAccessibleAfterFirstUnlock
        SecItemAdd(attributes as CFDictionary, nil)
    }
}
