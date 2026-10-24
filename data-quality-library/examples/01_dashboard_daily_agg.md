# Example 01 — Dashboard daily aggregation: warnings + error handling

A DAG task that runs a set of data quality checks against a daily
aggregation table and sends an HTML email report. Warnings go out as a
WARNING report; any exception in the task triggers a separate ERROR email.

## Checks

```python
import logging
import smtplib
import sys
from email.message import EmailMessage

from libs import dq_library as dq

logger = logging.getLogger(__name__)

try:
    results = [
        # Grain uniqueness: daily / weekly / monthly
        dq.check_duplicates(
            "my_schema.dashboard_daily_agg",
            ["contact_date", "contact_channel", "os_name",
             "device_type_name", "product_promoted", "user_client"],
            severity=dq.WARNING,
        ),
        dq.check_duplicates(
            "my_schema.dashboard_daily_agg",
            ["week_date", "contact_channel", "os_name",
             "device_type_name", "product_promoted", "user_client"],
            severity=dq.WARNING,
        ),
        dq.check_duplicates(
            "my_schema.dashboard_daily_agg",
            ["month_date", "contact_channel", "os_name",
             "device_type_name", "product_promoted", "user_client"],
            severity=dq.WARNING,
        ),

        # Required dimensions must not be NULL
        dq.check_nulls(
            "my_schema.dashboard_daily_agg",
            ["CONTACT_CHANNEL", "TIME_PERIOD", "PRODUCT_PROMOTED"],
            severity=dq.WARNING,
        ),

        # Referential integrity: product values must exist in the dictionary
        dq.check_relationships(
            source_table="my_schema.dashboard_daily_agg",
            source_column="PRODUCT_PROMOTED",
            target_table="my_schema.dim_advertising_campaign_type",
            target_column="PRODUCT_PROMOTED",
            severity=dq.WARNING,
        ),
    ]

    warnings = [c for c in results if c["status"] == dq.WARNING]

    if warnings:
        body = dq.render_warnings_html(results)
        # ... build and send WARNING email with `body` embedded ...
        send_email(subject="Data Quality Monetizing Dashboard",
                   body=body,
                   to="team@example.com")
    else:
        logger.info("Data quality checks passed with no warnings")

except Exception as ex:
    _, err, _ = sys.exc_info()
    logger.error(err)
    # ... build and send ERROR email with str(err) ...
    send_email(subject="ERROR: Data Quality Monetizing Dashboard",
               body=f"DQ task failed: {err}",
               to="team@example.com")