import Foundation
import Security

final class SettingsStore {
    private let defaults = UserDefaults.standard

    private let urlKey = "webhookURL"
    private let includeExtrasKey = "includeExtras"
    private let syncOnOpenKey = "syncOnOpen"
    private let deviceIDKey = "deviceID"

    private let secretService = "uk.rebecchi.applehealthsync"
    private let secretAccount = "webhook-secret"

    var webhookURL: String {
        get { defaults.string(forKey: urlKey) ?? "" }
        set { defaults.set(newValue, forKey: urlKey) }
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
        get { readSecret() }
        set { writeSecret(newValue) }
    }

    private var keychainQuery: [String: Any] {
        [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: secretService,
            kSecAttrAccount as String: secretAccount,
        ]
    }

    private func readSecret() -> String {
        var query = keychainQuery
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

    private func writeSecret(_ value: String) {
        SecItemDelete(keychainQuery as CFDictionary)

        let trimmed = value.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }

        var attributes = keychainQuery
        attributes[kSecValueData as String] = Data(trimmed.utf8)
        attributes[kSecAttrAccessible as String] = kSecAttrAccessibleAfterFirstUnlock
        SecItemAdd(attributes as CFDictionary, nil)
    }
}
