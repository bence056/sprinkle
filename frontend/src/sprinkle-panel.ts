import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { HomeAssistant } from './types';
import '@material/mwc-button';
import '@material/mwc-textfield';
import '@material/mwc-list/mwc-list-item';
import '@ha/components/ha-card';
import '@ha/components/ha-select';
import '@ha/components/ha-textfield';
import '@ha/components/ha-button';
import '@ha/components/ha-checkbox';
import '@ha/components/ha-dialog';
import '@ha/components/ha-icon';

interface Zone {
  id: string;
  name: string;
  valves: string[];
}

interface CycleEntry {
  zoneId: string;
  time: number;
}

interface Cycle {
  id: string;
  name: string;
  entries: CycleEntry[];
}

interface Schedule {
  id: string;
  name: string;
  days: string[];
  times: string[];
  cycleId: string;
}

@customElement('sprinkle-panel')
export class SprinklePanel extends LitElement {
  @property({ attribute: false }) hass!: HomeAssistant;

  @state() private zones: Zone[] = [];
  @state() private cycles: Cycle[] = [];
  @state() private schedules: Schedule[] = [];
  @state() private cycleBuffer: CycleEntry[] = [];
  @state() private selectedValves: Set<string> = new Set();
  @state() private zoneDialogOpen: boolean = false;
  @state() private editingZone: Zone | null = null;
  @state() private zoneNameInput: string = '';

  static styles = css`
    ha-card {
      margin: 16px;
      padding: 16px;
    }
    .section {
      margin-bottom: 32px;
    }
    .form-row {
      display: flex;
      align-items: center;
      gap: 16px;
      flex-wrap: wrap;
    }
    .valve-checkboxes {
      display: flex;
      flex-direction: column;
      max-height: 200px;
      overflow-y: auto;
      padding: 8px;
      border: 1px solid #ccc;
      border-radius: 8px;
      margin-top: 16px;
    }
    .valve-select-row {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .zone-entry {
      display: grid;
      grid-template-columns: 1fr 2fr auto;
      align-items: center;
      gap: 16px;
      padding: 8px;
    }   
    .zone-valves {
      display: flex;
      flex-direction: column;
    }
    .zone-valve-item {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .zone-actions {
      display: flex;
      flex-direction: row;
      gap: 8px;
      justify-content: flex-end;
    }
    ha-dialog::part(content) {
      width: 500px;
    }
  `;

  private get valveEntities(): string[] {
    return Object.keys(this.hass.states).filter(eid => eid.includes('valve'));
  }

  private getValveName(id: string): string {
    return this.hass.states[id]?.attributes.friendly_name || id;
  }

  private getValveIcon(id: string): string {
    return this.hass.states[id]?.attributes.icon || "mdi:valve";
  }

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
                      <ha-icon icon=${this.getValveIcon(valveId)}></ha-icon>
                      ${this.getValveName(valveId)}
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

