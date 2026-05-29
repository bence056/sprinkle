import {ConfigEntry, Cycle, GeneralSettings, HomeAssistant, Zone} from "./types";

export const createZone = (hass: HomeAssistant, config_entry: string, zone: Partial<Zone>) : Promise<boolean> => {
    return hass.callWS({
        type: "sprinkle/zone",
        entry: config_entry,
        zone: zone
    })
}

export const modifyZoneValves = (hass: HomeAssistant, config_entry: string, zone_id: string, valve_list: string[]) : Promise<boolean> => {
    return hass.callWS({
        type: "sprinkle/zone",
        entry: config_entry,
        zone:
            {
            zone_id: zone_id,
            zone_valves: valve_list
        }
    })
}

export const deleteZone = (hass: HomeAssistant, config_entry: string, zone_id: string) : Promise<boolean> => {
    return hass.callWS({
        type: "sprinkle/zone",
        entry: config_entry,
        zone: {
            zone_id: zone_id,
            zone_delete: true
        }
    })
}

export const getZones = (hass: HomeAssistant, config_entry: string,) : Promise<Zone[]> => {
    return hass.callWS({
        type: "sprinkle/get_zones",
        entry: config_entry
    })
}

export const createCycle = (hass: HomeAssistant, config_entry: string, cycle: Partial<Cycle>) : Promise<boolean> => {
    return hass.callWS({
        type: "sprinkle/cycle",
        entry: config_entry,
        cycle: cycle
    })
}

export const modifyCycle = (hass: HomeAssistant, config_entry: string, cycle: Partial<Cycle>) : Promise<boolean> => {
    return hass.callWS({
        type: "sprinkle/cycle",
        entry: config_entry,
        cycle: cycle
    })
}

export const deleteCycle = (hass: HomeAssistant, config_entry: string, cycle_id: string) : Promise<boolean> => {
    return hass.callWS({
        type: "sprinkle/cycle",
        entry: config_entry,
        cycle: {
            cycle_id: cycle_id,
            cycle_delete: true
        }
    })
}

export const getCycles = (hass: HomeAssistant, config_entry: string) : Promise<Cycle[]> => {
    return hass.callWS({
        type: "sprinkle/get_cycles",
        entry: config_entry
    })
}

export const getGeneralSettings = (hass: HomeAssistant, config_entry: string,) : Promise<GeneralSettings> => {
    return hass.callWS({
        type: "sprinkle/get_gs",
        entry: config_entry
    })
}

export const getConfigEntries = (hass: HomeAssistant) : Promise<ConfigEntry[]> => {
    return hass.callWS({
        type: "sprinkle/get_entries",
    })
}


export const updateGeneralSettings = (hass: HomeAssistant, config_entry: string, settingsObject: Partial<GeneralSettings>) : Promise<boolean> => {
    return hass.callWS({
        type: "sprinkle/gs",
        entry: config_entry,
        settings: settingsObject
    })
}