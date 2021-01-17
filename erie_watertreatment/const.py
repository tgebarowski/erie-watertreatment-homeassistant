"""Constants for Erie Water Treatment."""
from datetime import timedelta

OPTION_EMAIL = "__email"

DOMAIN = "erie_watertreatment"
BASE_NAME = "Erie"
SCAN_INTERVAL = timedelta(seconds=90)
COORDINATOR = "coordinator"
API = "api"

CONF_EMAIL = "_conf_email"
CONF_PASSWORD = "_conf_password"
CONF_ACCESS_TOKEN = "_conf_access_token"
CONF_CLIENT_ID = "_conf_client_id"
CONF_UID = "_conf_uid"
CONF_EXPIRY = "_conf_expiry"
CONF_DEVICE_ID = "_conf_device_id"
CONF_DEVICE_NAME = "_conf_device_name"