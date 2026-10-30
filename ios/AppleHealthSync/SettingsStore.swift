import Foundation
import Security

final class SettingsStore {
    private let defaults = UserDefaults.standard

    private let includeExtrasKey = "includeExtras"
    private let syncOnOpenKey = "syncOnOpen"
    private let deviceIDKey = "deviceID"

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
