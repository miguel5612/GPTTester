import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { Client, Project, User } from '../../models';

@Component({
  selector: 'app-client-admin',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="main-panel">
      <h1>Administración de Clientes</h1>
      <div *ngFor="let c of clients" class="mb-4">
        <h3>{{ c.name }}</h3>
        <ul class="list-group">
          <li class="list-group-item" *ngFor="let p of projectsByClient(c.id)">
            {{ p.name }} - Analistas:
            <span *ngFor="let a of p.analysts; let i = index">
              {{ a.username }}<span *ngIf="i < p.analysts.length - 1">, </span>
            </span>
          </li>
        </ul>
      </div>
    </div>
  `
})
export class ClientAdminComponent implements OnInit {
  clients: Client[] = [];
  projects: Project[] = [];
  users: User[] = [];

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.loadData();
  }

  loadData() {
    this.api.getClients().subscribe(cs => (this.clients = cs));
    this.api.getProjects().subscribe(ps => (this.projects = ps));
    this.api.getUsers().subscribe(us => (this.users = us));
  }

  projectsByClient(clientId: number): Project[] {
    return this.projects.filter(p => p.client_id === clientId);
  }
}
