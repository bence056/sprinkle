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
            height: 50px;
            background: var(--primary-color);
            display: flex;
            align-items: center;
            justify-content: start;
          }
          
      `
  ];

  render() {
      console.log(this.narrow);
    return html`
        
        <div class="header">
            ${this.narrow ? html`
            <ha-menu-button .hass=${this.hass} .narrow=${this.narrow}></ha-menu-button>` : null}
        </div>
        
        <general-panel .hass="${this.hass}"></general-panel>
        <zone-panel .hass="${this.hass}"></zone-panel>
        <cycle-panel .hass="${this.hass}"></cycle-panel>
    `
  }

}