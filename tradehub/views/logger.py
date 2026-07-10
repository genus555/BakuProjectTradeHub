import logging
import requests

class GoLoggingHandler(logging.Handler):
    def emit(self, record):
        try:
            log = self.format(record)
            requests.post('http://localhost:8080/log',
                          json={
                              "level": record.levelname,
                              "message": record.getMessage(),
                              "details": log
                          },
                          timeout=0.5
            )
        except Exception:
            pass