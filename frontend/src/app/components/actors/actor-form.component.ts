import { Component, EventEmitter, Input, Output, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Actor, ActorCreate, Client, User } from '../../models';
import { ActorService } from '../../services/actor.service';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-actor-form',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="card">
      <div class="card-body">
        <h3 class="card-title">{{ actor ? 'Editar Actor' : 'Nuevo Actor' }}</h3>
        <form (ngSubmit)="save()">
          <div class="mb-3">
            <label class="form-label">Nombre</label>
            <input class="form-control" [(ngModel)]="form.name" name="name" required>
          </div>
          <div class="mb-3">
            <label class="form-label">Cliente</label>
            <select class="form-control" [(ngModel)]="form.client_id" name="client_id" required>
              <option *ngFor="let c of clients" [ngValue]="c.id">{{ c.name }}</option>
            </select>
          </div>
          <button class="btn btn-primary" type="submit">Guardar</button>
          <button type="button" class="btn btn-secondary ms-2" (click)="cancel.emit()">Cancelar</button>
        </form>
      </div>
    </div>
  `
})
export class ActorFormComponent implements OnInit {
  @Input() actor: Actor | null = null;
  @Output() saved = new EventEmitter<void>();
  @Output() cancel = new EventEmitter<void>();

  form: ActorCreate = { name: '', client_id: 0 };
  clients: Client[] = [];
  currentUser: User | null = null;

  constructor(private service: ActorService, private api: ApiService) {}

  ngOnInit() {
    this.api.getCurrentUser().subscribe(user => {
      this.currentUser = user;
      this.loadClients();
      if (this.actor) {
        this.form = { name: this.actor.name, client_id: this.actor.client_id };
      }
    });
  }

  loadClients() {
    this.api.getClients().subscribe(c => {
      if (
        this.currentUser &&
        this.currentUser.role?.name !== 'Administrador' &&
        this.currentUser.role?.name !== 'Gerente de servicios'
      ) {
        this.clients = c.filter(cl =>
          cl.analysts.some(a => a.id === this.currentUser!.id)
        );
      } else {
        this.clients = c;
      }
    });
  }

  save() {
    const obs = this.actor ?
      this.service.updateActor(this.actor.id, this.form) :
      this.service.createActor(this.form);
    obs.subscribe(() => this.saved.emit());
  }
}
