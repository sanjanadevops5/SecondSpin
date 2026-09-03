import { api } from './api';
import type { Review } from '../types';

export const reviewService = {
  async submitReview(transaction_id: string, rating: number, comment?: string): Promise<{ review_id: string; message: string }> {
    return api.post('/reviews/', { transaction_id, rating, comment });
  },

  async getProductReviews(product_id: string): Promise<{ reviews: Review[]; count: number; average_rating: number }> {
    return api.get<{ reviews: Review[]; count: number; average_rating: number }>(`/reviews/product/${product_id}`);
  },

  async getUserReviews(user_id: string): Promise<{ reviews: Review[]; count: number; average_rating: number }> {
    return api.get<{ reviews: Review[]; count: number; average_rating: number }>(`/reviews/user/${user_id}`);
  },

  async getReviewDetail(id: string): Promise<Review> {
    return api.get<Review>(`/reviews/${id}`);
  },
};
