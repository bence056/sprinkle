import {HomeAssistant, Zone} from "./types";

export const modifyZone = (hass: HomeAssistant, zone: Partial<Zone>) : Promise<boolean> => {
    return hass.callApi('POST', 'sprinkle/zones', zone)
}

export const deleteZone = (hass: HomeAssistant, zone_id: string) : Promise<boolean> => {
    return hass.callApi('POST', 'sprinkle/zones', {
        zone_id: zone_id,
        zone_delete: true
    })
}

export const getZones = (hass: HomeAssistant) : Promise<Zone[]> => {
    return hass.callWS({
        type: "sprinkle/get_zones"
    })
}