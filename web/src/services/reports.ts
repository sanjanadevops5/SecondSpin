import { api } from './api';
import type { Report } from '../types';

export const reportService = {
  async submitReport(target_type: 'PRODUCT' | 'USER', target_id: string, reason: string, description?: string): Promise<{ report_id: string; message: string }> {
    return api.post('/reports/', { target_type, target_id, reason, description });
  },

  async getReportDetail(id: string): Promise<Report> {
    return api.get<Report>(`/reports/${id}`);
  },
};
