import {LitElement, html, css, PropertyValues} from 'lit';
import {customElement, property, state, query} from 'lit/decorators.js';
import {HomeAssistant, Cycle, Schedule, ConfigEntry} from './types';
import {commonStyle} from "./style";
import "./panels/zone-panel"
import "./panels/cycle-panel"
import "./panels/general-panel"
import {getConfigEntries} from "./websockets";
import {ConfigHandler} from "./config-handler";
import {config} from "home-assistant-js-websocket/dist/messages";

@customElement('sprinkle-panel')
export class SprinklePanel extends LitElement {
    @property({attribute: false}) hass!: HomeAssistant;
    @property({type: Boolean, reflect: true}) public narrow!: boolean;

    @state() tab: string = "setup"
    @state() private config_ready: boolean = false;

    connectedCallback() {
        super.connectedCallback()
        //Get the config entry data.
        ConfigHandler.instance.registerHass(this.hass).then(() => {
            this.config_ready = true;
        });
        ConfigHandler.instance.subscribeToEntryChange((newEntry) => {
            this.config_ready = newEntry != undefined;
            //request update to update the selector and the menubar.
            this.requestUpdate();
        });
    }

    static styles = [
        commonStyle,
        css`

            .header {
                width: 100%;
                margin: 0;
                padding: 0;
                background: var(--card-background-color);
                display: flex;
                align-items: center;
            }

            .tabs {
                display: inline-flex;
                align-items: center;
                align-self: end;
                justify-content: start;
            }

            .config-selector {
                display: inline-flex;
                flex-direction: row-reverse;
                padding: 5px 20px;
                margin-left: auto;
            }

            @media (max-width: 600px) {

                .header {

                }

            }
        `
    ];

    private renderTabs() {

        if (this.tab == "setup") {
            return html`
                <general-panel .hass=${this.hass} .narrow=${this.narrow}></general-panel>
                <zone-panel .hass=${this.hass} .narrow=${this.narrow}></zone-panel>
                <cycle-panel .hass=${this.hass} .narrow=${this.narrow}></cycle-panel>
            `

        }
        return null;
    }

    render() {

        if (!this.config_ready) {
            return html`
                Loading...`
        }


        return html`

            <div class="header">
                <div class="tabs">
                    ${this.narrow ? html`
                        <ha-menu-button .hass=${this.hass} .narrow=${this.narrow}></ha-menu-button>` : null}
                    <ha-tab-group @wa-tab-show=${(e: CustomEvent) => this.tab = e.detail.name}>
                        <ha-tab-group-tab panel="setup">Setup</ha-tab-group-tab>
                        <ha-tab-group-tab panel="schedule">Scheduling</ha-tab-group-tab>
                </div>

                <div class="config-selector">
                    <ha-dropdown class="button" @wa-select=${(e: CustomEvent)=> ConfigHandler.instance.selectEntry(e.detail.item.value)}>
                        <ha-button slot="trigger" with-caret>${ConfigHandler.instance.active_entry_name}</ha-button>

                        ${ConfigHandler.instance.entries.map(entry => {

                            return html`

                                <ha-dropdown-item value=${entry.entry_id}>
                                    <ha-icon
                                            icon=${ConfigHandler.instance.active_entry_id == entry.entry_id ? "mdi:circle-slice-8" : "mdi:circle-outline"}></ha-icon>
                                    ${entry.entry_name}
                                </ha-dropdown-item>

                            `

                        })}


                        <ha-dropdown>
                </div>
            </div>

            ${this.renderTabs()}
        `
    }

}