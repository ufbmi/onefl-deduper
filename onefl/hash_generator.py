"""
Goal: Store functions used for converting PHI data into hashed strings

@authors:
    Andrei Sura <sura.andrei@gmail.com>
"""

import os
import pandas as pd
from onefl import utils


class HashGenerator():
    logger = None

    @classmethod
    def configure_logger(cls, logger):
        cls.logger = logger

    @classmethod
    def generate(cls, inputdir, outputdir):
        """
        Read the "phi_data.csv" file and generate "hashes.csv"
        containing two (or more) sha256 strings for each line
        in the input file.

        This method is invoked from

        .. seealso::

            ../gen_hashes.py

        :param inputdir: directory name for the source file
        :param outputdir: directory name for generated file

        """
        cls.logger.info("Using [{}] as source folder".format(inputdir))
        cls.logger.info("Using [{}] as destination folder".format(outputdir))

        # TODO: add config to allow adding more rules
        # TODO: add config to specify the output file name

        inputfile = os.path.join(inputdir, 'phi.csv')
        df = cls.get_result_frame(inputfile)
        utils.frame_to_file(df,
                            os.path.join(outputdir, 'phi_hashes.csv'),
                            delimiter="\t")

        return True

    @classmethod
    def get_result_frame(cls, inputfile):
        """

        rtype: DataFrame
        :return the frame with hashes of the PHI data

        Columns:
            - patid
            - sha_rule_1 (first_last_dob_gender)
            - sha_rule_2 (first_last_dob_race)

        """
        df = pd.DataFrame()
        return df
