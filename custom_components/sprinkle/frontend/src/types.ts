import { HassEntity, HassEntityAttributeBase, MessageBase, Connection, HassEntities, HassServices } from 'home-assistant-js-websocket';

export interface Dictionary<TValue> {
  [id: string]: TValue;
}

export interface ServiceCallRequest {
  domain: string;
  service: string;
  serviceData?: Record<string, any>;
  target?: {
    entity_id?: string | string[];
    device_id?: string | string[];
    area_id?: string | string[];
  };
}

export interface HomeAssistant {
  connection: Connection;
  language: string;
  panels: {
    [name: string]: {
      component_name: string;
      config: { [key: string]: any } | null;
      icon: string | null;
      title: string | null;
      url_path: string;
    };
  };
  states: HassEntities;
  services: HassServices;
  localize: (key: string, ...args: any[]) => string;
  translationMetadata: {
    fragments: string[];
    translations: {
      [lang: string]: {
        nativeName: string;
        isRTL: boolean;
        fingerprints: { [fragment: string]: string };
      };
    };
  };
  callApi: <T>(
    method: "GET" | "POST" | "PUT" | "DELETE",
    path: string,
    parameters?: { [key: string]: any }
  ) => Promise<T>;
  callService: (
    domain: ServiceCallRequest["domain"],
    service: ServiceCallRequest["service"],
    serviceData?: ServiceCallRequest["serviceData"],
    target?: ServiceCallRequest["target"]
  ) => Promise<void>;
  callWS: <T>(msg: MessageBase) => Promise<T>;
}

export interface Schedule {
  id: string;
  name: string;
  days: string[];
  times: string[];
  cycleId: string;
}


export interface Zone {
  zone_id: string;
  zone_name: string;
  zone_valves: string[];
}

export interface Cycle {
    cycle_id: string;
    cycle_name: string;
    cycle_steps: CycleStep[];
}

export interface CycleStep {
    zone_id: string;
    zone_minutes: number;
}

export interface GeneralSettings {
    use_master_valve: boolean;
    master_valve_entity_id: string;
    valve_toggle_delay_ms: number;
}