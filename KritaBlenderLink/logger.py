import logging

logger = logging.getLogger("KritaBlenderLink")

def configure_logger(port: int):
    # Clear existing handlers to avoid duplicate log entries
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Map specific ports to log levels; default to highest level (CRITICAL) for others
    port_level_map = {
        65441: logging.INFO,
        65442: logging.WARNING,
        65443: logging.ERROR,
        65444: logging.DEBUG,
    }
    logger.setLevel(port_level_map.get(port, logging.CRITICAL))

    handler = logging.StreamHandler()
    formatter = logging.Formatter("[KritaBlenderLink] %(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
