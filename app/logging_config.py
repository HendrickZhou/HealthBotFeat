import logging
import sys

logging.basicConfig(
    level=logging.INFO,  # or INFO
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)

logging.getLogger().debug("Logging is initialized")

