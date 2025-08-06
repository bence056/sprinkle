import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { HomeAssistant, Cycle, Schedule } from './types';
import {commonStyle} from "./style";
import "./panels/zone-panel"
import "./panels/cycle-panel"

@customElement('sprinkle-panel')
export class SprinklePanel extends LitElement {
  @property({ attribute: false }) hass!: HomeAssistant;

  static styles = commonStyle;

  render() {
    return html`
        <zone-panel .hass="${this.hass}"></zone-panel>
        <cycle-panel .hass="${this.hass}"></cycle-panel>
    `
  }

}