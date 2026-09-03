import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { MessageSquare, Check, X, Ban, Repeat, User } from 'lucide-react';
import { requestService } from '../services/requests';
import { transactionService } from '../services/transactions';
import type { PurchaseRequest } from '../types';
import { Badge } from '../components/common/Badge';

export const Requests: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'mine' | 'received'>('mine');
  const [myRequests, setMyRequests] = useState<PurchaseRequest[]>([]);
  const [receivedRequests, setReceivedRequests] = useState<PurchaseRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const fetchRequests = async () => {
    try {
      setLoading(true);
      setError(null);
      const [mineRes, recRes] = await Promise.all([
        requestService.getMyRequests(),
        requestService.getReceivedRequests(),
      ]);
      setMyRequests(mineRes.requests || []);
      setReceivedRequests(recRes.requests || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load purchase requests.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRequests();
  }, []);

  const handleAccept = async (id: string) => {
    try {
      setActionLoading(id);
      await requestService.acceptRequest(id);
      fetchRequests();
    } catch (err: any) {
      alert(err.message || 'Failed to accept request.');
    } finally {
      setActionLoading(null);
    }
  };

  const handleReject = async (id: string) => {
    try {
      setActionLoading(id);
      await requestService.rejectRequest(id);
      fetchRequests();
    } catch (err: any) {
      alert(err.message || 'Failed to reject request.');
    } finally {
      setActionLoading(null);
    }
  };

  const handleCancel = async (id: string) => {
    try {
      setActionLoading(id);
      await requestService.cancelRequest(id);
      fetchRequests();
    } catch (err: any) {
      alert(err.message || 'Failed to cancel request.');
    } finally {
      setActionLoading(null);
    }
  };

  const handleInitiateTransaction = async (request: PurchaseRequest) => {
    try {
      setActionLoading(request._id);
      await transactionService.createTransaction(request._id);
      navigate('/transactions');
    } catch (err: any) {
      alert(err.message || 'Failed to create transaction.');
    } finally {
      setActionLoading(null);
    }
  };

  const currentList = activeTab === 'mine' ? myRequests : receivedRequests;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div className="border-b border-slate-200 pb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-black text-slate-900">Purchase Requests</h1>
          <p className="text-sm text-slate-500">Manage buyer requests and seller notifications</p>
        </div>

        {/* Sub-tabs */}
        <div className="flex bg-slate-100 p-1 rounded-2xl">
          <button
            onClick={() => setActiveTab('mine')}
            className={`px-4 py-2 text-xs font-bold rounded-xl transition-all ${
              activeTab === 'mine' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-500 hover:text-slate-900'
            }`}
          >
            My Requests ({myRequests.length})
          </button>
          <button
            onClick={() => setActiveTab('received')}
            className={`px-4 py-2 text-xs font-bold rounded-xl transition-all ${
              activeTab === 'received' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-500 hover:text-slate-900'
            }`}
          >
            Received Requests ({receivedRequests.length})
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-700 text-sm font-semibold rounded-2xl">
          {error}
        </div>
      )}

      {loading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((n) => (
            <div key={n} className="h-28 bg-slate-100 animate-pulse rounded-2xl" />
          ))}
        </div>
      ) : currentList.length > 0 ? (
        <div className="space-y-4">
          {currentList.map((req) => (
            <div
              key={req._id}
              className="p-6 bg-white rounded-2xl border border-slate-200/80 shadow-xs hover:shadow-md transition-all flex flex-col md:flex-row md:items-center justify-between gap-4"
            >
              <div className="space-y-2 flex-1">
                <div className="flex items-center gap-2">
                  <Badge status={req.status} size="sm" />
                  <span className="text-xs text-slate-400">
                    Requested on {new Date(req.created_at).toLocaleDateString()}
                  </span>
                </div>

                <div className="flex items-center gap-3">
                  <Link
                    to={`/products/${req.product_id}`}
                    className="text-base font-bold text-slate-900 hover:text-emerald-600 transition-colors"
                  >
                    {req.product?.title || `Product ID: ${req.product_id}`}
                  </Link>
                  {req.product?.price && (
                    <span className="text-sm font-extrabold text-emerald-700">
                      ${req.product.price.toFixed(2)}
                    </span>
                  )}
                </div>

                {req.message && (
                  <p className="text-xs text-slate-600 bg-slate-50 p-3 rounded-xl border border-slate-100 italic">
                    "{req.message}"
                  </p>
                )}

                <div className="text-xs text-slate-500 flex items-center gap-2">
                  <User size={12} />
                  <span>
                    {activeTab === 'mine'
                      ? `Seller: ${req.seller?.name || 'Campus Seller'}`
                      : `Buyer: ${req.buyer?.name || 'Campus Buyer'}`}
                  </span>
                </div>
              </div>

              {/* Actions depending on Tab & Status */}
              <div className="flex items-center gap-2 self-end md:self-center">
                {activeTab === 'received' && req.status === 'PENDING' && (
                  <>
                    <button
                      disabled={actionLoading === req._id}
                      onClick={() => handleAccept(req._id)}
                      className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-xl shadow-xs flex items-center gap-1.5"
                    >
                      <Check size={14} /> Accept Request
                    </button>
                    <button
                      disabled={actionLoading === req._id}
                      onClick={() => handleReject(req._id)}
                      className="px-4 py-2 bg-rose-50 text-rose-700 hover:bg-rose-100 font-bold text-xs rounded-xl border border-rose-200 flex items-center gap-1.5"
                    >
                      <X size={14} /> Reject
                    </button>
                  </>
                )}

                {activeTab === 'mine' && req.status === 'PENDING' && (
                  <button
                    disabled={actionLoading === req._id}
                    onClick={() => handleCancel(req._id)}
                    className="px-4 py-2 bg-slate-100 text-slate-700 hover:bg-slate-200 font-bold text-xs rounded-xl flex items-center gap-1.5"
                  >
                    <Ban size={14} /> Cancel Request
                  </button>
                )}

                {activeTab === 'mine' && req.status === 'ACCEPTED' && (
                  <button
                    disabled={actionLoading === req._id}
                    onClick={() => handleInitiateTransaction(req)}
                    className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs rounded-xl shadow-md flex items-center gap-1.5"
                  >
                    <Repeat size={14} /> Initiate Transaction
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-12 text-center bg-white rounded-3xl border border-slate-200 space-y-4">
          <MessageSquare size={36} className="mx-auto text-slate-300" />
          <h3 className="text-lg font-bold text-slate-800">
            {activeTab === 'mine' ? 'No purchase requests sent yet' : 'No purchase requests received'}
          </h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto">
            {activeTab === 'mine'
              ? 'Find an item on the marketplace and send a purchase request to the seller.'
              : 'List an item for sale to receive buyer requests.'}
          </p>
        </div>
      )}
    </div>
  );
};
