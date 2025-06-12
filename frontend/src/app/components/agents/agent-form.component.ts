import { Component, EventEmitter, Input, Output, OnInit, OnChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Agent, AgentCreate, Project } from '../../models';
import { AgentService } from '../../services/agent.service';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-agent-form',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="agent-form">
      <h2>{{ agent ? 'Editar' : 'Crear' }} Agente</h2>
      <form (ngSubmit)="submit()">
        <div class="form-group">
          <label>Alias</label>
          <input class="form-control" [(ngModel)]="form.alias" name="alias" required>
        </div>
        <div class="form-group">
          <label>Hostname</label>
          <input class="form-control" [(ngModel)]="form.hostname" name="hostname" required (blur)="validateHostname()" [class.is-invalid]="hostTaken">
          <div class="invalid-feedback" *ngIf="hostTaken">Hostname ya registrado</div>
        </div>
        <div class="form-group">
          <label>Sistema Operativo</label>
          <select class="form-control" [(ngModel)]="form.os" name="os" required (change)="onOsChange()">
            <option value="Windows">Windows</option>
            <option value="Linux">Linux</option>
            <option value="Mac">Mac</option>
            <option value="Android">Android</option>
            <option value="iOS">iOS</option>
          </select>
        </div>
        <div class="form-group" *ngIf="form.os === 'Android' || form.os === 'iOS'">
          <label>Categoría</label>
          <select class="form-control" [(ngModel)]="form.categoria" name="categoria">
            <option value="">--</option>
            <option value="granja móvil">Granja Móvil</option>
          </select>
        </div>
        <div class="form-group">
          <label>Proyecto</label>
          <select class="form-control" [(ngModel)]="projectId" name="project">
            <option [ngValue]="null">--</option>
            <option *ngFor="let p of projects" [ngValue]="p.id">{{ p.name }}</option>
          </select>
        </div>
        <div class="mt-3">
          <button type="submit" class="btn btn-primary mr-2" [disabled]="hostTaken">Guardar</button>
          <button type="button" class="btn btn-secondary" (click)="cancel.emit()">Cancelar</button>
        </div>
      </form>
    </div>
  `,
  styles: [`
    .agent-form { padding: 1rem; }
    .form-group { margin-bottom: 1rem; }
    .mr-2 { margin-right: 0.5rem; }
  `]
})
export class AgentFormComponent implements OnInit, OnChanges {
  @Input() agent: Agent | null = null;
  @Output() saved = new EventEmitter<void>();
  @Output() cancel = new EventEmitter<void>();

  form: AgentCreate = { alias: '', hostname: '', os: 'Windows', categoria: '' };
  projects: Project[] = [];
  projectId: number | null = null;
  hostTaken = false;

  constructor(private service: AgentService, private api: ApiService) {}

  ngOnInit() {
    this.api.getProjects().subscribe(p => this.projects = p);
  }

  ngOnChanges() {
    if (this.agent) {
      this.form = { alias: this.agent.alias, hostname: this.agent.hostname, os: this.agent.os, categoria: this.agent.categoria };
    } else {
      this.form = { alias: '', hostname: '', os: 'Windows', categoria: '' };
    }
  }

  validateHostname() {
    this.service.checkHostname(this.form.hostname, this.agent?.id).subscribe(t => this.hostTaken = t);
  }

  onOsChange() {
    if (this.form.os !== 'Android' && this.form.os !== 'iOS') {
      this.form.categoria = '';
    }
  }

  submit() {
    if (this.hostTaken) return;
    const obs = this.agent ?
      this.service.updateAgent(this.agent.id, this.form) :
      this.service.createAgent(this.form);
    obs.subscribe(agent => {
      if (this.projectId) {
        this.service.assignToProject(agent.id, this.projectId!).subscribe(() => this.saved.emit());
      } else {
        this.saved.emit();
      }
    });
  }
}
