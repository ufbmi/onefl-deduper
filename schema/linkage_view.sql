-- create an indexed view
-- @see:
--	https://docs.microsoft.com/en-us/sql/relational-databases/views/create-indexed-views
--	https://docs.microsoft.com/en-us/sql/t-sql/functions/count-big-transact-sql

IF OBJECT_ID ('dbo.linkage_view_2', 'view') IS NOT NULL
	DROP VIEW dbo.linkage_view_2;
GO

CREATE VIEW dbo.linkage_view_2
WITH SCHEMABINDING 
AS
SELECT
    linkage_uuid AS PATID  
    , sum( CASE WHEN partner_code = 'UFH' THEN 1 ELSE 0 END) as FOUND_IN_UFH
    , sum( CASE WHEN partner_code = 'FLM' THEN 1 ELSE 0 END) as FOUND_IN_FLM
    , sum( CASE WHEN partner_code = 'ORH' THEN 1 ELSE 0 END) as FOUND_IN_ORH
    , sum( CASE WHEN partner_code = 'UMI' THEN 1 ELSE 0 END) as FOUND_IN_UMI
    , sum( CASE WHEN partner_code = 'TMA' THEN 1 ELSE 0 END) as FOUND_IN_TMA
    , sum( CASE WHEN partner_code = 'TMC' THEN 1 ELSE 0 END) as FOUND_IN_TMC
    , sum( CASE WHEN partner_code = 'CHP' THEN 1 ELSE 0 END) as FOUND_IN_CHP
    , COUNT_BIG(*) as big
FROM
    dbo.linkage
GROUP BY
    linkage_uuid
GO

-- cant't create non-clustered idx without a clustred one
CREATE UNIQUE CLUSTERED INDEX IDX_PATID   
    ON linkage_view_2 (PATID)
GO

CREATE NONCLUSTERED INDEX IDX_FOUND_IN_UFH   
    ON linkage_view_2 (FOUND_IN_UFH)
GO  
CREATE NONCLUSTERED INDEX IDX_FOUND_IN_FLM   
    ON linkage_view_2 (FOUND_IN_FLM)
GO  
CREATE NONCLUSTERED INDEX IDX_FOUND_IN_ORH   
    ON linkage_view_2 (FOUND_IN_ORH)
GO  
CREATE NONCLUSTERED INDEX IDX_FOUND_IN_TMA   
    ON linkage_view_2 (FOUND_IN_TMA)
GO
CREATE NONCLUSTERED INDEX IDX_FOUND_IN_TMC   
    ON linkage_view_2 (FOUND_IN_TMC)
GO
CREATE NONCLUSTERED INDEX IDX_FOUND_IN_CHP   
    ON linkage_view_2 (FOUND_IN_CHP)
GO

