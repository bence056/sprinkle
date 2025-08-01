import {HomeAssistant, Zone} from "./types";

export type ZoneRequest = {
    zone_id: string;
    zone_name: string;
    zone_valves: string[];
    zone_delete: boolean;
}

export const saveZone = (hass: HomeAssistant, zone: Partial<ZoneRequest>) : Promise<boolean> => {
    zone.zone_delete = false;
    return hass.callApi('POST', 'sprinkle/zones', zone)
}