from src.utils.logger import get_logger

logger = get_logger(__name__)

logger.debug("Ini DEBUG")
logger.info("Ini INFO")
logger.warning("Ini WARNING")
logger.error("Ini ERROR")
logger.critical("Ini CRITICAL")

