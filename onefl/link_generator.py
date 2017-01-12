"""
Goal: Lookup hashed strings in the database
    and generate a new uuid or return an existing one.

@authors:
    Andrei Sura <sura.andrei@gmail.com>
"""
import os
import pandas as pd
from onefl import utils
from onefl.exc import ConfigErr
# from onefl.rules import AVAILABLE_RULES_MAP as rulz

pd.set_option('display.width', 1500)


class LinkGenerator():
    log = None

    @classmethod
    def configure_logger(cls, logger):
        cls.log = logger

    @classmethod
    def _process_frame(cls, df_source, config):
        """
        """
        df = pd.DataFrame()

        # keep the patid from the source
        df['PATID'] = df_source['PATID']

        # TODO: finish...
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
    def generate(cls, config, inputdir, outputdir):
        """
        Read the "phi_hashes.csv" file and generate UUID's.

        Optionally save the "hash -> UUID" mapping to "links.csv"
        """
        cls._validate_config(config)

        EXPECTED_COLS = config['EXPECTED_COLS']

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
            df = cls._process_frame(df_source, config)
            frames.append(df)

        df = pd.concat(frames, ignore_index=True)
        print(df)

        out_file = os.path.join(outputdir, config['OUT_FILE'])
        utils.frame_to_file(df, out_file,
                            delimiter=config['OUT_DELIMITER'])

        cls.log.info("Wrote output file: {} ({} data rows, {})"
                     .format(out_file,
                             len(df),
                             utils.get_file_size(out_file)))

        return True
