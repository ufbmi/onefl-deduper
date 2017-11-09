"""
Goal: Lookup hashed strings in the database
    and generate a new uuid or return an existing one.

@authors:
    Andrei Sura <sura.andrei@gmail.com>
"""
import collections  # noqa
import multiprocessing as mp
import os
import pandas as pd
import numpy as np
import pprint  # noqa
import sys
import traceback

from binascii import unhexlify
from datetime import datetime  # noqa

from onefl import utils
from onefl.utils import db as db_utils
from onefl.exc import ConfigErr
from onefl.models.linkage_entity import (
    FLAG_HASH_NOT_FOUND, FLAG_HASH_FOUND,
    FLAG_SKIP_MATCH, FLAG_SKIP_REPEATED)
from onefl.models.linkage_entity import LinkageEntity
from onefl.models.rule_entity import RuleEntity  # noqa
# from onefl.rules import AVAILABLE_RULES_MAP as rulz
from onefl.rules import RULE_CODE_F_L_D_R, RULE_CODE_F_L_D_S, RULE_CODE_NO_HASH  # noqa

pd.set_option('display.width', 1500)

# How many processes to use?
NUM_CPUS = max(1, mp.cpu_count() - 2)


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

        cls.log.debug("Searching UUID's for {} distinct hashes."
                      .format(len(hashes)))
        hash_uuid_lut = LinkageEntity.init_hash_uuid_lut(session,
                                                         list(hashes))
        # from pprint import pprint as pp
        # pp("From hashes: {} got:".format(list(hashes)))
        # pp(hash_uuid_lut)
        return hash_uuid_lut

    @classmethod
    def _process_patient_row_no_lookup(cls, patid, pat_hashes,
                                       rules_cache, config, session,
                                       partner_code):
        links = {}
        to_investigate = {}

        if len(pat_hashes) == 1:
            # only one hash was received
            rule_code, ahash = pat_hashes.popitem()
            binary_hash = unhexlify(ahash.encode('utf-8'))
            uuid = utils.get_uuid()

            new_link = LinkageEntity.create(
                partner_code=partner_code,
                rule_id=rules_cache.get(rule_code),  # we need the rule_id here
                linkage_patid=patid,
                linkage_flag=FLAG_SKIP_MATCH,  # set to 2
                linkage_uuid=uuid,
                linkage_hash=binary_hash,
                linkage_added_at=datetime.now())
            if rule_code == RULE_CODE_F_L_D_R:
                links = {ahash: new_link}
            else:
                links = {'': None, ahash: new_link}
        else:
            # insert two rows
            pass

        return links, to_investigate

    @classmethod
    def _process_patient_row(cls, patid, pat_hashes, hash_uuid_lut,
                             rules_cache, config, session,
                             partner_code, skip_db_lookup):
        """
        TODO: This function is not handling the case when we run the linkage
        for the same patient twice.

        :return a tuple of OrderedDicts (linkage_entities, sha_to_investigate)
        """
        links = {}
        to_investigate = {}

        if len(pat_hashes) == 0:
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
            links = {'': new_link}

        elif len(pat_hashes) == 1:
            # only one hash was received
            rule_code, ahash = pat_hashes.popitem()
            """
            Note: there are multiple cases when the same hash is associated
            with 2 or 3 different patients from the same partner --
            which means that we have to checking every link object
            in the LUT to avoid linking different patids even if they have
            same hash value.

            Example query:
                SELECT
                    linkage_hash, count(*) cc
                FROM
                    linkage
                WHERE
                    linkage_flag = 2  -- FLAG_SKIP_MATCH
                    and partner_code = 'xyz'
                GROUP BY
                    linkage_hash
                HAVING
                    COUNT(*) > 1
            """
            # list type
            existing_links = hash_uuid_lut.get(ahash)
            binary_hash = unhexlify(ahash.encode('utf-8'))

            if skip_db_lookup:
                # we detected two or more rows with same hash
                uuid = utils.get_uuid()
                flag = FLAG_SKIP_REPEATED
            elif len(existing_links) == 0:
                # the hash search did not find any records => create new UUID
                uuid = utils.get_uuid()
                flag = FLAG_HASH_NOT_FOUND
            else:
                # If we find a link with the same hash from the same source
                # we ignore it and mark it accordingly
                if LinkageEntity.needs_to_skip_match_for_partner(
                        existing_links,
                        partner_code,
                        patid):
                    uuid = utils.get_uuid()
                    flag = FLAG_SKIP_MATCH
                else:
                    # reuse the first existing UUID
                    # TODO: check if the source of the link matters here?
                    uuid = existing_links[0].linkage_uuid
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
                partner_code, skip_db_lookup)
        return links, to_investigate

    @classmethod
    def _process_two_hashes(cls, patid, pat_hashes, hash_uuid_lut,
                            rules_cache, config, session,
                            partner_code, skip_db_lookup):
        """
        :param patid: string representing the patient processed
        :param hash_uuid_lut: a dictionary of links found in the database
            for every hash associated with the patid we are processing

        Note: a `1` in the comments below indicates that a hash is already in
            the database!

        We have to cover 2^2 + 1 = 5 cases:
            1. h1 => 0, h2 => 0     - create new UUID and use for both rows
            2. h1 => 0, h2 => 1  \  _ reuse a UUID
            3. h1 => 1, h2 => 0  /
            4. h1 => 1, h2 => 1 and UUIDs match
                - reuse a UUID and create two rows
            5. h1 => 1, h2 => 1 and the corresponding UUIDs do NOT match
                - reuse the UUID but link only the first hash
        """
        links = {}
        to_investigate = {}
        added_date = datetime.now()

        # TODO: This is ugly but we can make (if needed)
        # the logic work for "n" rules
        rule_code_1, ahash_1 = pat_hashes.popitem()
        rule_code_2, ahash_2 = pat_hashes.popitem()

        # The dictionary contains lists of links
        existing_links_1 = hash_uuid_lut.get(ahash_1)
        existing_links_2 = hash_uuid_lut.get(ahash_2)

        both_not_found = (len(existing_links_1) == 0
                          and len(existing_links_2) == 0)
        only_one_found = ((len(existing_links_1) == 0 and
                           len(existing_links_2) > 0) or
                          (len(existing_links_1) > 0 and
                           len(existing_links_2) == 0))

        if both_not_found or skip_db_lookup:
            # create two links with a `fresh` UUID
            uuid = utils.get_uuid()
            flag = FLAG_SKIP_REPEATED if skip_db_lookup else FLAG_HASH_NOT_FOUND  # noqa

            new_link_1 = LinkageEntity.create(
                partner_code=partner_code,
                rule_id=rules_cache.get(rule_code_1),
                linkage_patid=patid,
                linkage_flag=flag,
                linkage_uuid=uuid,
                linkage_hash=unhexlify(ahash_1.encode('utf-8')),
                linkage_added_at=added_date)

            new_link_2 = LinkageEntity.create(
                partner_code=partner_code,
                rule_id=rules_cache.get(rule_code_2),
                linkage_patid=patid,
                linkage_flag=flag,
                linkage_uuid=uuid,
                linkage_hash=unhexlify(ahash_2.encode('utf-8')),
                linkage_added_at=added_date)

        elif only_one_found:
            # reuse the existing UUID
            if len(existing_links_1) > 0:
                flag_2 = FLAG_HASH_NOT_FOUND

                # Two distinct patids with same hash from same partner are
                # considered different persons and get distinct UUIDs

                if skip_db_lookup:
                    uuid = utils.get_uuid()
                    flag_1 = FLAG_SKIP_REPEATED
                elif LinkageEntity.needs_to_skip_match_for_partner(
                        existing_links_1, partner_code, patid):
                    uuid = utils.get_uuid()
                    flag_1 = FLAG_SKIP_MATCH
                else:
                    uuid = existing_links_1[0].linkage_uuid
                    flag_1 = FLAG_HASH_FOUND
            else:
                flag_1 = FLAG_HASH_NOT_FOUND

                if skip_db_lookup:
                    uuid = utils.get_uuid()
                    flag_2 = FLAG_SKIP_REPEATED
                if LinkageEntity.needs_to_skip_match_for_partner(
                        existing_links_2,
                        partner_code,
                        patid):
                    uuid = utils.get_uuid()
                    flag_2 = FLAG_SKIP_MATCH
                else:
                    uuid = existing_links_2[0].linkage_uuid
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
            # both are found
            if LinkageEntity.needs_to_skip_match_for_partner(
                    existing_links_1,
                    partner_code,
                    patid):
                uuid = utils.get_uuid()
                flag = FLAG_SKIP_MATCH
            else:
                uuid = existing_links_1[0].linkage_uuid
                flag = FLAG_HASH_FOUND

            new_link_1 = LinkageEntity.create(
                partner_code=partner_code,
                rule_id=rules_cache.get(rule_code_1),
                linkage_patid=patid,
                linkage_flag=flag,
                linkage_uuid=uuid,
                linkage_hash=unhexlify(ahash_1.encode('utf-8')),
                linkage_added_at=added_date)

            distinct_uuids = LinkageEntity.get_unique_uuids(
                existing_links_1,
                existing_links_2)

            if 1 == len(distinct_uuids):
                # UUID's match - insert row for the second hash too
                new_link_2 = LinkageEntity.create(
                    partner_code=partner_code,
                    rule_id=rules_cache.get(rule_code_2),
                    linkage_patid=patid,
                    linkage_flag=flag,
                    linkage_uuid=uuid,
                    linkage_hash=unhexlify(ahash_2.encode('utf-8')),
                    linkage_added_at=added_date)
            else:
                # the UUID's do not match - we need to investigate
                to_investigate = {
                    ahash_2: [
                        [lnk.linkage_uuid for lnk in existing_links_1] +
                        [lnk.linkage_uuid for lnk in existing_links_2]
                    ]
                }
                cls.log.warning("Hashes of the patid [{}] are linked"
                                " to two distinct UUIDs: {}."
                                " We linked only the first hash!"
                                .format(patid, to_investigate))
                return {ahash_1: new_link_1}, to_investigate

        links[ahash_1] = new_link_1
        links[ahash_2] = new_link_2

        return links, {}

    @classmethod
    def _process_frame(cls, config, df_source, partner_code):
        """
        Process a fragment of the large file.

        Note: since the `session` object can't be pickled we
        create the session in every call (see commit bde49a90)

       .. seealso::
           :meth:`generate`

        """
        engine = db_utils.get_db_engine(config)
        session = db_utils.get_db_session(engine)
        # Init an empty frame and copy the patid from the source
        df = pd.DataFrame()
        df['PATID'] = df_source['PATID']
        investigations = []
        rules_cache = RuleEntity.get_rules_cache(session)

        hash_uuid_lut = cls._populate_hash_uuid_lut(config, session, df_source)
        mapped_hashes = {ahash: links
                         for ahash, links in hash_uuid_lut.items()}
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

            # cls.log.debug("Parsing row for patient {} with {} hashes".format(patid, len(pat_hashes)))  # noqa
            links, to_investigate = cls._process_patient_row(
                patid, pat_hashes.copy(), hash_uuid_lut,
                rules_cache, config, session,
                partner_code, row['SKIP'])
            # cls.log.debug("Created {} links for patid: {}".format(len(links), patid))  # noqa

            if len(to_investigate) > 0:
                investigations.append(to_investigate)

            i = 0
            for ahash, link in links.items():
                i += 1
                df.loc[df['PATID'] == patid, 'UUID'] = (link.linkage_uuid
                                                        if link else '')
                df.loc[df['PATID'] == patid, "hash_{}".format(i)] = ahash

        len_missing_both = len(patients_with_no_hashes)

        if len_missing_both > 0:
            cls.log.warning("Patients with no hashes: {} (out of {}). {}"
                            .format(len_missing_both, len(df),
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
    def _prepare_frame(cls, config, inputdir, outputdir):
        """
        Load the frame and detect re-used hashes - the corresponding rows
        are marked with SKIP=True which is later used to avoid database lookups
        """
        EXPECTED_COLS = config['EXPECTED_COLS']
        in_file = os.path.join(inputdir, config['IN_FILE'])
        df = None

        try:
            df = pd.read_csv(in_file,
                             sep=config['IN_DELIMITER'],
                             dtype=object,
                             skipinitialspace=True,
                             skip_blank_lines=True,
                             usecols=list(EXPECTED_COLS),
                             )
            df.fillna('', inplace=True)
            rules = config['ENABLED_RULES']

            if len(rules) == 2:
                df['H1_REPEAT_COUNT'] = df.groupby(rules.get('1')
                                                   )['PATID'].transform(len)
                df['H2_REPEAT_COUNT'] = df.groupby(rules.get('2')
                                                   )['PATID'].transform(len)

                df['SKIP'] = np.where(
                    df.H1_REPEAT_COUNT > 1, True,
                    np.where(df.H2_REPEAT_COUNT > 1, True, False))
            else:
                raise Exception("Config error for ENABLED_RULES. Expected two rules!")  # noqa
        except ValueError as exc:
            cls.log.info("Please check if the actual column names"
                         " in [{}] match the expected column names"
                         " file: {}.".format(in_file, sorted(EXPECTED_COLS)))
            cls.log.error("Error: {}".format(exc))

        return df

    @classmethod
    def generate(cls, config, inputdir, outputdir, partner,
                 ask=True, create_tables=True):
        """
        Read the "phi_hashes.csv" file and generate UUID's.

        Optionally save the "hash -> UUID" mapping to "links.csv"

       .. seealso::
           :meth:`_process_frame`

        """
        cls._validate_config(config)
        in_file = os.path.join(inputdir, config['IN_FILE'])
        cls.log.info("Using {} as input file ({})".format(in_file, utils.get_file_size(in_file)))  # noqa
        cls.log.info("Connection HOST:DB - {}/{}"
                     .format(config['DB_HOST'], config['DB_NAME']))

        if ask:
            confirmed = utils.ask_yes_no(
                "Continue link procedure to create files in the [{}] folder?"
                .format(outputdir))

            if not confirmed:
                sys.exit("If you say so...")

        df = cls._prepare_frame(config, inputdir, outputdir)

        frames = []
        investigations = []
        pool = mp.Pool(processes=NUM_CPUS)
        jobs = []

        chunksize = config['LINES_PER_CHUNK']

        # for index, df_source in enumerate(reader):
        for index, group in df.groupby(np.arange(len(df)) // chunksize):
            # cls.log.error("Frame chunk [{}]".format(index))
            df_source = pd.DataFrame(group)
            # The magic happens here...
            job = utils.apply_async(pool,
                                    cls._process_frame,
                                    (config, df_source, partner))
            jobs.append(job)

        job_count = len(jobs)
        cls.log.info("Total multiproc jobs: {}".format(job_count))

        # collect the results
        for index, job in enumerate(jobs):
            try:
                df_temp, to_investigate = job.get()
                frames.append(df_temp)
                investigations.extend(to_investigate)

                if index % 100 == 0:
                    cls.log.info("Appended result {} (out of {})"
                                 .format(index, job_count))
            except Exception as exc:
                cls.log.error("Job [{}] error: {}".format(index, exc))
                cls.log.error(traceback.format_exc())

        pool.close()
        pool.join()

        if config['SAVE_OUT_FILE']:
            cls.save_output_file(config, outputdir, job_count, frames,
                                 investigations)

        return True

    @classmethod
    def save_output_file(cls, config, outputdir, job_count, frames,
                         investigations):

        cls.log.info("Got {} frames. Concatenating...".format(job_count))
        df = pd.concat(frames, ignore_index=True)

        out_file = os.path.join(outputdir, config['OUT_FILE'])
        out_file_investigate = os.path.join(outputdir, config['OUT_FILE_INVESTIGATE'])  # noqa
        utils.frame_to_file(df, out_file, delimiter=config['OUT_DELIMITER'])
        cls.log.info("Wrote output file: {} ({} data rows, {})"
                     .format(out_file, len(df), utils.get_file_size(out_file)))

        with open(out_file_investigate, 'w') as invf:
            for line in investigations:
                invf.write("{}\n".format(line))

        cls.log.info("Wrote hashes that need investigation to {}"
                     .format(out_file_investigate))
