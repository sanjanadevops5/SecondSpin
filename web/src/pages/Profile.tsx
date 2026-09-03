import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Mail, Building, PlusCircle, Trash2, Edit } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { productService } from '../services/products';
import { reviewService } from '../services/reviews';
import type { Product, Review } from '../types';
import { Badge } from '../components/common/Badge';
import { RatingStars } from '../components/common/RatingStars';

export const Profile: React.FC = () => {
  const { user } = useAuth();
  const [myProducts, setMyProducts] = useState<Product[]>([]);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [avgRating, setAvgRating] = useState<number>(0);
  const [activeTab, setActiveTab] = useState<'listings' | 'reviews'>('listings');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) return;

    const loadProfileData = async () => {
      try {
        setLoading(true);
        const [prodRes, revRes] = await Promise.all([
          productService.getMyProducts(),
          reviewService.getUserReviews(user._id).catch(() => ({ reviews: [], average_rating: 0 })),
        ]);

        setMyProducts(prodRes.items || []);
        setReviews(revRes.reviews || []);
        setAvgRating(revRes.average_rating || 0);
      } catch (err) {
        console.error('Failed to load profile data:', err);
      } finally {
        setLoading(false);
      }
    };

    loadProfileData();
  }, [user]);

  const handleDeleteListing = async (id: string) => {
    if (!window.confirm('Are you sure you want to remove this listing?')) return;
    try {
      await productService.deleteProduct(id);
      setMyProducts((prev) => prev.filter((p) => p._id !== id));
    } catch (err: any) {
      alert(err.message || 'Failed to remove product.');
    }
  };

  if (!user) return null;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Profile Overview Card */}
      <div className="bg-white p-8 rounded-3xl border border-slate-200 shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-3xl bg-emerald-100 text-emerald-800 font-extrabold text-2xl flex items-center justify-center border-2 border-emerald-300 shadow-md">
            {user.name.charAt(0).toUpperCase()}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-black text-slate-900">{user.name}</h1>
              <Badge status={user.role} size="sm" />
            </div>
            <p className="text-xs text-slate-400 flex items-center gap-1.5 mt-1">
              <Mail size={14} /> {user.email}
            </p>
            {user.department && (
              <p className="text-xs text-slate-500 flex items-center gap-1.5 mt-0.5">
                <Building size={14} /> {user.department}
              </p>
            )}
          </div>
        </div>

        {/* Rating Summary */}
        <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 flex items-center gap-4">
          <div className="text-center">
            <span className="text-xs font-semibold text-slate-400 block">Seller Rating</span>
            <div className="flex items-center gap-1.5">
              <span className="text-2xl font-black text-slate-900">{avgRating.toFixed(1)}</span>
              <RatingStars rating={avgRating} size={16} />
            </div>
            <span className="text-[10px] text-slate-400">{reviews.length} reviews received</span>
          </div>

          <Link
            to="/sell"
            className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-xl shadow-md transition-all flex items-center gap-1.5"
          >
            <PlusCircle size={16} /> List Item
          </Link>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-200 pb-4 flex items-center gap-4">
        <button
          onClick={() => setActiveTab('listings')}
          className={`pb-2 text-sm font-bold border-b-2 transition-all ${
            activeTab === 'listings'
              ? 'border-emerald-600 text-emerald-600'
              : 'border-transparent text-slate-500 hover:text-slate-900'
          }`}
        >
          My Listings ({myProducts.length})
        </button>
        <button
          onClick={() => setActiveTab('reviews')}
          className={`pb-2 text-sm font-bold border-b-2 transition-all ${
            activeTab === 'reviews'
              ? 'border-emerald-600 text-emerald-600'
              : 'border-transparent text-slate-500 hover:text-slate-900'
          }`}
        >
          Campus Reviews ({reviews.length})
        </button>
      </div>

      {/* Content */}
      {activeTab === 'listings' ? (
        loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2].map((n) => (
              <div key={n} className="h-64 bg-slate-100 animate-pulse rounded-2xl" />
            ))}
          </div>
        ) : myProducts.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {myProducts.map((prod) => (
              <div key={prod._id} className="p-5 bg-white rounded-2xl border border-slate-200 shadow-xs flex flex-col justify-between">
                <div className="space-y-2 mb-4">
                  <div className="flex items-center justify-between">
                    <Badge status={prod.status} size="sm" />
                    <span className="text-sm font-extrabold text-slate-900">${prod.price.toFixed(2)}</span>
                  </div>
                  <h3 className="text-base font-bold text-slate-900">{prod.title}</h3>
                  <p className="text-xs text-slate-500 line-clamp-2">{prod.description}</p>
                </div>

                <div className="flex items-center justify-between pt-3 border-t border-slate-100">
                  <Link to={`/sell?edit=${prod._id}`} className="px-3 py-1.5 bg-slate-100 text-slate-700 rounded-lg text-xs font-bold flex items-center gap-1">
                    <Edit size={12} /> Edit
                  </Link>
                  <button
                    onClick={() => handleDeleteListing(prod._id)}
                    className="px-3 py-1.5 bg-rose-50 text-rose-700 rounded-lg text-xs font-bold flex items-center gap-1"
                  >
                    <Trash2 size={12} /> Remove
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-12 text-center bg-white rounded-3xl border border-slate-200">
            <p className="text-sm text-slate-500">You have no active or previous listings yet.</p>
          </div>
        )
      ) : (
        /* Reviews tab */
        reviews.length > 0 ? (
          <div className="space-y-4">
            {reviews.map((rev) => (
              <div key={rev._id} className="p-5 bg-white rounded-2xl border border-slate-200 space-y-2">
                <div className="flex items-center justify-between">
                  <RatingStars rating={rev.rating} size={16} />
                  <span className="text-xs text-slate-400">{new Date(rev.created_at).toLocaleDateString()}</span>
                </div>
                {rev.comment && <p className="text-xs text-slate-700 italic">"{rev.comment}"</p>}
              </div>
            ))}
          </div>
        ) : (
          <div className="p-12 text-center bg-white rounded-3xl border border-slate-200">
            <p className="text-sm text-slate-500">No reviews received yet.</p>
          </div>
        )
      )}
    </div>
  );
};
