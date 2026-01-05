import os
import sys
import logging

def setup_logging(log_file: str = "log.txt") -> logging.Logger:
    """Initialize logging to file + stdout, truncating old log file."""
    if os.path.exists(log_file):
        with open(log_file, 'w', encoding='utf-8'):
            pass

    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_file, mode='a', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger()
