import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-projects',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="main-panel">
      <h1>Proyectos</h1>
      <p *ngIf="clientId">Cliente ID: {{ clientId }}</p>
    </div>
  `
})
export class ProjectsComponent implements OnInit {
  clientId: number | null = null;

  constructor(private route: ActivatedRoute) {}

  ngOnInit() {
    const cid = this.route.snapshot.paramMap.get('clientId');
    this.clientId = cid ? Number(cid) : null;
  }
}
