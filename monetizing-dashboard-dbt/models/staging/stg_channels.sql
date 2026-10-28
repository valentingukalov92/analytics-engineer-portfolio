SELECT
    contact_channel,
    channel_group
FROM {{ ref('raw_channels') }}  