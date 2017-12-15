#!/usr/bin/env python
"""
Goal: Extract existing linkage mappings from the database

@authors:
    Andrei Sura <sura.andrei@gmail.com>
"""
# flake8: noqa
import sqlalchemy as db
import pandas as pd
from collections import namedtuple
from urllib import parse

from config import DB_HOST, DB_USER, DB_PASS, DB_NAME

OUT_SEP = "\t"
OUT_UFH = 'ufh_existing_rawpatid_to_uuid.csv'
OUT_FLM = 'flm_existing_rawpatid_to_uuid.csv'


def get_db_url(db_host, db_name, db_user, db_pass):
    """
    Helper function for creating the "pyodbc" connection string.

    @see /etc/freetds.conf
    @see http://docs.sqlalchemy.org/en/latest/dialects/mssql.html
    @see https://code.google.com/p/pyodbc/wiki/ConnectionStrings
    """
    params = parse.quote(
        "Driver={{FreeTDS}};Server={};Port=1433;"
        "Database={};UID={};PWD={};"
        .format(db_host, db_name, db_user, db_pass))
    return 'mssql+pyodbc:///?odbc_connect={}'.format(params)


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


def main():
    url = get_db_url(db_host=DB_HOST, db_name=DB_NAME,
                     db_user=DB_USER, db_pass=DB_PASS)
    print("url: {}".format(url))
    conn = db.create_engine(url)

    print("Reading UFH...")
    df_ufh = read_ufh(conn)
    print("Writing [{}] lines to: {}".format(len(df_ufh), OUT_UFH ))
    df_ufh.to_csv(OUT_UFH, sep=OUT_SEP, index=False)

    print("Reading FLM...")
    df_flm = read_flm(conn)
    print("Writing [{} lines to: {} ".format(len(df_flm), OUT_FLM))
    df_flm.to_csv(OUT_FLM, sep=OUT_SEP, index=False)


if __name__ == '__main__':
    main()
