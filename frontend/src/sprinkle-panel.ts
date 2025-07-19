import {LitElement, html} from "lit";
import {property, customElement} from "lit/decorators.js"

@customElement("sprinkle-panel")
export class SprinklePanel extends LitElement {

    @property({type: Object})
    hass?: HomeAssistant

    render() {
        return html`
            <h1>Hello World</h1>
            ${this.hass?.states}
        `
        }

}