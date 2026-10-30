import Foundation
import HealthKit
import AppleHealthSyncCore

enum MetricAggregation {
    case latest
    case todaySum
}

struct QuantityMetric: Identifiable {
    var id: String { key }

    let key: String
    let name: String
    let identifier: HKQuantityTypeIdentifier
    let unit: HKUnit
    let payloadUnit: String?
    let aggregation: MetricAggregation
    let isPercent: Bool
    let canonical: Bool

    func reading(from rawValue: Double) -> MetricReading {
        let transformed = isPercent ? MetricMath.percent(rawValue) : rawValue
        return MetricReading(
            key: key,
            name: name,
            value: MetricMath.rounded(transformed),
            unit: payloadUnit,
            canonical: canonical
        )
    }
}

enum HealthUnits {
    static let kilogram = HKUnit.gramUnit(with: .kilo)
    static let meter = HKUnit.meter()
    static let kilocalorie = HKUnit.kilocalorie()
    static let bpm = HKUnit.count().unitDivided(by: HKUnit.minute())
    static let milliseconds = HKUnit.secondUnit(with: .milli)
    static let mmHg = HKUnit.millimeterOfMercury()
    static let percent = HKUnit.percent()
    static let count = HKUnit.count()
    static let milliliter = HKUnit.literUnit(with: .milli)
    static let hour = HKUnit.hour()
    static let minute = HKUnit.minute()
    static let gram = HKUnit.gram()
    static let liter = HKUnit.liter()
    static let literPerMinute = HKUnit.liter().unitDivided(by: HKUnit.minute())
    static let metersPerSecond = HKUnit.meter().unitDivided(by: HKUnit.second())
    static let watt = HKUnit.watt()
    static let internationalUnit = HKUnit.internationalUnit()
    static let siemen = HKUnit.siemen()
    static let celsius = HKUnit.degreeCelsius()
    static let decibel = HKUnit.decibelAWeightedSoundPressureLevel()
    static let milligramsPerDeciliter = HKUnit.gramUnit(with: .milli)
        .unitDivided(by: HKUnit.literUnit(with: .deci))
    static let vo2Max = HKUnit.literUnit(with: .milli)
        .unitDivided(
            by: HKUnit.gramUnit(with: .kilo).unitMultiplied(by: HKUnit.minute())
        )
    static let kcalPerKilogramHour = HKUnit.kilocalorie()
        .unitDivided(
            by: HKUnit.gramUnit(with: .kilo).unitMultiplied(by: HKUnit.hour())
        )
}

