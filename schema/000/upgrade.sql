
CREATE TABLE dbo.partner (
    partner_code varchar(3) primary key,
    partner_description varchar(255) NOT NULL,
    partner_added_at datetime NOT NULL
)
GO

/*
Notes:
	- by combining two 4-bit hex characters into one byte
	we reduce the storage requirements.
	This is done in python using `binascii.unhexlify()` function

    - the 36-character uuid is stored as 32/2 = 16 binary
    - the 64-character sha256 string is stored as 64/2 = 32 binary
*/

CREATE TABLE dbo.linkage (
    linkage_id bigint IDENTITY(1,1) NOT NULL primary key,
    partner_code varchar(3) NOT NULL,
    linkage_patid varchar(128) NOT NULL,
    linkage_flag int NOT NULL,
    linkage_uuid binary(16) NOT NULL,
    linkage_hash binary(32) NOT NULL,
    linkage_added_at datetime NOT NULL,
    constraint fk_linkage_partner_code foreign key (partner_code) references partner (partner_code)
)
GO

CREATE NONCLUSTERED INDEX ix_linkage_linkage_patid
    ON dbo.linkage ( linkage_patid )
    WITH( STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO

CREATE NONCLUSTERED INDEX ix_linkage_linkage_flag
    ON dbo.linkage ( linkage_flag )
    WITH( STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO

CREATE NONCLUSTERED INDEX ix_linkage_linkage_uuid
    ON dbo.linkage ( linkage_uuid )
    WITH( STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO

CREATE NONCLUSTERED INDEX ix_linkage_linkage_hash
    ON dbo.linkage ( linkage_hash )
    WITH( STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO

CREATE NONCLUSTERED INDEX ix_linkage_linkage_added_at
    ON dbo.linkage ( linkage_added_at )
    WITH( STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO

