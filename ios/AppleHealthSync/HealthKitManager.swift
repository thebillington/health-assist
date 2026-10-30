import Foundation
import HealthKit
import AppleHealthSyncCore

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

        if let sleep = try? await sleepMetrics(now: now) {
            readings.merge(sleep) { _, new in new }
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

    private func sleepMetrics(now: Date) async throws -> [String: MetricReading] {
        guard let type = HKObjectType.categoryType(forIdentifier: .sleepAnalysis) else {
            return [:]
        }

        let calendar = Calendar.current
        let startOfDay = calendar.startOfDay(for: now)
        let windowStart = calendar.date(byAdding: .hour, value: -12, to: startOfDay)
            ?? now.addingTimeInterval(-12 * 3_600)
        let predicate = HKQuery.predicateForSamples(
            withStart: windowStart,
            end: now,
            options: []
        )
        let samples = try await categorySamples(type: type, predicate: predicate)

        var asleep: [DateInterval] = []
        var deep: [DateInterval] = []
        var rem: [DateInterval] = []
        var core: [DateInterval] = []
        var awake: [DateInterval] = []

        for sample in samples {
            guard let value = HKCategoryValueSleepAnalysis(rawValue: sample.value) else {
                continue
            }
            let interval = DateInterval(start: sample.startDate, end: sample.endDate)

            switch value {
            case .awake:
                awake.append(interval)
            case .asleepDeep:
                deep.append(interval)
                asleep.append(interval)
            case .asleepREM:
                rem.append(interval)
                asleep.append(interval)
            case .asleepCore:
                core.append(interval)
                asleep.append(interval)
            case .asleepUnspecified:
                asleep.append(interval)
            case .inBed:
                break
            @unknown default:
                break
            }
        }

        let total = IntervalMerger.mergedDuration(asleep) / 3_600
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
                value: IntervalMerger.mergedDuration(deep) / 3_600,
                unit: "h"
            ),
            "sleep_rem": reading(
                key: "sleep_rem",
                name: "REM sleep",
                value: IntervalMerger.mergedDuration(rem) / 3_600,
                unit: "h"
            ),
            "sleep_core": reading(
                key: "sleep_core",
                name: "Core sleep",
                value: IntervalMerger.mergedDuration(core) / 3_600,
                unit: "h"
            ),
            "sleep_awake": reading(
                key: "sleep_awake",
                name: "Awake time",
                value: IntervalMerger.mergedDuration(awake) / 3_600,
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
