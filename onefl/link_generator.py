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

from binascii import unhexlify
from datetime import datetime  # noqa

from onefl import utils
from onefl.utils import db
from onefl.exc import ConfigErr
from onefl.models.linkage_entity import LinkageEntity
from onefl.models.rule_entity import RuleEntity  # noqa
# from onefl.rules import AVAILABLE_RULES_MAP as rulz
from onefl.rules import RULE_CODE_F_L_D_R, RULE_CODE_F_L_D_S  # noqa

pd.set_option('display.width', 1500)

FLAG_HASH_NOT_FOUND = 0  # 'hash not found'
FLAG_HASH_FOUND = 1  # 'hash found'
FLAG_HASH_FOUND_BUT_IGNORED = 2  # 'hash found but ignored'


class LinkGenerator():
    log = None

    @classmethod
    def configure_logger(cls, logger):
        cls.log = logger

    @classmethod
    def _populate_hash_uuid_lut(cls, config, session, df_source):
        """
        Create a hash->UUID lookup-table for a set of patients
        we are parsing as a group.
        Note: the intent here is to reduce the number of database lookups.

       .. seealso::
           :meth:`LinkageEntity:init_hash_uuid_lut`
        """
        rules = config['ENABLED_RULES'].values()
        hashes = set()

        for rule in rules:
            hashes.update(df_source[rule].tolist())

        cls.log.info("Searching UUID's for {} distinct hashes."
                     .format(len(hashes)))
        hash_uuid_lut = LinkageEntity.init_hash_uuid_lut(session,
                                                         list(hashes))
        # distinct_uuids = {link.friendly_uuid() for link in
        #                   hash_uuid_lut.values() if link is not None}

        # cls.log.info("Found {} distinct UUID's from {} hashes."
        #              .format(len(distinct_uuids), len(hashes)))

        return hash_uuid_lut

    @classmethod
    def _process_patient_row(cls, patid, pat_hashes, hash_uuid_lut,
                             rules_cache, config, session,
                             partner_code):
        """
        :return OrderedDict: with the newly created linkage entities
        """
        links = {}
        to_investigate = {}

        # keep the hashes in the order defined by the rules
        # pat_hashes = sorted({row[rule] for rule in rules if row[rule] != ''})
        # pat_hashes = {rule: row[rule] for rule in rules if row[rule] != ''}

        if len(pat_hashes) == 1:
            # only one hash was received
            rule_code, ahash = pat_hashes.popitem()
            existing_link = hash_uuid_lut.get(ahash)
            binary_hash = unhexlify(ahash.encode('utf-8'))

            if existing_link is None:
                # create new UUID
                binary_uuid = utils.get_uuid_bin()
                flag = FLAG_HASH_NOT_FOUND
            else:
                # reuse the existing UUID
                binary_uuid = existing_link.linkage_uuid
                flag = FLAG_HASH_FOUND

            new_link = LinkageEntity.create(
                partner_code=partner_code,
                rule_id=rules_cache.get(rule_code),  # we need the rule_id here
                linkage_patid=patid,
                linkage_flag=flag,
                linkage_uuid=binary_uuid,
                linkage_hash=binary_hash,
                linkage_added_at=datetime.now())

            links = {ahash: new_link}

        elif len(pat_hashes) == 2:
            links, to_investigate = cls._process_two_hashes(
                patid, pat_hashes, hash_uuid_lut,
                rules_cache, config, session,
                partner_code)
        return links, to_investigate

    @classmethod
    def _process_two_hashes(cls, patid, pat_hashes, hash_uuid_lut,
                            rules_cache, config, session,
                            partner_code):
        links = {}
        added_date = datetime.now()

        # TODO: This is ugly but we can make (if needed)
        # the logic work for "n" rules
        rule_code_1, ahash_1 = pat_hashes.popitem()
        rule_code_2, ahash_2 = pat_hashes.popitem()
        existing_link_1 = hash_uuid_lut.get(ahash_1)
        existing_link_2 = hash_uuid_lut.get(ahash_2)

        if existing_link_1 is None:
            # respect the main rule - create two links with a `fresh` UUID
            binary_uuid = utils.get_uuid_bin()
            flag_1 = FLAG_HASH_NOT_FOUND

            # Flag 2 is set depending on presence of the link in the database
            if existing_link_2 is None:
                flag_2 = FLAG_HASH_NOT_FOUND
            else:
                flag_2 = FLAG_HASH_FOUND_BUT_IGNORED

            new_link_1 = LinkageEntity.create(
                partner_code=partner_code,
                rule_id=rules_cache.get(rule_code_1),
                linkage_patid=patid,
                linkage_flag=flag_1,
                linkage_uuid=binary_uuid,
                linkage_hash=unhexlify(ahash_1.encode('utf-8')),
                linkage_added_at=added_date)

            new_link_2 = LinkageEntity.create(
                partner_code=partner_code,
                rule_id=rules_cache.get(rule_code_2),
                linkage_patid=patid,
                linkage_flag=flag_2,
                linkage_uuid=binary_uuid,
                linkage_hash=unhexlify(ahash_2.encode('utf-8')),
                linkage_added_at=added_date)

        if existing_link_1 is not None:
            # respect the main rule - create two links with an `existing` UUID
            flag_1 = FLAG_HASH_FOUND

            if existing_link_2 is None:
                flag_2 = FLAG_HASH_NOT_FOUND
            else:
                if (existing_link_1.linkage_uuid ==
                        existing_link_2.linkage_uuid):
                    # consensus hence no problem
                    flag_2 = FLAG_HASH_FOUND
                else:
                    # the UUID's do not match - we need to investigate
                    to_investigate = {
                        ahash_1: existing_link_1.friendly_uuid(),
                        ahash_2: existing_link_2.friendly_uuid()
                    }
                    cls.log.warning("Hashes of the patid: {} are linked "
                                    "to two distinct UUIDs: {}"
                                    .format(patid, to_investigate))
                    return links, to_investigate

            # reuse the existing UUID
            binary_uuid = existing_link_1.linkage_uuid

            new_link_1 = LinkageEntity.create(
                partner_code=partner_code,
                rule_id=rules_cache.get(rule_code_1),
                linkage_patid=patid,
                linkage_flag=flag_1,
                linkage_uuid=binary_uuid,
                linkage_hash=unhexlify(ahash_1.encode('utf-8')),
                linkage_added_at=added_date)

            new_link_2 = LinkageEntity.create(
                partner_code=partner_code,
                rule_id=rules_cache.get(rule_code_2),
                linkage_patid=patid,
                linkage_flag=flag_2,
                linkage_uuid=binary_uuid,
                linkage_hash=unhexlify(ahash_2.encode('utf-8')),
                linkage_added_at=added_date)

        links[ahash_1] = new_link_1
        links[ahash_2] = new_link_2

        return links, {}

    @classmethod
    def _process_frame(cls, config, session, df_source, partner_code):
        """
        """
        # Init an empty frame and copy the patid from the source
        df = pd.DataFrame()
        df['PATID'] = df_source['PATID']
        hash_uuid_lut = cls._populate_hash_uuid_lut(config, session, df_source)
        mapped_hashes = {ahash: link.friendly_uuid()
                         for ahash, link in hash_uuid_lut.items()
                         if link is not None}
        rules_cache = RuleEntity.get_rules_cache(session)
        cls.log.debug("Found {} linked hashes in db: {}"
                      .format(len(mapped_hashes), mapped_hashes))

        # the rules are ordered by their importance
        rules = config['ENABLED_RULES'].values()
        patients_with_no_hashes = []

        for index, row in df_source.iterrows():
            patid = row['PATID']
            pat_hashes = {rule: row[rule] for rule in rules if row[rule] != ''}
            cls.log.debug("Parsing row for patient {} with {} hashes"
                          .format(patid, len(pat_hashes)))
            links, to_investigate = cls._process_patient_row(
                patid, pat_hashes.copy(), hash_uuid_lut,
                rules_cache, config, session,
                partner_code)

            i = 0
            for ahash, link in links.items():
                i += 1
                # print("Hash: {} link: {}".format(ahash, link))
                df.loc[df['PATID'] == patid, 'UUID'] = link.friendly_uuid()
                df.loc[df['PATID'] == patid, "hash_{}".format(i)] = ahash

            if len(pat_hashes) < 1:
                patients_with_no_hashes.append(patid)
                cls.log.warning("Patient [{}] has no hashes. "
                                "No UUID was created!".format(patid))
            else:
                cls.log.info("Created {} links for patid: {}"
                             .format(len(links), patid))
        cls.log.info("{} out of {} patients did not have any hashes: {}"
                     .format(len(patients_with_no_hashes), len(df),
                             patients_with_no_hashes))
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
