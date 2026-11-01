import Foundation
import HealthKit
import AppleHealthSyncCore

enum HistoryAggregation {
    case samples
    case hourlyAverage
    case dailySum
}

extension QuantityMetric {
    var historyAggregation: HistoryAggregation {
        if aggregation == .todaySum {
            return .dailySum
        }
        if HealthKitManager.highFrequencyIdentifiers.contains(identifier) {
            return .hourlyAverage
        }
        return .samples
    }
}

enum HealthKitError: LocalizedError {
    case unavailable
    case authorizationFailed

    var errorDescription: String? {
        switch self {
        case .unavailable:
            "HealthKit is not available on this device. You can still use Send a Test Payload."
        case .authorizationFailed:
            "Apple Health access could not be requested."
        }
    }
}

final class HealthKitManager {
    private let store = HKHealthStore()

    var isAvailable: Bool {
        HKHealthStore.isHealthDataAvailable()
    }

    func requestAuthorization(includeExtras: Bool) async throws {
        guard isAvailable else { throw HealthKitError.unavailable }

        let types = MetricCatalog.readTypes(includeExtras: includeExtras)
        try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<Void, Error>) in
            store.requestAuthorization(toShare: [], read: types) { success, error in
                if let error {
                    continuation.resume(throwing: error)
                } else if success {
                    continuation.resume()
                } else {
                    continuation.resume(throwing: HealthKitError.authorizationFailed)
                }
            }
        }
    }

    func authorizationRequestStatus(includeExtras: Bool) async -> HKAuthorizationRequestStatus {
        guard isAvailable else { return .unknown }

        let types = MetricCatalog.readTypes(includeExtras: includeExtras)
        return await withCheckedContinuation { continuation in
            store.getRequestStatusForAuthorization(toShare: [], read: types) { status, _ in
                continuation.resume(returning: status)
            }
        }
    }

    /// Read all available metrics. Individual query failures are skipped so a
    /// missing or denied type does not prevent the rest of the sync.
    func fetchMetrics(includeExtras: Bool) async -> [MetricReading] {
        guard isAvailable else { return [] }

        let now = Date()
        let calendar = Calendar.current
        let startOfDay = calendar.startOfDay(for: now)
        let latestSince = calendar.date(byAdding: .day, value: -365, to: now)
            ?? now.addingTimeInterval(-365 * 86_400)

        var readings: [String: MetricReading] = [:]

        for metric in MetricCatalog.canonical {
            guard let type = HKObjectType.quantityType(forIdentifier: metric.identifier) else {
                continue
            }
            if let raw = await quantityValue(
                for: metric,
                type: type,
                latestSince: latestSince,
                startOfDay: startOfDay
            ) {
                readings[metric.key] = metric.reading(from: raw)
            }
        }

        do {
            let sleep = try await sleepMetrics(now: now)
            #if DEBUG
            print("AHS sleep metrics: \(sleep.mapValues(\.value))")
            #endif
            readings.merge(sleep) { _, new in new }
        } catch {
            #if DEBUG
            print("AHS sleep query failed: \(error)")
            #endif
        }

        if let stand = try? await standHoursMetric(start: startOfDay) {
            readings[stand.key] = stand
        }

        if includeExtras {
            let canonicalIdentifiers = Set(MetricCatalog.canonical.map(\.identifier))
            for metric in MetricCatalog.extras where !canonicalIdentifiers.contains(metric.identifier) {
                guard let type = HKObjectType.quantityType(forIdentifier: metric.identifier) else {
                    continue
                }
                if let raw = await quantityValue(
                    for: metric,
                    type: type,
                    latestSince: latestSince,
                    startOfDay: startOfDay
                ) {
                    readings[metric.key] = metric.reading(from: raw)
                }
            }
        }

        return readings.values.sorted {
            $0.name.localizedCaseInsensitiveCompare($1.name) == .orderedAscending
        }
    }

    private func quantityValue(
        for metric: QuantityMetric,
        type: HKQuantityType,
        latestSince: Date,
        startOfDay: Date
    ) async -> Double? {
        do {
            switch metric.aggregation {
            case .latest:
                return try await latestSample(
                    type: type,
                    unit: metric.unit,
                    since: latestSince
                )
            case .todaySum:
                return try await cumulativeSum(
                    type: type,
                    unit: metric.unit,
                    start: startOfDay
                )
            }
        } catch {
            return nil
        }
    }

    private func latestSample(
        type: HKQuantityType,
        unit: HKUnit,
        since: Date
    ) async throws -> Double? {
        try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<Double?, Error>) in
            let predicate = HKQuery.predicateForSamples(
                withStart: since,
                end: Date(),
                options: .strictStartDate
            )
            let sort = NSSortDescriptor(
                key: HKSampleSortIdentifierEndDate,
                ascending: false
            )
            let query = HKSampleQuery(
                sampleType: type,
                predicate: predicate,
                limit: 1,
                sortDescriptors: [sort]
            ) { _, samples, error in
                if let error {
                    continuation.resume(throwing: error)
                    return
                }
                guard let sample = samples?.first as? HKQuantitySample else {
                    continuation.resume(returning: nil)
                    return
                }
                continuation.resume(returning: sample.quantity.doubleValue(for: unit))
            }
            store.execute(query)
        }
    }

    private func cumulativeSum(
        type: HKQuantityType,
        unit: HKUnit,
        start: Date
    ) async throws -> Double? {
        try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<Double?, Error>) in
            let predicate = HKQuery.predicateForSamples(
                withStart: start,
                end: Date(),
                options: .strictStartDate
            )
            let query = HKStatisticsQuery(
                quantityType: type,
                quantitySamplePredicate: predicate,
                options: .cumulativeSum
            ) { _, statistics, error in
                if let error {
                    continuation.resume(throwing: error)
                    return
                }
                continuation.resume(
                    returning: statistics?.sumQuantity()?.doubleValue(for: unit)
                )
            }
            store.execute(query)
        }
    }

    static let highFrequencyIdentifiers: Set<HKQuantityTypeIdentifier> = [
        .heartRate,
        .heartRateVariabilitySDNN,
        .respiratoryRate,
        .oxygenSaturation,
        .walkingHeartRateAverage,
        .heartRateRecoveryOneMinute,
        .environmentalAudioExposure,
        .headphoneAudioExposure,
        .peripheralPerfusionIndex,
        .electrodermalActivity,
        .physicalEffort,
        .runningPower,
        .cyclingPower,
        .runningSpeed,
        .cyclingSpeed,
        .stairAscentSpeed,
        .stairDescentSpeed,
        .walkingSpeed,
    ]

    /// Read one metric's history, aggregated appropriately for Home Assistant
    /// long-term statistics (one mean per hour, or one sum per day).
    func quantityHistory(
        for metric: QuantityMetric,
        from start: Date,
        to end: Date
    ) async throws -> [HistoryEntry] {
        guard start < end,
              let type = HKObjectType.quantityType(forIdentifier: metric.identifier) else {
            return []
        }

        switch metric.historyAggregation {
        case .samples:
            return try await quantitySamples(type: type, metric: metric, start: start, end: end)
        case .hourlyAverage:
            return try await statisticsHistory(
                type: type,
                metric: metric,
                start: start,
                end: end,
                interval: DateComponents(hour: 1),
                options: .discreteAverage
            )
        case .dailySum:
            return try await statisticsHistory(
                type: type,
                metric: metric,
                start: start,
                end: end,
                interval: DateComponents(day: 1),
                options: .cumulativeSum
            )
        }
    }

    private func quantitySamples(
        type: HKQuantityType,
        metric: QuantityMetric,
        start: Date,
        end: Date
    ) async throws -> [HistoryEntry] {
        try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<[HistoryEntry], Error>) in
            let predicate = HKQuery.predicateForSamples(withStart: start, end: end, options: [])
            let sort = NSSortDescriptor(
                key: HKSampleSortIdentifierStartDate,
                ascending: true
            )
            let query = HKSampleQuery(
                sampleType: type,
                predicate: predicate,
                limit: HKObjectQueryNoLimit,
                sortDescriptors: [sort]
            ) { _, samples, error in
                if let error {
                    continuation.resume(throwing: error)
                    return
                }

                let entries = (samples as? [HKQuantitySample] ?? []).compactMap { sample -> HistoryEntry? in
                    let raw = sample.quantity.doubleValue(for: metric.unit)
                    let value = metric.isPercent ? MetricMath.percent(raw) : raw
                    guard value.isFinite else { return nil }
                    return HistoryEntry(
                        timestamp: sample.endDate,
                        value: MetricMath.rounded(value),
                        unit: metric.payloadUnit
                    )
                }
                continuation.resume(returning: entries)
            }
            store.execute(query)
        }
    }

    private func statisticsHistory(
        type: HKQuantityType,
        metric: QuantityMetric,
        start: Date,
        end: Date,
        interval: DateComponents,
        options: HKStatisticsOptions
    ) async throws -> [HistoryEntry] {
        let calendar = Calendar.current
        let anchor: Date
        if interval.day != nil {
            anchor = calendar.startOfDay(for: start)
        } else {
            let components = calendar.dateComponents(
                [.year, .month, .day, .hour],
                from: start
            )
            anchor = calendar.date(from: components) ?? start
        }

        return try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<[HistoryEntry], Error>) in
            let predicate = HKQuery.predicateForSamples(withStart: start, end: end, options: [])
            let query = HKStatisticsCollectionQuery(
                quantityType: type,
                quantitySamplePredicate: predicate,
                options: options,
                anchorDate: anchor,
                intervalComponents: interval
            )
            query.initialResultsHandler = { _, collection, error in
                if let error {
                    continuation.resume(throwing: error)
                    return
                }

                let entries = collection?.statistics().compactMap { statistics -> HistoryEntry? in
                    let quantity = options.contains(.cumulativeSum)
                        ? statistics.sumQuantity()
                        : statistics.averageQuantity()
                    guard let quantity else { return nil }

                    let raw = quantity.doubleValue(for: metric.unit)
                    let value = metric.isPercent ? MetricMath.percent(raw) : raw
                    guard value.isFinite else { return nil }
                    return HistoryEntry(
                        timestamp: statistics.startDate,
                        value: MetricMath.rounded(value),
                        unit: metric.payloadUnit
                    )
                } ?? []
                continuation.resume(returning: entries)
            }
            store.execute(query)
        }
    }

    /// Sleep history is one row per sleep session for each stage.
    func sleepHistory(
        from start: Date,
        to end: Date
    ) async throws -> [String: [HistoryEntry]] {
        guard start < end,
              let type = HKObjectType.categoryType(forIdentifier: .sleepAnalysis) else {
            return [:]
        }

        let predicate = HKQuery.predicateForSamples(withStart: start, end: end, options: [])
        let samples = try await categorySamples(type: type, predicate: predicate)
        let sessions = sleepSessions(from: samples)

        var result: [String: [HistoryEntry]] = [
            "sleep_total": [],
            "sleep_deep": [],
            "sleep_rem": [],
            "sleep_core": [],
            "sleep_awake": [],
        ]

        for session in sessions {
            let durations = sleepDurations(for: session)
            let total = durations["sleep_total"] ?? 0
            guard total > 0,
                  let timestamp = session.map(\.interval.end).max() else {
                continue
            }
            for key in result.keys {
                result[key]?.append(
                    HistoryEntry(
                        timestamp: timestamp,
                        value: MetricMath.rounded(durations[key] ?? 0),
                        unit: "h"
                    )
                )
            }
        }

        return result
    }

    /// Stand hours are one count per day.
    func standHistory(from start: Date, to end: Date) async throws -> [HistoryEntry] {
        guard start < end,
              let type = HKObjectType.categoryType(forIdentifier: .appleStandHour) else {
            return []
        }

        let predicate = HKQuery.predicateForSamples(withStart: start, end: end, options: [])
        let samples = try await categorySamples(type: type, predicate: predicate)
        let calendar = Calendar.current
        var byDay: [Date: Int] = [:]

        for sample in samples {
            guard let value = HKCategoryValueAppleStandHour(rawValue: sample.value) else {
                continue
            }
            let day = calendar.startOfDay(for: sample.startDate)
            byDay[day, default: 0] += (value == .stood ? 1 : 0)
        }

        return byDay
            .sorted { $0.key < $1.key }
            .map { day, hours in
                HistoryEntry(
                    timestamp: day,
                    value: Double(hours),
                    unit: "h"
                )
            }
    }

    private struct SleepEntry {
        let interval: DateInterval
        let value: HKCategoryValueSleepAnalysis
    }

    private func sleepSessions(from samples: [HKCategorySample]) -> [[SleepEntry]] {
        var entries: [SleepEntry] = []

        for sample in samples {
            guard let value = HKCategoryValueSleepAnalysis(rawValue: sample.value),
                  value != .inBed else {
                continue
            }
            let interval = DateInterval(start: sample.startDate, end: sample.endDate)
            guard interval.duration > 0 else { continue }
            entries.append(SleepEntry(interval: interval, value: value))
        }

        entries.sort { $0.interval.start < $1.interval.start }

        var sessions: [[SleepEntry]] = []
        var current: [SleepEntry] = []
        var sessionEnd: Date?

        for entry in entries {
            if let sessionEnd,
               entry.interval.start.timeIntervalSince(sessionEnd) > 4 * 3_600 {
                sessions.append(current)
                current = []
            }
            current.append(entry)
            sessionEnd = max(sessionEnd ?? entry.interval.end, entry.interval.end)
        }
        if !current.isEmpty {
            sessions.append(current)
        }
        return sessions
    }

    private func sleepDurations(for session: [SleepEntry]) -> [String: Double] {
        var asleep: [DateInterval] = []
        var deep: [DateInterval] = []
        var rem: [DateInterval] = []
        var core: [DateInterval] = []
        var awake: [DateInterval] = []

        for entry in session {
            switch entry.value {
            case .awake:
                awake.append(entry.interval)
            case .asleepDeep:
                deep.append(entry.interval)
                asleep.append(entry.interval)
            case .asleepREM:
                rem.append(entry.interval)
                asleep.append(entry.interval)
            case .asleepCore:
                core.append(entry.interval)
                asleep.append(entry.interval)
            case .asleepUnspecified:
                asleep.append(entry.interval)
            case .inBed:
                break
            @unknown default:
                break
            }
        }

        return [
            "sleep_total": IntervalMerger.mergedDuration(asleep) / 3_600,
            "sleep_deep": IntervalMerger.mergedDuration(deep) / 3_600,
            "sleep_rem": IntervalMerger.mergedDuration(rem) / 3_600,
            "sleep_core": IntervalMerger.mergedDuration(core) / 3_600,
            "sleep_awake": IntervalMerger.mergedDuration(awake) / 3_600,
        ]
    }

    private func sleepMetrics(now: Date) async throws -> [String: MetricReading] {
        guard let type = HKObjectType.categoryType(forIdentifier: .sleepAnalysis) else {
            return [:]
        }

        let calendar = Calendar.current
        // Sleep is often recorded in a block that ends before "last night" if
        // the watch was not worn, so look back a week and use the most recent
        // meaningful sleep session rather than requiring data from the last
        // 12 hours.
        let windowStart = calendar.date(byAdding: .day, value: -7, to: now)
            ?? now.addingTimeInterval(-7 * 86_400)
        let predicate = HKQuery.predicateForSamples(
            withStart: windowStart,
            end: now,
            options: []
        )
        let samples = try await categorySamples(type: type, predicate: predicate)
        let sessions = sleepSessions(from: samples)

        // Prefer the most recent session with at least an hour of sleep so a
        // short nap does not replace the last real night.
        let chosen = sessions.reversed().first { session in
            let durations = sleepDurations(for: session)
            return (durations["sleep_total"] ?? 0) >= 1
        } ?? sessions.last

        guard let chosen else { return [:] }

        let durations = sleepDurations(for: chosen)
        let total = durations["sleep_total"] ?? 0
        #if DEBUG
        print("AHS sleep session selected: \(total)h from \(chosen.count) samples")
        #endif
        guard total > 0 else { return [:] }

        return [
            "sleep_total": reading(
                key: "sleep_total",
                name: "Sleep total",
                value: total,
                unit: "h"
            ),
            "sleep_deep": reading(
                key: "sleep_deep",
                name: "Deep sleep",
                value: durations["sleep_deep"] ?? 0,
                unit: "h"
            ),
            "sleep_rem": reading(
                key: "sleep_rem",
                name: "REM sleep",
                value: durations["sleep_rem"] ?? 0,
                unit: "h"
            ),
            "sleep_core": reading(
                key: "sleep_core",
                name: "Core sleep",
                value: durations["sleep_core"] ?? 0,
                unit: "h"
            ),
            "sleep_awake": reading(
                key: "sleep_awake",
                name: "Awake time",
                value: durations["sleep_awake"] ?? 0,
                unit: "h"
            ),
        ]
    }

    private func standHoursMetric(start: Date) async throws -> MetricReading? {
        guard let type = HKObjectType.categoryType(forIdentifier: .appleStandHour) else {
            return nil
        }

        let predicate = HKQuery.predicateForSamples(withStart: start, end: Date(), options: [])
        let samples = try await categorySamples(type: type, predicate: predicate)
        guard !samples.isEmpty else { return nil }

        let stood = samples.reduce(into: 0) { count, sample in
            guard let value = HKCategoryValueAppleStandHour(rawValue: sample.value),
                  value == .stood else {
                return
            }
            count += 1
        }

        return reading(
            key: "stand_hours",
            name: "Stand hours",
            value: Double(stood),
            unit: "h"
        )
    }

    private func categorySamples(
        type: HKCategoryType,
        predicate: NSPredicate
    ) async throws -> [HKCategorySample] {
        try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<[HKCategorySample], Error>) in
            let sort = NSSortDescriptor(
                key: HKSampleSortIdentifierStartDate,
                ascending: true
            )
            let query = HKSampleQuery(
                sampleType: type,
                predicate: predicate,
                limit: HKObjectQueryNoLimit,
                sortDescriptors: [sort]
            ) { _, samples, error in
                if let error {
                    continuation.resume(throwing: error)
                    return
                }
                let categorySamples = samples?.compactMap { $0 as? HKCategorySample } ?? []
                continuation.resume(returning: categorySamples)
            }
            store.execute(query)
        }
    }

    private func reading(
        key: String,
        name: String,
        value: Double,
        unit: String
    ) -> MetricReading {
        MetricReading(
            key: key,
            name: name,
            value: MetricMath.rounded(value),
            unit: unit,
            canonical: true
        )
    }
}
