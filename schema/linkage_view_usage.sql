
-- Find ORH patients linked to FLM
SELECT
    dl.PATID, dl.ORIGINAL_PATID
FROM
    demographic_lookup dl
    JOIN (
SELECT
    DISTINCT ln.linkage_patid
FROM 
    linkage ln
    JOIN linkage_view_2 lv on ln.linkage_uuid = lv.PATID
WHERE 
   FOUND_IN_FLM > 0 AND FOUND_IN_ORH > 0
   AND ln.partner_code = 'ORH'
) x on x.linkage_patid = dl.ORIGINAL_PATID


-- Note: For properly linked partners the query is simpler
SELECT
    dl.PATID, dl.ORIGINAL_PATID
FROM
    demographic_lookup dl
    JOIN linkage_view_2 lv on dl.PATID = lv.PATID
WHERE 
   FOUND_IN_FLM > 0 AND FOUND_IN_UFH > 0
   AND dl.SOURCE = 'UFH'
