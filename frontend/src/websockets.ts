import {HomeAssistant, Zone} from "./types";

export type ZoneRequest = {
    zone_id: string;
    zone_name: string;
    zone_valves: string[];
    zone_delete: boolean;
}

export const modifyZone = (hass: HomeAssistant, zone: Partial<ZoneRequest>) : Promise<boolean> => {
    zone.zone_delete = false;
    return hass.callApi('POST', 'sprinkle/zones', zone)
}

export const deleteZone = (hass: HomeAssistant, zone: Partial<ZoneRequest>) : Promise<boolean> => {
    zone.zone_delete = true;
    return hass.callApi('POST', 'sprinkle/zones', zone)
}