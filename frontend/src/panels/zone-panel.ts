import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { HomeAssistant, Zone } from '../types';
import {getValveName, getValveEntities, getValveIcon, createSimpleUUID} from "../helpers";
import {commonStyle} from "../style";
import {SubscribeMixin} from "../subscribe-mixin";
import {UnsubscribeFunc} from "home-assistant-js-websocket";
import {createZone, deleteZone as apiDeleteZone, getGeneralSettings, getZones, modifyZoneValves} from '../websockets'

@customElement('zone-panel')
export class ZonePanel extends SubscribeMixin(LitElement) {

    hass!: HomeAssistant;

    @state() private zones: Zone[] = [];
    @state() private master_valve: string = ""
    @state() private editingZone: Zone | null = null;
    @state() private selectedValves: Set<string> = new Set();
    @state() private zoneDialogOpen: boolean = false;
    @state() private zoneDialogModifyOnly: boolean = false;
    @state() private zoneNameInput: string = '';

    protected hassSubscribe(): Array<UnsubscribeFunc | Promise<UnsubscribeFunc>> {
        this.fetchData();
        return [this.hass.connection.subscribeMessage(()=> this.fetchData(), {type: "sprinkle_update_listen"})]
    }

    private async fetchData() {
        if(!this.hass) return;

           this.zones = await getZones(this.hass);
           this.master_valve = (await getGeneralSettings(this.hass)).master_valve_entity_id;
           this.requestUpdate();

    }

    static styles = commonStyle;

    render() {
        return html`
            <div class="section">
                <ha-card header="Zones">
                    ${this.zones.map(zone => html`
                        <ha-card>
                            <div class="zone-entry">
                                <div><strong>${zone.zone_name}</strong></div>
                                <div class="zone-valves">
                                    ${zone.zone_valves.map(valveId => html`
                                        <div class="zone-valve-item">
                                            <ha-icon icon=${getValveIcon(this.hass, valveId)}></ha-icon>
                                            ${getValveName(this.hass, valveId)}
                                        </div>
                                    `)}
                                </div>
                                <div class="zone-actions">
                                    <ha-button @click=${() => this.openZoneDialog(zone)}>Modify</ha-button>
                                    <ha-button @click=${() => this.deleteZone(zone.zone_id)}>Delete</ha-button>
                                </div>
                            </div>
                        </ha-card>
                    `)}
                    <ha-button @click=${() => this.openZoneDialog(null)}>Add Zone</ha-button>
                </ha-card>
            </div>

            ${this.renderZoneDialog()}
        `;
    }

    private openZoneDialog(zone: Zone | null) {
        this.editingZone = zone;
        this.zoneNameInput = zone?.zone_name || '';
        if(zone) this.zoneDialogModifyOnly = true
        this.selectedValves = new Set(zone?.zone_valves || []);
        this.zoneDialogOpen = true;
    }

    private closeZoneDialog() {
        this.zoneDialogOpen = false;
        this.zoneDialogModifyOnly = false;
        this.editingZone = null;
        this.zoneNameInput = '';
        this.selectedValves.clear();
    }

    private toggleValve(valveId: string, checked: boolean) {
        if (checked) {
            this.selectedValves.add(valveId);
        } else {
            this.selectedValves.delete(valveId);
        }
        this.selectedValves = new Set(this.selectedValves);
    }

    private saveZone = () => {
        const name = this.zoneNameInput.trim();
        if (!name || this.selectedValves.size === 0) return;
        if (!this.editingZone && this.zones.some(z => z.zone_name.toLowerCase() === name.toLowerCase())) return;

        if(this.zoneDialogModifyOnly && this.editingZone) {
            modifyZoneValves(this.hass, this.editingZone.zone_id, Array.from(this.selectedValves)).then(() => {
                console.log("API call finished");
            });
        }else {
            const newZone: Zone = {
            zone_id: this.editingZone?.zone_id || `zone-${createSimpleUUID()}`,
            zone_name: name,
            zone_valves: Array.from(this.selectedValves),
        };
            createZone(this.hass, newZone).then(() => {
                console.log("API call finished");
            });
        }

        this.closeZoneDialog();
    };

    private deleteZone = (id: string) => {
        this.zones = this.zones.filter(z => z.zone_id !== id);
        apiDeleteZone(this.hass, id).then(()=> {
            console.log("API call finished");
        });
    };

    private renderZoneDialog() {
        if (!this.zoneDialogOpen) return null;
        return html`
            <ha-dialog open header-title="${this.editingZone ? 'Modify Zone' : 'Add Zone'}" @closed=${this.closeZoneDialog}>
                <div>
                    <ha-input
                            label="Zone Name"
                            .value=${this.zoneNameInput}
                            @input=${(e: Event) => this.zoneNameInput = (e.target as HTMLInputElement).value}
                            ?disabled=${this.zoneDialogModifyOnly}
                    ></ha-input>
                    <div class="valve-checkboxes">
                        ${getValveEntities(this.hass).filter((a) => a != this.master_valve)
                                .sort((a,b) => 
                                getValveName(this.hass, a).localeCompare(getValveName(this.hass, b)))
                                .map(id => html`
                            <label class="valve-select-row">
                                <ha-checkbox
                                        .checked=${this.selectedValves.has(id)}
                                        @change=${(e: Event) => this.toggleValve(id, (e.target as HTMLInputElement).checked)}
                                ></ha-checkbox>
                                ${getValveName(this.hass, id)}
                                <ha-icon icon=${getValveIcon(this.hass, id)}></ha-icon>
                            </label>
                        `)}
                    </div>
                </div>
                <ha-dialog-footer slot="footer">
                <ha-button slot="primaryAction" dialogAction="save"
                           @click=${this.saveZone}
                           .disabled=${this.zoneNameInput == "" || this.selectedValves.size <= 0}>Save</ha-button>
                <ha-button slot="secondaryAction" dialogAction="cancel" @click=${this.closeZoneDialog}>Cancel</ha-button>
                </ha-dialog-footer>
            </ha-dialog>
        `;
    }

}