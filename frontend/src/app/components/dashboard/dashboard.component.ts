import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { User, Test, Action, Agent } from '../../models';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  currentUser: User | null = null;
  tests: Test[] = [];
  actions: Action[] = [];
  agents: Agent[] = [];
  
  // Flow builder state
  selectedTest: Test | null = null;
  selectedActions: Action[] = [];
  flowSteps: any[] = [];
  showConditionField = false;
  conditionValue = '';
  
  // Progress tracking
  currentStep = 0;
  totalSteps = 4;

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.loadUserData();
    this.loadTests();
    this.loadActions();
    this.loadAgents();
  }

  loadUserData() {
    if (this.apiService.isAuthenticated()) {
      this.apiService.getCurrentUser().subscribe({
        next: (user) => {
          this.currentUser = user;
        },
        error: (error) => {
          console.error('Error loading user data:', error);
        }
      });
    }
  }

  loadTests() {
    this.apiService.getTests().subscribe({
      next: (tests) => {
        this.tests = tests;
      },
      error: (error) => {
        console.error('Error loading tests:', error);
      }
    });
  }

  loadActions() {
    this.apiService.getActions().subscribe({
      next: (actions) => {
        this.actions = actions;
      },
      error: (error) => {
        console.error('Error loading actions:', error);
      }
    });
  }

  loadAgents() {
    this.apiService.getAgents().subscribe({
      next: (agents) => {
        this.agents = agents;
      },
      error: (error) => {
        console.error('Error loading agents:', error);
      }
    });
  }

  // Flow builder methods
  selectTest(test: Test) {
    this.selectedTest = test;
    this.currentStep = 1;
    this.updateProgress();
  }

  addAction(action: Action) {
    if (!this.selectedActions.find(a => a.id === action.id)) {
      this.selectedActions.push(action);
      this.updateFlowSteps();
    }
  }

  removeAction(action: Action) {
    this.selectedActions = this.selectedActions.filter(a => a.id !== action.id);
    this.updateFlowSteps();
  }

  updateFlowSteps() {
    this.flowSteps = this.selectedActions.map((action, index) => ({
      id: index + 1,
      action: action,
      completed: false
    }));
    this.currentStep = 2;
    this.updateProgress();
  }

  toggleConditionField() {
    this.showConditionField = !this.showConditionField;
  }

  addCondition() {
    if (this.conditionValue.trim()) {
      this.flowSteps.push({
        id: this.flowSteps.length + 1,
        type: 'condition',
        value: this.conditionValue,
        completed: false
      });
      this.conditionValue = '';
      this.showConditionField = false;
    }
  }

  previewFlow() {
    this.currentStep = 3;
    this.updateProgress();
    
    // Simulate flow execution preview
    this.flowSteps.forEach((step, index) => {
      setTimeout(() => {
        step.completed = true;
      }, (index + 1) * 1000);
    });
  }

  executeFlow() {
    this.currentStep = 4;
    this.updateProgress();
    
    // Here you would implement the actual flow execution
    console.log('Executing flow with:', {
      test: this.selectedTest,
      actions: this.selectedActions,
      steps: this.flowSteps
    });
  }

  updateProgress() {
    const progressBar = document.querySelector('.progress-bar') as HTMLElement;
    if (progressBar) {
      const percentage = (this.currentStep / this.totalSteps) * 100;
      progressBar.style.width = `${percentage}%`;
    }
  }

  resetFlow() {
    this.selectedTest = null;
    this.selectedActions = [];
    this.flowSteps = [];
    this.currentStep = 0;
    this.showConditionField = false;
    this.conditionValue = '';
    this.updateProgress();
  }

  createNewTest() {
    // Navigate to test creation or open modal
    console.log('Create new test');
  }

  createNewActor() {
    // Navigate to actor creation or open modal
    console.log('Create new actor');
  }
}
