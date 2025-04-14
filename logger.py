import logging
from logging.handlers import RotatingFileHandler
import os
import os.path
from typing import Optional

default_level = logging.INFO

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[94m',  # Bleu
        'INFO': '\033[92m',   # Vert
        'WARNING': '\033[93m', # Jaune
        'ERROR': '\033[91m',   # Rouge
        'CRITICAL': '\033[91m' # Rouge
    }
    
    def __init__(self, fmt=None, datefmt=None, style='%', color: Optional[str] = None):
        super().__init__(fmt, datefmt, style)
        self.color = color
        
    def format(self, record):
        msg = super().format(record)
        color = self.color or self.COLORS.get(record.levelname, '')
        reset = '\033[0m'
        return f'{color}{msg}{reset}'

def update_level(level: int) -> None:
    global default_level
    default_level = level

def configure_custom_logger(logs_dir, color: Optional[str] = None, thread_id: Optional[str] = "main"):
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    logs_dir = os.path.join(os.getcwd(), logs_dir)
    logger = logging.getLogger('custom_logger')
    logger.setLevel(default_level)
    formatter = f'%(asctime)s - Thread {thread_id} - %(levelname)s - %(message)s'
    # File handler
    log_file = os.path.join(logs_dir, 'app.log')
    file_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024, backupCount=10)
    file_handler.setFormatter(logging.Formatter(formatter))
    logger.addHandler(file_handler)
    
    # Console handler avec couleur
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColoredFormatter(formatter, color=color))
    logger.addHandler(console_handler)
    
    return logger

logger = configure_custom_logger(logs_dir="./logs")