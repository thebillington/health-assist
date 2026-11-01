# History and statistics

Health Sync does more than update the latest sensor value.

## First sync = full history

The first successful sync exports Apple Health history from **1 January 2014**
in resumable chunks. The app stores a checkpoint per metric, so an interrupted
export continues where it stopped on the next sync.

The data is uploaded in chunks of 1,000 samples. The server accepts up to 2,000
history samples per request, within the 256 KB request limit.

## What the app sends

| Metric type | History granularity |
| --- | --- |
| Discrete measurements (weight, body fat, blood pressure, VO2 max, …) | Every sample |
| Activity totals (steps, distance, energy, flights, water, …) | One daily total |
| High-frequency metrics (heart rate, HRV, oxygen, respiratory rate, audio exposure, …) | Hourly average |
| Sleep | One row per sleep session, for total/deep/REM/core/awake |
| Stand hours | One count per day |

The app reads every relevant HealthKit sample, then aggregates high-frequency
data so the upload stays practical. HealthKit percentages (body fat, oxygen
saturation) are converted from the 0–1 HealthKit representation to percent.

## How Home Assistant stores it

Home Assistant cannot backfill normal entity *state* history through a custom
integration. Health Sync imports historical samples as **long-term statistics**
under each sensor entity's `statistic_id`. They appear in:

**Developer Tools → Statistics** and in Statistics/History dashboards.

The live sensor state still updates normally. Historical statistics and live
states are two views of the same metric.

## Re-export

Tap **Re-export All History** in the app to reset all per-metric checkpoints and
upload the full history again. Re-importing the same UTC hour updates the
statistics row instead of duplicating it.

## Restarts

The live values are in memory. After a Home Assistant restart, sensors are
unavailable until the next sync, but previously imported statistics remain in
the recorder database.

## Limitations

- Individual raw states are not reconstructed; long-term statistics are hourly.
- A history import depends on the recorder being enabled. Home Assistant's
  default configuration includes it.
- The first full export can take minutes and needs the app to stay in the
  foreground. Checkpoints make it resumable.
- Workouts, ECG and clinical records are not exported yet.
