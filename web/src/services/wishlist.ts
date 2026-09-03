import { api } from './api';
import type { WishlistItem } from '../types';

export const wishlistService = {
  async getWishlist(): Promise<{ wishlist: WishlistItem[]; count: number }> {
    return api.get<{ wishlist: WishlistItem[]; count: number }>('/wishlist/');
  },

  async addToWishlist(product_id: string): Promise<{ wishlist_id: string; message: string }> {
    return api.post('/wishlist/', { product_id });
  },

  async removeFromWishlist(product_id: string): Promise<{ message: string }> {
    return api.delete(`/wishlist/${product_id}`);
  },
};
