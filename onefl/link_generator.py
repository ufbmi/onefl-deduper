"""
Goal: Lookup hashed strings in the database
    and generate a new uuid or return an existing one.

@authors:
    Andrei Sura <sura.andrei@gmail.com>
"""
import collections  # noqa
import os
import pandas as pd
import pprint  # noqa

from binascii import unhexlify  # noqa
from datetime import datetime

from onefl import utils
from onefl.utils import db
from onefl.exc import ConfigErr
from onefl.models.linkage_entity import LinkageEntity
# from onefl.rules import AVAILABLE_RULES_MAP as rulz

pd.set_option('display.width', 1500)


class LinkGenerator():
    log = None

    @classmethod
    def configure_logger(cls, logger):
        cls.log = logger

    @classmethod
    def _process_frame(cls, config, session, df_source, partner_code):
        """
        """
        # Init an empty frame and copy the patid from the source
        df = pd.DataFrame()
        df['PATID'] = df_source['PATID']

        # result = collections.defaultdict(dict)
        added_date = datetime.now()
        hashes = set()

        rules = config['ENABLED_RULES'].values()

        # add all known hashes to one set to reduce
        # the number of database lookups
        for rule in rules:
            hashes.update(df_source[rule].tolist())

        cls.log.info("Searching UUID's for {} distinct hashes."
                     .format(len(hashes)))
        # create a hash->UUID lookup-table for a set of hashes
        hash_uuid_lut = LinkageEntity.init_hash_uuid_lut(session,
                                                         list(hashes))
        distinct_uuids = {link.friendly_uuid() for link in
                          hash_uuid_lut.values() if link is not None}

        cls.log.info("Found {} distinct UUID's from {} hashes."
                     .format(len(distinct_uuids), len(hashes)))

        for index, row in df_source.iterrows():
            # TODO: check if we need to encrypt the `patid` here
            patid = row['PATID']
            # cls.log.info("Parsing row for patient {}".format(patid))
            pat_hashes = sorted({row[rule] for rule in rules
                                 if row[rule] != ''})
            binary_uuid = None

            if len(pat_hashes) >= 1:
                # patient has at least one hash
                ahash = pat_hashes[0]
                link = hash_uuid_lut.get(ahash, None)

                if link is None:
                    # Generate a new UUID...
                    binary_uuid = utils.get_uuid_bin()
                else:
                    # Re-use existing UUID...
                    binary_uuid = link.linkage_uuid

            # Revisit every hash to add a row as needed
            for i, ahash in enumerate(pat_hashes):
                link = hash_uuid_lut.get(ahash)
                binary_hash = unhexlify(ahash.encode('utf-8'))

                if link is None or link.linkage_patid != patid:
                    # Save the new UUID and update the LUT...
                    link = LinkageEntity.create(
                        partner_code=partner_code,
                        linkage_patid=patid,
                        linkage_uuid=binary_uuid,
                        linkage_hash=binary_hash,
                        linkage_added_at=added_date)
                    # cls.log.info("Added: {}".format(link))
                    hash_uuid_lut[ahash] = link

                df.loc[df['PATID'] == patid, 'UUID'] = link.friendly_uuid()
                df.loc[df['PATID'] == patid, "hash_{}".format(i)] = ahash

        # Log the updated number of UUID's
        updated_uuids = {ln.friendly_uuid() for ln in
                         hash_uuid_lut.values() if ln is not None}
        cls.log.info("Distinct UUIDs: {}".format(len(updated_uuids)))
        # cls.log.debug(pprint.pformat(updated_uuids))
        return df

    @classmethod
    def _validate_config(cls, config):
        """
        Helper method for preventing config errors
        """
        if not config.get('DB_TYPE'):
            raise ConfigErr('Please verify that the config specifies'
                            ' the DB_TYPE parameter.')

    @classmethod
    def generate(cls, config, inputdir, outputdir, partner):
        """
        Read the "phi_hashes.csv" file and generate UUID's.

        Optionally save the "hash -> UUID" mapping to "links.csv"
        """
        cls._validate_config(config)
        engine = db.get_db_engine(config)

        # pass a session object to avoid creating it in the loop
        session = db.get_db_session(engine, create_tables=True)

        EXPECTED_COLS = config['EXPECTED_COLS']
        SAVE_OUT_FILE = config['SAVE_OUT_FILE']
        in_file = os.path.join(inputdir, config['IN_FILE'])

        reader = None

        try:
            reader = pd.read_csv(in_file,
                                 sep=config['IN_DELIMITER'],
                                 dtype=object,
                                 skipinitialspace=True,
                                 skip_blank_lines=True,
                                 usecols=list(EXPECTED_COLS),
                                 chunksize=config['LINES_PER_CHUNK'],
                                 iterator=True)
            cls.log.info("Reading data from file: {} ({})"
                         .format(in_file, utils.get_file_size(in_file)))

        except ValueError as exc:
            cls.log.info("Please check if the actual column names"
                         " in [{}] match the expected column names"
                         " file: {}.".format(in_file,
                                             sorted(EXPECTED_COLS)))
            cls.log.error("Error: {}".format(exc))

        frames = []

        for df_source in reader:
            df_source.fillna('', inplace=True)
            # The magic happens here...
            df = cls._process_frame(config, session, df_source, partner)
            if SAVE_OUT_FILE:
                frames.append(df)

        if SAVE_OUT_FILE:
            df = pd.concat(frames, ignore_index=True)
            out_file = os.path.join(outputdir, config['OUT_FILE'])
            utils.frame_to_file(df, out_file,
                                delimiter=config['OUT_DELIMITER'])
            cls.log.info("Wrote output file: {} ({} data rows, {})"
                         .format(
                             out_file, len(df), utils.get_file_size(out_file)))
        return True
