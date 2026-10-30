import Foundation

/// One value in the `metrics` object of the Home Assistant webhook contract.
public struct MetricSample: Encodable, Equatable, Sendable {
    public let value: Double
    public let unit: String?

    public init(value: Double, unit: String?) {
        self.value = value
        self.unit = unit
    }

    private enum CodingKeys: String, CodingKey {
        case value
        case unit
    }

    public func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)

        // Home Assistant stores integral JSON numbers as ints, which makes
        // sensors such as steps display as 8432 rather than 8432.0.
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

/// The exact JSON body posted to Home Assistant.
public struct HealthPayload: Encodable, Equatable, Sendable {
    public let deviceID: String
    public let deviceName: String
    public let timestamp: Date
    public let metrics: [String: MetricSample]

    public init(
        deviceID: String,
        deviceName: String,
        timestamp: Date = Date(),
        readings: [MetricReading]
    ) {
        self.deviceID = deviceID
        self.deviceName = deviceName
        self.timestamp = timestamp

        var metrics: [String: MetricSample] = [:]
        for reading in readings {
            metrics[reading.key] = MetricSample(
                value: reading.value,
                unit: reading.unit
            )
        }
        self.metrics = metrics
    }

    /// Encode the payload as UTF-8 JSON.
    public func encoded() throws -> Data {
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.sortedKeys]
        return try encoder.encode(self)
    }

    private enum CodingKeys: String, CodingKey {
        case deviceID = "device_id"
        case deviceName = "device_name"
        case timestamp
        case metrics
    }

    public func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(deviceID, forKey: .deviceID)
        try container.encode(deviceName, forKey: .deviceName)

        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime]
        try container.encode(formatter.string(from: timestamp), forKey: .timestamp)

        try container.encode(metrics, forKey: .metrics)
    }
}
