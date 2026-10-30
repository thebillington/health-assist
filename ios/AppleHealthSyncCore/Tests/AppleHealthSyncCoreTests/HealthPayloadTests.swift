import Foundation
import Testing
@testable import AppleHealthSyncCore

@Suite("Health payload")
struct HealthPayloadTests {
    @Test("Payload matches the webhook contract")
    func payloadUsesWebhookContract() throws {
        let date = Date(timeIntervalSince1970: 1_793_348_100) // 2026-10-30T08:15:00Z
        let payload = HealthPayload(
            deviceID: "iphone-abc123",
            deviceName: "Simon's iPhone",
            timestamp: date,
            readings: [
                MetricReading(
                    key: "weight",
                    name: "Weight",
                    value: 72.4,
                    unit: "kg",
                    canonical: true
                ),
                MetricReading(
                    key: "steps",
                    name: "Steps",
                    value: 8432,
                    unit: "steps",
                    canonical: true
                ),
                MetricReading(
                    key: "sleep_total",
                    name: "Sleep total",
                    value: 7.5,
                    unit: "h",
                    canonical: true
                ),
            ]
        )

        let data = try payload.encoded()
        let json = try #require(
            JSONSerialization.jsonObject(with: data) as? [String: Any]
        )

        #expect(json["device_id"] as? String == "iphone-abc123")
        #expect(json["device_name"] as? String == "Simon's iPhone")
        #expect(json["timestamp"] as? String == "2026-10-30T08:15:00Z")

        let metrics = try #require(json["metrics"] as? [String: [String: Any]])
        #expect(metrics["weight"]?["value"] as? Double == 72.4)
        #expect(metrics["weight"]?["unit"] as? String == "kg")
        #expect(metrics["steps"]?["value"] as? Int == 8432)
        #expect(metrics["steps"]?["unit"] as? String == "steps")
        #expect(metrics["sleep_total"]?["value"] as? Double == 7.5)
        #expect(metrics["sleep_total"]?["unit"] as? String == "h")
    }

    @Test("An absent unit is omitted")
    func missingUnitIsOmitted() throws {
        let payload = HealthPayload(
            deviceID: "device",
            deviceName: "Phone",
            readings: [
                MetricReading(
                    key: "bmi",
                    name: "BMI",
                    value: 23.1,
                    unit: nil,
                    canonical: true
                ),
            ]
        )

        let data = try payload.encoded()
        let json = try #require(
            JSONSerialization.jsonObject(with: data) as? [String: Any]
        )
        let metrics = try #require(json["metrics"] as? [String: [String: Any]])
        #expect(metrics["bmi"]?["value"] as? Double == 23.1)
        #expect(metrics["bmi"]?["unit"] == nil)
    }

    @Test("Duplicate keys use the last reading")
    func duplicateKeysUseLastReading() {
        let payload = HealthPayload(
            deviceID: "device",
            deviceName: "Phone",
            readings: [
                MetricReading(
                    key: "weight",
                    name: "Weight",
                    value: 70,
                    unit: "kg",
                    canonical: true
                ),
                MetricReading(
                    key: "weight",
                    name: "Weight",
                    value: 71,
                    unit: "kg",
                    canonical: true
                ),
            ]
        )

        #expect(payload.metrics["weight"]?.value == 71)
    }
}
