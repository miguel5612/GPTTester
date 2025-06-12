import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Agent } from '../../models';
import { AgentService } from '../../services/agent.service';
import { AgentFormComponent } from './agent-form.component';

@Component({
  selector: 'app-agents',
  standalone: true,
  imports: [CommonModule, FormsModule, AgentFormComponent],
  template: `
    <div class="main-panel">
      <h1>Agentes de Ejecución</h1>
      <div class="d-flex flex-wrap gap-2 mb-3">
        <input class="form-control" [(ngModel)]="search" placeholder="Buscar" (ngModelChange)="load()">
        <select class="form-control" [(ngModel)]="os" (change)="load()">
          <option value="">Todos</option>
          <option value="Windows">Windows</option>
          <option value="Linux">Linux</option>
          <option value="Mac">Mac</option>
          <option value="Android">Android</option>
          <option value="iOS">iOS</option>
        </select>
        <button class="btn btn-primary" (click)="new()">Nuevo</button>
      </div>
      <table class="table table-bordered" *ngIf="agents.length > 0">
        <thead>
          <tr>
            <th>Alias</th>
            <th>Hostname</th>
            <th>OS</th>
            <th>Disponibilidad</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr *ngFor="let a of agents">
            <td>{{ a.alias }}</td>
            <td>{{ a.hostname }}</td>
            <td>{{ a.os }} <span *ngIf="a.categoria">({{ a.categoria }})</span></td>
            <td>{{ a.available ? 'Disponible' : 'Ocupado' }}</td>
            <td>
              <button class="btn btn-sm btn-secondary mr-2" (click)="edit(a)">Editar</button>
              <button class="btn btn-sm btn-danger" (click)="remove(a)">Eliminar</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div *ngIf="agents.length === 0">No hay agentes.</div>

      <app-agent-form *ngIf="showForm" [agent]="editing" (saved)="onSaved()" (cancel)="showForm=false"></app-agent-form>
    </div>
  `,
  styles: [`
    .gap-2 { gap: 0.5rem; }
    .mr-2 { margin-right: 0.25rem; }
  `]
})
export class AgentsComponent implements OnInit {
  agents: (Agent & { available?: boolean })[] = [];
  search = '';
  os = '';
  showForm = false;
  editing: Agent | null = null;

  constructor(private service: AgentService) {}

  ngOnInit() {
    this.load();
  }

  load() {
    this.service.getAgents().subscribe(list => {
      let filtered = list;
      if (this.search) {
        filtered = filtered.filter(a => a.alias.toLowerCase().includes(this.search.toLowerCase()) || a.hostname.toLowerCase().includes(this.search.toLowerCase()));
      }
      if (this.os) {
        filtered = filtered.filter(a => a.os === this.os);
      }
      this.agents = filtered.map(a => ({ ...a, available: true }));
    });
  }

  new() {
    this.editing = null;
    this.showForm = true;
  }

  edit(a: Agent) {
    this.editing = a;
    this.showForm = true;
  }

  remove(a: Agent) {
    if (confirm('¿Eliminar agente?')) {
      this.service.deleteAgent(a.id).subscribe(() => this.load());
    }
  }

  onSaved() {
    this.showForm = false;
    this.load();
  }
}
