import os
import logging

DEBUG = os.environ.get("DEBUG") or True

IP_ADDRESS = os.environ.get("IP_ADDRESS") or "0.0.0.0"
PORT = os.environ.get("PORT") or 5000
PROTOCOL = os.environ.get("PROTOCOL") or "http://"

VERSION = os.environ.get("VERSION") or "0.1"
SECRET_KEY = os.environ.get(
    "SECRET_KEY") or "883de00834f5c0a64d51106751b7606d9782a7af"
DB_URL = os.environ.get("DB_URL") or "bolt://neo4j:neo4j@localhost:7687"

X_AUTH_TOKEN = "X-AUTH-TOKEN"
CONTENT_TYPE = "CONTENT_TYPE"
ACCEPT = "ACCEPT"

LOG_ENABLED = False
LOG_LOCATION = os.environ.get("LOG_LOCATION") or "."
LOG_FILENAME = os.environ.get("LOG_FILENAME") or "grest.log"
LOG_LEVEL = os.environ.get("LOG_LEVEL") or logging.INFO
LOG_MAX_BYTES = os.environ.get("LOG_MAX_BYTES") or 1000000  # 1 Megabyte
LOG_BACKUP_COUNT = os.environ.get("LOG_BACKUP_COUNT") or 100
LOG_FORMAT = os.environ.get(
    "LOG_FORMAT") or "%(levelname)s::%(asctime)-15s::%(process)d::%(filename)s::%(message)s"

QUERY_LIMIT = 20
