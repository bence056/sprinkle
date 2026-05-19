import { LitElement, html, css } from 'lit';
import { customElement, state } from 'lit/decorators.js';
import { HomeAssistant, Cycle, CycleStep } from '../types';
import { commonStyle } from "../style";
import { SubscribeMixin } from "../subscribe-mixin";
import { UnsubscribeFunc } from "home-assistant-js-websocket";
import { getCycles, getZones, createCycle, modifyCycle, deleteCycle } from "../websockets";
import { getValveName } from "../helpers";

@customElement('cycle-panel')
export class CyclePanel extends SubscribeMixin(LitElement) {

    hass!: HomeAssistant;

    @state() private cycles: Cycle[] = [];
    @state() private editingCycle: Cycle | null = null;
    @state() private cycleDialogOpen: boolean = false;
    @state() private cycleDialogModifyOnly: boolean = false;
    @state() private cycleNameInput: string = '';
    @state() private availableZones: { id: string; name: string }[] = [];
    @state() private currentSteps: CycleStep[] = [];

    protected hassSubscribe(): Array<UnsubscribeFunc | Promise<UnsubscribeFunc>> {
        this.fetchData();
        return [this.hass.connection.subscribeMessage(() => this.fetchData(), { type: "sprinkle_update_listen" })];
    }

    private async fetchData() {
        this.cycles = await getCycles(this.hass);
        console.log(this.cycles);
        const zones = await getZones(this.hass);
        this.availableZones = zones.sort((a,b)=>a.zone_name.localeCompare(b.zone_name))
            .map(z => ({ id: z.zone_id, name: z.zone_name }));
        this.requestUpdate();
    }

    static styles = [
        commonStyle,
        css`
        .step-row {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 8px;
        }

        ha-select, ha-textfield {
            width: 150px;
        }

        .move-buttons {
            display: flex;
            flex-direction: column;
        }
    `
    ];

    render() {
        return html`
            <div class="section">
                <ha-card header="Cycles">
                    ${this.cycles.map(cycle => html`
                        <ha-card>
                            <div class="zone-entry">
                                <div><strong>${cycle.cycle_name}</strong></div>
                                <div class="zone-valves">
                                    ${cycle.cycle_steps.map(step => html`
                                        <div class="zone-valve-item">
                                            <ha-icon icon="mdi:grass"></ha-icon>
                                                ${this.availableZones.find((z) => z.id === step.zone_id)?.name || "N/A"}:
                                            <ha-icon icon="mdi:timer-marker-outline"></ha-icon>
                                                ${step.zone_minutes} min
                                        </div>
                                    `)}
                                </div>
                                <div class="zone-actions">
                                    <ha-button @click=${() => this.openCycleDialog(cycle)}>Modify</ha-button>
                                    <ha-button @click=${() => this.deleteCycle(cycle.cycle_id)}>Delete</ha-button>
                                </div>
                            </div>
                        </ha-card>
                    `)}
                    <ha-button .disabled=${this.availableZones.length == 0} @click=${() => this.openCycleDialog(null)}>Add Cycle</ha-button>
                </ha-card>
            </div>

            ${this.renderCycleDialog()}
        `;
    }

    private openCycleDialog(cycle: Cycle | null) {
        this.editingCycle = cycle;
        if(cycle) this.cycleDialogModifyOnly = true;
        this.cycleNameInput = cycle?.cycle_name || '';
        this.currentSteps = [...(cycle?.cycle_steps || [])];
        this.cycleDialogOpen = true;

        if (this.currentSteps.length === 0) this.addStep();
    }

    private closeCycleDialog() {
        this.cycleDialogOpen = false;
        this.cycleDialogModifyOnly = false;
        this.editingCycle = null;
        this.cycleNameInput = '';
        this.currentSteps = [];
    }

    private addStep() {
        if (this.availableZones.length === 0) return;
        const firstZoneId = this.availableZones[0].id;
        this.currentSteps.push({ zone_id: firstZoneId, zone_minutes: 5 });
        this.requestUpdate();
    }

    private removeStep(index: number) {
        if (this.availableZones.length <=1) return;
        this.currentSteps.splice(index, 1);
        this.requestUpdate();
    }

    private updateStepZone(index: number, zone_id: string) {
        this.currentSteps[index].zone_id = zone_id;
        this.requestUpdate();
    }

