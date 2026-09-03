import { api } from './api';
import type { User, Product, Report, Category, AnalyticsOverview } from '../types';

export const adminService = {
  async getUsers(params: { role?: string; status?: string; search?: string } = {}): Promise<{ users: User[]; count: number }> {
    const query = new URLSearchParams();
    if (params.role) query.append('role', params.role);
    if (params.status) query.append('status', params.status);
    if (params.search) query.append('search', params.search);
    const q = query.toString();
    return api.get<{ users: User[]; count: number }>(`/admin/users${q ? `?${q}` : ''}`);
  },

  async getUserDetail(id: string): Promise<User> {
    return api.get<User>(`/admin/users/${id}`);
  },

  async updateUserStatus(id: string, account_status: 'ACTIVE' | 'SUSPENDED'): Promise<{ message: string }> {
    return api.patch(`/admin/users/${id}/status`, { account_status });
  },

  async updateUserRole(id: string, role: 'student' | 'admin'): Promise<{ message: string }> {
    return api.patch(`/admin/users/${id}/role`, { role });
  },

  async getProducts(params: { status?: string; category?: string } = {}): Promise<{ products: Product[]; count: number }> {
    const query = new URLSearchParams();
    if (params.status) query.append('status', params.status);
    if (params.category) query.append('category', params.category);
    const q = query.toString();
    return api.get<{ products: Product[]; count: number }>(`/admin/products${q ? `?${q}` : ''}`);
  },

  async moderateProductStatus(id: string, status: 'ACTIVE' | 'RESERVED' | 'SOLD' | 'REMOVED'): Promise<{ message: string }> {
    return api.patch(`/admin/products/${id}/status`, { status });
  },

  async getReports(params: { status?: string; target_type?: string } = {}): Promise<{ reports: Report[]; count: number }> {
    const query = new URLSearchParams();
    if (params.status) query.append('status', params.status);
    if (params.target_type) query.append('target_type', params.target_type);
    const q = query.toString();
    return api.get<{ reports: Report[]; count: number }>(`/admin/reports${q ? `?${q}` : ''}`);
  },

  async updateReportStatus(id: string, status: 'OPEN' | 'REVIEWING' | 'RESOLVED' | 'DISMISSED'): Promise<{ message: string }> {
    return api.patch(`/admin/reports/${id}/status`, { status });
  },

  async getCategories(): Promise<{ categories: Category[] }> {
    return api.get<{ categories: Category[] }>('/admin/categories');
  },

  async createCategory(name: string, slug: string, description?: string): Promise<{ category: Category; message: string }> {
    return api.post('/admin/categories', { name, slug, description });
  },

  async updateCategory(slug: string, is_active: boolean): Promise<{ message: string }> {
    return api.patch(`/admin/categories/${slug}`, { is_active });
  },

  async getAnalyticsOverview(): Promise<AnalyticsOverview> {
    return api.get<AnalyticsOverview>('/admin/analytics/overview');
  },
};
