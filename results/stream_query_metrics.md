| query | micro_batches | input_rows | avg_input_rows_per_s | avg_processed_rows_per_s | avg_batch_duration_ms | max_batch_duration_ms | rows_dropped_by_watermark | max_state_rows | last_watermark |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| events | 50 | 2282 | 1.53 | 30.00 | 1508.44 | 2105 | 0 | 0 |  |
| sliding | 51 | 2282 | 1.51 | 28.24 | 1557.08 | 2131 | 0 | 55 | 2026-11-14T16:12:42.000Z |
| tumbling | 51 | 2282 | 1.50 | 28.37 | 1541.69 | 2102 | 8 | 6 | 2026-11-14T16:12:43.000Z |
