// TypeScript Interfaces for SecondSpin Web Application API Integration

export interface User {
  _id: string;
  name: string;
  email: string;
  role: 'student' | 'admin';
  department?: string | null;
  verification_status: 'VERIFIED' | 'UNVERIFIED';
  account_status: 'ACTIVE' | 'SUSPENDED';
  profile?: Record<string, any>;
  created_at?: string;
  updated_at?: string;
}

export interface SellerInfo {
  id: string;
  name: string;
  department?: string | null;
}

export interface Product {
  _id: string;
  title: string;
  description: string;
  price: number;
  category_id: string;
  condition: 'NEW' | 'LIKE_NEW' | 'GOOD' | 'FAIR' | 'POOR';
  images?: string[];
  attributes?: Record<string, any>;
  status: 'ACTIVE' | 'RESERVED' | 'SOLD' | 'REMOVED';
  seller_id?: string;
  seller?: SellerInfo;
  created_at?: string;
  updated_at?: string;
}

export interface Category {
  _id: string;
  name: string;
  slug: string;
  description?: string;
  icon?: string;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface WishlistItem {
  _id: string;
  user_id: string;
  product_id: string;
  created_at: string;
  product?: Product;
}

export interface PurchaseRequest {
  _id: string;
  product_id: string;
  buyer_id: string;
  seller_id: string;
  message?: string;
  status: 'PENDING' | 'ACCEPTED' | 'REJECTED' | 'CANCELLED';
  created_at: string;
  updated_at: string;
  responded_at?: string | null;
  cancelled_at?: string | null;
  product?: Product;
  buyer?: User;
  seller?: User;
}

export interface Transaction {
  _id: string;
  purchase_request_id: string;
  product_id: string;
  buyer_id: string;
  seller_id: string;
  status: 'PENDING' | 'RESERVED' | 'COMPLETED' | 'CANCELLED';
  created_at: string;
  updated_at: string;
  completed_at?: string | null;
  cancelled_at?: string | null;
  product?: Product;
  buyer?: User;
  seller?: User;
}

export interface Review {
  _id: string;
  transaction_id: string;
  reviewer_id: string;
  reviewee_id: string;
  product_id: string;
  rating: number;
  comment?: string;
  created_at: string;
  reviewer?: User;
  reviewee?: User;
  product?: Product;
}

export interface Report {
  _id: string;
  reporter_id: string;
  target_type: 'PRODUCT' | 'USER';
  target_id: string;
  reason: string;
  description?: string;
  status: 'OPEN' | 'REVIEWING' | 'RESOLVED' | 'DISMISSED';
  created_at: string;
  updated_at: string;
  resolved_at?: string | null;
  resolved_by?: string | null;
}

export interface RecommendedItem {
  product: Product;
  score?: number;
  popularity_score?: number;
  reason: string;
}

export interface CategoryDemandItem {
  category: Category;
  demand_score: number;
  active_listings: number;
  reason: string;
}

export interface PriceInsights {
  product_id: string;
  current_price: number;
  historical_average: number | null;
  min_price: number | null;
  max_price: number | null;
  comparable_count: number;
  insufficient_data: boolean;
  price_comparison: string;
}

export interface AnalyticsOverview {
  users: {
    total: number;
    active: number;
    suspended: number;
    students: number;
    admins: number;
  };
  products: {
    total: number;
    active: number;
    reserved: number;
    sold: number;
    removed: number;
  };
  transactions: {
    total: number;
    pending: number;
    reserved: number;
    completed: number;
    cancelled: number;
  };
  purchase_requests: {
    total: number;
    pending: number;
    accepted: number;
    rejected: number;
    cancelled: number;
  };
  reviews: {
    total: number;
    average_rating: number;
  };
  reports: {
    total: number;
    open: number;
  };
  categories: {
    category_id: string;
    name: string;
    product_count: number;
  }[];
}

export interface PaginationMeta {
  page: number;
  limit: number;
  total: number;
  pages: number;
}

export interface PaginatedResult<T> {
  items: T[];
  pagination?: PaginationMeta;
  count?: number;
}
