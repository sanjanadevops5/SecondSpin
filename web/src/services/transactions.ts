import { api } from './api';
import type { Transaction } from '../types';

export const transactionService = {
  async createTransaction(purchase_request_id: string): Promise<{ transaction_id: string; message: string }> {
    return api.post('/transactions/', { purchase_request_id });
  },

  async getMyTransactions(): Promise<{ transactions: Transaction[]; count: number }> {
    return api.get<{ transactions: Transaction[]; count: number }>('/transactions/mine');
  },

  async getReceivedTransactions(): Promise<{ transactions: Transaction[]; count: number }> {
    return api.get<{ transactions: Transaction[]; count: number }>('/transactions/received');
  },

  async getTransactionDetail(id: string): Promise<Transaction> {
    return api.get<Transaction>(`/transactions/${id}`);
  },

  async reserveTransaction(id: string): Promise<{ message: string }> {
    return api.post(`/transactions/${id}/reserve`);
  },

  async completeTransaction(id: string): Promise<{ message: string }> {
    return api.post(`/transactions/${id}/complete`);
  },

  async cancelTransaction(id: string): Promise<{ message: string }> {
    return api.post(`/transactions/${id}/cancel`);
  },
};
