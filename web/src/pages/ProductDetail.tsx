import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  Heart,
  MessageSquare,
  ShieldAlert,
  Tag,
  CheckCircle2,
  TrendingUp,
  Sparkles,
  ArrowLeft,
  AlertTriangle,
} from 'lucide-react';
import { productService } from '../services/products';
import { wishlistService } from '../services/wishlist';
import { requestService } from '../services/requests';
import { smartService } from '../services/smart';
import { reportService } from '../services/reports';
import type { Product, PriceInsights, RecommendedItem } from '../types';
import { Badge } from '../components/common/Badge';
import { Modal } from '../components/common/Modal';
import { ProductCard } from '../components/common/ProductCard';
import { useAuth } from '../context/AuthContext';

export const ProductDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();

  const [product, setProduct] = useState<Product | null>(null);
  const [priceInsights, setPriceInsights] = useState<PriceInsights | null>(null);
  const [relatedProducts, setRelatedProducts] = useState<RecommendedItem[]>([]);
  const [isWishlisted, setIsWishlisted] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Request Modal State
  const [requestModalOpen, setRequestModalOpen] = useState(false);
  const [requestMessage, setRequestMessage] = useState('');
  const [requestSubmitting, setRequestSubmitting] = useState(false);
  const [requestSuccess, setRequestSuccess] = useState<string | null>(null);
  const [requestError, setRequestError] = useState<string | null>(null);

  // Report Modal State
  const [reportModalOpen, setReportModalOpen] = useState(false);
  const [reportReason, setReportReason] = useState('Inappropriate Content');
  const [reportDescription, setReportDescription] = useState('');
  const [reportSubmitting, setReportSubmitting] = useState(false);
  const [reportSuccess, setReportSuccess] = useState<string | null>(null);
  const [reportError, setReportError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;

    const loadProductData = async () => {
      try {
        setLoading(true);
        setError(null);

        const data = await productService.getProduct(id);
        setProduct(data);

        // Fetch price insights
        try {
          const insights = await smartService.getPriceInsights(id);
          setPriceInsights(insights);
        } catch (e) {
          console.warn('Price insights warning:', e);
        }

        // Fetch related products
        try {
          const related = await smartService.getRelatedProducts(id, 4);
          setRelatedProducts(related.items || []);
        } catch (e) {
          console.warn('Related products warning:', e);
        }

        // Check wishlist state if logged in
        if (isAuthenticated) {
          try {
            const wishRes = await wishlistService.getWishlist();
            const rawWish = (wishRes as any).items || wishRes.wishlist || [];
            const exists = rawWish.some((w: any) => w.product_id === id);
            setIsWishlisted(exists);
          } catch (e) {
            console.warn('Wishlist check warning:', e);
          }
        }
      } catch (err: any) {
        setError(err.message || 'Failed to load product details.');
      } finally {
        setLoading(false);
      }
    };

    loadProductData();
  }, [id, isAuthenticated]);

  const handleWishlistToggle = async () => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    if (!product) return;

    try {
      if (isWishlisted) {
        await wishlistService.removeFromWishlist(product._id);
        setIsWishlisted(false);
      } else {
        await wishlistService.addToWishlist(product._id);
        setIsWishlisted(true);
      }
    } catch (err: any) {
      alert(err.message || 'Failed to update wishlist.');
    }
  };

  const handleSendRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!product) return;

    try {
      setRequestSubmitting(true);
      setRequestError(null);
      await requestService.createRequest(product._id, requestMessage);
      setRequestSuccess('Purchase request submitted successfully! The seller has been notified.');
      setTimeout(() => {
        setRequestModalOpen(false);
        setRequestSuccess(null);
        setRequestMessage('');
      }, 2000);
    } catch (err: any) {
      setRequestError(err.message || 'Failed to send purchase request.');
    } finally {
      setRequestSubmitting(false);
    }
  };

  const handleSubmitReport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!product) return;

    try {
      setReportSubmitting(true);
      setReportError(null);
      await reportService.submitReport('PRODUCT', product._id, reportReason, reportDescription);
      setReportSuccess('Report submitted. SecondSpin moderators will review this listing.');
      setTimeout(() => {
        setReportModalOpen(false);
        setReportSuccess(null);
        setReportDescription('');
      }, 2000);
    } catch (err: any) {
      setReportError(err.message || 'Failed to submit report.');
    } finally {
      setReportSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 flex items-center justify-center">
        <div className="w-10 h-10 border-4 border-emerald-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="max-w-xl mx-auto px-4 py-16 text-center space-y-4">
        <AlertTriangle size={48} className="mx-auto text-amber-500" />
        <h2 className="text-2xl font-bold text-slate-900">Listing Unavailable</h2>
        <p className="text-sm text-slate-500">{error || 'This listing does not exist or has been removed.'}</p>
        <Link
          to="/marketplace"
          className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white font-bold rounded-xl text-sm"
        >
          <ArrowLeft size={16} /> Back to Marketplace
        </Link>
      </div>
    );
  }

  const isOwner = user?._id === product.seller?.id || user?._id === product.seller_id;
  const isAvailable = product.status === 'ACTIVE';
  const imageUrl =
    product.images && product.images.length > 0
      ? product.images[0]
      : 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=600&q=80';

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-12">
      {/* Breadcrumb Navigation */}
      <Link to="/marketplace" className="inline-flex items-center gap-2 text-xs font-bold text-slate-500 hover:text-emerald-600 transition-colors">
        <ArrowLeft size={14} /> Back to Marketplace
      </Link>

      {/* Main Product Overview Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        {/* Left: Image Container */}
        <div className="space-y-4">
          <div className="relative aspect-4/3 rounded-3xl bg-slate-100 border border-slate-200 overflow-hidden shadow-lg">
            <img
              src={imageUrl}
              alt={product.title}
              className="w-full h-full object-cover"
              onError={(e) => {
                (e.target as HTMLImageElement).src =
                  'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=600&q=80';
              }}
            />
            <div className="absolute top-4 left-4 flex gap-2">
              <Badge status={product.status} size="lg" />
              <Badge status={product.condition} size="lg" />
            </div>
          </div>
        </div>

        {/* Right: Product Details & Actions */}
        <div className="space-y-6">
          <div>
            <div className="flex items-center justify-between gap-2 mb-2">
              <span className="inline-flex items-center gap-1 text-xs font-bold uppercase tracking-wider text-emerald-600">
                <Tag size={14} /> {product.category_id.replace(/-/g, ' ')}
              </span>
              <button
                onClick={handleWishlistToggle}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors"
              >
                <Heart size={16} fill={isWishlisted ? '#f43f5e' : 'none'} className={isWishlisted ? 'text-rose-500' : 'text-slate-500'} />
                {isWishlisted ? 'Wishlisted' : 'Save to Wishlist'}
              </button>
            </div>

            <h1 className="text-3xl sm:text-4xl font-black text-slate-900 leading-tight">
              {product.title}
            </h1>

            <div className="mt-4 flex items-baseline gap-3">
              <span className="text-3xl font-black text-slate-900">${product.price.toFixed(2)}</span>
              <span className="text-xs font-semibold text-slate-400">Campus Pickup</span>
            </div>
          </div>

          {/* Seller Card */}
          <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200/80 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-emerald-100 text-emerald-800 font-bold flex items-center justify-center border border-emerald-300">
                {product.seller?.name?.charAt(0).toUpperCase() || 'S'}
              </div>
              <div>
                <span className="text-xs font-semibold text-slate-400 block">Seller</span>
                <span className="text-sm font-bold text-slate-900">{product.seller?.name || 'Campus Student'}</span>
                {product.seller?.department && (
                  <span className="text-xs text-slate-500 block">{product.seller.department}</span>
                )}
              </div>
            </div>

            <div className="text-right">
              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-extrabold uppercase">
                <CheckCircle2 size={12} /> Verified Student
              </span>
            </div>
          </div>

          {/* Product Description */}
          <div className="space-y-2">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500">Item Description</h3>
            <p className="text-sm text-slate-700 leading-relaxed whitespace-pre-line bg-white p-4 rounded-2xl border border-slate-100">
              {product.description}
            </p>
          </div>

          {/* Action Buttons */}
          <div className="space-y-3 pt-2">
            {isOwner ? (
              <div className="p-4 bg-amber-50 border border-amber-200 rounded-2xl text-amber-800 text-sm font-semibold flex items-center justify-between">
                <span>You own this listing</span>
                <Link to={`/sell?edit=${product._id}`} className="px-4 py-1.5 bg-amber-600 text-white rounded-xl text-xs font-bold">
                  Edit Listing
                </Link>
              </div>
            ) : isAvailable ? (
              <button
                onClick={() => {
                  if (!isAuthenticated) navigate('/login');
                  else setRequestModalOpen(true);
                }}
                className="w-full py-4 bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-base rounded-2xl shadow-lg shadow-emerald-600/20 hover:shadow-xl transition-all flex items-center justify-center gap-2"
              >
                <MessageSquare size={20} /> Request to Buy ($ {product.price.toFixed(2)})
              </button>
            ) : (
              <button
                disabled
                className="w-full py-4 bg-slate-200 text-slate-500 font-bold text-base rounded-2xl cursor-not-allowed"
              >
                Item Currently {product.status}
              </button>
            )}

            {/* Report Button */}
            {!isOwner && isAuthenticated && (
              <button
                onClick={() => setReportModalOpen(true)}
                className="w-full text-center text-xs font-semibold text-slate-400 hover:text-rose-600 transition-colors py-2 flex items-center justify-center gap-1"
              >
                <ShieldAlert size={14} /> Report Listing to Moderators
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Historical Price Insights Card */}
      {priceInsights && (
        <section className="bg-gradient-to-r from-slate-900 to-slate-800 text-white p-6 sm:p-8 rounded-3xl space-y-4 shadow-xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <TrendingUp size={22} className="text-emerald-400" />
              <h2 className="text-xl font-black">Historical Price Insights</h2>
            </div>
            <span className="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 text-xs font-bold border border-emerald-500/30">
              {priceInsights.price_comparison}
            </span>
          </div>

          {priceInsights.insufficient_data ? (
            <p className="text-xs text-slate-400">
              Insufficient historical data ({priceInsights.comparable_count} comparable listings). Benchmark statistics require at least 2 comparable category listings.
            </p>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-2">
              <div className="p-4 rounded-2xl bg-white/5 border border-white/10">
                <span className="text-xs text-slate-400 block font-medium">Listed Price</span>
                <span className="text-2xl font-black text-white">${priceInsights.current_price.toFixed(2)}</span>
              </div>
              <div className="p-4 rounded-2xl bg-white/5 border border-white/10">
                <span className="text-xs text-slate-400 block font-medium">Category Average</span>
                <span className="text-2xl font-black text-emerald-400">
                  ${priceInsights.historical_average?.toFixed(2)}
                </span>
              </div>
              <div className="p-4 rounded-2xl bg-white/5 border border-white/10">
                <span className="text-xs text-slate-400 block font-medium">Lowest Listing</span>
                <span className="text-2xl font-black text-slate-200">
                  ${priceInsights.min_price?.toFixed(2)}
                </span>
              </div>
              <div className="p-4 rounded-2xl bg-white/5 border border-white/10">
                <span className="text-xs text-slate-400 block font-medium">Comparables Evaluated</span>
                <span className="text-2xl font-black text-slate-200">{priceInsights.comparable_count}</span>
              </div>
            </div>
          )}
        </section>
      )}

      {/* Related Products Grid */}
      {relatedProducts.length > 0 && (
        <section className="space-y-6">
          <div className="flex items-center gap-2">
            <Sparkles size={20} className="text-emerald-600" />
            <h2 className="text-2xl font-black text-slate-900">Similar Items You Might Like</h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {relatedProducts.map((item) => (
              <ProductCard key={item.product._id} product={item.product} reason={item.reason} />
            ))}
          </div>
        </section>
      )}

      {/* Purchase Request Modal */}
      <Modal isOpen={requestModalOpen} onClose={() => setRequestModalOpen(false)} title="Send Purchase Request">
        <form onSubmit={handleSendRequest} className="space-y-4">
          <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs space-y-1">
            <span className="font-bold text-slate-800 block">{product.title}</span>
            <span className="text-emerald-700 font-extrabold block">${product.price.toFixed(2)}</span>
            <span className="text-slate-500 block">Seller: {product.seller?.name}</span>
          </div>

          {requestError && <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs font-semibold rounded-xl">{requestError}</div>}
          {requestSuccess && <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-semibold rounded-xl">{requestSuccess}</div>}

          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-700">Optional Note to Seller</label>
            <textarea
              rows={3}
              placeholder="e.g. Hi! I'm interested in buying this. Can we meet near the library tomorrow afternoon?"
              value={requestMessage}
              onChange={(e) => setRequestMessage(e.target.value)}
              className="w-full p-3 border border-slate-200 rounded-xl text-xs focus:border-emerald-500"
            />
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={() => setRequestModalOpen(false)}
              className="px-4 py-2 border border-slate-200 rounded-xl text-xs font-bold text-slate-600"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={requestSubmitting}
              className="px-5 py-2 bg-emerald-600 text-white rounded-xl text-xs font-bold hover:bg-emerald-700 shadow-md"
            >
              {requestSubmitting ? 'Sending...' : 'Submit Request'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Report Listing Modal */}
      <Modal isOpen={reportModalOpen} onClose={() => setReportModalOpen(false)} title="Report Listing">
        <form onSubmit={handleSubmitReport} className="space-y-4">
          {reportError && <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs font-semibold rounded-xl">{reportError}</div>}
          {reportSuccess && <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-semibold rounded-xl">{reportSuccess}</div>}

          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-700">Reason</label>
            <select
              value={reportReason}
              onChange={(e) => setReportReason(e.target.value)}
              className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs"
            >
              <option value="Inappropriate Content">Inappropriate Content</option>
              <option value="Fraudulent or Misleading">Fraudulent or Misleading</option>
              <option value="Prohibited Item">Prohibited Item</option>
              <option value="Spam">Spam</option>
              <option value="Other">Other</option>
            </select>
          </div>

          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-700">Description</label>
            <textarea
              rows={3}
              placeholder="Describe the issue with this listing..."
              value={reportDescription}
              onChange={(e) => setReportDescription(e.target.value)}
              className="w-full p-3 border border-slate-200 rounded-xl text-xs focus:border-emerald-500"
            />
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={() => setReportModalOpen(false)}
              className="px-4 py-2 border border-slate-200 rounded-xl text-xs font-bold text-slate-600"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={reportSubmitting}
              className="px-5 py-2 bg-rose-600 text-white rounded-xl text-xs font-bold hover:bg-rose-700 shadow-md"
            >
              {reportSubmitting ? 'Submitting...' : 'Submit Report'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
