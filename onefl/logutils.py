"""
Goal: expose one method for getting a logger
"""
import os
import logging
import logging.config


def get_a_logger(name):
    """
    Read log config from `log.conf` if file is present.
    See the `log.conf.example` for a sample.

    :param name: string used for naming the logger
    """
    basedir, f = os.path.split(__file__)
    log_conf = os.path.join(os.path.dirname(basedir), "logs/config.txt")

    if os.path.exists(log_conf):
        logging.config.fileConfig(log_conf)
        log = logging.getLogger(name)
        log.debug("{} logging was configured using: {}"
                  .format(name, log_conf))
        handlers = logging.getLoggerClass().root.handlers

        for h in [h for h in handlers if hasattr(h, 'baseFilename')]:
            log.debug("log file: {}".format(h.baseFilename))
    else:
        lformat = '%(asctime)s: %(name)s.%(levelname)s ' \
            '- %(filename)s+%(lineno)d: %(message)s'
        logging.basicConfig(format=lformat, level=logging.INFO)
        log = logging.getLogger(name)
        log.warn("logging was configured using defaults")

    return log