    private updateStepMinutes(index: number, time: number) {
        this.currentSteps[index].zone_minutes = time;
        this.requestUpdate();
    }

    private moveStep(index: number, direction: -1 | 1) {
        const newIndex = index + direction;
        if (newIndex < 0 || newIndex >= this.currentSteps.length) return;
        const steps = [...this.currentSteps];
        [steps[index], steps[newIndex]] = [steps[newIndex], steps[index]];
        this.currentSteps = steps;
        this.requestUpdate()
    }

    private saveCycle = () => {
        const name = this.cycleNameInput.trim();
        if (!name || this.currentSteps.length === 0) return;

        const newCycle: Cycle = {
            cycle_id: this.editingCycle?.cycle_id || crypto.randomUUID(),
            cycle_name: this.editingCycle?.cycle_name || name,
            cycle_steps: this.currentSteps,
        };
        if (this.cycleDialogModifyOnly && this.editingCycle) {
            // Call backend to modify cycle
            modifyCycle(this.hass, newCycle).then(()=>{console.log("Cycle API call sent!")});
        } else {
            // Call backend to create new cycle
            createCycle(this.hass, newCycle).then(()=>{console.log("Cycle API call sent!")});
        }

        this.closeCycleDialog();
    };

    private deleteCycle(id: string) {
        this.cycles = this.cycles.filter(c => c.cycle_id !== id);
        // Call backend to delete the cycle
        deleteCycle(this.hass, id).then(()=>{console.log("Cycle API call sent!")});
    }

    private renderCycleDialog() {
        if (!this.cycleDialogOpen) return null;
        return html`
            <ha-dialog open .heading="${this.editingCycle ? 'Modify Cycle' : 'Add Cycle'}" @closed=${this.closeCycleDialog}>
                <div>
                    <ha-textfield
                        label="Cycle Name"
                        .value=${this.cycleNameInput}
                        @input=${(e: Event) => this.cycleNameInput = (e.target as HTMLInputElement).value}
                        ?disabled=${this.cycleDialogModifyOnly}
                    ></ha-textfield>

                    <div class="draggable-list">
                        ${this.currentSteps.map((step, index) => html`
                            <div class="step-row">
                                <ha-icon-button
                                        title="Remove Step"
                                        @click=${() => this.removeStep(index)}
                                        .disabled=${this.currentSteps.length<=1}
                                ><ha-icon icon="mdi:close"></ha-icon></ha-icon-button>
                                <ha-select
                                    .value=${step.zone_id}
                                    @selected=${(e: Event) => 
                                            this.updateStepZone(index, (e.target as HTMLSelectElement).value)}
                                    @closed=${(e: CustomEvent) => e.stopPropagation()}>
                                    ${this.availableZones.map(z => html`
                                        <mwc-list-item .value=${z.id}>${z.name}</mwc-list-item>
                                    `)}
                                </ha-select>
                                <ha-textfield
                                    label="Minutes"
                                    type="number"
                                    min="1"
                                    .value=${step.zone_minutes.toString()}
                                    @input=${(e: Event) => this.updateStepMinutes(index, parseInt((e.target as HTMLInputElement).value))}
                                ></ha-textfield>
                                <div class="move-buttons">
                                    <ha-icon-button
                                        title="Move Up"    
                                        @click=${() => this.moveStep(index, -1)}
                                        .disabled=${index === 0}
                                    ><ha-icon icon="mdi:arrow-up"></ha-icon></ha-icon-button>
                                    <ha-icon-button
                                        title="Move Down"    
                                        @click=${() => this.moveStep(index, 1)}
                                        .disabled=${index === this.currentSteps.length - 1}
                                    ><ha-icon icon="mdi:arrow-down"></ha-icon></ha-icon-button>
                                </div>
                            </div>
                        `)}
                    </div>

                    <ha-button @click=${this.addStep}>Add Step</ha-button>
                </div>
                <ha-dialog-footer slot="footer">
                <ha-button slot="primaryAction" dialogAction="save"
                           @click=${this.saveCycle}
                           .disabled=${this.cycleNameInput == "" || this.currentSteps.length <= 0}>Save</ha-button>
                <ha-button slot="secondaryAction" dialogAction="cancel" @click=${this.closeCycleDialog}>Cancel</ha-button>
                </ha-dialog-footer>
            </ha-dialog>
        `;
    }
}
