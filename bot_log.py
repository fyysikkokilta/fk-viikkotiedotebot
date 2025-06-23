import logging
import sys


class Logger:
    def __init__(self):
        # Enable logging
        logger = logging.getLogger("fk-viikkotiedotebot")
        logger.setLevel(logging.DEBUG)

        # Create stream handler to output to console (sysout)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        ch.setFormatter(formatter)

        logger.addHandler(ch)

        self.logger = logger


if __name__ == "__main__":
    test_logger = Logger().logger
    test_logger.debug("testdebug")
    test_logger.info("testinfo")
    test_logger.error("testerror")
