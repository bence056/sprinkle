import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { HomeAssistant } from './types';
import {commonStyle} from "./style";
import "./panels/zone-panel"

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

  @state() private cycles: Cycle[] = [];
  @state() private schedules: Schedule[] = [];
  @state() private cycleBuffer: CycleEntry[] = [];

  static styles = commonStyle;

  render() {
    return html`
        <zone-panel .hass="${this.hass}"></zone-panel>
    `
  }


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


}