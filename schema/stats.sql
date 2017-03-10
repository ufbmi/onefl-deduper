
-- Queries use to calculate deduplicaiton rate for two partners
declare @distinct_patids_UFH int
declare @distinct_uuids_UFH int
declare @linked_patients_UFH_FLM int
declare @linked_percentage_UFH float

set @distinct_patids_UFH=(select count(distinct linkage_patid) from linkage where partner_code = 'UFH')
set @distinct_uuids_UFH=(select count(distinct linkage_uuid) from linkage where partner_code = 'UFH')
set @linked_patients_UFH_FLM=(select count(*) from (select linkage_uuid, count(distinct partner_code) as cc from linkage where partner_code in ('UFH', 'FLM') group by linkage_uuid having count(distinct partner_code) > 1) as c)
set @linked_percentage_UFH = (@linked_patients_UFH_FLM * 100.0)/@distinct_uuids_UFH

print CONCAT('Distinct UFH patients: ', CAST(@distinct_patids_UFH as varchar))
print CONCAT('Linked UFH patients: ', CAST(@linked_patients_UFH_FLM as varchar(100)))
print CONCAT('Distinct UFH UUIDs: ', CAST(@distinct_uuids_UFH as varchar(100)))
print CONCAT('Percentage of linked UFH patients: ', CAST(@linked_percentage_UFH  as varchar(100)))
