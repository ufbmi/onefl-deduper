

-- Create two tables to store UUIDs with special properties

insert into dbo.linkage_r1
select linkage_uuid from (
select
    linkage_uuid
    , count(distinct partner_code) as cc
from
    linkage
where
    partner_code in ('UFH', 'FLM')
    AND rule_id = 1
group by linkage_uuid having count(distinct partner_code) > 1
) as x


insert into dbo.linkage_r2
select linkage_uuid from (
select
    linkage_uuid
    , count(distinct partner_code) as cc
from
    linkage
where
    partner_code in ('UFH', 'FLM')
    AND rule_id = 2
group by linkage_uuid having count(distinct partner_code) > 1
) as x


-- Find patients matched by R1 only
select
    partner_code, linkage_patid, ln.linkage_uuid, rule_id
FROM
    linkage ln
    JOIN (select r1.linkage_uuid
from
    linkage_r1 r1
    left join linkage_r2 r2 on r1.linkage_uuid = r2.linkage_uuid
where r2.linkage_uuid is null
) as x on x.linkage_uuid = ln.linkage_uuid

and partner_code = 'UFH'

-- Find patients matched by R2 only
select
    partner_code, linkage_patid, ln.linkage_uuid, rule_id
FROM
    linkage ln
    JOIN (select r2.linkage_uuid
from
    linkage_r2 r2
    left join linkage_r1 r1 on r1.linkage_uuid = r2.linkage_uuid
where r1.linkage_uuid is null
) as x on x.linkage_uuid = ln.linkage_uuid

and partner_code = 'UFH'


-- ===============================
-- Create list for R1&R2 mathces
SELECT DISTINCT top(2000) ln.linkage_patid as flm_patid,
   ln.linkage_uuid,
   l2.linkage_patid as ufh_patid -- partner_code, linkage_patid, ln.linkage_uuid, rule_id,
   -- linkage_hash
FROM
    linkage ln
JOIN
    linkage_r1 r1 ON r1.linkage_uuid = ln.linkage_uuid
JOIN
    linkage_r2 r2 ON r2.linkage_uuid = ln.linkage_uuid AND partner_code = 'FLM'
JOIN
    linkage l2 ON l2.linkage_uuid = ln.linkage_uuid AND l2.partner_code = 'UFH'
ORDER BY ln.linkage_uuid


-- ===============================
-- Create list for R1 mathces only
SELECT DISTINCT top(500)
    ln.linkage_patid as flm_patid,
    ln.linkage_uuid,
    l2.linkage_patid as ufh_patid
    -- partner_code, linkage_patid, ln.linkage_uuid, rule_id,
    -- linkage_hash
FROM
    linkage ln
    JOIN
        (
        SELECT r1.linkage_uuid
        FROM linkage_r1 r1
        LEFT JOIN linkage_r2 r2 ON r1.linkage_uuid = r2.linkage_uuid
        WHERE
            r2.linkage_uuid is null
       ) as x ON x.linkage_uuid = ln.linkage_uuid AND partner_code = 'FLM'
    JOIN linkage l2 ON l2.linkage_uuid = ln.linkage_uuid AND l2.partner_code = 'UFH'
ORDER BY ln.linkage_uuid


-- ===============================
-- Create list for R2 mathces only

SELECT DISTINCT top(500)
    ln.linkage_patid as flm_patid,
    ln.linkage_uuid,
    l2.linkage_patid as ufh_patid
    -- partner_code, linkage_patid, ln.linkage_uuid, rule_id,
    -- linkage_hash
FROM
    linkage ln
    JOIN
        (
        SELECT r2.linkage_uuid
        FROM linkage_r2 r2
        LEFT JOIN linkage_r1 r1 ON r1.linkage_uuid = r2.linkage_uuid
        WHERE
            r1.linkage_uuid is null
       ) as x ON x.linkage_uuid = ln.linkage_uuid AND partner_code = 'FLM'
    JOIN linkage l2 ON l2.linkage_uuid = ln.linkage_uuid AND l2.partner_code = 'UFH'
ORDER BY ln.linkage_uuid