enum MetricCatalog {
    /// Canonical metrics from the Home Assistant integration registry.
    static let canonical: [QuantityMetric] = [
        QuantityMetric(
            key: "weight",
            name: "Weight",
            identifier: .bodyMass,
            unit: HealthUnits.kilogram,
            payloadUnit: "kg",
            aggregation: .latest,
            isPercent: false,
            canonical: true
        ),
        QuantityMetric(
            key: "bmi",
            name: "BMI",
            identifier: .bodyMassIndex,
            unit: HealthUnits.count,
            payloadUnit: nil,
            aggregation: .latest,
            isPercent: false,
            canonical: true
        ),
        QuantityMetric(
            key: "body_fat",
            name: "Body fat",
            identifier: .bodyFatPercentage,
            unit: HealthUnits.percent,
            payloadUnit: "%",
            aggregation: .latest,
            isPercent: true,
            canonical: true
        ),
        QuantityMetric(
            key: "lean_body_mass",
            name: "Lean body mass",
            identifier: .leanBodyMass,
            unit: HealthUnits.kilogram,
            payloadUnit: "kg",
            aggregation: .latest,
            isPercent: false,
            canonical: true
        ),
        QuantityMetric(
            key: "steps",
            name: "Steps",
            identifier: .stepCount,
            unit: HealthUnits.count,
            payloadUnit: "steps",
            aggregation: .todaySum,
            isPercent: false,
            canonical: true
        ),
        QuantityMetric(
            key: "distance",
            name: "Distance",
            identifier: .distanceWalkingRunning,
            unit: HealthUnits.meter,
            payloadUnit: "m",
            aggregation: .todaySum,
            isPercent: false,
            canonical: true
        ),
        QuantityMetric(
            key: "active_energy",
            name: "Active energy",
            identifier: .activeEnergyBurned,
            unit: HealthUnits.kilocalorie,
            payloadUnit: "kcal",
            aggregation: .todaySum,
            isPercent: false,
            canonical: true
        ),
        QuantityMetric(
            key: "resting_heart_rate",
            name: "Resting heart rate",
            identifier: .restingHeartRate,
            unit: HealthUnits.bpm,
            payloadUnit: "bpm",
            aggregation: .latest,
            isPercent: false,
            canonical: true
        ),
        QuantityMetric(
            key: "heart_rate",
            name: "Heart rate",
            identifier: .heartRate,
            unit: HealthUnits.bpm,
            payloadUnit: "bpm",
            aggregation: .latest,
            isPercent: false,
            canonical: true
        ),
        QuantityMetric(
            key: "heart_rate_variability",
            name: "Heart rate variability",
            identifier: .heartRateVariabilitySDNN,
            unit: HealthUnits.milliseconds,
            payloadUnit: "ms",
            aggregation: .latest,
            isPercent: false,
            canonical: true
        ),
        QuantityMetric(
            key: "respiratory_rate",
            name: "Respiratory rate",
            identifier: .respiratoryRate,
            unit: HealthUnits.bpm,
            payloadUnit: "breaths/min",
            aggregation: .latest,
            isPercent: false,
            canonical: true
        ),
        QuantityMetric(
            key: "blood_oxygen",
            name: "Blood oxygen",
            identifier: .oxygenSaturation,
            unit: HealthUnits.percent,
            payloadUnit: "%",
            aggregation: .latest,
            isPercent: true,
            canonical: true
        ),
        QuantityMetric(
            key: "systolic",
            name: "Systolic blood pressure",
            identifier: .bloodPressureSystolic,
            unit: HealthUnits.mmHg,
            payloadUnit: "mmHg",
            aggregation: .latest,
            isPercent: false,
            canonical: true
        ),
        QuantityMetric(
            key: "diastolic",
            name: "Diastolic blood pressure",
            identifier: .bloodPressureDiastolic,
            unit: HealthUnits.mmHg,
            payloadUnit: "mmHg",
            aggregation: .latest,
            isPercent: false,
            canonical: true
        ),
        QuantityMetric(
            key: "vo2_max",
            name: "VO2 max",
            identifier: .vo2Max,
            unit: HealthUnits.vo2Max,
            payloadUnit: "mL/kg/min",
            aggregation: .latest,
            isPercent: false,
            canonical: true
        ),
        QuantityMetric(
            key: "flights_climbed",
            name: "Flights climbed",
            identifier: .flightsClimbed,
            unit: HealthUnits.count,
            payloadUnit: "flights",
            aggregation: .todaySum,
            isPercent: false,
            canonical: true
        ),
        QuantityMetric(
            key: "water_intake",
            name: "Water intake",
            identifier: .dietaryWater,
            unit: HealthUnits.milliliter,
            payloadUnit: "mL",
            aggregation: .todaySum,
            isPercent: false,
            canonical: true
        ),
    ]

