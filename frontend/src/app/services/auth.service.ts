import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, BehaviorSubject, throwError } from 'rxjs';
import { map, catchError, tap } from 'rxjs/operators';

export interface UserRegisterData {
  username: string;
  password: string;
  user_type: 'analyst' | 'service_manager' | 'architect';
}

export interface LoginData {
  username: string;
  password: string;
}

export interface UserInfo {
  id: number;
  username: string;
  role: {
    id: number;
    name: string;
  };
  is_active: boolean;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: UserInfo;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private baseUrl = 'http://localhost:8000/api/auth';
  private currentUserSubject = new BehaviorSubject<UserInfo | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();
  
  private tokenKey = 'access_token';
  private userKey = 'current_user';

  constructor(
    private http: HttpClient,
    private router: Router
  ) {
    // Cargar usuario de localStorage si existe
    const savedUser = localStorage.getItem(this.userKey);
    if (savedUser) {
      try {
        this.currentUserSubject.next(JSON.parse(savedUser));
      } catch (e) {
        this.logout();
      }
    }
  }

  private getHeaders(): HttpHeaders {
    const token = this.getToken();
    return new HttpHeaders({
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    });
  }

  register(data: UserRegisterData): Observable<UserInfo> {
    return this.http.post<UserInfo>(`${this.baseUrl}/register`, data)
      .pipe(
        catchError(error => {
          let message = 'Error al registrar usuario';
          if (error.error?.detail) {
            message = error.error.detail;
          }
          return throwError(() => new Error(message));
        })
      );
  }

  login(credentials: LoginData): Observable<AuthResponse> {
    // Usar FormData para OAuth2
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    return this.http.post<AuthResponse>(`${this.baseUrl}/login`, formData)
      .pipe(
        tap(response => {
          // Guardar token y usuario
          localStorage.setItem(this.tokenKey, response.access_token);
          localStorage.setItem(this.userKey, JSON.stringify(response.user));
          this.currentUserSubject.next(response.user);
        }),
        catchError(error => {
          let message = 'Error al iniciar sesión';
          if (error.error?.detail) {
            message = error.error.detail;
          }
          return throwError(() => new Error(message));
        })
      );
  }

  logout(): void {
    // Llamar al endpoint de logout (opcional)
    this.http.post(`${this.baseUrl}/logout`, {}, { headers: this.getHeaders() })
      .subscribe({
        complete: () => {
          this.clearSession();
        },
        error: () => {
          // Limpiar sesión incluso si falla la petición
          this.clearSession();
        }
      });
  }

  private clearSession(): void {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.userKey);
    localStorage.removeItem('workspace'); // Limpiar workspace también
    this.currentUserSubject.next(null);
    this.router.navigate(['/login']);
  }

  getCurrentUser(): Observable<UserInfo> {
    return this.http.get<UserInfo>(`${this.baseUrl}/me`, { headers: this.getHeaders() })
      .pipe(
        tap(user => {
          localStorage.setItem(this.userKey, JSON.stringify(user));
          this.currentUserSubject.next(user);
        }),
        catchError(error => {
          if (error.status === 401) {
            this.clearSession();
          }
          return throwError(() => error);
        })
      );
  }

  getPermissions(): Observable<{ permissions: string[], role: string }> {
    return this.http.get<{ permissions: string[], role: string }>(
      `${this.baseUrl}/permissions`, 
      { headers: this.getHeaders() }
    );
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  getUserRole(): string | null {
    const user = this.currentUserSubject.value;
    return user?.role?.name || null;
  }

  isAdmin(): boolean {
    return this.getUserRole() === 'Administrador';
  }

  isServiceManager(): boolean {
    return this.getUserRole() === 'Gerente de servicios';
  }

  isArchitect(): boolean {
    return this.getUserRole() === 'Arquitecto de Automatización';
  }

  isAnalyst(): boolean {
    const role = this.getUserRole();
    return role?.includes('Analista') || role === 'Automatizador de Pruebas';
  }

  hasRole(roles: string[]): boolean {
    const userRole = this.getUserRole();
    return userRole ? roles.includes(userRole) : false;
  }

  // Método para refrescar el token si es necesario
  refreshUserInfo(): void {
    if (this.isAuthenticated()) {
      this.getCurrentUser().subscribe({
        error: () => {
          this.clearSession();
        }
      });
    }
  }
}
