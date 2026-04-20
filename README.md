# Interval Metrics Dashboard

Streamlit dashboard that reads the interval-level metrics Excel export and surfaces
team-wise performance (Chat TTA, Chat TFR, Email TFR, ABN, ABN%) at overall /
daily / hourly / 15-min interval granularity with an auto-generated action plan.

## Time handling (strict)

- Hourly and interval views use `created_at_interval` **only** (HH:MM, 15-min buckets).
  Hour = first 2 chars of `created_at_interval`.
- The calendar date for day-level views is parsed from `created_at` **only**.
- No other column is used for time calculations.

## Metric units (from the source file)

| Metric              | Unit      | Source column           |
|---------------------|-----------|-------------------------|
| Chat TTA            | seconds   | `Chat TTA`              |
| Chat TFR            | minutes   | `Chat TFR`              |
| Email TFR           | hours     | `Email TFR`             |
| ABN (count)         | cases     | `ABN` (non-null rows)   |
| Chat Volume Actual  | cases     | `Chat Volume (Actual)`  |
| Email Volume Actual | cases     | `Email Volume (Actual)` |
| ABN %               | %         | count(ABN) / count(Chat Volume Actual) |

## Run

```bash
cd "/Users/matsyendrashukla/My Apps/interval-metrics-dashboard"
pip install -r requirements.txt
streamlit run app.py
```

The sidebar has a file uploader; if nothing is uploaded it will try the default
path:
`/Users/matsyendrashukla/Downloads/Drilldown_in_Interval_Level_Metrics-69e674ab093f334cba5c0911.xlsx`

## Pages

- **Overview** (`app.py`) — KPI strip, team scorecard, action plan.
- **Team View** — per-team deep dive with volume, TTA, TFR, ABN% charts.
- **Hourly Heatmap** — Team × Hour heatmaps for every metric.
- **Daily Trend** — per-date trend lines (date from `created_at`).
- **Interval Drilldown** — sortable 15-min `created_at_interval` table.

## Tuning thresholds

Edit the constants at the top of `action_plan.py`:

- `CHAT_TTA_TARGET_SEC` (default 60)
- `CHAT_TFR_TARGET_MIN` (default 2)
- `EMAIL_TFR_TARGET_HR` (default 4)
- `ABN_PCT_TARGET` (default 0.03)
- `HOTSPOT_MULTIPLIER` (default 1.5) and `HOTSPOT_MIN_VOLUME` (default 20)
