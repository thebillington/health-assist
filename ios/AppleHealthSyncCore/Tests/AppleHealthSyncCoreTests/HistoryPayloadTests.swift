import Foundation
import Testing
@testable import AppleHealthSyncCore

@Suite("History payload")
struct HistoryPayloadTests {
    @Test("History payload uses timestamped samples")
    func historyPayloadEncoding() throws {
        let timestamp = Date(timeIntervalSince1970: 1_793_348_100) // 2026-10-30T08:15:00Z
        let sampleTime = Date(timeIntervalSince1970: 1_793_308_800)
        let payload = HistoryPayload(
            deviceID: "device",
            deviceName: "Phone",
            timestamp: timestamp,
            history: [
                "steps": [
                    HistoryEntry(timestamp: sampleTime, value: 9000, unit: "steps"),
                    HistoryEntry(timestamp: sampleTime.addingTimeInterval(3600), value: 12.5, unit: "steps"),
                ],
            ]
        )

        let data = try payload.encoded()
        let json = try #require(
            JSONSerialization.jsonObject(with: data) as? [String: Any]
        )
        #expect(json["device_id"] as? String == "device")
        #expect(json["timestamp"] as? String == "2026-10-30T08:15:00Z")

        let history = try #require(json["history"] as? [String: [[String: Any]]])
        let steps = try #require(history["steps"])
        #expect(steps.count == 2)
        #expect(steps[0]["value"] as? Int == 9000)
        #expect(steps[0]["unit"] as? String == "steps")
        #expect(steps[0]["timestamp"] is String)
        #expect(steps[1]["value"] as? Double == 12.5)
    }
}
