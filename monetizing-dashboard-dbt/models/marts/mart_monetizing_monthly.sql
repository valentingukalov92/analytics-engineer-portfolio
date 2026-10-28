SELECT
    DATE_TRUNC('month', contact_date)  AS month_date,
    contact_channel,
    channel_group,
    product_promoted,
    device_type_name,
    SUM(contact_count)                 AS total_contacts,
    COUNT(DISTINCT contact_id)         AS unique_contacts
FROM {{ ref('int_contacts_enriched') }}
GROUP BY 1, 2, 3, 4, 5