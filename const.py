DOMAIN = "sprinkle"
NAME = "Sprinkle Virtual Irrigation"
VERSION = "1.0.0"
MANUFACTURER = "bence056"

CUSTOM_COMPONENTS = "custom_components"
INTEGRATION_FOLDER = DOMAIN
PANEL_FOLDER = "frontend"
PANEL_FILENAME = "dist/sprinkle-panel.js"

PANEL_URL = "/api/panel_custom/sprinkle"
PANEL_TITLE = NAME
PANEL_ICON = "mdi:sprinkler-variant"
PANEL_NAME = "sprinkle-panel"

STORAGE_KEY = f"{DOMAIN}.storage"
DATA_REGISTRY = f"{DOMAIN}_storage"
STORAGE_VERSION = 1
SAVE_DELAY = 10

PLATFORMS = ["sensor", "switch", "button", "number"]


#Http attributes

ATTR_ZONE_ID = "zone_id"
ATTR_ZONE_NAME = "zone_name"
ATTR_ZONE_VALVES = "zone_valves"
ATTR_ZONE_DELETE = "zone_delete"
ATTR_RAIN_DELAY_CURRENT_SETTING = "rain_delay_set_value"
ATTR_RAIN_DELAY_END_TIME_SECONDS = "rain_delay_end_time_seconds"
