import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Search, Filter, SlidersHorizontal, ChevronLeft, ChevronRight, RefreshCw, X } from 'lucide-react';
import { productService } from '../services/products';
import { categoryService } from '../services/categories';
import { wishlistService } from '../services/wishlist';
import type { Product, Category } from '../types';
import { ProductCard } from '../components/common/ProductCard';
import { useAuth } from '../context/AuthContext';

export const Marketplace: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const { isAuthenticated } = useAuth();

  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [wishlistIds, setWishlistIds] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Pagination state
  const [page, setPage] = useState<number>(parseInt(searchParams.get('page') || '1'));
  const [totalPages, setTotalPages] = useState<number>(1);
  const [totalCount, setTotalCount] = useState<number>(0);

  // Filter state initialized from URL params
  const [search, setSearch] = useState<string>(searchParams.get('search') || '');
  const [selectedCategory, setSelectedCategory] = useState<string>(searchParams.get('category') || '');
  const [selectedCondition, setSelectedCondition] = useState<string>(searchParams.get('condition') || '');
  const [minPrice, setMinPrice] = useState<string>(searchParams.get('min_price') || '');
  const [maxPrice, setMaxPrice] = useState<string>(searchParams.get('max_price') || '');
  const [sort, setSort] = useState<'newest' | 'oldest' | 'price_low_to_high' | 'price_high_to_low'>(
    (searchParams.get('sort') as any) || 'newest'
  );

  const [filterPanelOpen, setFilterPanelOpen] = useState(false);

  const DEFAULT_CATEGORIES: Category[] = [
    { _id: 'cat_1', name: 'Textbooks', slug: 'textbooks', is_active: true },
    { _id: 'cat_2', name: 'Scientific Calculators', slug: 'scientific-calculators', is_active: true },
    { _id: 'cat_3', name: 'Electronics', slug: 'electronics', is_active: true },
    { _id: 'cat_4', name: 'Laptops & Computers', slug: 'laptops', is_active: true },
    { _id: 'cat_5', name: 'Bicycles', slug: 'bicycles', is_active: true },
    { _id: 'cat_6', name: 'Lab Equipment', slug: 'lab-equipment', is_active: true },
    { _id: 'cat_7', name: 'Hostel Essentials', slug: 'hostel-essentials', is_active: true },
    { _id: 'cat_8', name: 'Stationery', slug: 'stationery', is_active: true },
    { _id: 'cat_9', name: 'Sports Equipment', slug: 'sports-equipment', is_active: true },
    { _id: 'cat_10', name: 'Accessories & Other', slug: 'other', is_active: true },
  ];

  // Fetch categories on mount
  useEffect(() => {
    categoryService
      .getCategories()
      .then((res: any) => {
        const fetched = Array.isArray(res) ? res : res?.items || [];
        setCategories(fetched.length > 0 ? fetched : DEFAULT_CATEGORIES);
      })
      .catch(() => setCategories(DEFAULT_CATEGORIES));
  }, []);

  // Sync state when URL searchParams change
  useEffect(() => {
    setSearch(searchParams.get('search') || '');
    setSelectedCategory(searchParams.get('category') || '');
    setSelectedCondition(searchParams.get('condition') || '');
    setMinPrice(searchParams.get('min_price') || '');
    setMaxPrice(searchParams.get('max_price') || '');
    setSort((searchParams.get('sort') as any) || 'newest');
    setPage(parseInt(searchParams.get('page') || '1'));
  }, [searchParams]);

  // Fetch products whenever filters change
  const fetchProducts = async () => {
    try {
      setLoading(true);
      setError(null);

      const params: any = {
        page,
        limit: 12,
        sort,
      };

      if (search.trim()) params.search = search.trim();
      if (selectedCategory) params.category = selectedCategory;
      if (selectedCondition) params.condition = selectedCondition;
      if (minPrice) params.min_price = parseFloat(minPrice);
      if (maxPrice) params.max_price = parseFloat(maxPrice);

      const res = await productService.getProducts(params);
      setProducts(res.items || []);

      if (res.pagination) {
        setTotalPages(res.pagination.pages || 1);
        setTotalCount(res.pagination.total || 0);
      } else {
        setTotalCount(res.count || res.items.length);
      }

      if (isAuthenticated) {
        const wishRes = await wishlistService.getWishlist();
        const rawItems = (wishRes as any).items || wishRes.wishlist || [];
        const ids = new Set<string>(rawItems.map((w: any) => String(w.product_id)));
        setWishlistIds(ids);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load marketplace products.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, [page, selectedCategory, selectedCondition, sort, isAuthenticated]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchProducts();
  };

  const handleClearFilters = () => {
    setSearch('');
    setSelectedCategory('');
    setSelectedCondition('');
    setMinPrice('');
    setMaxPrice('');
    setSort('newest');
    setPage(1);
    setSearchParams({});
  };

  const handleWishlistToggle = async (product: Product) => {
    if (!isAuthenticated) return;
    const exists = wishlistIds.has(product._id);
    try {
      if (exists) {
        await wishlistService.removeFromWishlist(product._id);
        setWishlistIds((prev) => {
          const next = new Set(prev);
          next.delete(product._id);
          return next;
        });
      } else {
        await wishlistService.addToWishlist(product._id);
        setWishlistIds((prev) => new Set(prev).add(product._id));
      }
    } catch (err) {
      console.error('Wishlist toggle failed:', err);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 pb-6">
        <div>
          <h1 className="text-3xl font-black text-slate-900">Campus Marketplace</h1>
          <p className="text-sm text-slate-500">
            Browse verified listings from students ({totalCount} items available)
          </p>
        </div>

        {/* Sorting Dropdown */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => setFilterPanelOpen(!filterPanelOpen)}
            className="md:hidden px-4 py-2 bg-slate-100 text-slate-700 text-sm font-bold rounded-xl flex items-center gap-2"
          >
            <SlidersHorizontal size={16} /> Filters
          </button>

          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-slate-400">Sort by:</span>
            <select
              value={sort}
              onChange={(e) => {
                setSort(e.target.value as any);
                setPage(1);
              }}
              className="bg-white border border-slate-200 text-slate-800 text-xs font-bold rounded-xl px-3 py-2 focus:outline-hidden focus:border-emerald-500 shadow-xs"
            >
              <option value="newest">Newest First</option>
              <option value="oldest">Oldest First</option>
              <option value="price_low_to_high">Price: Low to High</option>
              <option value="price_high_to_low">Price: High to Low</option>
            </select>
          </div>
        </div>
      </div>

      {/* Main Layout: Sidebar Filters + Product Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
        {/* Sidebar Filter Panel */}
        <div
          className={`md:block space-y-6 ${
            filterPanelOpen ? 'block fixed inset-0 z-50 bg-white p-6 overflow-y-auto' : 'hidden'
          }`}
        >
          <div className="flex items-center justify-between md:hidden pb-4 border-b border-slate-200">
            <h3 className="text-lg font-bold text-slate-900">Filter Marketplace</h3>
            <button onClick={() => setFilterPanelOpen(false)}>
              <X size={20} />
            </button>
          </div>

          {/* Search Box */}
          <form onSubmit={handleSearchSubmit} className="space-y-2">
            <label className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Search Keywords
            </label>
            <div className="relative">
              <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder="Search title, details..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:bg-white focus:border-emerald-500"
              />
            </div>
            <button
              type="submit"
              className="w-full py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl shadow-xs transition-colors"
            >
              Apply Search
            </button>
          </form>

          {/* Category Filter */}
          <div className="space-y-2">
            <label className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Category
            </label>
            <select
              value={selectedCategory}
              onChange={(e) => {
                setSelectedCategory(e.target.value);
                setPage(1);
              }}
              className="w-full bg-slate-50 border border-slate-200 text-slate-800 text-xs font-semibold rounded-xl px-3 py-2 focus:bg-white focus:border-emerald-500"
            >
              <option value="">All Categories</option>
              {categories.map((c) => (
                <option key={c.slug} value={c.slug}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>

          {/* Condition Filter */}
          <div className="space-y-2">
            <label className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Condition
            </label>
            <select
              value={selectedCondition}
              onChange={(e) => {
                setSelectedCondition(e.target.value);
                setPage(1);
              }}
              className="w-full bg-slate-50 border border-slate-200 text-slate-800 text-xs font-semibold rounded-xl px-3 py-2 focus:bg-white focus:border-emerald-500"
            >
              <option value="">Any Condition</option>
              <option value="NEW">Brand New</option>
              <option value="LIKE_NEW">Like New</option>
              <option value="GOOD">Good Condition</option>
              <option value="FAIR">Fair Condition</option>
              <option value="POOR">Poor Condition</option>
            </select>
          </div>

          {/* Price Filter */}
          <div className="space-y-2">
            <label className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Price Range ($)
            </label>
            <div className="flex items-center gap-2">
              <input
                type="number"
                placeholder="Min"
                value={minPrice}
                onChange={(e) => setMinPrice(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs"
              />
              <span className="text-slate-400 font-bold">-</span>
              <input
                type="number"
                placeholder="Max"
                value={maxPrice}
                onChange={(e) => setMaxPrice(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs"
              />
            </div>
            <button
              onClick={() => {
                setPage(1);
                fetchProducts();
              }}
              className="w-full py-2 bg-slate-800 hover:bg-slate-900 text-white text-xs font-bold rounded-xl transition-colors"
            >
              Filter Price
            </button>
          </div>

          {/* Clear Filters Button */}
          <button
            onClick={handleClearFilters}
            className="w-full py-2 text-xs font-semibold text-rose-600 hover:bg-rose-50 rounded-xl border border-rose-200 flex items-center justify-center gap-1.5 transition-colors"
          >
            <RefreshCw size={14} /> Clear All Filters
          </button>
        </div>

        {/* Product Grid Area */}
        <div className="md:col-span-3 space-y-8">
          {error && (
            <div className="p-4 bg-rose-50 border border-rose-200 text-rose-700 text-sm font-semibold rounded-2xl">
              {error}
            </div>
          )}

          {loading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3, 4, 5, 6].map((n) => (
                <div key={n} className="h-72 bg-slate-100 animate-pulse rounded-2xl" />
              ))}
            </div>
          ) : products.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {products.map((prod) => (
                <ProductCard
                  key={prod._id}
                  product={prod}
                  isWishlisted={wishlistIds.has(prod._id)}
                  onWishlistToggle={handleWishlistToggle}
                />
              ))}
            </div>
          ) : (
            <div className="p-12 text-center bg-white rounded-2xl border border-slate-200 text-slate-500 space-y-3">
              <Filter size={36} className="mx-auto text-slate-300" />
              <p className="text-base font-bold text-slate-700">No matching products found</p>
              <p className="text-xs text-slate-400 max-w-sm mx-auto">
                Try adjusting your search terms, removing filters, or choosing a different category.
              </p>
              <button
                onClick={handleClearFilters}
                className="px-4 py-2 bg-emerald-600 text-white text-xs font-bold rounded-xl shadow-xs hover:bg-emerald-700 transition-colors"
              >
                Reset Filters
              </button>
            </div>
          )}

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between pt-6 border-t border-slate-200">
              <button
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(p - 1, 1))}
                className="px-4 py-2 border border-slate-200 rounded-xl text-xs font-bold text-slate-700 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-50 flex items-center gap-1"
              >
                <ChevronLeft size={16} /> Previous
              </button>

              <span className="text-xs font-bold text-slate-600">
                Page {page} of {totalPages}
              </span>

              <button
                disabled={page >= totalPages}
                onClick={() => setPage((p) => Math.min(p + 1, totalPages))}
                className="px-4 py-2 border border-slate-200 rounded-xl text-xs font-bold text-slate-700 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-50 flex items-center gap-1"
              >
                Next <ChevronRight size={16} />
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
