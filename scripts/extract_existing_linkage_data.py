#!/usr/bin/env python
"""
Goal: Extract existing linkage data from the database

Usage:
    $ python extract_existing_linkage_data.py
    or
    $ python extract_existing_linkage_data.py -lnk (extract linked rows only)

@authors:
    Andrei Sura <sura.andrei@gmail.com>
"""
# flake8: noqa
import argparse
import os
import sys
import utils
import sqlalchemy as db
import pandas as pd


from config import DB_HOST, DB_USER, DB_PASS, DB_NAME

OUT_SEP = "\t"
OUT_DIR = "out"
OUT_SUFFIX = '_existing_rawpatid_to_uuid.csv'
OUT_LNK = 'list_of_linked_uuids.csv'


def read_partner(conn, partner):
    query = """
SELECT
    DISTINCT linkage_patid AS PATID, linkage_uuid
FROM
    linkage
WHERE
    partner_code = '{}'
ORDER BY
    linkage_patid
""".format(partner)
    # df.rename(columns = {'': ''}, inplace = True)
    df = pd.read_sql(query, conn)
    return df


def read_linkage(conn):
    query_old = """
SELECT
    linkage_uuid AS PATID
FROM (
    SELECT
        linkage_uuid, count(distinct partner_code) as cc
    FROM
        linkage
    WHERE
        -- partner_code in ('UFH', 'FLM')
        partner_code IS NOT NULL
    GROUP BY
        linkage_uuid
    HAVING
        COUNT(DISTINCT partner_code) > 1
) c
"""
    query = """
SELECT
    linkage_uuid AS PATID
    , CASE WHEN sum( CASE WHEN partner_code = 'UFH' THEN 1 ELSE 0 END) > 0 THEN 1 ELSE 0 END as FOUND_IN_UFH
    , CASE WHEN sum( CASE WHEN partner_code = 'FLM' THEN 1 ELSE 0 END) > 0 THEN 1 ELSE 0 END as FOUND_IN_FLM
    , CASE WHEN sum( CASE WHEN partner_code = 'ORH' THEN 1 ELSE 0 END) > 0 THEN 1 ELSE 0 END as FOUND_IN_ORH
    , CASE WHEN sum( CASE WHEN partner_code = 'UMI' THEN 1 ELSE 0 END) > 0 THEN 1 ELSE 0 END as FOUND_IN_UMI
    , CASE WHEN sum( CASE WHEN partner_code = 'TMA' THEN 1 ELSE 0 END) > 0 THEN 1 ELSE 0 END as FOUND_IN_TMA
    , CASE WHEN sum( CASE WHEN partner_code = 'TMC' THEN 1 ELSE 0 END) > 0 THEN 1 ELSE 0 END as FOUND_IN_TMC
    , CASE WHEN sum( CASE WHEN partner_code = 'CHP' THEN 1 ELSE 0 END) > 0 THEN 1 ELSE 0 END as FOUND_IN_CHP
    , COUNT(distinct partner_code) AS FOUND_IN_TOTAL
FROM
    linkage
GROUP BY
    linkage_uuid
HAVING
    COUNT(DISTINCT partner_code) > 1
ORDER BY
    FOUND_IN_TOTAL
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
        out_file = os.path.join(OUT_DIR, OUT_LNK)

        if not utils.ask_yes_no("Extract linkage data to: {} ?"
                                .format(out_file)):
            sys.exit('Got it.')

        df_linkage = read_linkage(conn)
        print("Writing [{}] lines to: {} ".format(len(df_linkage), out_file))
        df_linkage.to_csv(out_file, sep=OUT_SEP, index=False)

        sys.exit()

    if not utils.ask_yes_no("Extract raw_patid_to_uuid maps?"):
        sys.exit('Got it.')

    partners = ['UFH', 'FLM', 'ORH', 'UMI', 'TMA', 'TMC']

    for partner in partners:
        print("{}: Reading RAW_PATID -> UUID mapping...".format(partner))
        df = read_partner(conn, partner)

        out_file = os.path.join(OUT_DIR,
                                "{}{}".format(partner, OUT_SUFFIX))
        print("{}: Writing [{}] output lines to {}"
              .format(partner, len(df), out_file))
        df.to_csv(out_file, sep=OUT_SEP, index=False)

    print("All done!")


if __name__ == '__main__':
    main()
