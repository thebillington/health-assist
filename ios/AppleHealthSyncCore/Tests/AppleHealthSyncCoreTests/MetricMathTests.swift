import Testing
@testable import AppleHealthSyncCore

@Suite("Metric math")
struct MetricMathTests {
    @Test("Fractions are converted to percentages")
    func percentConvertsFraction() {
        #expect(abs(MetricMath.percent(0.185) - 18.5) < 0.0001)
        #expect(abs(MetricMath.percent(0.98) - 98.0) < 0.0001)
    }

    @Test("Already-scaled percentages are left alone")
    func percentLeavesAlreadyScaledValues() {
        #expect(abs(MetricMath.percent(18.5) - 18.5) < 0.0001)
        #expect(abs(MetricMath.percent(100) - 100.0) < 0.0001)
    }

    @Test("Values are rounded to two places")
    func rounding() {
        #expect(abs(MetricMath.rounded(7.1234) - 7.12) < 0.0001)
        #expect(abs(MetricMath.rounded(7.1264) - 7.13) < 0.0001)
    }
}
