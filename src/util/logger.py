import json
import logging
import sys
from datetime import datetime


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'thread': record.thread,
            'process': record.process
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_entry)

level = logging.INFO
# level = logging.DEBUG

logger = logging.getLogger(__name__)
logger.setLevel(level)

logger.propagate = False

# Create handler
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(level)

# # Create JSON formatter
formatter = JsonFormatter()

# formatter = logging.Formatter(
#     fmt='%(asctime)s|%(name)s|%(levelname)s|%(module)s|%(funcName)s|%(lineno)d|%(message)s',
#     datefmt='%Y-%m-%d %H:%M:%S'
# )

# formatter = logging.Formatter(
#     fmt='%(asctime)s\t%(levelname)s\t%(name)s\t%(module)s\t%(funcName)s\t%(lineno)d\t%(message)s',
#     datefmt='%Y-%m-%d %H:%M:%S'
# )

# Add formatter to handler
handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(handler)