import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Page, PageCreate } from '../models';

@Injectable({ providedIn: 'root' })
export class PageService {
  constructor(private api: ApiService) {}

  getPages(): Observable<Page[]> {
    return this.api.getPages();
  }

  getPage(id: number): Observable<Page> {
    return this.api.getPage(id);
  }

  createPage(page: PageCreate): Observable<Page> {
    return this.api.createPage(page);
  }

  updatePage(id: number, page: PageCreate): Observable<Page> {
    return this.api.updatePage(id, page);
  }

  deletePage(id: number): Observable<any> {
    return this.api.deletePage(id);
  }
}
