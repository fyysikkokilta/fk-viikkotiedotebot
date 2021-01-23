import logging
import os


class Logger:
    def __init__(self, log_path):
        # Enable logging
        logger = logging.getLogger('fk-viikkotiedotebot')
        logger.setLevel(logging.DEBUG)

        # Create file handler for logs
        try:
            len(log_path)
        except (NameError, TypeError) as inputError:
            log_path = os.path.join('logs', 'fk-viikkotiedotebot.log')

        fh = logging.FileHandler(log_path)
        fh.setLevel(logging.INFO)

        # Create stream handler to output errors to console
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)

        self.logger = logger


if __name__ == '__main__':
    test_logger = Logger(None).logger
    test_logger.debug('testdebug')
    test_logger.info('testinfo')
    test_logger.error('testerror')
