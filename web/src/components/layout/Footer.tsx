import React from 'react';
import { Link } from 'react-router-dom';
import { RotateCcw, ShieldCheck, Heart } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-slate-900 text-slate-300 border-t border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand & Vision */}
          <div className="space-y-4 md:col-span-1">
            <Link to="/" className="flex items-center gap-2">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center text-slate-900 font-bold">
                <RotateCcw size={20} />
              </div>
              <span className="text-xl font-black text-white tracking-tight">
                Second<span className="text-emerald-400">Spin</span>
              </span>
            </Link>
            <p className="text-xs text-slate-400 leading-relaxed">
              Campus-exclusive marketplace for students to buy, sell, and exchange pre-owned student essentials safely.
            </p>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-800 text-emerald-400 text-xs font-semibold border border-slate-700">
              <ShieldCheck size={14} /> Verified Campus Community
            </div>
          </div>

          {/* Marketplace Navigation */}
          <div>
            <h4 className="text-sm font-bold text-white uppercase tracking-wider mb-4">
              Marketplace
            </h4>
            <ul className="space-y-2 text-xs text-slate-400">
              <li>
                <Link to="/marketplace?category=textbooks" className="hover:text-emerald-400 transition-colors">
                  Textbooks & Guides
                </Link>
              </li>
              <li>
                <Link to="/marketplace?category=electronics" className="hover:text-emerald-400 transition-colors">
                  Laptops & Electronics
                </Link>
              </li>
              <li>
                <Link to="/marketplace?category=calculators" className="hover:text-emerald-400 transition-colors">
                  Graphing Calculators
                </Link>
              </li>
              <li>
                <Link to="/marketplace?category=bicycles" className="hover:text-emerald-400 transition-colors">
                  Bicycles & Scooters
                </Link>
              </li>
              <li>
                <Link to="/marketplace?category=hostel-essentials" className="hover:text-emerald-400 transition-colors">
                  Hostel Essentials
                </Link>
              </li>
            </ul>
          </div>

          {/* Student Hub */}
          <div>
            <h4 className="text-sm font-bold text-white uppercase tracking-wider mb-4">
              Student Hub
            </h4>
            <ul className="space-y-2 text-xs text-slate-400">
              <li>
                <Link to="/sell" className="hover:text-emerald-400 transition-colors">
                  List an Item for Sale
                </Link>
              </li>
              <li>
                <Link to="/wishlist" className="hover:text-emerald-400 transition-colors">
                  Saved Wishlist
                </Link>
              </li>
              <li>
                <Link to="/requests" className="hover:text-emerald-400 transition-colors">
                  Purchase Requests
                </Link>
              </li>
              <li>
                <Link to="/transactions" className="hover:text-emerald-400 transition-colors">
                  Transaction History
                </Link>
              </li>
            </ul>
          </div>

          {/* Campus Trust */}
          <div>
            <h4 className="text-sm font-bold text-white uppercase tracking-wider mb-4">
              Trust & Safety
            </h4>
            <p className="text-xs text-slate-400 mb-3">
              SecondSpin enforces student authorization, transaction confirmation, and seller ratings.
            </p>
            <div className="p-3 rounded-xl bg-slate-800/80 border border-slate-700/80 text-xs text-slate-300">
              <span className="font-bold text-white block mb-1">Peer-to-Peer Campus Pickup</span>
              Safe in-person campus meetups arranged directly between buyers and sellers.
            </div>
          </div>
        </div>

        <div className="mt-12 pt-6 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-4">
          <p>© {new Date().getFullYear()} SecondSpin Campus Marketplace. All rights reserved.</p>
          <div className="flex items-center gap-1">
            <span>Built for smart campus re-use</span>
            <Heart size={14} className="text-rose-500 fill-rose-500" />
          </div>
        </div>
      </div>
    </footer>
  );
};
