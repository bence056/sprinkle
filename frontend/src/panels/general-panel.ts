import {LitElement, html, css, Part} from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import {GeneralSettings, HomeAssistant, Zone} from '../types';
import {commonStyle} from "../style";
import {SubscribeMixin} from "../subscribe-mixin";
import {UnsubscribeFunc} from "home-assistant-js-websocket";
import {getGeneralSettings, apiUpdateGeneralSettings} from "../websockets";
import {getValveEntities, getValveName} from "../helpers";

@customElement('general-panel')
export class ZonePanel extends SubscribeMixin(LitElement) {

    hass!: HomeAssistant;
    private settingsObject!: GeneralSettings;
    @state()
    private modifiedSettingsObject!: GeneralSettings;
    @state()
    private settingsSaveNeeded: boolean = false;

    protected hassSubscribe(): Array<UnsubscribeFunc | Promise<UnsubscribeFunc>> {
        this.fetchData();
        return [this.hass.connection.subscribeMessage(()=> this.fetchData(), {type: "sprinkle_update_listen"})]
    }

    private async fetchData() {
        if(!this.hass) return;

           this.settingsObject = await getGeneralSettings(this.hass);
           this.modifiedSettingsObject = this.settingsObject;
           this.requestUpdate();

    }

    private updateGeneralSettings(partialSettings: Partial<GeneralSettings>) {
        this.modifiedSettingsObject = {...this.modifiedSettingsObject, ...partialSettings}
        if(!this.modifiedSettingsObject.use_master_valve) this.modifiedSettingsObject.master_valve_entity_id = "";
        this.settingsSaveNeeded = true;
    }

    private onSettingsSaveRequested() {
        //set id to empty string if the general settings

        //send the api call.
        apiUpdateGeneralSettings(this.hass, this.modifiedSettingsObject).then(() => {
            console.log("General settings updated.");
            this.settingsSaveNeeded = false;
            }
        );
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
                            this.updateGeneralSettings({
                                use_master_valve: (e.target as any).checked
                            });
                        }}" style="grid-area: switch; justify-content: space-around"></ha-switch>
                        <p style="grid-area: label; font-size: 18px; margin-right: 20px; display: flex; align-items: center">Use master valve</p>
                        <ha-select .value=${this.modifiedSettingsObject?.master_valve_entity_id || ""}
                                   .disabled = ${this.modifiedSettingsObject?.use_master_valve == false}
                                   .options=${getValveEntities(this.hass)
                                .sort((a,b) => 
                                getValveName(this.hass, a).localeCompare(getValveName(this.hass, b))).map((e) => (
                                                   {
                                                       value: e,
                                                       label: getValveName(this.hass, e)
                                                   }
                                           ))}
                                   @selected=${(e: CustomEvent) => {
                                            this.updateGeneralSettings({
                                                master_valve_entity_id: e.detail.value
                                            })}}
                                    @closed=${(e: CustomEvent) => e.stopPropagation()}
                                   style="grid-area: dropdown"></ha-select>
                    </div>
                    <div class="valve-delay-config">
                        <p style="font-size: 18px; margin-right: 5px; grid-area: label; display: flex; align-items: center">Valve transition delay (ms)</p>
                        <ha-icon id="help" style="grid-area: hint; display: flex; align-items: center" icon="mdi:help-circle"></ha-icon>
                        <ha-tooltip for="help">The minimum delay that has to pass after closing a valve, before a new set of valves can be opened.
                            <br/><br/>This is useful if you want to prevent high pressure fluctuations and backflow.</ha-tooltip>
                        <ha-input .value=${this.modifiedSettingsObject?.valve_toggle_delay_ms || 500}
                                  @input=${(e: Event) => this.updateGeneralSettings({
                                      valve_toggle_delay_ms: Number((e.target as HTMLInputElement).value)
                                  })}
                                  label="0 ms" type="number" min="0" max="5000" step="100" style="grid-area: input"></ha-input>
                        ${ this.settingsSaveNeeded ? 
                                html`<ha-button style="grid-area: save" @click=${() => {this.onSettingsSaveRequested();} }>Save</ha-button>` : ""}
                     
                </ha-expansion-panel>    
                </ha-card>
            </div>
            
        `;
    }

}