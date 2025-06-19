import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';

export interface FormField {
  label: string;
  name: string;
  type?: string;
  required?: boolean;
}

@Component({
  selector: 'app-responsive-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  template: `
    <form [formGroup]="form" (ngSubmit)="submit()" novalidate>
      <div class="form-field" *ngFor="let f of fields">
        <input [type]="f.type || 'text'" [formControlName]="f.name" [id]="f.name" placeholder=" " [required]="f.required">
        <label [for]="f.name">{{ f.label }}</label>
        <div class="error" *ngIf="form.get(f.name)?.invalid && form.get(f.name)?.touched">Campo requerido</div>
      </div>
      <ng-content></ng-content>
    </form>
  `,
  styles: [`
    :host { display:block; container-type:inline-size; }
    form { display:flex; flex-wrap:wrap; gap:var(--gap,1rem); }
    .form-field { position:relative; flex:1 1 100%; }
    .form-field input { width:100%; padding:0.75rem; border:1px solid var(--border-color); border-radius:4px; background:var(--input-bg); }
    .form-field label { position:absolute; left:0.75rem; top:0.75rem; color:var(--secondary-text); transition:0.2s; pointer-events:none; }
    .form-field input:focus + label,
    .form-field input:not(:placeholder-shown) + label { transform:translateY(-1.2rem) scale(0.85); background:var(--panel-bg); padding:0 0.25rem; }
    .error { color:#dc3545; font-size:0.8rem; margin-top:0.25rem; }
    @container (min-width:600px) { .form-field { flex:1 0 calc(50% - var(--gap,1rem)); } }
  `]
})
export class ResponsiveFormComponent {
  @Input() fields: FormField[] = [];
  @Output() submitted = new EventEmitter<any>();
  form: FormGroup;

  constructor(private fb: FormBuilder) {
    this.form = this.fb.group({});
  }

  ngOnChanges() {
    const group: any = {};
    for (const f of this.fields) {
      group[f.name] = f.required ? ['', Validators.required] : [''];
    }
    this.form = this.fb.group(group);
  }

  submit() {
    this.form.markAllAsTouched();
    if (this.form.valid) {
      this.submitted.emit(this.form.value);
    }
  }
}
