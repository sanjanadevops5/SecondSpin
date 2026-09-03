import React, { useEffect, useState } from 'react';
import {
  Users,
  Package,
  Repeat,
  ShieldAlert,
  Star,
  RefreshCw,
  TrendingUp,
} from 'lucide-react';
import { adminService } from '../../services/admin';
import type { User, Product, Report, Category, AnalyticsOverview } from '../../types';
import { Badge } from '../../components/common/Badge';

export const AdminDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'users' | 'products' | 'reports' | 'categories'>('users');
  const [analytics, setAnalytics] = useState<AnalyticsOverview | null>(null);

  // Tab Data States
  const [users, setUsers] = useState<User[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [reports, setReports] = useState<Report[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);

  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  // New Category Form Modal
  const [newCatName, setNewCatName] = useState('');
  const [newCatSlug, setNewCatSlug] = useState('');
  const [newCatDesc, setNewCatDesc] = useState('');

  const loadData = async () => {
    try {
      setLoading(true);
      const overview = await adminService.getAnalyticsOverview();
      setAnalytics(overview);

      const [usersRes, prodsRes, reportsRes, catsRes] = await Promise.all([
        adminService.getUsers(),
        adminService.getProducts(),
        adminService.getReports(),
        adminService.getCategories(),
      ]);

      setUsers(usersRes.users || []);
      setProducts(prodsRes.products || []);
      setReports(reportsRes.reports || []);
      setCategories(catsRes.categories || []);
    } catch (err) {
      console.error('Failed to load admin dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleToggleUserStatus = async (userItem: User) => {
    const newStatus = userItem.account_status === 'ACTIVE' ? 'SUSPENDED' : 'ACTIVE';
    if (!window.confirm(`Are you sure you want to change ${userItem.name}'s status to ${newStatus}?`)) return;

    try {
      setActionLoading(userItem._id);
      await adminService.updateUserStatus(userItem._id, newStatus);
      loadData();
    } catch (err: any) {
      alert(err.message || 'Failed to update user status.');
    } fontally: {
      setActionLoading(null);
    }
  };

  const handleToggleUserRole = async (userItem: User) => {
    const newRole = userItem.role === 'admin' ? 'student' : 'admin';
    if (!window.confirm(`Are you sure you want to change ${userItem.name}'s role to ${newRole}?`)) return;

    try {
      setActionLoading(userItem._id);
      await adminService.updateUserRole(userItem._id, newRole);
      loadData();
    } catch (err: any) {
      alert(err.message || 'Failed to update user role.');
    } finally {
      setActionLoading(null);
    }
  };

  const handleModerateProduct = async (product: Product, newStatus: 'ACTIVE' | 'REMOVED') => {
    if (!window.confirm(`Are you sure you want to set product status to ${newStatus}?`)) return;

    try {
      setActionLoading(product._id);
      await adminService.moderateProductStatus(product._id, newStatus);
      loadData();
    } catch (err: any) {
      alert(err.message || 'Failed to moderate product.');
    } finally {
      setActionLoading(null);
    }
  };

  const handleUpdateReportStatus = async (reportId: string, status: 'RESOLVED' | 'DISMISSED') => {
    try {
      setActionLoading(reportId);
      await adminService.updateReportStatus(reportId, status);
      loadData();
    } catch (err: any) {
      alert(err.message || 'Failed to update report status.');
    } finally {
      setActionLoading(null);
    }
  };

  const handleCreateCategory = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCatName || !newCatSlug) return;

    try {
      setActionLoading('new-cat');
      await adminService.createCategory(newCatName.trim(), newCatSlug.trim(), newCatDesc.trim());
      setNewCatName('');
      setNewCatSlug('');
      setNewCatDesc('');
      loadData();
    } catch (err: any) {
      alert(err.message || 'Failed to create category.');
    } finally {
      setActionLoading(null);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Admin Title */}
      <div className="flex items-center justify-between border-b border-slate-200 pb-6">
        <div>
          <h1 className="text-3xl font-black text-slate-900">Admin Control Center</h1>
          <p className="text-sm text-slate-500">Platform moderation, user management, and marketplace analytics</p>
        </div>
        <button
          onClick={loadData}
          className="px-4 py-2 bg-slate-100 text-slate-700 font-bold text-xs rounded-xl hover:bg-slate-200 transition-colors flex items-center gap-1.5"
        >
          <RefreshCw size={14} /> Refresh Data
        </button>
      </div>

      {/* Analytics Metric Cards */}
      {analytics && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-xs space-y-1">
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-xs font-bold uppercase">Users</span>
              <Users size={16} className="text-blue-500" />
            </div>
            <span className="text-2xl font-black text-slate-900">{analytics.users.total}</span>
            <span className="text-[10px] font-semibold text-emerald-600 block">{analytics.users.active} Active</span>
          </div>

          <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-xs space-y-1">
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-xs font-bold uppercase">Listings</span>
              <Package size={16} className="text-emerald-500" />
            </div>
            <span className="text-2xl font-black text-slate-900">{analytics.products.total}</span>
            <span className="text-[10px] font-semibold text-emerald-600 block">{analytics.products.active} Active</span>
          </div>

          <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-xs space-y-1">
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-xs font-bold uppercase">Transactions</span>
              <Repeat size={16} className="text-indigo-500" />
            </div>
            <span className="text-2xl font-black text-slate-900">{analytics.transactions.total}</span>
            <span className="text-[10px] font-semibold text-emerald-600 block">{analytics.transactions.completed} Completed</span>
          </div>

          <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-xs space-y-1">
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-xs font-bold uppercase">Requests</span>
              <TrendingUp size={16} className="text-amber-500" />
            </div>
            <span className="text-2xl font-black text-slate-900">{analytics.purchase_requests.total}</span>
            <span className="text-[10px] font-semibold text-indigo-600 block">{analytics.purchase_requests.accepted} Accepted</span>
          </div>

          <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-xs space-y-1">
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-xs font-bold uppercase">Avg Rating</span>
              <Star size={16} className="text-amber-400 fill-amber-400" />
            </div>
            <span className="text-2xl font-black text-slate-900">
              {analytics.reviews.average_rating.toFixed(1)}
            </span>
            <span className="text-[10px] font-semibold text-slate-400 block">{analytics.reviews.total} Reviews</span>
          </div>

          <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-xs space-y-1">
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-xs font-bold uppercase">Reports</span>
              <ShieldAlert size={16} className="text-rose-500" />
            </div>
            <span className="text-2xl font-black text-slate-900">{analytics.reports.total}</span>
            <span className="text-[10px] font-semibold text-rose-600 block">{analytics.reports.open} Open</span>
          </div>
        </div>
      )}

      {/* Navigation Sub-Tabs */}
      <div className="border-b border-slate-200 pb-4 flex items-center gap-4">
        <button
          onClick={() => setActiveTab('users')}
          className={`pb-2 text-sm font-bold border-b-2 transition-all ${
            activeTab === 'users' ? 'border-emerald-600 text-emerald-600' : 'border-transparent text-slate-500'
          }`}
        >
          Users ({users.length})
        </button>
        <button
          onClick={() => setActiveTab('products')}
          className={`pb-2 text-sm font-bold border-b-2 transition-all ${
            activeTab === 'products' ? 'border-emerald-600 text-emerald-600' : 'border-transparent text-slate-500'
          }`}
        >
          Listings ({products.length})
        </button>
        <button
          onClick={() => setActiveTab('reports')}
          className={`pb-2 text-sm font-bold border-b-2 transition-all ${
            activeTab === 'reports' ? 'border-emerald-600 text-emerald-600' : 'border-transparent text-slate-500'
          }`}
        >
          Moderation Reports ({reports.length})
        </button>
        <button
          onClick={() => setActiveTab('categories')}
          className={`pb-2 text-sm font-bold border-b-2 transition-all ${
            activeTab === 'categories' ? 'border-emerald-600 text-emerald-600' : 'border-transparent text-slate-500'
          }`}
        >
          Categories ({categories.length})
        </button>
      </div>

      {/* Tab Content */}
      {loading ? (
        <div className="h-64 bg-slate-100 animate-pulse rounded-2xl" />
      ) : activeTab === 'users' ? (
        /* Users Table */
        <div className="bg-white rounded-2xl border border-slate-200 overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-bold uppercase">
              <tr>
                <th className="px-6 py-3">User</th>
                <th className="px-6 py-3">Role</th>
                <th className="px-6 py-3">Status</th>
                <th className="px-6 py-3">Department</th>
                <th className="px-6 py-3">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-800">
              {users.map((u) => (
                <tr key={u._id} className="hover:bg-slate-50">
                  <td className="px-6 py-4 font-bold">{u.name} <span className="text-slate-400 block font-normal">{u.email}</span></td>
                  <td className="px-6 py-4"><Badge status={u.role} size="sm" /></td>
                  <td className="px-6 py-4"><Badge status={u.account_status} size="sm" /></td>
                  <td className="px-6 py-4">{u.department || '—'}</td>
                  <td className="px-6 py-4 flex gap-2">
                    <button
                      disabled={actionLoading === u._id}
                      onClick={() => handleToggleUserStatus(u)}
                      className={`px-3 py-1 rounded-lg font-bold text-[10px] ${
                        u.account_status === 'ACTIVE' ? 'bg-rose-50 text-rose-700' : 'bg-emerald-50 text-emerald-700'
                      }`}
                    >
                      {u.account_status === 'ACTIVE' ? 'Suspend' : 'Activate'}
                    </button>
                    <button
                      disabled={actionLoading === u._id}
                      onClick={() => handleToggleUserRole(u)}
                      className="px-3 py-1 rounded-lg font-bold text-[10px] bg-slate-100 text-slate-700"
                    >
                      Make {u.role === 'admin' ? 'Student' : 'Admin'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : activeTab === 'products' ? (
        /* Products Moderation Table */
        <div className="bg-white rounded-2xl border border-slate-200 overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-bold uppercase">
              <tr>
                <th className="px-6 py-3">Product</th>
                <th className="px-6 py-3">Price</th>
                <th className="px-6 py-3">Category</th>
                <th className="px-6 py-3">Status</th>
                <th className="px-6 py-3">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-800">
              {products.map((p) => (
                <tr key={p._id} className="hover:bg-slate-50">
                  <td className="px-6 py-4 font-bold">{p.title}</td>
                  <td className="px-6 py-4 font-extrabold text-emerald-700">${p.price.toFixed(2)}</td>
                  <td className="px-6 py-4">{p.category_id}</td>
                  <td className="px-6 py-4"><Badge status={p.status} size="sm" /></td>
                  <td className="px-6 py-4">
                    {p.status !== 'REMOVED' ? (
                      <button
                        onClick={() => handleModerateProduct(p, 'REMOVED')}
                        className="px-3 py-1 bg-rose-50 text-rose-700 font-bold rounded-lg text-[10px]"
                      >
                        Remove Listing
                      </button>
                    ) : (
                      <span className="text-slate-400">Removed</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : activeTab === 'reports' ? (
        /* Reports Table */
        <div className="bg-white rounded-2xl border border-slate-200 overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-bold uppercase">
              <tr>
                <th className="px-6 py-3">Target Type</th>
                <th className="px-6 py-3">Reason</th>
                <th className="px-6 py-3">Status</th>
                <th className="px-6 py-3">Description</th>
                <th className="px-6 py-3">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-800">
              {reports.map((r) => (
                <tr key={r._id} className="hover:bg-slate-50">
                  <td className="px-6 py-4 font-bold">{r.target_type}</td>
                  <td className="px-6 py-4">{r.reason}</td>
                  <td className="px-6 py-4"><Badge status={r.status} size="sm" /></td>
                  <td className="px-6 py-4 text-slate-500">{r.description || '—'}</td>
                  <td className="px-6 py-4 flex gap-2">
                    {r.status === 'OPEN' && (
                      <>
                        <button
                          onClick={() => handleUpdateReportStatus(r._id, 'RESOLVED')}
                          className="px-3 py-1 bg-emerald-50 text-emerald-700 font-bold rounded-lg text-[10px]"
                        >
                          Resolve
                        </button>
                        <button
                          onClick={() => handleUpdateReportStatus(r._id, 'DISMISSED')}
                          className="px-3 py-1 bg-slate-100 text-slate-600 font-bold rounded-lg text-[10px]"
                        >
                          Dismiss
                        </button>
                      </>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        /* Category Management */
        <div className="space-y-6">
          <form onSubmit={handleCreateCategory} className="p-6 bg-white rounded-2xl border border-slate-200 space-y-4">
            <h3 className="text-sm font-bold text-slate-900">Create New Category</h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <input
                type="text"
                placeholder="Category Name (e.g. Lab Equipment)"
                value={newCatName}
                onChange={(e) => {
                  setNewCatName(e.target.value);
                  setNewCatSlug(e.target.value.toLowerCase().replace(/\s+/g, '-'));
                }}
                required
                className="px-3 py-2 border border-slate-200 rounded-xl text-xs"
              />
              <input
                type="text"
                placeholder="Slug (e.g. lab-equipment)"
                value={newCatSlug}
                onChange={(e) => setNewCatSlug(e.target.value)}
                required
                className="px-3 py-2 border border-slate-200 rounded-xl text-xs"
              />
              <button
                type="submit"
                className="px-4 py-2 bg-emerald-600 text-white font-bold text-xs rounded-xl shadow-xs"
              >
                Create Category
              </button>
            </div>
          </form>

          <div className="bg-white rounded-2xl border border-slate-200 overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-bold uppercase">
                <tr>
                  <th className="px-6 py-3">Category</th>
                  <th className="px-6 py-3">Slug</th>
                  <th className="px-6 py-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-800">
                {categories.map((c) => (
                  <tr key={c.slug} className="hover:bg-slate-50">
                    <td className="px-6 py-4 font-bold">{c.name}</td>
                    <td className="px-6 py-4 text-slate-400">{c.slug}</td>
                    <td className="px-6 py-4">
                      <Badge status={c.is_active ? 'ACTIVE' : 'SUSPENDED'} size="sm" />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
