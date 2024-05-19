import logging
import structlog
from pathlib import Path

# Function to create a logger with a specific file handler
def create_logger(log_file_path):
    log_file = Path(log_file_path)
    
    # Standard logging configuration
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger = logging.getLogger(log_file_path)
    file_handler = logging.FileHandler(log_file)
    logger.addHandler(file_handler)
    
    # Remove the default StreamHandler to avoid logging to stdout
    logger.propagate = False

    # Wrap logger with structlog
    struct_logger = structlog.wrap_logger(
        logger,
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
    )
    return struct_logger

# Create the first logger
voting_logger = create_logger("voting.log")

# Create the second logger
election_logger = create_logger("election.log")

# Example usage of the two loggers
voting_logger.info("Request finished", id="request_id_1", model="model_1", response="streamed_text_1")
election_logger.info("Request finished", id="request_id_2", model="model_2", response="streamed_text_2")
