# create an object of the logger class

import logging
import os
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


class Logger(object):
    def __init__(
        self,
        project_title,
        logger_name=None,
        logger_level=logging.DEBUG,
        logger_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        backupCount=14,
        interval=1,
        when="D",
        log_dir=None,
    ) -> None:
        if logger_name is None:
            logger_name = project_title
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logger_level)
        self.formatter = logging.Formatter(logger_format)
        # self.console_handler = logging.StreamHandler(sys.stdout)
        # self.console_handler.setFormatter(self.formatter)
        # self.logger.addHandler(self.console_handler)

        if log_dir is None:
            log_dir = os.path.join(os.getcwd(), "logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # create a log file attribute (path to the log file)
        self.logger.log_file = str(Path(log_dir) / f"{logger_name}.log")

        self.file_handler = TimedRotatingFileHandler(
            filename=Path(log_dir) / f"{project_title}.log",
            backupCount=backupCount,
            encoding="utf-8",
            interval=interval,
            when=when,
        )
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)

    def get_logger(self):
        return self.logger
