import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Repeat, CheckCircle2, Lock, Ban, Star, User, Calendar } from 'lucide-react';
import { transactionService } from '../services/transactions';
import { reviewService } from '../services/reviews';
import type { Transaction } from '../types';
import { Badge } from '../components/common/Badge';
import { Modal } from '../components/common/Modal';
import { RatingStars } from '../components/common/RatingStars';

export const Transactions: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'mine' | 'received'>('mine');
  const [purchases, setPurchases] = useState<Transaction[]>([]);
  const [sales, setSales] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  // Review Modal State
  const [reviewModalOpen, setReviewModalOpen] = useState(false);
  const [targetTransaction, setTargetTransaction] = useState<Transaction | null>(null);
  const [rating, setRating] = useState<number>(5);
  const [comment, setComment] = useState<string>('');
  const [reviewSubmitting, setReviewSubmitting] = useState<boolean>(false);
  const [reviewSuccess, setReviewSuccess] = useState<string | null>(null);
  const [reviewError, setReviewError] = useState<string | null>(null);

  const fetchTransactions = async () => {
    try {
      setLoading(true);
      setError(null);
      const [mineRes, recRes] = await Promise.all([
        transactionService.getMyTransactions(),
        transactionService.getReceivedTransactions(),
      ]);
      setPurchases(mineRes.items || mineRes.transactions || []);
      setSales(recRes.items || recRes.transactions || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load transactions.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTransactions();
  }, []);

  const handleReserve = async (id: string) => {
    try {
      setActionLoading(id);
      await transactionService.reserveTransaction(id);
      fetchTransactions();
    } catch (err: any) {
      alert(err.message || 'Failed to reserve transaction.');
    } finally {
      setActionLoading(null);
    }
  };

  const handleComplete = async (id: string) => {
    try {
      setActionLoading(id);
      await transactionService.completeTransaction(id);
      fetchTransactions();
    } catch (err: any) {
      alert(err.message || 'Failed to complete transaction.');
    } finally {
      setActionLoading(null);
    }
  };

  const handleCancel = async (id: string) => {
    try {
      setActionLoading(id);
      await transactionService.cancelTransaction(id);
      fetchTransactions();
    } catch (err: any) {
      alert(err.message || 'Failed to cancel transaction.');
    } finally {
      setActionLoading(null);
    }
  };

  const handleOpenReviewModal = (tx: Transaction) => {
    setTargetTransaction(tx);
    setRating(5);
    setComment('');
    setReviewError(null);
    setReviewSuccess(null);
    setReviewModalOpen(true);
  };

  const handleSubmitReview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetTransaction) return;

    try {
      setReviewSubmitting(true);
      setReviewError(null);
      await reviewService.submitReview(targetTransaction._id, rating, comment);
      setReviewSuccess('Review submitted successfully! Thank you for building campus trust.');
      setTimeout(() => {
        setReviewModalOpen(false);
        setReviewSuccess(null);
      }, 2000);
    } catch (err: any) {
      setReviewError(err.message || 'Failed to submit review.');
    } finally {
      setReviewSubmitting(false);
    }
  };

  const currentList = activeTab === 'mine' ? purchases : sales;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div className="border-b border-slate-200 pb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-black text-slate-900">Campus Transactions</h1>
          <p className="text-sm text-slate-500">Track purchase reservations, completions, and reviews</p>
        </div>

        <div className="flex bg-slate-100 p-1 rounded-2xl">
          <button
            onClick={() => setActiveTab('mine')}
            className={`px-4 py-2 text-xs font-bold rounded-xl transition-all ${
              activeTab === 'mine' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-500 hover:text-slate-900'
            }`}
          >
            My Purchases ({purchases.length})
          </button>
          <button
            onClick={() => setActiveTab('received')}
            className={`px-4 py-2 text-xs font-bold rounded-xl transition-all ${
              activeTab === 'received' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-500 hover:text-slate-900'
            }`}
          >
            My Sales ({sales.length})
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
            <div key={n} className="h-32 bg-slate-100 animate-pulse rounded-2xl" />
          ))}
        </div>
      ) : currentList.length > 0 ? (
        <div className="space-y-4">
          {currentList.map((tx) => (
            <div
              key={tx._id}
              className="p-6 bg-white rounded-2xl border border-slate-200/80 shadow-xs hover:shadow-md transition-all flex flex-col md:flex-row md:items-center justify-between gap-4"
            >
              <div className="space-y-2 flex-1">
                <div className="flex items-center gap-2">
                  <Badge status={tx.status} size="sm" />
                  <span className="text-xs text-slate-400 inline-flex items-center gap-1">
                    <Calendar size={12} /> {new Date(tx.created_at).toLocaleDateString()}
                  </span>
                </div>

                <div className="flex items-center gap-3">
                  <Link
                    to={`/products/${tx.product_id}`}
                    className="text-base font-bold text-slate-900 hover:text-emerald-600 transition-colors"
                  >
                    {tx.product?.title || `Product ID: ${tx.product_id}`}
                  </Link>
                  {tx.product?.price && (
                    <span className="text-sm font-extrabold text-emerald-700">
                      ${tx.product.price.toFixed(2)}
                    </span>
                  )}
                </div>

                <div className="text-xs text-slate-500 flex items-center gap-4">
                  <span className="inline-flex items-center gap-1">
                    <User size={12} />
                    {activeTab === 'mine'
                      ? `Seller: ${tx.seller?.name || 'Campus Seller'}`
                      : `Buyer: ${tx.buyer?.name || 'Campus Buyer'}`}
                  </span>
                </div>
              </div>

              {/* Actions based on Tab & Status */}
              <div className="flex items-center gap-2 self-end md:self-center">
                {activeTab === 'received' && tx.status === 'PENDING' && (
                  <button
                    disabled={actionLoading === tx._id}
                    onClick={() => handleReserve(tx._id)}
                    className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs rounded-xl shadow-xs flex items-center gap-1.5"
                  >
                    <Lock size={14} /> Reserve Item
                  </button>
                )}

                {(tx.status === 'PENDING' || tx.status === 'RESERVED') && (
                  <>
                    <button
                      disabled={actionLoading === tx._id}
                      onClick={() => handleComplete(tx._id)}
                      className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-xl shadow-md flex items-center gap-1.5"
                    >
                      <CheckCircle2 size={14} /> Complete Transaction
                    </button>
                    <button
                      disabled={actionLoading === tx._id}
                      onClick={() => handleCancel(tx._id)}
                      className="px-3 py-2 bg-slate-100 text-slate-600 hover:bg-slate-200 font-bold text-xs rounded-xl flex items-center gap-1.5"
                    >
                      <Ban size={14} /> Cancel
                    </button>
                  </>
                )}

                {tx.status === 'COMPLETED' && (
                  <button
                    onClick={() => handleOpenReviewModal(tx)}
                    className="px-4 py-2 bg-amber-50 text-amber-800 hover:bg-amber-100 border border-amber-200 font-bold text-xs rounded-xl flex items-center gap-1.5 shadow-xs"
                  >
                    <Star size={14} className="fill-amber-400 text-amber-500" /> Leave Review & Rating
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-12 text-center bg-white rounded-3xl border border-slate-200 space-y-4">
          <Repeat size={36} className="mx-auto text-slate-300" />
          <h3 className="text-lg font-bold text-slate-800">
            {activeTab === 'mine' ? 'No purchases yet' : 'No sales transactions yet'}
          </h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto">
            Transactions are created when a purchase request is accepted by the seller.
          </p>
        </div>
      )}

      {/* Review Modal */}
      <Modal isOpen={reviewModalOpen} onClose={() => setReviewModalOpen(false)} title="Rate & Review Transaction">
        <form onSubmit={handleSubmitReview} className="space-y-4">
          {reviewError && (
            <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs font-semibold rounded-xl">
              {reviewError}
            </div>
          )}
          {reviewSuccess && (
            <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-semibold rounded-xl">
              {reviewSuccess}
            </div>
          )}

          <div className="text-center space-y-2 py-2 bg-slate-50 rounded-2xl border border-slate-100">
            <span className="text-xs font-bold text-slate-500 block">Select Rating (1 to 5 Stars)</span>
            <div className="flex justify-center">
              <RatingStars rating={rating} interactive={true} onRatingChange={setRating} size={28} />
            </div>
          </div>

          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-700">Optional Review Comment</label>
            <textarea
              rows={3}
              placeholder="How was the item condition and campus meetup experience?"
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              className="w-full p-3 border border-slate-200 rounded-xl text-xs focus:border-emerald-500"
            />
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={() => setReviewModalOpen(false)}
              className="px-4 py-2 border border-slate-200 rounded-xl text-xs font-bold text-slate-600"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={reviewSubmitting}
              className="px-5 py-2 bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold text-xs rounded-xl shadow-md"
            >
              {reviewSubmitting ? 'Submitting...' : 'Submit Rating'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