      ${this.renderCycles()}
      ${this.renderSchedules()}
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
            ${this.valveEntities.map(id => html`
              <label class="valve-select-row">
                <ha-checkbox
                  .checked=${this.selectedValves.has(id)}
                  @change=${(e: Event) => this.toggleValve(id, (e.target as HTMLInputElement).checked)}
                ></ha-checkbox>
                ${this.getValveName(id)}
                  <ha-icon icon=${this.getValveIcon(id)}></ha-icon>
              </label>
            `)}
          </div>
        </div>
        <ha-button slot="primaryAction" dialogAction="save" @click=${this.saveZone}>Save</ha-button>
        <ha-button slot="secondaryAction" dialogAction="cancel" @click=${this.closeZoneDialog}>Cancel</ha-button>
      </ha-dialog>
    `;
  }

  // ... rest of renderCycles and renderSchedules unchanged ...

  private addCycleEntry = () => {
    const zoneId = (this.shadowRoot!.getElementById('cycle-zone') as any).value;
    const time = parseInt((this.shadowRoot!.getElementById('cycle-time') as any).value, 10);
    if (!zoneId || isNaN(time)) return;
    this.cycleBuffer = [...this.cycleBuffer, { zoneId, time }];
  };

  private moveEntry(index: number, direction: number) {
    const newIndex = index + direction;
    if (newIndex < 0 || newIndex >= this.cycleBuffer.length) return;
    const updated = [...this.cycleBuffer];
    const [moved] = updated.splice(index, 1);
    updated.splice(newIndex, 0, moved);
    this.cycleBuffer = updated;
  }

  private removeEntry(index: number) {
    this.cycleBuffer = this.cycleBuffer.filter((_, i) => i !== index);
  }

  private createCycle = () => {
    const name = (this.shadowRoot!.getElementById('cycle-name') as any).value.trim();
    if (!name || this.cycleBuffer.length === 0) return;
    this.cycles = [...this.cycles, { id: crypto.randomUUID(), name, entries: [...this.cycleBuffer] }];
    this.cycleBuffer = [];
  };

  private deleteCycle = (id: string) => {
    this.cycles = this.cycles.filter(c => c.id !== id);
  };

  private createSchedule = () => {
    const name = (this.shadowRoot!.getElementById('schedule-name') as any).value.trim();
    const cycleId = (this.shadowRoot!.getElementById('schedule-cycle') as any).value;
    const days = (this.shadowRoot!.getElementById('schedule-days') as any).value.split(',').map((d: string) => d.trim().toLowerCase());
    const times = (this.shadowRoot!.getElementById('schedule-times') as any).value.split(',').map((t: string) => t.trim());
    if (!name || !cycleId || days.length === 0 || times.length === 0) return;
    this.schedules = [...this.schedules, { id: crypto.randomUUID(), name, days, times, cycleId }];
  };

  private deleteSchedule = (id: string) => {
    this.schedules = this.schedules.filter(s => s.id !== id);
  };

  private renderCycles() {
    return html`
      <div class="section">
        <ha-card header="Cycles">
          ${this.cycles.map(cycle => html`
            <div>
              <strong>${cycle.name}</strong>
              <ul>
                ${cycle.entries.map((entry, idx) => {
                  const zone = this.zones.find(z => z.id === entry.zoneId);
                  return html`<li>${zone?.name || 'Unknown'}: ${entry.time} min
                    <ha-button @click=${() => this.moveEntry(idx, -1)}>↑</ha-button>
                    <ha-button @click=${() => this.moveEntry(idx, 1)}>↓</ha-button>
                    <ha-button @click=${() => this.removeEntry(idx)}>Remove</ha-button>
                  </li>`;
                })}
              </ul>
              <ha-button @click=${() => this.deleteCycle(cycle.id)}>Delete</ha-button>
            </div>
          `)}
          <div class="form-row">
            <ha-textfield label="Cycle Name" id="cycle-name"></ha-textfield>
            <ha-select label="Zone" id="cycle-zone">
              ${this.zones.map(z => html`<mwc-list-item value="${z.id}">${z.name}</mwc-list-item>`)}
            </ha-select>
            <ha-textfield label="Time (min)" id="cycle-time" type="number"></ha-textfield>
            <ha-button @click=${this.addCycleEntry}>Add Entry</ha-button>
            <ha-button @click=${this.createCycle}>Create Cycle</ha-button>
          </div>
        </ha-card>
      </div>
    `;
  }

  private renderSchedules() {
    return html`
      <div class="section">
        <ha-card header="Schedules">
          ${this.schedules.map(schedule => {
            const cycle = this.cycles.find(c => c.id === schedule.cycleId);
            return html`
              <div>
                <strong>${schedule.name}</strong>
                <p>Days: ${schedule.days.join(', ')}</p>
                <p>Times: ${schedule.times.join(', ')}</p>
                <p>Cycle: ${cycle?.name || 'Unknown'}</p>
                <ha-button @click=${() => this.deleteSchedule(schedule.id)}>Delete</ha-button>
              </div>
            `;
          })}
          <div class="form-row">
            <ha-textfield label="Schedule Name" id="schedule-name"></ha-textfield>
            <ha-select label="Cycle" id="schedule-cycle">
              ${this.cycles.map(c => html`<mwc-list-item value="${c.id}">${c.name}</mwc-list-item>`)}
            </ha-select>
            <ha-textfield label="Days (mon,tue,...)" id="schedule-days"></ha-textfield>
            <ha-textfield label="Times (HH:MM,...)" id="schedule-times"></ha-textfield>
            <ha-button @click=${this.createSchedule}>Add Schedule</ha-button>
          </div>
        </ha-card>
      </div>
    `;
  }
}