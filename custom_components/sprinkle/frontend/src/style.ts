import {css} from 'lit'


export const commonStyle = css`

    ha-card {
        margin: 16px;
        padding: 16px;
    }

    ha-expansion-panel {
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

    .zone-entry, .cycle-entry {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        padding: 8px;
    }

    .zone-valves, .cycle-steps {
        display: flex;
        flex-direction: column;
    }

    .zone-valve-item, .cycle-step-item {
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .zone-actions, .cycle-actions {
        display: flex;
        flex-direction: row;
        gap: 8px;
        justify-content: flex-end;
    }

    ha-dialog::part(content) {
        width: 500px;
    }

    @media (max-width: 600px) {
        .zone-entry, .cycle-entry {
            flex-direction: column;
        }
    }

`;