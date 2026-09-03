import { api } from './api';
import type { Product, PaginatedResult } from '../types';

export interface GetProductsParams {
  page?: number;
  limit?: number;
  search?: string;
  category?: string;
  condition?: string;
  min_price?: number;
  max_price?: number;
  status?: string;
  sort?: 'newest' | 'oldest' | 'price_low_to_high' | 'price_high_to_low';
}

export const productService = {
  async getProducts(params: GetProductsParams = {}): Promise<PaginatedResult<Product>> {
    const query = new URLSearchParams();
    if (params.page) query.append('page', params.page.toString());
    if (params.limit) query.append('limit', params.limit.toString());
    if (params.search) query.append('search', params.search);
    if (params.category) query.append('category', params.category);
    if (params.condition) query.append('condition', params.condition);
    if (params.min_price !== undefined) query.append('min_price', params.min_price.toString());
    if (params.max_price !== undefined) query.append('max_price', params.max_price.toString());
    if (params.status) query.append('status', params.status);
    if (params.sort) query.append('sort', params.sort);

    const queryString = query.toString();
    const endpoint = `/products${queryString ? `?${queryString}` : ''}`;
    return api.get<PaginatedResult<Product>>(endpoint);
  },

  async getProduct(id: string): Promise<Product> {
    return api.get<Product>(`/products/${id}`);
  },

  async getMyProducts(): Promise<{ items: Product[] }> {
    return api.get<{ items: Product[] }>('/products/me');
  },

  async createProduct(data: {
    title: string;
    description: string;
    price: number;
    category_id: string;
    condition: string;
    images?: string[];
    attributes?: Record<string, any>;
  }): Promise<{ product_id: string; message: string }> {
    return api.post('/products/', data);
  },

  async updateProduct(id: string, updates: Partial<Product>): Promise<{ message: string }> {
    return api.put(`/products/${id}`, updates);
  },

  async deleteProduct(id: string): Promise<{ message: string }> {
    return api.delete(`/products/${id}`);
  },
};