    /// Extra HealthKit quantity types that become generic Home Assistant
    /// sensors. The user can turn these off to keep the permission sheet short.
    static let extras: [QuantityMetric] = [
        extra(.appleSleepingWristTemperature, unit: HealthUnits.celsius, payloadUnit: "°C"),
        extra(.appleWalkingSteadiness, unit: HealthUnits.percent, payloadUnit: "%", percent: true),
        extra(.atrialFibrillationBurden, unit: HealthUnits.percent, payloadUnit: "%", percent: true),
        extra(.basalBodyTemperature, unit: HealthUnits.celsius, payloadUnit: "°C"),
        extra(
            .basalEnergyBurned,
            unit: HealthUnits.kilocalorie,
            payloadUnit: "kcal",
            aggregation: .todaySum
        ),
        extra(.bloodGlucose, unit: HealthUnits.milligramsPerDeciliter, payloadUnit: "mg/dL"),
        extra(.bloodAlcoholContent, unit: HealthUnits.percent, payloadUnit: "%", percent: true),
        extra(.bodyTemperature, unit: HealthUnits.celsius, payloadUnit: "°C"),
        extra(
            .dietaryCarbohydrates,
            unit: HealthUnits.gram,
            payloadUnit: "g",
            aggregation: .todaySum
        ),
        extra(
            .dietaryEnergyConsumed,
            unit: HealthUnits.kilocalorie,
            payloadUnit: "kcal",
            aggregation: .todaySum
        ),
        extra(.dietaryFatTotal, unit: HealthUnits.gram, payloadUnit: "g", aggregation: .todaySum),
        extra(.dietaryFiber, unit: HealthUnits.gram, payloadUnit: "g", aggregation: .todaySum),
        extra(.dietaryProtein, unit: HealthUnits.gram, payloadUnit: "g", aggregation: .todaySum),
        extra(.dietarySugar, unit: HealthUnits.gram, payloadUnit: "g", aggregation: .todaySum),
        extra(.dietaryCaffeine, unit: HealthUnits.gram, payloadUnit: "g", aggregation: .todaySum),
        extra(.dietarySodium, unit: HealthUnits.gram, payloadUnit: "g", aggregation: .todaySum),
        extra(.height, unit: HealthUnits.meter, payloadUnit: "m"),
        extra(.waistCircumference, unit: HealthUnits.meter, payloadUnit: "m"),
        extra(.heartRateRecoveryOneMinute, unit: HealthUnits.bpm, payloadUnit: "bpm"),
        extra(.walkingHeartRateAverage, unit: HealthUnits.bpm, payloadUnit: "bpm"),
        extra(
            .peripheralPerfusionIndex,
            unit: HealthUnits.percent,
            payloadUnit: "%",
            percent: true
        ),
        extra(
            .environmentalAudioExposure,
            unit: HealthUnits.decibel,
            payloadUnit: "dBASPL"
        ),
        extra(
            .headphoneAudioExposure,
            unit: HealthUnits.decibel,
            payloadUnit: "dBASPL"
        ),
        extra(
            .appleExerciseTime,
            unit: HealthUnits.minute,
            payloadUnit: "min",
            aggregation: .todaySum
        ),
        extra(
            .appleMoveTime,
            unit: HealthUnits.minute,
            payloadUnit: "min",
            aggregation: .todaySum
        ),
        extra(
            .appleStandTime,
            unit: HealthUnits.minute,
            payloadUnit: "min",
            aggregation: .todaySum
        ),
        extra(
            .timeInDaylight,
            unit: HealthUnits.minute,
            payloadUnit: "min",
            aggregation: .todaySum
        ),
        extra(
            .numberOfTimesFallen,
            unit: HealthUnits.count,
            payloadUnit: "count",
            aggregation: .todaySum
        ),
        extra(
            .pushCount,
            unit: HealthUnits.count,
            payloadUnit: "count",
            aggregation: .todaySum
        ),
        extra(
            .swimmingStrokeCount,
            unit: HealthUnits.count,
            payloadUnit: "count",
            aggregation: .todaySum
        ),
        extra(
            .inhalerUsage,
            unit: HealthUnits.count,
            payloadUnit: "count",
            aggregation: .todaySum
        ),
        extra(
            .insulinDelivery,
            unit: HealthUnits.internationalUnit,
            payloadUnit: "IU",
            aggregation: .todaySum
        ),
        extra(
            .numberOfAlcoholicBeverages,
            unit: HealthUnits.count,
            payloadUnit: "count",
            aggregation: .todaySum
        ),
        extra(.forcedExpiratoryVolume1, unit: HealthUnits.liter, payloadUnit: "L"),
        extra(.forcedVitalCapacity, unit: HealthUnits.liter, payloadUnit: "L"),
        extra(
            .peakExpiratoryFlowRate,
            unit: HealthUnits.literPerMinute,
            payloadUnit: "L/min"
        ),
        extra(.sixMinuteWalkTestDistance, unit: HealthUnits.meter, payloadUnit: "m"),
        extra(.walkingSpeed, unit: HealthUnits.metersPerSecond, payloadUnit: "m/s"),
        extra(.stairAscentSpeed, unit: HealthUnits.metersPerSecond, payloadUnit: "m/s"),
        extra(.stairDescentSpeed, unit: HealthUnits.metersPerSecond, payloadUnit: "m/s"),
        extra(.runningPower, unit: HealthUnits.watt, payloadUnit: "W"),
        extra(.cyclingPower, unit: HealthUnits.watt, payloadUnit: "W"),
        extra(.underwaterDepth, unit: HealthUnits.meter, payloadUnit: "m"),
        extra(.waterTemperature, unit: HealthUnits.celsius, payloadUnit: "°C"),
        extra(
            .appleSleepingBreathingDisturbances,
            unit: HealthUnits.count,
            payloadUnit: "count"
        ),
        extra(
            .distanceCycling,
            unit: HealthUnits.meter,
            payloadUnit: "m",
            aggregation: .todaySum
        ),
        extra(
            .distanceSwimming,
            unit: HealthUnits.meter,
            payloadUnit: "m",
            aggregation: .todaySum
        ),
        extra(
            .distanceWheelchair,
            unit: HealthUnits.meter,
            payloadUnit: "m",
            aggregation: .todaySum
        ),
        extra(
            .distanceDownhillSnowSports,
            unit: HealthUnits.meter,
            payloadUnit: "m",
            aggregation: .todaySum
        ),
        extra(.electrodermalActivity, unit: HealthUnits.siemen, payloadUnit: "S"),
        extra(
            .physicalEffort,
            unit: HealthUnits.kcalPerKilogramHour,
            payloadUnit: "kcal/(kg*hr)"
        ),
        extra(.runningSpeed, unit: HealthUnits.metersPerSecond, payloadUnit: "m/s"),
        extra(.cyclingSpeed, unit: HealthUnits.metersPerSecond, payloadUnit: "m/s"),
    ]

