import Foundation
import Testing
@testable import AppleHealthSyncCore

@Suite("Interval merger")
struct IntervalMergerTests {
    private let start = Date(timeIntervalSince1970: 1_000_000)

    private func interval(_ startOffset: TimeInterval, _ endOffset: TimeInterval) -> DateInterval {
        DateInterval(
            start: start.addingTimeInterval(startOffset),
            end: start.addingTimeInterval(endOffset)
        )
    }

    @Test("Empty input has zero duration")
    func emptyIsZero() {
        #expect(IntervalMerger.mergedDuration([]) == 0)
    }

    @Test("Disjoint intervals are summed")
    func disjointIntervalsAreSummed() {
        let intervals = [
            interval(0, 100),
            interval(200, 300),
        ]
        #expect(IntervalMerger.mergedDuration(intervals) == 200)
    }

    @Test("Overlapping intervals are merged")
    func overlappingIntervalsAreMerged() {
        let intervals = [
            interval(0, 100),
            interval(50, 150),
            interval(140, 200),
        ]
        #expect(IntervalMerger.mergedDuration(intervals) == 200)
    }

    @Test("Unsorted and duplicate intervals are merged")
    func unsortedAndDuplicateIntervalsAreMerged() {
        let intervals = [
            interval(200, 300),
            interval(0, 100),
            interval(0, 100),
        ]
        #expect(IntervalMerger.mergedDuration(intervals) == 200)
    }

    @Test("A contained interval does not extend the total")
    func containedIntervalDoesNotExtendTotal() {
        let intervals = [
            interval(0, 300),
            interval(50, 100),
        ]
        #expect(IntervalMerger.mergedDuration(intervals) == 300)
    }
}
