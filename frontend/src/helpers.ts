import {HomeAssistant} from "./types";

    export function getValveEntities(hass: HomeAssistant): string[] {
    return Object.keys(hass.states).filter(eid => eid.startsWith('valve.'));
  }

    export function getValveName(hass: HomeAssistant, id: string): string {
    return hass.states[id]?.attributes.friendly_name || id;
  }

  export function getValveIcon(hass: HomeAssistant, id: string): string {
    return hass.states[id]?.attributes.icon || "mdi:valve";
  }

  export function zoneNameToId(zoneName: string) {
        let zone_id = zoneName.replace(/ /g, "_");
        zone_id = "sprinkle_" + zone_id;
        return zone_id;
  }