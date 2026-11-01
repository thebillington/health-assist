import Foundation

/// A single historical sample in a history payload.
public struct HistoryEntry: Encodable, Equatable, Sendable {
    public let timestamp: Date
    public let value: Double
    public let unit: String?

    public init(timestamp: Date, value: Double, unit: String?) {
        self.timestamp = timestamp
        self.value = value
        self.unit = unit
    }

    private enum CodingKeys: String, CodingKey {
        case timestamp
        case value
        case unit
    }

    public func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)

        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime]
        try container.encode(formatter.string(from: timestamp), forKey: .timestamp)

        if value.isFinite, value == value.rounded(), abs(value) <= Double(Int64.max) {
            try container.encode(Int64(value), forKey: .value)
        } else {
            try container.encode(value, forKey: .value)
        }

        if let unit {
            try container.encode(unit, forKey: .unit)
        }
    }
}

/// A chunk of historical samples sent separately from the live metrics snapshot.
public struct HistoryPayload: Encodable, Sendable {
    public let deviceID: String
    public let deviceName: String
    public let timestamp: Date
    public let history: [String: [HistoryEntry]]

    public init(
        deviceID: String,
        deviceName: String,
        timestamp: Date = Date(),
        history: [String: [HistoryEntry]]
    ) {
        self.deviceID = deviceID
        self.deviceName = deviceName
        self.timestamp = timestamp
        self.history = history
    }

    public func encoded() throws -> Data {
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.sortedKeys]
        return try encoder.encode(self)
    }

    private enum CodingKeys: String, CodingKey {
        case deviceID = "device_id"
        case deviceName = "device_name"
        case timestamp
        case history
    }

    public func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(deviceID, forKey: .deviceID)
        try container.encode(deviceName, forKey: .deviceName)

        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime]
        try container.encode(formatter.string(from: timestamp), forKey: .timestamp)

        try container.encode(history, forKey: .history)
    }
}
