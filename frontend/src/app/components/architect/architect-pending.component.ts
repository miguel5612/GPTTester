import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-architect-pending',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="main-panel">
      <h1>Revisiones Pendientes</h1>

      <h3>Interacciones</h3>
      <table class="table" *ngIf="pendingInteractions.length">
        <thead><tr><th>Nombre</th><th>Acciones</th></tr></thead>
        <tbody>
          <tr *ngFor="let item of pendingInteractions">
            <td>{{ item.interaction.name }}</td>
            <td>
              <button class="btn btn-sm btn-success" (click)="approveInteraction(item.approval.id)">Aprobar</button>
              <button class="btn btn-sm btn-danger" (click)="rejectInteraction(item.approval.id)">Rechazar</button>
            </td>
          </tr>
        </tbody>
      </table>
      <p *ngIf="!pendingInteractions.length">Sin interacciones pendientes</p>

      <h3>Validaciones</h3>
      <table class="table" *ngIf="pendingValidations.length">
        <thead><tr><th>Nombre</th><th>Acciones</th></tr></thead>
        <tbody>
          <tr *ngFor="let item of pendingValidations">
            <td>{{ item.validation.name }}</td>
            <td>
              <button class="btn btn-sm btn-success" (click)="approveValidation(item.approval.id)">Aprobar</button>
              <button class="btn btn-sm btn-danger" (click)="rejectValidation(item.approval.id)">Rechazar</button>
            </td>
          </tr>
        </tbody>
      </table>
      <p *ngIf="!pendingValidations.length">Sin validaciones pendientes</p>
    </div>
  `
})
export class ArchitectPendingComponent implements OnInit {
  pendingInteractions: any[] = [];
  pendingValidations: any[] = [];

  constructor(private api: ApiService) {}

  ngOnInit() { this.load(); }

  load() {
    this.api.getPendingInteractions().subscribe(data => this.pendingInteractions = data);
    this.api.getPendingValidations().subscribe(data => this.pendingValidations = data);
  }

  approveInteraction(id: number) {
    this.api.approveInteraction(id).subscribe(() => this.load());
  }

  rejectInteraction(id: number) {
    this.api.rejectInteraction(id).subscribe(() => this.load());
  }

  approveValidation(id: number) {
    this.api.approveValidation(id).subscribe(() => this.load());
  }

  rejectValidation(id: number) {
    this.api.rejectValidation(id).subscribe(() => this.load());
  }
}
