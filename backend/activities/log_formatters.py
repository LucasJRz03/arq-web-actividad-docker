import json
import logging
# utilizado en config/setting.py
class JsonFormatter(logging.Formatter):
    def format(self, record):
        # Campos requeridos
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname.lower(),
            "event": record.getMessage(),
        }

        # Extrae dinámicamente los atributos si se los pasamos al loguear
        if hasattr(record, 'correlation_id'):
            log_record['correlation_id'] = record.correlation_id
        if hasattr(record, 'method'):
            log_record['method'] = record.method
        if hasattr(record, 'path'):
            log_record['path'] = record.path
        if hasattr(record, 'result'):
            log_record['result'] = record.result

        # Convierte el diccionario seguro a un string JSON
        return json.dumps(log_record)