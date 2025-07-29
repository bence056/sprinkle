import {css} from 'lit'

export const commonStyle = css`
    
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