    static func readTypes(includeExtras: Bool) -> Set<HKObjectType> {
        var types = Set<HKObjectType>()
        let metrics = includeExtras ? canonical + extras : canonical

        for metric in metrics {
            if let type = HKObjectType.quantityType(forIdentifier: metric.identifier) {
                types.insert(type)
            }
        }

        if let sleep = HKObjectType.categoryType(forIdentifier: .sleepAnalysis) {
            types.insert(sleep)
        }
        if let stand = HKObjectType.categoryType(forIdentifier: .appleStandHour) {
            types.insert(stand)
        }
        return types
    }

    private static func extra(
        _ identifier: HKQuantityTypeIdentifier,
        unit: HKUnit,
        payloadUnit: String?,
        aggregation: MetricAggregation = .latest,
        percent: Bool = false
    ) -> QuantityMetric {
        let key = snakeCase(identifier)
        let name = key
            .split(separator: "_")
            .map { $0.capitalized }
            .joined(separator: " ")

        return QuantityMetric(
            key: key,
            name: name,
            identifier: identifier,
            unit: unit,
            payloadUnit: payloadUnit,
            aggregation: aggregation,
            isPercent: percent,
            canonical: false
        )
    }

    private static func snakeCase(_ identifier: HKQuantityTypeIdentifier) -> String {
        var raw = identifier.rawValue
        let prefix = "HKQuantityTypeIdentifier"
        if raw.hasPrefix(prefix) {
            raw.removeFirst(prefix.count)
        }

        var result = ""
        for (index, character) in raw.enumerated() {
            if character.isUppercase {
                if index > 0 {
                    result.append("_")
                }
                result.append(contentsOf: character.lowercased())
            } else {
                result.append(character)
            }
        }
        return result
    }
}
