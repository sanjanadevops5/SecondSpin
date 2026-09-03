import { api } from './api';
import type { PurchaseRequest } from '../types';

export const requestService = {
  async createRequest(product_id: string, message?: string): Promise<{ request_id: string; message: string }> {
    return api.post('/purchase-requests/', { product_id, message });
  },

  async getMyRequests(): Promise<{ items: PurchaseRequest[]; requests?: PurchaseRequest[]; count?: number }> {
    return api.get<{ items: PurchaseRequest[]; requests?: PurchaseRequest[]; count?: number }>('/purchase-requests/mine');
  },

  async getReceivedRequests(): Promise<{ items: PurchaseRequest[]; requests?: PurchaseRequest[]; count?: number }> {
    return api.get<{ items: PurchaseRequest[]; requests?: PurchaseRequest[]; count?: number }>('/purchase-requests/received');
  },

  async getRequestDetail(id: string): Promise<PurchaseRequest> {
    return api.get<PurchaseRequest>(`/purchase-requests/${id}`);
  },

  async acceptRequest(id: string): Promise<{ message: string }> {
    return api.patch(`/purchase-requests/${id}/accept`);
  },

  async rejectRequest(id: string): Promise<{ message: string }> {
    return api.patch(`/purchase-requests/${id}/reject`);
  },

  async cancelRequest(id: string): Promise<{ message: string }> {
    return api.patch(`/purchase-requests/${id}/cancel`);
  },
};
