import { api } from './api';
import type { Category, CategoryDemandItem } from '../types';

export const categoryService = {
  async getCategories(): Promise<Category[]> {
    return api.get<Category[]>('/categories/');
  },

  async getPopularCategories(limit = 10): Promise<{ items: CategoryDemandItem[]; count: number }> {
    return api.get<{ items: CategoryDemandItem[]; count: number }>(`/categories/popular?limit=${limit}`);
  },
};
