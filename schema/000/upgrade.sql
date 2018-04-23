-- linkage
IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'linkage' AND TABLE_SCHEMA = 'dbo')
    DROP TABLE dbo.linkage
GO

-- partner
IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'partner' AND TABLE_SCHEMA = 'dbo')
    DROP TABLE dbo.partner
GO

-- rule
IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'rule' AND TABLE_SCHEMA = 'dbo')
    DROP TABLE dbo.[rule]
GO


/*
Notes:
    - the 36-character uuid is stored as 36-4 = 32 varchar
    - by combining two 4-bit hex characters into one byte
    we reduce the storage requirements.
    This is done in python using `binascii.unhexlify()` function

    - the 64-character sha256 string is stored as 64/2 = 32 binary
*/

CREATE TABLE [dbo].[linkage](
    [linkage_id] [bigint] IDENTITY(1,1) NOT NULL,
    [partner_code] [varchar](3) NOT NULL,
    [rule_id] [int] NOT NULL,
    [linkage_patid] [varchar](64) NOT NULL,
    [linkage_flag] [int] NOT NULL,
    [linkage_uuid] [varchar](32) NULL,
    [linkage_hash] [binary](32) NULL,
    [linkage_added_at] [datetime] NOT NULL,
PRIMARY KEY CLUSTERED
(
    [linkage_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO

CREATE TABLE [dbo].[partner](
    [partner_code] [varchar](3) NOT NULL,
    [partner_description] [varchar](255) NOT NULL,
    [partner_added_at] [datetime] NOT NULL,
PRIMARY KEY CLUSTERED
(
    [partner_code] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO

CREATE TABLE [dbo].[rule](
    [RULE_ID] [int] IDENTITY(1,1) NOT NULL,
    [RULE_CODE] [varchar](10) NOT NULL,
    [RULE_DESCRIPTION] [varchar](255) NOT NULL,
    [RULE_ADDED_AT] [datetime] NOT NULL,
PRIMARY KEY CLUSTERED
(
    [RULE_ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
UNIQUE NONCLUSTERED
(
    [RULE_CODE] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO

-- =====================================================================
-- ============================= Indexes ===============================
CREATE NONCLUSTERED INDEX [ix_linkage_linkage_added_at] ON [dbo].[linkage]
(
    [linkage_added_at] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO

CREATE NONCLUSTERED INDEX [ix_linkage_linkage_flag] ON [dbo].[linkage]
(
    [linkage_flag] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
SET ANSI_PADDING ON

GO

CREATE NONCLUSTERED INDEX [ix_linkage_linkage_hash] ON [dbo].[linkage]
(
    [linkage_hash] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
SET ANSI_PADDING ON

GO

CREATE NONCLUSTERED INDEX [ix_linkage_linkage_patid] ON [dbo].[linkage]
(
    [linkage_patid] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
SET ANSI_PADDING ON

GO

CREATE NONCLUSTERED INDEX [ix_linkage_linkage_uuid] ON [dbo].[linkage]
(
    [linkage_uuid] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
SET ANSI_PADDING ON

GO

CREATE NONCLUSTERED INDEX [ix_linkage_partner_code] ON [dbo].[linkage]
(
    [partner_code] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
SET ANSI_PADDING ON

GO

CREATE NONCLUSTERED INDEX [ix_linkage_partner_code_patid_uuid] ON [dbo].[linkage]
(
    [partner_code] ASC
)
INCLUDE (     [linkage_patid],
    [linkage_uuid]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
SET ANSI_PADDING ON

GO

CREATE NONCLUSTERED INDEX [ix_linkage_rule_id] ON [dbo].[linkage]
(
    [rule_id] ASC
)
INCLUDE (     [partner_code]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
ALTER TABLE [dbo].[linkage]  WITH CHECK ADD  CONSTRAINT [fk_linkage_partner_code] FOREIGN KEY([partner_code])
REFERENCES [dbo].[partner] ([partner_code])
GO
ALTER TABLE [dbo].[linkage] CHECK CONSTRAINT [fk_linkage_partner_code]
GO
ALTER TABLE [dbo].[linkage]  WITH CHECK ADD  CONSTRAINT [fk_linkage_rule_id] FOREIGN KEY([rule_id])
REFERENCES [dbo].[rule] ([RULE_ID])
GO
ALTER TABLE [dbo].[linkage] CHECK CONSTRAINT [fk_linkage_rule_id]
GO
