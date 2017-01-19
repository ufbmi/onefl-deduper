# Intro

This schema creates the two tables to be used for storing

    PATID -> UUID -> PHI_HASH mapping


# Storing strings as binary

    -- 0x616263
    select CONVERT(VARBINARY(MAX), 'abc') AS toBinary;

    -- abc
    select  CONVERT(VARCHAR(MAX), 0x616263) as toString;


# Sample data


	-- select partner_code, left(partner_description, 50) partner_description, partner_added_at from partner;

	partner_code partner_description                                partner_added_at
	------------ -------------------------------------------------- -----------------------
	BND          Bond Community Health Center Inc.                  2017-01-18 14:07:14.677
	CHP          Capital Health Plan - claims                       2017-01-18 14:07:14.677
	FLH          Florida Hospital                                   2017-01-18 14:07:14.677
	FLM          Florida Medicaid (ICHP) - claims                   2017-01-18 14:07:14.677
	HCN          Health Choice Network                              2017-01-18 14:07:14.677
	MCH          Miami Children's Health System                     2017-01-18 14:07:14.677
	ORH          Orlando Health System                              2017-01-18 14:07:14.677
	TMA          Tallahassee Memorial HealthCare                    2017-01-18 14:07:14.677
	TMC          Tallahassee Memorial HealthCare                    2017-01-18 14:07:14.677
	UFH          University of Florida                              2017-01-18 14:07:14.677
	UMI          University of Miami                                2017-01-18 14:07:14.677


	-- select linkage_id, partner_code, left(linkage_patid, 10) pat_id, linkage_uuid, linkage_hash from dbo.linkage

	linkage_id           partner_code pat_id     linkage_uuid                       linkage_hash
	-------------------- ------------ ---------- ---------------------------------- ------------------------------------------------------------------
	1                    HCN          patid_1    0x1B0839BC538CBC46B79798C398B5FE0C 0x6162630000000000000000000000000000000000000000000000000000000000

