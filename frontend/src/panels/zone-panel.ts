import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { HomeAssistant } from '../types';
import {getValveName, getValveEntities, getValveIcon} from "../helpers";
import {commonStyle} from "../style";

interface Zone {
  id: string;
  name: string;
  valves: string[];
}

@customElement('zone-panel')
export class ZonePanel extends LitElement {

    hass!: HomeAssistant;

    @state() private zones: Zone[] = [];
    @state() private editingZone: Zone | null = null;
    @state() private selectedValves: Set<string> = new Set();
    @state() private zoneDialogOpen: boolean = false;
    @state() private zoneNameInput: string = '';

    static styles = commonStyle;

      render() {
    return html`
      <div class="section">
        <ha-card header="Zones">
          ${this.zones.map(zone => html`
            <ha-card>
              <div class="zone-entry">
                <div><strong>${zone.name}</strong></div>
                <div class="zone-valves">
                  ${zone.valves.map(valveId => html`
                    <div class="zone-valve-item">
                      <ha-icon icon=${getValveIcon(this.hass, valveId)}></ha-icon>
                      ${getValveName(this.hass, valveId)}
                    </div>
                  `)}
                </div>
                <div class="zone-actions">
                  <ha-button @click=${() => this.openZoneDialog(zone)}>Modify</ha-button>
                  <ha-button @click=${() => this.deleteZone(zone.id)}>Delete</ha-button>
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
    this.zoneNameInput = zone?.name || '';
    this.selectedValves = new Set(zone?.valves || []);
    this.zoneDialogOpen = true;
  }

  private closeZoneDialog() {
    this.zoneDialogOpen = false;
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
    if (!this.editingZone && this.zones.some(z => z.name.toLowerCase() === name.toLowerCase())) return;

    const newZone: Zone = {
      id: this.editingZone?.id || crypto.randomUUID(),
      name,
      valves: Array.from(this.selectedValves),
    };

    if (this.editingZone) {
      this.zones = this.zones.map(z => z.id === newZone.id ? newZone : z);
    } else {
      this.zones = [...this.zones, newZone];
    }

    this.closeZoneDialog();
  };

  private deleteZone = (id: string) => {
    this.zones = this.zones.filter(z => z.id !== id);
  };

  private renderZoneDialog() {
    if (!this.zoneDialogOpen) return null;
    return html`
      <ha-dialog open .heading="${this.editingZone ? 'Modify Zone' : 'Add Zone'}" @closed=${this.closeZoneDialog}>
        <div>
          <ha-textfield
            label="Zone Name"
            .value=${this.zoneNameInput}
            @input=${(e: Event) => this.zoneNameInput = (e.target as HTMLInputElement).value}
          ></ha-textfield>
          <div class="valve-checkboxes">
            ${getValveEntities(this.hass).map(id => html`
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
        <ha-button slot="primaryAction" dialogAction="save" @click=${this.saveZone}>Save</ha-button>
        <ha-button slot="secondaryAction" dialogAction="cancel" @click=${this.closeZoneDialog}>Cancel</ha-button>
      </ha-dialog>
    `;
  }

}