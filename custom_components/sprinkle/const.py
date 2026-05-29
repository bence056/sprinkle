DOMAIN = "sprinkle"
NAME = "Sprinkle Virtual Irrigation"
VERSION = "1.2.1"
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
STORAGE_VERSION = 2
SAVE_DELAY = 10

PLATFORMS = ["sensor", "switch", "button", "number"]

#Zone Status options
ZONE_IDLE = "Idle"
ZONE_RUNNING_MANUAL = "Running (Manual)"
ZONE_RUNNING_CYCLE = "Running (From Cycle)"
ZONE_RAIN_DELAY = "Inactive (Rain Delay Active)"

#Cycle Status options
CYCLE_IDLE = "Idle"
CYCLE_RUNNING = "Running"
CYCLE_RAIN_DELAY = ZONE_RAIN_DELAY


#Http attributes

ATTR_ZONE_ID = "zone_id"
ATTR_ZONE_NAME = "zone_name"
ATTR_ZONE_VALVES = "zone_valves"
ATTR_ZONE_DELETE = "zone_delete"
ATTR_RAIN_DELAY_CURRENT_SETTING = "rain_delay_set_value"
ATTR_RAIN_DELAY_END_TIME_SECONDS = "rain_delay_end_time_seconds"

ATTR_CYCLE_ID = "cycle_id"
ATTR_CYCLE_NAME = "cycle_name"
ATTR_CYCLE_STEPS = "cycle_steps"
ATTR_CYCLE_DELETE = "cycle_delete"

ATTR_SETTINGS_USE_MASTER_VALVE = "use_master_valve"
ATTR_SETTINGS_MASTER_VALVE_ID = "master_valve_entity_id"
ATTR_SETTINGS_VALVE_TOGGLE_DELAY_MS = "valve_toggle_delay_ms"
