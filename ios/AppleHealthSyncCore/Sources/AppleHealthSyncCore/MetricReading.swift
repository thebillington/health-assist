import Foundation

/// A single metric value ready to be sent to Home Assistant.
public struct MetricReading: Identifiable, Equatable, Sendable {
    public var id: String { key }

    public let key: String
    public let name: String
    public let value: Double
    public let unit: String?
    public let canonical: Bool

    public init(
        key: String,
        name: String,
        value: Double,
        unit: String?,
        canonical: Bool
    ) {
        self.key = key
        self.name = name
        self.value = value
        self.unit = unit
        self.canonical = canonical
    }
}
