
-- Note: to insert a quote you have to "double" it
INSERT INTO dbo.partner
    (partner_code, partner_description, partner_added_at)
VALUES
    ('FLM', 'Florida Medicaid (ICHP) - claims', GETDATE()),
    ('UFH', 'University of Florida', GETDATE()),
    ('FLH', 'Florida Hospital', GETDATE()),
    ('CHP', 'Capital Health Plan - claims', GETDATE()),

    ('HCN', 'Health Choice Network', GETDATE()),
    ('UMI', 'University of Miami', GETDATE()),
    ('BND', 'Bond Community Health Center Inc.', GETDATE()),

    ('MCH', 'Miami Children''s Health System', GETDATE()),
    ('TMA', 'Tallahassee Memorial HealthCare', GETDATE()),
    ('TMC', 'Tallahassee Memorial HealthCare', GETDATE()),
    ('ORH',  'Orlando Health System', GETDATE())
;

/*
INSERT INTO dbo.linkage 
    (partner_code, linkage_patid, linkage_flag, linkage_uuid, linkage_hash, linkage_added_at)
VALUES
    ('HCN', 'patid_1', 0, NEWID(), CONVERT(VARBINARY(MAX), 'abc'), GETDATE())
*/

INSERT INTO dbo.[RULE]
    (RULE_CODE, RULE_DESCRIPTION, RULE_ADDED_AT)
VALUES
    ('F_L_D_R', 'First + Last + DOB + Race', GETDATE()),
    ('F_L_D_S', 'First + Last + DOB + Sex', GETDATE()),
    ('NO_HASH', 'No hashes', GETDATE())
GO
