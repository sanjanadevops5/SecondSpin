import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Search,
  BookOpen,
  Laptop,
  Calculator,
  Bike,
  Home as HomeIcon,
  Sparkles,
  TrendingUp,
  ArrowRight,
  Package,
} from 'lucide-react';
import { productService } from '../services/products';
import { smartService } from '../services/smart';
import { wishlistService } from '../services/wishlist';
import type { Product, RecommendedItem } from '../types';
import { ProductCard } from '../components/common/ProductCard';
import { useAuth } from '../context/AuthContext';

export const Home: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [searchTerm, setSearchTerm] = useState('');
  const [popularItems, setPopularItems] = useState<RecommendedItem[]>([]);
  const [recommendations, setRecommendations] = useState<RecommendedItem[]>([]);
  const [recentProducts, setRecentProducts] = useState<Product[]>([]);
  const [wishlistIds, setWishlistIds] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // Fetch recent products
        const recentRes = await productService.getProducts({ limit: 6, sort: 'newest' });
        setRecentProducts(recentRes.items || []);

        // Fetch popular products
        try {
          const popularRes = await smartService.getPopularProducts(4);
          setPopularItems(popularRes.items || []);
        } catch (e) {
          console.warn('Popular products fetch warning:', e);
        }

        // Fetch recommendations if authenticated
        if (isAuthenticated) {
          try {
            const recRes = await smartService.getPersonalizedRecommendations(4);
            setRecommendations(recRes.items || []);

            const wishRes = await wishlistService.getWishlist();
            const rawWish = (wishRes as any).items || wishRes.wishlist || [];
            const ids = new Set<string>(rawWish.map((w: any) => String(w.product_id)));
            setWishlistIds(ids);
          } catch (e) {
            console.warn('Recommendations fetch warning:', e);
          }
        }
      } catch (err) {
        console.error('Home page load error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [isAuthenticated]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchTerm.trim()) {
      navigate(`/marketplace?search=${encodeURIComponent(searchTerm.trim())}`);
    } else {
      navigate('/marketplace');
    }
  };

  const handleWishlistToggle = async (product: Product) => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
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
      console.error('Wishlist toggle error:', err);
    }
  };

  const categoryCards = [
    { name: 'Textbooks', slug: 'textbooks', icon: BookOpen, color: 'bg-emerald-500/10 text-emerald-600' },
    { name: 'Electronics', slug: 'electronics', icon: Laptop, color: 'bg-blue-500/10 text-blue-600' },
    { name: 'Calculators', slug: 'scientific-calculators', icon: Calculator, color: 'bg-amber-500/10 text-amber-600' },
    { name: 'Bicycles', slug: 'bicycles', icon: Bike, color: 'bg-purple-500/10 text-purple-600' },
    { name: 'Hostel Essentials', slug: 'hostel-essentials', icon: HomeIcon, color: 'bg-rose-500/10 text-rose-600' },
    { name: 'All Categories', slug: '', icon: Package, color: 'bg-slate-500/10 text-slate-600' },
  ];

  return (
    <div className="space-y-16 pb-16">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-b from-emerald-900 via-slate-900 to-slate-900 text-white pt-16 pb-24 rounded-b-3xl">
        <div className="absolute inset-0 opacity-10 bg-[radial-gradient(#10b981_1px,transparent_1px)] [background-size:16px_16px]" />
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-8">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-bold uppercase tracking-wider backdrop-blur-md">
            <Sparkles size={14} className="text-emerald-400" /> Campus Exclusive Marketplace
          </div>

          <h1 className="text-4xl sm:text-6xl font-black tracking-tight text-white max-w-4xl mx-auto leading-tight">
            Buy, Sell & Exchange Pre-Owned <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-300">Campus Essentials</span>
          </h1>

          <p className="text-base sm:text-xl text-slate-300 max-w-2xl mx-auto font-medium">
            Connect directly with fellow students on campus for textbooks, calculators, laptops, bicycles, and hostel gear. Smart, sustainable, affordable.
          </p>

          {/* Hero Search Bar */}
          <form onSubmit={handleSearchSubmit} className="max-w-2xl mx-auto">
            <div className="flex flex-col sm:flex-row items-center gap-2 p-2 bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl shadow-2xl">
              <div className="relative flex-1 w-full">
                <Search size={20} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-300" />
                <input
                  type="text"
                  placeholder="What do you need? (e.g. Calculus textbook, TI-84...)"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-12 pr-4 py-3 bg-transparent text-white placeholder:text-slate-300 text-sm focus:outline-hidden"
                />
              </div>
              <button
                type="submit"
                className="w-full sm:w-auto px-6 py-3 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-extrabold rounded-xl shadow-lg transition-all flex items-center justify-center gap-2 text-sm"
              >
                Browse Marketplace <ArrowRight size={16} />
              </button>
            </div>
          </form>

          {/* Hero CTAs */}
          <div className="flex items-center justify-center gap-4 pt-2">
            <Link
              to="/marketplace"
              className="px-6 py-3 rounded-xl bg-white/10 hover:bg-white/20 text-white font-bold text-sm border border-white/20 transition-all"
            >
              Explore All Items
            </Link>
            <Link
              to={isAuthenticated ? '/sell' : '/register'}
              className="px-6 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-sm shadow-md transition-all"
            >
              List an Item to Sell
            </Link>
          </div>
        </div>
      </section>

      {/* Category Grid */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-black text-slate-900">Browse by Category</h2>
            <p className="text-sm text-slate-500">Find exactly what you need for your courses and campus life</p>
          </div>
          <Link to="/marketplace" className="text-sm font-bold text-emerald-600 hover:underline flex items-center gap-1">
            View All <ArrowRight size={16} />
          </Link>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          {categoryCards.map((cat) => {
            const Icon = cat.icon;
            return (
              <Link
                key={cat.name}
                to={cat.slug ? `/marketplace?category=${cat.slug}` : '/marketplace'}
                className="flex flex-col items-center justify-center p-6 bg-white rounded-2xl border border-slate-200/80 shadow-xs hover:shadow-lg hover:-translate-y-1 transition-all group text-center"
              >
                <div className={`w-12 h-12 rounded-2xl ${cat.color} flex items-center justify-center mb-3 group-hover:scale-110 transition-transform`}>
                  <Icon size={24} />
                </div>
                <span className="text-sm font-bold text-slate-800 group-hover:text-emerald-600 transition-colors">
                  {cat.name}
                </span>
              </Link>
            );
          })}
        </div>
      </section>

      {/* Smart Personalized Recommendations (If Auth) */}
      {isAuthenticated && recommendations.length > 0 && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-xl bg-emerald-100 text-emerald-700">
                <Sparkles size={20} />
              </div>
              <div>
                <h2 className="text-2xl font-black text-slate-900">Recommended for You</h2>
                <p className="text-sm text-slate-500">Tailored to your wishlist and marketplace activity</p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {recommendations.map((item) => (
              <ProductCard
                key={item.product._id}
                product={item.product}
                reason={item.reason}
                isWishlisted={wishlistIds.has(item.product._id)}
                onWishlistToggle={handleWishlistToggle}
              />
            ))}
          </div>
        </section>
      )}

      {/* Popular Products Section */}
      {popularItems.length > 0 && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-xl bg-amber-100 text-amber-700">
                <TrendingUp size={20} />
              </div>
              <div>
                <h2 className="text-2xl font-black text-slate-900">Trending on Campus</h2>
                <p className="text-sm text-slate-500">Highest buyer interest, wishlist adds, and requests</p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {popularItems.map((item) => (
              <ProductCard
                key={item.product._id}
                product={item.product}
                reason={item.reason}
                isWishlisted={wishlistIds.has(item.product._id)}
                onWishlistToggle={handleWishlistToggle}
              />
            ))}
          </div>
        </section>
      )}

      {/* Recent Listings Grid */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-black text-slate-900">Fresh Campus Listings</h2>
            <p className="text-sm text-slate-500">Recently posted by students across campus</p>
          </div>
          <Link to="/marketplace" className="text-sm font-bold text-emerald-600 hover:underline">
            Explore All Listings
          </Link>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((n) => (
              <div key={n} className="h-72 bg-slate-100 animate-pulse rounded-2xl" />
            ))}
          </div>
        ) : recentProducts.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {recentProducts.map((prod) => (
              <ProductCard
                key={prod._id}
                product={prod}
                isWishlisted={wishlistIds.has(prod._id)}
                onWishlistToggle={handleWishlistToggle}
              />
            ))}
          </div>
        ) : (
          <div className="p-12 text-center bg-white rounded-2xl border border-slate-200 text-slate-500">
            No active listings found right now. Be the first to list an item!
          </div>
        )}
      </section>

      {/* How SecondSpin Works */}
      <section className="bg-slate-100/80 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
          <div className="text-center max-w-2xl mx-auto space-y-2">
            <h2 className="text-3xl font-black text-slate-900">How SecondSpin Works</h2>
            <p className="text-sm text-slate-600">A seamless peer-to-peer campus exchange process</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {[
              { step: '01', title: 'Find an Item', desc: 'Browse verified campus listings for textbooks, calculators, laptops, or gear.' },
              { step: '02', title: 'Submit Request', desc: 'Send a purchase request directly to the student seller.' },
              { step: '03', title: 'Campus Meetup', desc: 'Upon acceptance, item is reserved. Meet safely on campus to inspect and exchange.' },
              { step: '04', title: 'Complete & Review', desc: 'Confirm completed sale, update listing status, and build campus trust with seller ratings.' },
            ].map((s) => (
              <div key={s.step} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs relative">
                <span className="text-3xl font-black text-emerald-600 block mb-2">{s.step}</span>
                <h3 className="text-lg font-bold text-slate-900 mb-1">{s.title}</h3>
                <p className="text-xs text-slate-500 leading-relaxed">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};
