
-- Queries use to calculate deduplication rate for two partners

declare @distinct_patids_UFH int
declare @distinct_patids_FLM int

declare @distinct_uuids_UFH int
declare @distinct_uuids_FLM int

declare @linked_patients_UFH_FLM int
declare @linked_percentage_UFH float

set @distinct_patids_UFH=(select count(distinct linkage_patid) from linkage where partner_code = 'UFH')
set @distinct_patids_FLM=(select count(distinct linkage_patid) from linkage where partner_code = 'FLM')

set @distinct_uuids_UFH=(select count(distinct linkage_uuid) from linkage where partner_code = 'UFH')
set @distinct_uuids_FLM=(select count(distinct linkage_uuid) from linkage where partner_code = 'FLM')

set @linked_patients_UFH_FLM=(select count(*) from (select linkage_uuid, count(distinct partner_code) as cc from linkage where partner_code in ('UFH', 'FLM') group by linkage_uuid having count(distinct partner_code) > 1) as c)
set @linked_percentage_UFH = (@linked_patients_UFH_FLM * 100.0)/@distinct_uuids_UFH

print CONCAT('Distinct UFH patients: ', CAST(@distinct_patids_UFH as varchar))
print CONCAT('Distinct FLM patients: ', CAST(@distinct_patids_FLM as varchar))

print CONCAT('Distinct UFH UUIDs: ', CAST(@distinct_uuids_UFH as varchar(100)))
print CONCAT('Distinct FLM UUIDs: ', CAST(@distinct_uuids_FLM as varchar(100)))

print CONCAT('Linked UFH patients: ', CAST(@linked_patients_UFH_FLM as varchar(100)))
print CONCAT('Percentage of linked UFH patients: ', CAST(@linked_percentage_UFH  as varchar(100)))


-- Query used to extract PATID -> UUID mapping file
select
    distinct linkage_patid, linkage_uuid
from
    linkage
where 
    partner_code = 'xyz...'
order by
    linkage_patid



-- Query used to extract the list of linked UUIDs:
select
    linkage_uuid from (
    select
        linkage_uuid, count(distinct partner_code) as cc
    from
        linkage
    where
        partner_code in ('UFH', 'FLM')
    group by
        linkage_uuid
    having
        count(distinct partner_code) > 1
) c



-- Query used to find incorrectly linked patients within same source
select linkage_uuid, count(*) from linkage where partner_code = 'FLM' group by linkage_uuid having count(*) > 2


-- Query used to examine all the rows contributing to de-duplication rate
select *
from
    linkage lnk 
    join 
    (
    select
        linkage_uuid from (
        select
            linkage_uuid, count(distinct partner_code) as cc
        from
            linkage
        where
            partner_code in ('UFH', 'FLM')
        group by
            linkage_uuid
        having
            count(distinct partner_code) > 1
    ) c
    )x on x.linkage_uuid = lnk.linkage_uuid
where
    partner_code in ('UFH')
     -- linkage_added_at > '2017-07-01'
order by
    lnk.linkage_uuid, lnk.linkage_hash
