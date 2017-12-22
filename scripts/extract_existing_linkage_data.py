#!/usr/bin/env python
"""
Goal: Extract existing linkage data from the database

@authors:
    Andrei Sura <sura.andrei@gmail.com>
"""
import argparse
import sys
import utils
import sqlalchemy as db
import pandas as pd


from config import DB_HOST, DB_USER, DB_PASS, DB_NAME

OUT_SEP = "\t"
OUT_UFH = 'ufh_existing_rawpatid_to_uuid.csv'
OUT_FLM = 'flm_existing_rawpatid_to_uuid.csv'
OUT_LNK = 'list_of_linked_uuids.csv'


def read_ufh(conn):
    query = """
select
    distinct linkage_patid AS PATID, linkage_uuid
from
    linkage
where
    partner_code = 'UFH'
order by
    linkage_patid
"""
    # df.rename(columns = {'': ''}, inplace = True)
    df = pd.read_sql(query, conn)
    return df


def read_flm(conn):
    query = """
select
    distinct linkage_patid AS PATID, linkage_uuid
from
    linkage
where
    partner_code = 'FLM'
order by
    linkage_patid
    """
    df = pd.read_sql(query, conn)
    return df


def read_linkage(conn):
    query = """
SELECT
    linkage_uuid AS PATID
FROM (
    SELECT
        linkage_uuid, count(distinct partner_code) as cc
    FROM
        linkage
    WHERE
        partner_code in ('UFH', 'FLM')
    GROUP BY
        linkage_uuid
    HAVING
        COUNT(DISTINCT partner_code) > 1
) c
    """
    return pd.read_sql(query, conn)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-lnk', '--linkage_only', required=False,
                        action='store_true',
                        help='Extract linkage data only')
    args = parser.parse_args()

    url = utils.get_db_url(db_host=DB_HOST, db_name=DB_NAME,
                           db_user=DB_USER, db_pass=DB_PASS)
    print("url: {}".format(url))
    conn = db.create_engine(url)

    if args.linkage_only:
        if not utils.ask_yes_no("Extract linkage data to: {}".format(OUT_LNK)):
            sys.exit('Got it.')

        df_linkage = read_linkage(conn)
        print("Writing [{} lines to: {} ".format(len(df_linkage), OUT_LNK))
        df_linkage.to_csv(OUT_LNK, sep=OUT_SEP, index=False)

        sys.exit()

    if not utils.ask_yes_no("Extract raw_patid_to_uuid maps for UFH and FLM?"):
        sys.exit('Got it.')

    print("Reading UFH...")
    df_ufh = read_ufh(conn)
    print("Writing [{}] lines to: {}".format(len(df_ufh), OUT_UFH))
    df_ufh.to_csv(OUT_UFH, sep=OUT_SEP, index=False)

    print("Reading FLM...")
    df_flm = read_flm(conn)
    print("Writing [{} lines to: {} ".format(len(df_flm), OUT_FLM))
    df_flm.to_csv(OUT_FLM, sep=OUT_SEP, index=False)


if __name__ == '__main__':
    main()
