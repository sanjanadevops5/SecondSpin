import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { DollarSign, CheckCircle2, AlertCircle, Trash2 } from 'lucide-react';
import { productService } from '../services/products';
import { categoryService } from '../services/categories';
import type { Category } from '../types';

export const Sell: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const editId = searchParams.get('edit');

  const [categories, setCategories] = useState<Category[]>([]);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [price, setPrice] = useState('');
  const [categoryId, setCategoryId] = useState('');
  const [condition, setCondition] = useState('GOOD');
  const [imageUrlInput, setImageUrlInput] = useState('');
  const [images, setImages] = useState<string[]>([]);
  const [status, setStatus] = useState<'ACTIVE' | 'RESERVED' | 'SOLD'>('ACTIVE');

  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    categoryService.getCategories().then((cats) => {
      setCategories(cats);
      if (cats.length > 0 && !categoryId) {
        setCategoryId(cats[0].slug);
      }
    });

    if (editId) {
      setInitialLoading(true);
      productService
        .getProduct(editId)
        .then((prod) => {
          setTitle(prod.title);
          setDescription(prod.description);
          setPrice(prod.price.toString());
          setCategoryId(prod.category_id);
          setCondition(prod.condition);
          setImages(prod.images || []);
          setStatus(prod.status as any);
        })
        .catch((err) => setError(err.message || 'Failed to load existing listing.'))
        .finally(() => setInitialLoading(false));
    }
  }, [editId]);

  const handleAddImage = () => {
    if (!imageUrlInput.trim()) return;
    if (images.length >= 5) {
      setError('Maximum of 5 image URLs allowed.');
      return;
    }
    setImages([...images, imageUrlInput.trim()]);
    setImageUrlInput('');
  };

  const handleRemoveImage = (index: number) => {
    setImages(images.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !description.trim() || !price || !categoryId) {
      setError('Please fill in all required fields.');
      return;
    }

    const priceNum = parseFloat(price);
    if (isNaN(priceNum) || priceNum < 0) {
      setError('Please enter a valid positive price.');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      if (editId) {
        await productService.updateProduct(editId, {
          title: title.trim(),
          description: description.trim(),
          price: priceNum,
          category_id: categoryId,
          condition: condition as any,
          images,
          status,
        });
        navigate(`/products/${editId}`);
      } else {
        const res = await productService.createProduct({
          title: title.trim(),
          description: description.trim(),
          price: priceNum,
          category_id: categoryId,
          condition,
          images,
        });
        navigate(`/products/${res.product_id}`);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to save listing.');
    } finally {
      setLoading(false);
    }
  };

  if (initialLoading) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 flex items-center justify-center">
        <div className="w-10 h-10 border-4 border-emerald-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="bg-white p-8 rounded-3xl border border-slate-200 shadow-xl space-y-8">
        <div>
          <h1 className="text-3xl font-black text-slate-900">
            {editId ? 'Edit Your Listing' : 'List an Item for Sale'}
          </h1>
          <p className="text-xs text-slate-500">
            Reach thousands of fellow students on campus directly
          </p>
        </div>

        {error && (
          <div className="p-4 bg-rose-50 border border-rose-200 text-rose-700 text-xs font-semibold rounded-2xl flex items-center gap-2">
            <AlertCircle size={16} className="shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Title */}
          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-700">Listing Title *</label>
            <input
              type="text"
              placeholder="e.g. Calculus Stewart 8th Edition, TI-84 Plus, Trek Bicycle"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              maxLength={100}
              className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:bg-white focus:border-emerald-500"
            />
          </div>

          {/* Category & Condition */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-700">Category *</label>
              <select
                value={categoryId}
                onChange={(e) => setCategoryId(e.target.value)}
                required
                className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:bg-white focus:border-emerald-500"
              >
                {categories.map((c) => (
                  <option key={c.slug} value={c.slug}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-700">Condition *</label>
              <select
                value={condition}
                onChange={(e) => setCondition(e.target.value)}
                required
                className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:bg-white focus:border-emerald-500"
              >
                <option value="NEW">Brand New</option>
                <option value="LIKE_NEW">Like New</option>
                <option value="GOOD">Good</option>
                <option value="FAIR">Fair</option>
                <option value="POOR">Poor</option>
              </select>
            </div>
          </div>

          {/* Price */}
          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-700">Price ($ USD) *</label>
            <div className="relative">
              <DollarSign size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="number"
                step="0.01"
                min="0"
                placeholder="45.00"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                required
                className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:bg-white focus:border-emerald-500"
              />
            </div>
          </div>

          {/* Status (If editing) */}
          {editId && (
            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-700">Listing Status</label>
              <select
                value={status}
                onChange={(e) => setStatus(e.target.value as any)}
                className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:bg-white focus:border-emerald-500"
              >
                <option value="ACTIVE">ACTIVE (Available for buyers)</option>
                <option value="RESERVED">RESERVED (Pending deal)</option>
                <option value="SOLD">SOLD (Completed deal)</option>
              </select>
            </div>
          )}

          {/* Description */}
          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-700">Description *</label>
            <textarea
              rows={4}
              placeholder="Describe the item condition, edition, included accessories, or preferred campus pickup location..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              required
              maxLength={2000}
              className="w-full p-4 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:bg-white focus:border-emerald-500"
            />
          </div>

          {/* Image URLs */}
          <div className="space-y-3">
            <label className="text-xs font-bold text-slate-700">Image URLs (Optional, max 5)</label>
            <div className="flex gap-2">
              <input
                type="url"
                placeholder="https://images.unsplash.com/photo-..."
                value={imageUrlInput}
                onChange={(e) => setImageUrlInput(e.target.value)}
                className="flex-1 px-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs"
              />
              <button
                type="button"
                onClick={handleAddImage}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-900 text-white font-bold text-xs rounded-xl"
              >
                Add URL
              </button>
            </div>

            {images.length > 0 && (
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
                {images.map((url, index) => (
                  <div key={index} className="relative group aspect-square rounded-xl overflow-hidden border border-slate-200 bg-slate-100">
                    <img src={url} alt={`Preview ${index}`} className="w-full h-full object-cover" />
                    <button
                      type="button"
                      onClick={() => handleRemoveImage(index)}
                      className="absolute top-1.5 right-1.5 p-1 bg-rose-600 text-white rounded-full opacity-90 hover:opacity-100 transition-opacity"
                    >
                      <Trash2 size={12} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-4 bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-base rounded-2xl shadow-lg transition-all flex items-center justify-center gap-2"
          >
            {loading ? 'Saving Listing...' : editId ? 'Update Listing' : 'Publish Campus Listing'}{' '}
            <CheckCircle2 size={18} />
          </button>
        </form>
      </div>
    </div>
  );
};
