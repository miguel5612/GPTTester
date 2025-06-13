import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Actor, ActorCreate } from '../models';

@Injectable({ providedIn: 'root' })
export class ActorService {
  constructor(private api: ApiService) {}

  getActors(clientId?: number): Observable<Actor[]> {
    return this.api.getActors(clientId);
  }

  createActor(actor: ActorCreate): Observable<Actor> {
    return this.api.createActor(actor);
  }

  updateActor(id: number, actor: ActorCreate): Observable<Actor> {
    return this.api.updateActor(id, actor);
  }

  deleteActor(id: number): Observable<any> {
    return this.api.deleteActor(id);
  }
}
