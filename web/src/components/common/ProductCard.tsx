import React from 'react';
import { Link } from 'react-router-dom';
import { Heart, Tag, User } from 'lucide-react';
import type { Product } from '../../types';
import { Badge } from './Badge';

interface ProductCardProps {
  product: Product;
  isWishlisted?: boolean;
  onWishlistToggle?: (product: Product) => void;
  reason?: string;
}

export const ProductCard: React.FC<ProductCardProps> = ({
  product,
  isWishlisted = false,
  onWishlistToggle,
  reason,
}) => {
  const imageUrl =
    product.images && product.images.length > 0
      ? product.images[0]
      : 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=600&q=80';

  return (
    <div className="group relative flex flex-col bg-white rounded-2xl border border-slate-200/80 shadow-xs hover:shadow-xl hover:-translate-y-1 transition-all duration-300 overflow-hidden">
      {/* Image container */}
      <div className="relative aspect-4/3 w-full bg-slate-100 overflow-hidden">
        <img
          src={imageUrl}
          alt={product.title}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          onError={(e) => {
            (e.target as HTMLImageElement).src =
              'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=600&q=80';
          }}
        />
        
        {/* Status & Condition badges over image */}
        <div className="absolute top-3 left-3 flex flex-wrap gap-1.5 z-10">
          <Badge status={product.status} size="sm" />
          <Badge status={product.condition} size="sm" />
        </div>

        {/* Wishlist Button */}
        {onWishlistToggle && (
          <button
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              onWishlistToggle(product);
            }}
            className="absolute top-3 right-3 p-2 rounded-full bg-white/90 backdrop-blur-md shadow-md text-slate-600 hover:text-rose-500 hover:scale-110 transition-all z-10"
            title={isWishlisted ? 'Remove from Wishlist' : 'Add to Wishlist'}
          >
            <Heart
              size={18}
              fill={isWishlisted ? '#f43f5e' : 'none'}
              className={isWishlisted ? 'text-rose-500' : 'text-slate-600'}
            />
          </button>
        )}
      </div>

      {/* Card Content */}
      <div className="flex flex-col flex-1 p-5">
        <div className="flex items-center justify-between gap-2 text-xs font-medium text-emerald-600 mb-2">
          <span className="inline-flex items-center gap-1 uppercase tracking-wider font-bold">
            <Tag size={12} />
            {product.category_id}
          </span>
          {product.seller?.department && (
            <span className="text-slate-400 inline-flex items-center gap-1 truncate max-w-[120px]">
              <User size={12} />
              {product.seller.department}
            </span>
          )}
        </div>

        <Link
          to={`/products/${product._id}`}
          className="text-base font-bold text-slate-900 group-hover:text-emerald-600 transition-colors line-clamp-1 mb-1"
        >
          {product.title}
        </Link>

        <p className="text-xs text-slate-500 line-clamp-2 mb-4 flex-1">
          {product.description}
        </p>

        {/* Reason Pill (Smart Features) */}
        {reason && (
          <div className="mb-3 px-2.5 py-1 rounded-lg bg-emerald-50 text-emerald-700 text-xs font-medium border border-emerald-100 flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            <span className="truncate">{reason}</span>
          </div>
        )}

        {/* Price & CTA Footer */}
        <div className="flex items-center justify-between pt-3 border-t border-slate-100">
          <div>
            <span className="text-xs text-slate-400 block font-medium">Price</span>
            <span className="text-lg font-extrabold text-slate-900">
              ${product.price.toFixed(2)}
            </span>
          </div>

          <Link
            to={`/products/${product._id}`}
            className="px-3.5 py-2 text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-700 rounded-xl shadow-xs hover:shadow-md transition-all"
          >
            View Details
          </Link>
        </div>
      </div>
    </div>
  );
};
