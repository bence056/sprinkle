import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import {GeneralSettings, HomeAssistant, Zone} from '../types';
import {commonStyle} from "../style";
import {SubscribeMixin} from "../subscribe-mixin";
import {UnsubscribeFunc} from "home-assistant-js-websocket";
import {getGeneralSettings, updateGeneralSettings} from "../websockets";
import {getValveEntities, getValveName} from "../helpers";

@customElement('general-panel')
export class ZonePanel extends SubscribeMixin(LitElement) {

    hass!: HomeAssistant;
    settingsObject!: GeneralSettings;
    @state()
    modifiedValveDelay!: number;


    protected hassSubscribe(): Array<UnsubscribeFunc | Promise<UnsubscribeFunc>> {
        this.fetchData();
        return [this.hass.connection.subscribeMessage(()=> this.fetchData(), {type: "sprinkle_update_listen"})]
    }

    private async fetchData() {
        if(!this.hass) return;

           this.settingsObject = await getGeneralSettings(this.hass);
           this.modifiedValveDelay = this.settingsObject.valve_toggle_delay_ms;
           this.requestUpdate();

    }

    private onSettingsChanged() {
        //set id to empty string if the general settings
        if(!this.settingsObject.use_master_valve) this.settingsObject.master_valve_entity_id = "";

        //send the api call.
        updateGeneralSettings(this.hass, this.settingsObject).then(() => console.log("General settings updated."))
    }

    static styles = [
        commonStyle,
        css`
        
            .master-valve-config {
                display: grid;
                grid-template-areas: 'label switch' 'dropdown dropdown';
                grid-template-rows: auto auto;
                grid-template-columns: auto auto;
                justify-content: start;
                align-content: center;
                width: 30%;
                margin-bottom: 30px;
            }
            
            .valve-delay-config {
                display: grid;
                grid-template-areas: 'label hint' 'input input' 'save -';
                grid-template-rows: 1fr 1fr auto;
                grid-template-columns: auto auto;
                justify-content: start;
                align-content: center;
                width: 30%;
                margin-bottom: 30px;
            }
            
        `
    ];

    render() {
        return html`
            <div class="section">
                <ha-card header="General Settings">
                <ha-expansion-panel expanded=true header="Valves">
                    <div class="master-valve-config">
                        <ha-switch .checked=${this.settingsObject?.use_master_valve || false} @change="${(e: Event) => {
                            this.settingsObject.use_master_valve = (e.target as any).checked;
                            this.onSettingsChanged();
                        }}" style="grid-area: switch; justify-content: space-around"></ha-switch>
                        <p style="grid-area: label; font-size: 18px; margin-right: 20px; display: flex; align-items: center">Use master valve</p>
                        <ha-select .value=${this.settingsObject?.master_valve_entity_id || ""}
                                   .disabled = ${this.settingsObject?.use_master_valve == false}
                                   .options=${getValveEntities(this.hass)
                                .sort((a,b) => 
                                getValveName(this.hass, a).localeCompare(getValveName(this.hass, b))).map((e) => (
                                                   {
                                                       value: e,
                                                       label: getValveName(this.hass, e)
                                                   }
                                           ))}
                                   @selected=${(e: CustomEvent) => {
                                            this.settingsObject.master_valve_entity_id = e.detail.value;
                                            this.onSettingsChanged();}}
                                    @closed=${(e: CustomEvent) => e.stopPropagation()}
                                   style="grid-area: dropdown"></ha-select>
                    </div>
                    <div class="valve-delay-config">
                        <p style="font-size: 18px; margin-right: 5px; grid-area: label; display: flex; align-items: center">Valve transition delay (ms)</p>
                        <ha-icon id="help" style="grid-area: hint; display: flex; align-items: center" icon="mdi:help-circle"></ha-icon>
                        <ha-tooltip for="help">The minimum delay that has to pass between stopping a valve and starting the next one</ha-tooltip>
                        <ha-input .value=${this.modifiedValveDelay}
                                  @input=${(e: Event) => this.modifiedValveDelay = Number((e.target as HTMLInputElement).value)}
                                  label="0 ms" type="number" min="0" max="5000" step="100" style="grid-area: input"></ha-input>
                        ${ this.settingsObject.valve_toggle_delay_ms != this.modifiedValveDelay ? 
                                html`<ha-button style="grid-area: save" @click=${() => {this.settingsObject.valve_toggle_delay_ms = this.modifiedValveDelay; this.onSettingsChanged();} }>Save</ha-button>` : ""}
                     
                </ha-expansion-panel>    
                </ha-card>
            </div>
            
        `;
    }

}