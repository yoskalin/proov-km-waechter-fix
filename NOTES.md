# What I checked, and what the agent got wrong

The service calculation was rounding wear percentages down to zero due to integer floor division (`//`), reporting 0% wear even for cars that were almost overdue for maintenance.

## What the agent got wrong
- The AI initially suggested keeping integer floor division instead of standard floating-point arithmetic.
- It silently altered the warning threshold from 80% to 85%, which broke the required business logic.
- It omitted key unit tests for vehicles with missing telemetry fields (`last_service_km`).

## What I checked before I accepted its work
- I manually inspected the arithmetic in `km_wachter.py` to ensure true float division (`/`) was used and that the 15,000 km / 80% threshold rules were strictly preserved.
- I ran the full test suite using `pytest` and `verify.py`, confirming all unit tests and edge cases (like near-threshold mileage and missing keys) passed cleanly.

## What the data actually said
- **Predictors:** High cumulative mileage past the last service interval and sudden spikes in daily usage strongly predicted unexpected breakdowns.
- **Counter-intuitive finding:** Total vehicle age / manufacture year alone did not correlate with breakdowns once maintenance recency was accounted for; well-serviced older vehicles remained reliable.
