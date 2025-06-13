import { Component, Input, Output, EventEmitter, OnChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { User, Client } from '../../models';
import { ClientService } from '../../services/client.service';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-client-analysts',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="card" *ngIf="client">
      <div class="card-body">
        <h3 class="card-title">Analistas de {{ client.name }}</h3>
        <div *ngFor="let u of analysts" class="form-check">
          <input class="form-check-input" type="checkbox" [id]="'ca-'+u.id"
            [checked]="isAssigned(u)"
            (change)="toggle(u, ($event.target as HTMLInputElement).checked)">
          <label class="form-check-label" [for]="'ca-'+u.id">
            {{ u.username }} ({{ u.role.name }})
          </label>
        </div>
        <button class="btn btn-secondary mt-3" (click)="close.emit()">Cerrar</button>
      </div>
    </div>
  `,
  styles: [`
    .form-check { margin-bottom: 0.5rem; }
  `]
})
export class ClientAnalystsComponent implements OnChanges {
  @Input() clientId!: number;
  @Output() updated = new EventEmitter<void>();
  @Output() close = new EventEmitter<void>();

  client: Client | null = null;
  analysts: User[] = [];

  constructor(private clientService: ClientService, private api: ApiService) {}

  ngOnChanges() {
    if (this.clientId) {
      this.load();
    }
  }

  load() {
    this.clientService.getClients().subscribe(cs => {
      this.client = cs.find(c => c.id === this.clientId) || null;
    });
    this.api.getUsers().subscribe(users => {
      this.analysts = users.filter(u =>
        u.role.name === 'Analista de Pruebas con skill de automatización' ||
        u.role.name === 'Automatizador de Pruebas'
      );
    });
  }

  isAssigned(u: User): boolean {
    return this.client?.analysts.some(a => a.id === u.id) ?? false;
  }

  toggle(user: User, checked: boolean) {
    if (!this.client) return;
    const obs = checked
      ? this.clientService.assignAnalyst(this.client.id, user.id)
      : this.clientService.unassignAnalyst(this.client.id, user.id);
    obs.subscribe(c => {
      this.client = c;
      this.updated.emit();
    });
  }
}
