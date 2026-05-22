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


    protected hassSubscribe(): Array<UnsubscribeFunc | Promise<UnsubscribeFunc>> {
        this.fetchData();
        return [this.hass.connection.subscribeMessage(()=> this.fetchData(), {type: "sprinkle_update_listen"})]
    }

    private async fetchData() {
        if(!this.hass) return;

           this.settingsObject = await getGeneralSettings(this.hass);
           this.requestUpdate();

    }

    private onSettingsChanged() {
        //set id to empty string if the general settings
        if(!this.settingsObject.useMasterValve) this.settingsObject.masterValveEntityId = "";

        //send the api call.
        updateGeneralSettings(this.hass, this.settingsObject).then(() => console.log("General settings updated."))
    }

    static styles = [
        commonStyle,
        css`
        
            .horizontal-split {
                display: grid;
                grid-template-areas: 'label switch' 'dropdown dropdown';
                grid-template-rows: auto auto;
                grid-template-columns: auto auto;
                justify-content: start;
                align-content: center;
                width: 30%;
            }
            
        `
    ];

    render() {
        return html`
            <div class="section">
                <ha-card header="General Settings">
                <ha-expansion-panel expanded=true header="Master Valve">
                    <div class="horizontal-split">
                        <ha-switch .checked=${this.settingsObject?.useMasterValve || false} @change="${(e: Event) => {
                            this.settingsObject.useMasterValve = (e.target as any).checked;
                            this.onSettingsChanged();
                        }}" style="grid-area: switch; justify-content: space-around"></ha-switch>
                        <p style="grid-area: label; font-size: 18px; margin-right: 20px">Use master valve</p>
                        <ha-select .value=${this.settingsObject?.masterValveEntityId || ""}
                                   .disabled = ${this.settingsObject?.useMasterValve == false || true}
                                   .options=${getValveEntities(this.hass)
                                .sort((a,b) => 
                                getValveName(this.hass, a).localeCompare(getValveName(this.hass, b))).map((e) => (
                                                   {
                                                       value: e,
                                                       label: getValveName(this.hass, e)
                                                   }
                                           ))}
                                   @selected=${(e: CustomEvent) => {
                                            this.settingsObject.masterValveEntityId = e.detail.value;
                                            this.onSettingsChanged();}}
                                    @closed=${(e: CustomEvent) => e.stopPropagation()}
                                   style="grid-area: dropdown"></ha-select>
                    </div>
                </ha-expansion-panel>
                </ha-card>
            </div>
            
        `;
    }

}