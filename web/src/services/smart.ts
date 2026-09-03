import { api } from './api';
import type { RecommendedItem, PriceInsights } from '../types';

export const smartService = {
  async getRelatedProducts(product_id: string, limit = 10): Promise<{ items: RecommendedItem[]; count: number }> {
    return api.get<{ items: RecommendedItem[]; count: number }>(`/products/${product_id}/related?limit=${limit}`);
  },

  async getPopularProducts(limit = 10): Promise<{ items: RecommendedItem[]; count: number }> {
    return api.get<{ items: RecommendedItem[]; count: number }>(`/products/popular?limit=${limit}`);
  },

  async getPriceInsights(product_id: string): Promise<PriceInsights> {
    return api.get<PriceInsights>(`/products/${product_id}/price-insights`);
  },

  async getPersonalizedRecommendations(limit = 10): Promise<{ items: RecommendedItem[]; count: number }> {
    return api.get<{ items: RecommendedItem[]; count: number }>(`/recommendations?limit=${limit}`);
  },
};
