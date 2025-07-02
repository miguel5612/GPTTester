import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-scenarios',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="main-panel">
      <h1>Escenarios</h1>
      <p>Proyecto ID: {{ projectId }}</p>
    </div>
  `
})
export class ScenariosComponent implements OnInit {
  projectId!: number;

  constructor(private route: ActivatedRoute) {}

  ngOnInit() {
    this.projectId = Number(this.route.snapshot.paramMap.get('projectId'));
  }
}
