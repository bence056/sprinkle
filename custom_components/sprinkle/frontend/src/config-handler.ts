import {ConfigEntry, HomeAssistant} from "./types";
import {getConfigEntries, configureWebsocketEntry} from "./websockets";
import {UnsubscribeFunc} from "home-assistant-js-websocket";

export type EntryUpdateFunc = (newEntry: ConfigEntry | undefined) => void;

export class ConfigHandler {


    public static instance: ConfigHandler = new ConfigHandler()

    private hass?: HomeAssistant

    private config_entries: ConfigEntry[] = [];
    private active_entry?: ConfigEntry;

    private updateSubscriptions: Array<EntryUpdateFunc> = []
    private _hassUnsub?: UnsubscribeFunc

    public get active_entry_id(): string {
        return this.active_entry?.entry_id || ""
    }

    public get active_entry_name(): string {
        return this.active_entry?.entry_name || ""
    }

    public get entries() {
        return this.config_entries;
    }

    private notifyConfigChanged()
    {
        this.updateSubscriptions.forEach((update) => {
            update(this.active_entry);
        });
    }

    private async configArrayChangedCallback() {
        if(this.hass) {
            let oldEntry: ConfigEntry = {
                entry_id: this.active_entry_id,
                entry_name: this.active_entry_name
            }
            this.config_entries = await getConfigEntries(this.hass);
            if(!this.selectEntry(oldEntry.entry_id)) {
                //if the new array has elements, use the first one.
                if(this.config_entries.length > 0) {
                    this.active_entry = this.config_entries[0];
                }else {
                    this.active_entry = undefined;
                }
                this.notifyConfigChanged()
            }
        }
    }

    public subscribeToEntryChange(callback: EntryUpdateFunc) {
        this.updateSubscriptions.push(callback);
    }

    public async registerHass(hass: HomeAssistant) {
        this.hass = hass;
        this._hassUnsub = await this.hass.connection.subscribeMessage(() => this.configArrayChangedCallback(), { type: "sprinkle_update_listen" })
        configureWebsocketEntry(() => this.active_entry_id);
        await this.configArrayChangedCallback()
    }

    public selectEntry(entryId: string): boolean {
        let foundEntry = this.entries.find((entry) => entry.entry_id == entryId);
        if(foundEntry != undefined) {
            this.active_entry = foundEntry;
            this.notifyConfigChanged();
            return true;
        }
        return false;
    }

}