import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-tasks',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="main-panel">
      <h1>Tareas</h1>
      <p>Escenario ID: {{ scenarioId }}</p>
    </div>
  `
})
export class TasksComponent implements OnInit {
  scenarioId!: number;

  constructor(private route: ActivatedRoute) {}

  ngOnInit() {
    this.scenarioId = Number(this.route.snapshot.paramMap.get('scenarioId'));
  }
}
