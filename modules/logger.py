import logging

log = logging.getLogger('log')
log.setLevel(logging.INFO)

log_name = f"files/logs.txt"
handler = logging.FileHandler(log_name, encoding='utf-8')
format = logging.Formatter('[%(asctime)s] [%(levelname)s]: %(message)s', datefmt='%d/%b/%Y %H:%M:%S')
handler.setFormatter(format)

log.addHandler(handler)