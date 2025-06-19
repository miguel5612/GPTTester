import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

export interface TableColumn {
  label: string;
  key: string;
}

@Component({
  selector: 'app-responsive-table',
  standalone: true,
  imports: [CommonModule],
  template: `
    <ng-container *ngIf="data?.length; else empty">
      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th *ngFor="let c of columns">{{ c.label }}</th>
            </tr>
          </thead>
          <tbody>
            <tr *ngFor="let row of data">
              <td *ngFor="let c of columns">{{ row[c.key] }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="card-list">
        <div class="card" *ngFor="let row of data">
          <div class="card-item" *ngFor="let c of columns">
            <strong>{{ c.label }}:</strong> {{ row[c.key] }}
          </div>
        </div>
      </div>
    </ng-container>
    <ng-template #empty>
      <p>No data</p>
    </ng-template>
  `,
  styles: [`
    :host { display:block; container-type:inline-size; width:100%; }
    .table-wrapper { display:none; }
    .card { border:1px solid var(--border-color); padding:1rem; margin-bottom:1rem; border-radius:8px; background:var(--panel-bg); }
    .card-item { margin:0.25rem 0; }
    @container (min-width:600px) {
      .table-wrapper { display:block; overflow-x:auto; }
      table { width:100%; border-collapse:collapse; }
      th, td { padding:0.5rem; border-bottom:1px solid var(--border-color); }
      .card-list { display:none; }
    }
    @container (min-width:900px) {
      .table-wrapper { overflow:visible; }
    }
  `]
})
export class ResponsiveTableComponent {
  @Input() columns: TableColumn[] = [];
  @Input() data: any[] = [];
}
