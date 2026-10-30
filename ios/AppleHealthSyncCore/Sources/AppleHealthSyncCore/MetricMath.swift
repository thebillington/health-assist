import Foundation

/// Numeric helpers shared by the HealthKit queries and unit tests.
public enum MetricMath {
    /// Convert HealthKit's 0...1 percentage representation to 0...100.
    ///
    /// Some sources already write 0...100 values, so values above 1 are left
    /// untouched instead of being multiplied twice.
    public static func percent(_ value: Double) -> Double {
        guard value.isFinite else { return value }
        return value <= 1.0 ? value * 100.0 : value
    }

    /// Round a value to a small number of decimal places for cleaner payloads.
    public static func rounded(_ value: Double, places: Int = 2) -> Double {
        guard value.isFinite else { return value }
        let factor = pow(10.0, Double(places))
        return (value * factor).rounded() / factor
    }
}
