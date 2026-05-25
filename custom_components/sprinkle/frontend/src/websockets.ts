import {Cycle, GeneralSettings, HomeAssistant, Zone} from "./types";

export const createZone = (hass: HomeAssistant, zone: Partial<Zone>) : Promise<boolean> => {
    return hass.callWS({
        type: "sprinkle/zone",
        zone: zone
    })
}

export const modifyZoneValves = (hass: HomeAssistant, zone_id: string, valve_list: string[]) : Promise<boolean> => {
    return hass.callWS({
        type: "sprinkle/zone",
        zone:
            {
            zone_id: zone_id,
            zone_valves: valve_list
        }
    })
}

export const deleteZone = (hass: HomeAssistant, zone_id: string) : Promise<boolean> => {
    return hass.callWS({
        type: "sprinkle/zone",
        zone: {
            zone_id: zone_id,
            zone_delete: true
        }
    })
}

export const getZones = (hass: HomeAssistant) : Promise<Zone[]> => {
    return hass.callWS({
        type: "sprinkle/get_zones"
    })
}

export const createCycle = (hass: HomeAssistant, cycle: Partial<Cycle>) : Promise<boolean> => {
    return hass.callWS({
        type: "sprinkle/cycle",
        cycle: cycle
    })
}

export const modifyCycle = (hass: HomeAssistant, cycle: Partial<Cycle>) : Promise<boolean> => {
    return hass.callWS({
        type: "sprinkle/cycle",
        cycle: cycle
    })
}

export const deleteCycle = (hass: HomeAssistant, cycle_id: string) : Promise<boolean> => {
    return hass.callWS({
        type: "sprinkle/cycle",
        cycle: {
            cycle_id: cycle_id,
            cycle_delete: true
        }
    })
}

export const getCycles = (hass: HomeAssistant) : Promise<Cycle[]> => {
    return hass.callWS({
        type: "sprinkle/get_cycles"
    })
}

export const getGeneralSettings = (hass: HomeAssistant) : Promise<GeneralSettings> => {
    return hass.callWS({
        type: "sprinkle/get_gs"
    })
}


export const updateGeneralSettings = (hass: HomeAssistant, settingsObject: Partial<GeneralSettings>) : Promise<boolean> => {
    return hass.callWS({
        type: "sprinkle/gs",
        settings: settingsObject
    })
}