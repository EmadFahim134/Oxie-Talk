import logging

def setup_logging(log_file="oxie_talk.log"):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create file handler which logs info messages
    fh = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    fh.setLevel(logging.INFO)

    # Create formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(fh)
    return logger
