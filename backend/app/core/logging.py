import logging
import sys
from colorama import Fore, Style, init

init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        color = self.COLORS.get(record.levelno, Fore.WHITE)
        record.levelname = f"{color}{record.levelname:<8}{Style.RESET_ALL}"
        record.msg = f"{Style.BRIGHT}{record.msg}{Style.RESET_ALL}"
        return super().format(record)


def setup_logger(name: str = "OmniSpec") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = True
    
    # Remove existing handlers to avoid duplicate lines
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            ColoredFormatter(
                fmt="%(asctime)s | %(levelname)s | [%(name)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
        )
        logger.addHandler(handler)
        
    return logger


logger = setup_logger("OmniSpec")
