import {LitElement, html} from "lit";
import {property, customElement} from "lit/decorators.js"
import {HomeAssistant} from "../types";

@customElement("sprinkle-panel")
export class SprinklePanel extends LitElement {

    @property({type: Object})
    hass?: HomeAssistant

    @property() duration = {
        days: 0,
        hours: 1,
        minutes: 30,
        seconds: 0,
        milliseconds: 0,
    };

    render() {
        return html`
            <ha-card header="Zones">
                <div class="card-content">
                    <ha-button @click=${this.handleClick}>Test</ha-button>
                </div>
            </ha-card>
            <ha-card header="Cycles">
                <div class="card-content">
                    <ha-selector-icon label="Test Label"></ha-selector-icon>
                    <ha-control-select-menu options=${['a', 'b', 'c']} label="Select from here" show-arrow=true></ha-control-select-menu>
                    <ha-textfield></ha-textfield>
                </div>
            </ha-card>
            <ha-card header="Schedules">
                <div class="card-content">
                </div>
            </ha-card>
        `
        }

    handleClick() {
        console.log("Button Clicked!");
        this.hass?.connection.sendMessagePromise({
            type: "sprinkle/log",
            message: "Hello World"
        }).then(() => console.log("Sent!"))
    }

}