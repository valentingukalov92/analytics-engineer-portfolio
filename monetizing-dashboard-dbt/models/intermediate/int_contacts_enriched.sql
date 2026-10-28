SELECT
    c.contact_id,
    c.contact_date,
    c.contact_channel,
    ch.channel_group,
    c.product_promoted,
    c.device_type_name,
    c.contact_count
FROM {{ ref('stg_contacts') }} c
LEFT JOIN {{ ref('stg_channels') }} ch
    ON c.contact_channel = ch.contact_channel