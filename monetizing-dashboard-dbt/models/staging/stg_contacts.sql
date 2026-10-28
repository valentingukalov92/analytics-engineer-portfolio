SELECT
    contact_id,
    CAST(contact_date AS DATE)     AS contact_date,
    contact_channel,
    product_promoted,
    device_type_name,
    CAST(contact_count AS INTEGER) AS contact_count
FROM {{ ref('raw_contacts') }}