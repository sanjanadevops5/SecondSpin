import { api } from './api';
import type { PurchaseRequest } from '../types';

export const requestService = {
  async createRequest(product_id: string, message?: string): Promise<{ request_id: string; message: string }> {
    return api.post('/purchase-requests/', { product_id, message });
  },

  async getMyRequests(): Promise<{ requests: PurchaseRequest[]; count: number }> {
    return api.get<{ requests: PurchaseRequest[]; count: number }>('/purchase-requests/mine');
  },

  async getReceivedRequests(): Promise<{ requests: PurchaseRequest[]; count: number }> {
    return api.get<{ requests: PurchaseRequest[]; count: number }>('/purchase-requests/received');
  },

  async getRequestDetail(id: string): Promise<PurchaseRequest> {
    return api.get<PurchaseRequest>(`/purchase-requests/${id}`);
  },

  async acceptRequest(id: string): Promise<{ message: string }> {
    return api.post(`/purchase-requests/${id}/accept`);
  },

  async rejectRequest(id: string): Promise<{ message: string }> {
    return api.post(`/purchase-requests/${id}/reject`);
  },

  async cancelRequest(id: string): Promise<{ message: string }> {
    return api.post(`/purchase-requests/${id}/cancel`);
  },
};
