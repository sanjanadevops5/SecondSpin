import 'package:flutter_test/flutter_test.dart';
import 'package:secondspin_mobile/models/user_model.dart';
import 'package:secondspin_mobile/models/product_model.dart';
import 'package:secondspin_mobile/models/category_model.dart';
import 'package:secondspin_mobile/models/purchase_request_model.dart';
import 'package:secondspin_mobile/models/transaction_model.dart';
import 'package:secondspin_mobile/models/review_model.dart';
import 'package:secondspin_mobile/models/smart_models.dart';

void main() {
  group('SecondSpin Mobile Models & Deserialization Tests', () {
    test('UserModel.fromJson parses complete user JSON correctly', () {
      final json = {
        '_id': 'usr_123',
        'name': 'Alex Student',
        'email': 'alex@univ.edu',
        'role': 'student',
        'department': 'Computer Science',
        'verification_status': 'VERIFIED',
        'account_status': 'ACTIVE',
      };

      final user = UserModel.fromJson(json);

      expect(user.id, 'usr_123');
      expect(user.name, 'Alex Student');
      expect(user.email, 'alex@univ.edu');
      expect(user.role, 'student');
      expect(user.department, 'Computer Science');
      expect(user.verificationStatus, 'VERIFIED');
      expect(user.accountStatus, 'ACTIVE');
    });

    test('ProductModel.fromJson parses product with seller object correctly', () {
      final json = {
        '_id': 'prod_999',
        'title': 'TI-84 Plus Calculator',
        'description': 'Graphing calculator in great shape.',
        'price': 45.50,
        'category_id': 'calculators',
        'condition': 'GOOD',
        'images': ['https://example.com/calc.jpg'],
        'status': 'ACTIVE',
        'seller': {
          'id': 'usr_123',
          'name': 'Alex Student',
          'department': 'Math',
        },
      };

      final product = ProductModel.fromJson(json);

      expect(product.id, 'prod_999');
      expect(product.title, 'TI-84 Plus Calculator');
      expect(product.price, 45.50);
      expect(product.categoryId, 'calculators');
      expect(product.condition, 'GOOD');
      expect(product.images.length, 1);
      expect(product.seller?.name, 'Alex Student');
      expect(product.seller?.department, 'Math');
    });

    test('CategoryModel.fromJson parses category item correctly', () {
      final json = {
        '_id': 'cat_1',
        'name': 'Textbooks',
        'slug': 'textbooks',
        'description': 'Course textbooks',
        'is_active': true,
      };

      final cat = CategoryModel.fromJson(json);
      expect(cat.name, 'Textbooks');
      expect(cat.slug, 'textbooks');
      expect(cat.isActive, isTrue);
    });

    test('PurchaseRequestModel.fromJson parses buyer and seller nested fields', () {
      final json = {
        '_id': 'req_001',
        'product_id': 'prod_999',
        'buyer_id': 'usr_buyer',
        'seller_id': 'usr_seller',
        'message': 'Can meet at the student union?',
        'status': 'PENDING',
        'created_at': '2026-09-03T10:00:00Z',
      };

      final req = PurchaseRequestModel.fromJson(json);

      expect(req.id, 'req_001');
      expect(req.productId, 'prod_999');
      expect(req.buyerId, 'usr_buyer');
      expect(req.status, 'PENDING');
      expect(req.message, 'Can meet at the student union?');
    });

    test('TransactionModel.fromJson handles status lifecycle states', () {
      final json = {
        '_id': 'tx_777',
        'purchase_request_id': 'req_001',
        'product_id': 'prod_999',
        'buyer_id': 'usr_buyer',
        'seller_id': 'usr_seller',
        'status': 'RESERVED',
        'created_at': '2026-09-03T10:05:00Z',
      };

      final tx = TransactionModel.fromJson(json);

      expect(tx.id, 'tx_777');
      expect(tx.status, 'RESERVED');
      expect(tx.productId, 'prod_999');
    });

    test('ReviewModel.fromJson handles rating validation', () {
      final json = {
        '_id': 'rev_01',
        'transaction_id': 'tx_777',
        'reviewer_id': 'usr_buyer',
        'reviewee_id': 'usr_seller',
        'product_id': 'prod_999',
        'rating': 5,
        'comment': 'Prompt and friendly student seller!',
        'created_at': '2026-09-03T11:00:00Z',
      };

      final rev = ReviewModel.fromJson(json);

      expect(rev.rating, 5);
      expect(rev.comment, 'Prompt and friendly student seller!');
    });

    test('PriceInsightsModel.fromJson handles insufficient data fallback', () {
      final json = {
        'product_id': 'prod_123',
        'current_price': 50.00,
        'comparable_count': 0,
        'insufficient_data': true,
        'price_comparison': 'Not enough historical data for this category yet.',
      };

      final insights = PriceInsightsModel.fromJson(json);

      expect(insights.insufficientData, isTrue);
      expect(insights.priceComparison, contains('Not enough historical data'));
    });

    test('AnalyticsOverviewModel.fromJson parses platform totals', () {
      final json = {
        'users': {'total': 25, 'active': 25},
        'products': {'total': 50, 'active': 40},
        'transactions': {'total': 15, 'completed': 10},
        'purchase_requests': {'total': 20},
        'reviews': {'average_rating': 4.8},
        'reports': {'open': 2},
      };

      final stats = AnalyticsOverviewModel.fromJson(json);

      expect(stats.totalUsers, 25);
      expect(stats.activeProducts, 40);
      expect(stats.completedTransactions, 10);
      expect(stats.averageRating, 4.8);
      expect(stats.openReports, 2);
    });
  });
}
