import {ConfigEntry, Cycle, GeneralSettings, HomeAssistant, Zone} from "./types";

let getCurrentRoom: (() => string) | undefined

export function configureWebsocketEntry(getter: ()=> string) {
    getCurrentRoom = getter;
}

export const createZone = (hass: HomeAssistant, zone: Partial<Zone>, config_entry: string = getCurrentRoom?.() || "") : Promise<boolean> => {
    return hass.callWS({
        type: "sprinkle/zone",
        entry: config_entry,
        zone: zone
    })
}

export const modifyZoneValves = (hass: HomeAssistant, zone_id: string, valve_list: string[], config_entry: string = getCurrentRoom?.() || "") : Promise<boolean> => {
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

export const deleteZone = (hass: HomeAssistant, zone_id: string, config_entry: string = getCurrentRoom?.() || "") : Promise<boolean> => {
    return hass.callWS({
        type: "sprinkle/zone",
        entry: config_entry,
        zone: {
            zone_id: zone_id,
            zone_delete: true
        }
    })
}

export const getZones = (hass: HomeAssistant, config_entry: string = getCurrentRoom?.() || "") : Promise<Zone[]> => {
    return hass.callWS({
        type: "sprinkle/get_zones",
        entry: config_entry
    })
}

export const createCycle = (hass: HomeAssistant, cycle: Partial<Cycle>, config_entry: string = getCurrentRoom?.() || "") : Promise<boolean> => {
    return hass.callWS({
        type: "sprinkle/cycle",
        entry: config_entry,
        cycle: cycle
    })
}

export const modifyCycle = (hass: HomeAssistant, cycle: Partial<Cycle>, config_entry: string = getCurrentRoom?.() || "") : Promise<boolean> => {
    return hass.callWS({
        type: "sprinkle/cycle",
        entry: config_entry,
        cycle: cycle
    })
}

export const deleteCycle = (hass: HomeAssistant, cycle_id: string, config_entry: string = getCurrentRoom?.() || "") : Promise<boolean> => {
    return hass.callWS({
        type: "sprinkle/cycle",
        entry: config_entry,
        cycle: {
            cycle_id: cycle_id,
            cycle_delete: true
        }
    })
}

export const getCycles = (hass: HomeAssistant, config_entry: string = getCurrentRoom?.() || "") : Promise<Cycle[]> => {
    return hass.callWS({
        type: "sprinkle/get_cycles",
        entry: config_entry
    })
}

export const getGeneralSettings = (hass: HomeAssistant, config_entry: string = getCurrentRoom?.() || "") : Promise<GeneralSettings> => {
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


export const updateGeneralSettings = (hass: HomeAssistant, settingsObject: Partial<GeneralSettings>, config_entry: string = getCurrentRoom?.() || "") : Promise<boolean> => {
    return hass.callWS({
        type: "sprinkle/gs",
        entry: config_entry,
        settings: settingsObject
    })
}