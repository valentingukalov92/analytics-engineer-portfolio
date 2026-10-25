# Example 02 — Discounts detail views: nulls, accepted values, ranges, duplicates

A DAG task that validates four discount detail views (live/retro ×
subscription types) before they feed the Discounts report. Same
warning-vs-error pattern as Example 01, but covers the full check
catalog: NULLs, accepted values, numeric ranges, and grain uniqueness.

## Checks

```python
import logging
import sys

from libs import dq_library as dq

logger = logging.getLogger(__name__)

try:
    results = [
        # Required dimensions must not be NULL (all four detail views)
        dq.check_nulls(
            "my_schema.detail_live_cbm",
            ["subs_id", "service_id", "valid_from_date",
             "device_type_name", "product_promoted", "user_client"],
            severity=dq.WARNING,
        ),
        dq.check_nulls(
            "my_schema.detail_retro_cbm",
            ["subs_id", "service_id", "valid_from_date",
             "device_type_name", "product_promoted", "user_client"],
            severity=dq.WARNING,
        ),
        dq.check_nulls(
            "my_schema.detail_live_mnp",
            ["subs_id", "service_id", "valid_from_date",
             "device_type_name", "product_promoted", "user_client"],
            severity=dq.WARNING,
        ),
        dq.check_nulls(
            "my_schema.detail_retro_mnp",
            ["subs_id", "service_id", "valid_from_date",
             "device_type_name", "product_promoted", "user_client"],
            severity=dq.WARNING,
        ),

        # SERVICE_STATUS_ID must be one of the known statuses
        dq.check_accepted_values(
            "my_schema.detail_live_cbm", "SERVICE_STATUS_ID", [1, 3, 4],
            severity=dq.WARNING,
        ),
        dq.check_accepted_values(
            "my_schema.detail_retro_cbm", "SERVICE_STATUS_ID", [1, 3, 4],
            severity=dq.WARNING,
        ),
        dq.check_accepted_values(
            "my_schema.detail_live_mnp", "SERVICE_STATUS_ID", [1, 3, 4],
            severity=dq.WARNING,
        ),
        dq.check_accepted_values(
            "my_schema.detail_retro_mnp", "SERVICE_STATUS_ID", [1, 3, 4],
            severity=dq.WARNING,
        ),

        # Discount value must be a percentage
        dq.check_range(
            "my_schema.detail_live_cbm", "DISCOUNT_VALUE",
            min_value=0, max_value=100, severity=dq.WARNING,
        ),
        dq.check_range(
            "my_schema.detail_retro_cbm", "DISCOUNT_VALUE",
            min_value=0, max_value=100, severity=dq.WARNING,
        ),
        dq.check_range(
            "my_schema.detail_live_mnp", "DISCOUNT_VALUE",
            min_value=0, max_value=100, severity=dq.WARNING,
        ),
        dq.check_range(
            "my_schema.detail_retro_mnp", "DISCOUNT_VALUE",
            min_value=0, max_value=100, severity=dq.WARNING,
        ),

        # Grain uniqueness (note: live views include REPORT_DATE)
        dq.check_duplicates(
            "my_schema.detail_live_cbm",
            ["SUBS_ID", "VALID_FROM_DATE", "VALID_TO_DATE",
             "SERVICE_ID", "SERVICE_STATUS_ID", "REPORT_DATE"],
            severity=dq.WARNING,
        ),
        dq.check_duplicates(
            "my_schema.detail_live_mnp",
            ["SUBS_ID", "VALID_FROM_DATE", "VALID_TO_DATE",
             "SERVICE_ID", "SERVICE_STATUS_ID", "REPORT_DATE"],
            severity=dq.WARNING,
        ),
        dq.check_duplicates(
            "my_schema.detail_retro_cbm",
            ["SUBS_ID", "VALID_FROM_DATE", "VALID_TO_DATE",
             "SERVICE_ID", "SERVICE_STATUS_ID"],
            severity=dq.WARNING,
        ),
        dq.check_duplicates(
            "my_schema.detail_retro_mnp",
            ["SUBS_ID", "VALID_FROM_DATE", "VALID_TO_DATE",
             "SERVICE_ID", "SERVICE_STATUS_ID"],
            severity=dq.WARNING,
        ),
    ]

    warnings = [c for c in results if c["status"] == dq.WARNING]

    if warnings:
        body = dq.render_warnings_html(results)
        # ... build and send WARNING email with `body` embedded ...
        send_email(subject="Data Quality Discounts",
                   body=body,
                   to="team@example.com")
    else:
        logger.info("Data quality checks passed with no warnings")

except Exception as ex:
    _, err, _ = sys.exc_info()
    logger.error(err)
    # ... build and send ERROR email with str(err) ...
    send_email(subject="ERROR: Data Quality Discounts",
               body=f"DQ task failed: {err}",
               to="team@example.com")