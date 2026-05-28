import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { HomeAssistant, Cycle, Schedule } from './types';
import {commonStyle} from "./style";
import "./panels/zone-panel"
import "./panels/cycle-panel"
import "./panels/general-panel"

@customElement('sprinkle-panel')
export class SprinklePanel extends LitElement {
  @property({ attribute: false }) hass!: HomeAssistant;
  @property({ type: Boolean, reflect: true }) public narrow!: boolean;

  static styles = [
      commonStyle,
      css`
          .header {
            width: 100%;
            margin: 0;
            padding: 0;
            max-height: 60px;
            background: var(--primary-color);
            background: white;
            display: flex;
            align-items: center;
            justify-content: start;
          }
          
          .header .tabs {
              align-self: end;
          }
          
      `
  ];

  render() {
      console.log(this.narrow);
    return html`
        
        <div class="header">
            ${this.narrow ? html`
            <ha-menu-button .hass=${this.hass} .narrow=${this.narrow}></ha-menu-button>` : null}
            <div class="tabs">
                <ha-tab-group @wa-tab-show=${(e) => console.log(e.detail.name)}>
                <ha-tab-group-tab panel="test">Test</ha-tab-group-tab>
                <ha-tab-group-tab panel="test2">Test2</ha-tab-group-tab>
            </ha-tab-group>
            </div>
        </div>
        
        <general-panel .hass=${this.hass} .narrow=${this.narrow}></general-panel>
        <zone-panel .hass=${this.hass} .narrow=${this.narrow}></zone-panel>
        <cycle-panel .hass=${this.hass} .narrow=${this.narrow}></cycle-panel>
    `
  }

}