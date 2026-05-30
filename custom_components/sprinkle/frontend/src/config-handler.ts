import {ConfigEntry, HomeAssistant} from "./types";
import {getConfigEntries, configureWebsocketEntry} from "./websockets";

export class ConfigHandler {


    public static instance: ConfigHandler = new ConfigHandler()

    private config_entries: ConfigEntry[] = [];
    private active_entry?: ConfigEntry;

    private entryChangeCallback?: () => void;

    public get active_entry_id(): string {
        return this.active_entry?.entry_id || this.config_entries[0].entry_id
    }

    public get active_entry_name(): string {
        return this.active_entry?.entry_name || this.config_entries[0].entry_name
    }

    public get entries() {
        return this.config_entries;
    }

    private notifyConfigChanged()
    {
        if (this.entryChangeCallback) {
            this.entryChangeCallback();
        }
    }

    public async registerHandler(hass: HomeAssistant, callback) {
        this.entryChangeCallback = callback;
        this.config_entries = await getConfigEntries(hass);
        if(this.config_entries.length > 0) {
            this.active_entry = this.config_entries[0];
            configureWebsocketEntry(()=> {
                return this.active_entry_id;
            });
            this.notifyConfigChanged();
        }

    }

    public selectEntry(entryId: string) {
        console.log(entryId);
        let foundEntry = this.entries.find((entry) => entry.entry_id == entryId);
        if(foundEntry != undefined) {
            this.active_entry = foundEntry;
            this.notifyConfigChanged();
        }
    }

}