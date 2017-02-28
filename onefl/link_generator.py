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
from onefl.rules import RULE_CODE_F_L_D_R, RULE_CODE_F_L_D_S, RULE_CODE_NO_HASH  # noqa

pd.set_option('display.width', 1500)

FLAG_HASH_NOT_FOUND = 0  # 'hash not found'
FLAG_HASH_FOUND = 1  # 'hash found'
# FLAG_HASH_FOUND_BUT_IGNORED = 2  # 'hash found but ignored'


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

        if len(pat_hashes) == 0:
            cls.log.warn("Patient [{}] does not have any hashes"
                         .format(patid))
            # create a link anyway
            uuid = utils.get_uuid()
            flag = FLAG_HASH_NOT_FOUND

            new_link = LinkageEntity.create(
                partner_code=partner_code,
                rule_id=rules_cache.get(RULE_CODE_NO_HASH),
                linkage_patid=patid,
                linkage_flag=flag,
                linkage_uuid=uuid,
                linkage_hash=None,
                linkage_added_at=datetime.now())
            # TODO: add code to return this special link

        elif len(pat_hashes) == 1:
            # only one hash was received
            rule_code, ahash = pat_hashes.popitem()
            existing_link = hash_uuid_lut.get(ahash)
            binary_hash = unhexlify(ahash.encode('utf-8'))

            if existing_link is None:
                # create new UUID
                uuid = utils.get_uuid()
                flag = FLAG_HASH_NOT_FOUND
            else:
                # reuse the existing UUID
                uuid = existing_link.linkage_uuid
                flag = FLAG_HASH_FOUND

            new_link = LinkageEntity.create(
                partner_code=partner_code,
                rule_id=rules_cache.get(rule_code),  # we need the rule_id here
                linkage_patid=patid,
                linkage_flag=flag,
                linkage_uuid=uuid,
                linkage_hash=binary_hash,
                linkage_added_at=datetime.now())

            if rule_code == RULE_CODE_F_L_D_R:
                links = {ahash: new_link}
            else:
                links = {'': None, ahash: new_link}

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
        """
        We have to cover 2^2 + 1 = 5 cases:
            1. h1 => 0, h2 => 0     - create new UUID and use for both rows
            2. h1 => 0, h2 => 1  \  _ reuse a UUID
            3. h1 => 1, h2 => 0  /
            4. h1 => 1, h2 => 1 and UUIDs match - reuse a UUID
            5. h1 => 1, h2 => 1 and the corresponding UUIDs do NOT match
        """
        links = {}
        to_investigate = {}
        added_date = datetime.now()

        # TODO: This is ugly but we can make (if needed)
        # the logic work for "n" rules
        rule_code_1, ahash_1 = pat_hashes.popitem()
        rule_code_2, ahash_2 = pat_hashes.popitem()
        existing_link_1 = hash_uuid_lut.get(ahash_1)
        existing_link_2 = hash_uuid_lut.get(ahash_2)

        both_not_found = existing_link_1 is None and existing_link_2 is None
        only_one_found = ((existing_link_1 is None and
                           existing_link_2 is not None) or
                          (existing_link_1 is not None and
                           existing_link_2 is None))

        if both_not_found:
            # create two links with a `fresh` UUID
            uuid = utils.get_uuid()
            flag_1 = FLAG_HASH_NOT_FOUND
            flag_2 = FLAG_HASH_NOT_FOUND

            new_link_1 = LinkageEntity.create(
                partner_code=partner_code,
                rule_id=rules_cache.get(rule_code_1),
                linkage_patid=patid,
                linkage_flag=flag_1,
                linkage_uuid=uuid,
                linkage_hash=unhexlify(ahash_1.encode('utf-8')),
                linkage_added_at=added_date)

            new_link_2 = LinkageEntity.create(
                partner_code=partner_code,
                rule_id=rules_cache.get(rule_code_2),
                linkage_patid=patid,
                linkage_flag=flag_2,
                linkage_uuid=uuid,
                linkage_hash=unhexlify(ahash_2.encode('utf-8')),
                linkage_added_at=added_date)

        elif only_one_found:
            # reuse the existing UUID
            if existing_link_1 is not None:
                uuid = existing_link_1.linkage_uuid
                flag_1 = FLAG_HASH_FOUND
                flag_2 = FLAG_HASH_NOT_FOUND
            else:
                uuid = existing_link_2.linkage_uuid
                flag_1 = FLAG_HASH_NOT_FOUND
                flag_2 = FLAG_HASH_FOUND

            new_link_1 = LinkageEntity.create(
                partner_code=partner_code,
                rule_id=rules_cache.get(rule_code_1),
                linkage_patid=patid,
                linkage_flag=flag_1,
                linkage_uuid=uuid,
                linkage_hash=unhexlify(ahash_1.encode('utf-8')),
                linkage_added_at=added_date)

            new_link_2 = LinkageEntity.create(
                partner_code=partner_code,
                rule_id=rules_cache.get(rule_code_2),
                linkage_patid=patid,
                linkage_flag=flag_2,
                linkage_uuid=uuid,
                linkage_hash=unhexlify(ahash_2.encode('utf-8')),
                linkage_added_at=added_date)
        else:
            # both are found - reuse the existing UUID
            uuid = existing_link_1.linkage_uuid
            new_link_1 = LinkageEntity.create(
                partner_code=partner_code,
                rule_id=rules_cache.get(rule_code_1),
                linkage_patid=patid,
                linkage_flag=FLAG_HASH_FOUND,
                linkage_uuid=uuid,
                linkage_hash=unhexlify(ahash_1.encode('utf-8')),
                linkage_added_at=added_date)

            # UUID's match - insert row for the second hash too
            if (existing_link_1.linkage_uuid ==
                    existing_link_2.linkage_uuid):
                # consensus hence insert row for hash 2 too
                new_link_2 = LinkageEntity.create(
                    partner_code=partner_code,
                    rule_id=rules_cache.get(rule_code_2),
                    linkage_patid=patid,
                    linkage_flag=FLAG_HASH_FOUND,
                    linkage_uuid=uuid,
                    linkage_hash=unhexlify(ahash_2.encode('utf-8')),
                    linkage_added_at=added_date)
            else:
                # the UUID's do not match - we need to investigate
                to_investigate = {
                    ahash_2: [existing_link_1.linkage_uuid,
                              existing_link_2.linkage_uuid]
                }
                cls.log.warning("Hashes of the patid [{}] are linked"
                                " to two distinct UUIDs: {}, {}."
                                " We linked only the first hash!"
                                .format(patid,
                                        existing_link_1.linkage_uuid,
                                        existing_link_2.linkage_uuid))
                return {ahash_1: new_link_1}, to_investigate

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
        investigations = []
        hash_uuid_lut = cls._populate_hash_uuid_lut(config, session, df_source)
        mapped_hashes = {ahash: link.linkage_uuid
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

            if len(pat_hashes) < 1:
                patients_with_no_hashes.append(patid)

            cls.log.debug("Parsing row for patient {} with {} hashes"
                          .format(patid, len(pat_hashes)))
            links, to_investigate = cls._process_patient_row(
                patid, pat_hashes.copy(), hash_uuid_lut,
                rules_cache, config, session,
                partner_code)
            cls.log.debug("Created {} links for patid: {}".format(len(links), patid))  # noqa

            if len(to_investigate) > 0:
                investigations.append(to_investigate)

            i = 0
            for ahash, link in links.items():
                i += 1
                df.loc[df['PATID'] == patid, 'UUID'] = (link.linkage_uuid
                                                        if link else '')
                df.loc[df['PATID'] == patid, "hash_{}".format(i)] = ahash

        cls.log.warning("{} out of {} patients are missing both hashes: {}"
                        .format(len(patients_with_no_hashes), len(df),
                                patients_with_no_hashes))
        return df, investigations

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
        # TODO: add a method parameter for controlling the `create_table` flag
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
        investigations = []

        for df_source in reader:
            df_source.fillna('', inplace=True)
            # The magic happens here...
            df, to_investigate = cls._process_frame(config, session, df_source,
                                                    partner)
            if SAVE_OUT_FILE:
                frames.append(df)
                investigations.extend(to_investigate)

        if SAVE_OUT_FILE:
            df = pd.concat(frames, ignore_index=True)
            out_file = os.path.join(outputdir, config['OUT_FILE'])
            out_file_investigate = os.path.join(outputdir,
                                                config['OUT_FILE_INVESTIGATE'])
            utils.frame_to_file(df, out_file,
                                delimiter=config['OUT_DELIMITER'])
            cls.log.info("Wrote output file: {} ({} data rows, {})"
                         .format(
                             out_file, len(df), utils.get_file_size(out_file)))

            with open(out_file_investigate, 'w') as invf:
                for line in investigations:
                    invf.write("{}\n".format(line))
            cls.log.info("Wrote hashes that need investigation to {}"
                         .format(out_file_investigate))
        return True
