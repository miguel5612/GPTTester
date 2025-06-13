import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Client, ClientCreate } from '../models';

@Injectable({ providedIn: 'root' })
export class ClientService {
  constructor(private api: ApiService) {}

  getClients(): Observable<Client[]> {
    return this.api.getClients();
  }

  createClient(client: ClientCreate): Observable<Client> {
    return this.api.createClient(client);
  }

  updateClient(id: number, client: ClientCreate): Observable<Client> {
    return this.api.updateClient(id, client);
  }

  deleteClient(id: number): Observable<any> {
    return this.api.deleteClient(id);
  }

  assignAnalyst(clientId: number, userId: number, dedication?: number): Observable<Client> {
    return this.api.assignClientAnalyst(clientId, userId, dedication);
  }

  unassignAnalyst(clientId: number, userId: number): Observable<Client> {
    return this.api.unassignClientAnalyst(clientId, userId);
  }
}
