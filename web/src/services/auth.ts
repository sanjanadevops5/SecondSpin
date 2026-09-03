import { api, setToken, removeToken } from './api';
import type { User } from '../types';

export interface AuthResponse {
  token: string;
  user: User;
  message?: string;
}

export const authService = {
  async register(name: string, email: string, password: string, department?: string): Promise<AuthResponse> {
    const data = await api.post<AuthResponse>('/auth/register', {
      name,
      email,
      password,
      department: department || undefined,
    });
    if (data.token) {
      setToken(data.token);
    }
    return data;
  },

  async login(email: string, password: string): Promise<AuthResponse> {
    const data = await api.post<AuthResponse>('/auth/login', {
      email,
      password,
    });
    if (data.token) {
      setToken(data.token);
    }
    return data;
  },

  async getMe(): Promise<{ user: User }> {
    return api.get<{ user: User }>('/users/me');
  },

  async updateMe(updates: Partial<User>): Promise<{ user: User; message: string }> {
    return api.put('/users/me', updates);
  },

  logout(): void {
    removeToken();
  },
};
