import logging

class TuiLogHandler(logging.Handler):
    def __init__(self, log_list):
        super().__init__()
        self.log_list = log_list

    def emit(self, record):
        log_entry = self.format(record)
        self.log_list.append(f"[PYTHON] {log_entry}")
        if len(self.log_list) > 500:
            self.log_list.pop(0)

def setup_logging(log_list):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = TuiLogHandler(log_list)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
