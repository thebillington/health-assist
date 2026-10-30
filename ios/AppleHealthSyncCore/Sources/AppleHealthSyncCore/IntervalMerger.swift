import Foundation

/// Merge overlapping time intervals before summing them.
///
/// HealthKit sleep samples can overlap when multiple devices recorded the same
/// night, and Apple Watch stage samples can sit inside a broader in-bed sample.
/// Summing raw sample durations would double count those.
public enum IntervalMerger {
    public static func mergedDuration(_ intervals: [DateInterval]) -> TimeInterval {
        let valid = intervals
            .filter { $0.duration > 0 }
            .sorted { $0.start < $1.start }

        guard var current = valid.first else { return 0 }

        var total: TimeInterval = 0
        for interval in valid.dropFirst() {
            if interval.start <= current.end {
                current = DateInterval(
                    start: current.start,
                    end: max(current.end, interval.end)
                )
            } else {
                total += current.duration
                current = interval
            }
        }
        total += current.duration
        return total
    }
}
