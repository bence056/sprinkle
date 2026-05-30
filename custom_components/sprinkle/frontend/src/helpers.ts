import {HomeAssistant} from "./types";
import {SprinklePanel} from "./sprinkle-panel";

    export function getValveEntities(hass: HomeAssistant): string[] {
    return Object.keys(hass.states).filter(eid => eid.startsWith('valve.'));
  }

    export function getValveName(hass: HomeAssistant, id: string): string {
    return hass.states[id]?.attributes.friendly_name || id;
  }

  export function getValveIcon(hass: HomeAssistant, id: string): string {
    return hass.states[id]?.attributes.icon || "mdi:valve";
  }

  export function createSimpleUUID(): string {
        const parts: string[] = [];
        for(let i=0; i<2; i++) {
            parts[i] = Math.floor((Date.now() * (Math.random() * 1024))).toString(36);
        }
        return parts.reduce((prev, currentValue) => prev.concat(currentValue));
  }