import datetime
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from backend.db import get_db

class UserModel:
    @staticmethod
    def collection():
        return get_db().users

    @staticmethod
    def create_user(name, email, plain_password, allowed_domains):
        """
        Creates a new user with hashed password.
        Returns the user ID or None if email already exists.
        """
        email = email.lower().strip()
        
        # Check for duplicates
        if UserModel.collection().find_one({'email': email}):
            return None
            
        password_hash = generate_password_hash(plain_password)
        
        # Student-focused verification foundation
        domain = email.split('@')[-1]
        verification_status = 'VERIFIED' if domain in allowed_domains else 'UNVERIFIED'
        
        user_doc = {
            'name': name,
            'email': email,
            'password_hash': password_hash,
            'role': 'student', # Never self-selectable admin
            'department': None,
            'verification_status': verification_status,
            'account_status': 'ACTIVE',
            'profile': {},
            'created_at': datetime.datetime.now(datetime.timezone.utc),
            'updated_at': datetime.datetime.now(datetime.timezone.utc)
        }
        
        result = UserModel.collection().insert_one(user_doc)
        return str(result.inserted_id)

    @staticmethod
    def get_by_email(email):
        """Retrieve a user by email."""
        return UserModel.collection().find_one({'email': email.lower().strip()})

    @staticmethod
    def get_by_id(user_id):
        """Retrieve a user by their string ID."""
        try:
            return UserModel.collection().find_one({'_id': ObjectId(user_id)})
        except:
            return None

    @staticmethod
    def verify_password(password_hash, plain_password):
        """Verify the password hash."""
        return check_password_hash(password_hash, plain_password)

    @staticmethod
    def update_profile(user_id, updates):
        """
        Update safe profile fields for a user.
        """
        try:
            UserModel.collection().update_one(
                {'_id': ObjectId(user_id)},
                {
                    '$set': {
                        **updates,
                        'updated_at': datetime.datetime.now(datetime.timezone.utc)
                    }
                }
            )
            return True
        except Exception:
            return False
        
    @staticmethod
    def setup_indexes():
        """Creates the necessary indexes for the users collection."""
        collection = UserModel.collection()
        collection.create_index('email', unique=True, sparse=True)
        collection.create_index('role')
        collection.create_index('account_status')

    @staticmethod
    def sanitize_user(user):
        """Removes sensitive fields like password_hash from user dictionary."""
        if not user:
            return None
        user_copy = dict(user)
        user_copy['_id'] = str(user_copy['_id'])
        user_copy.pop('password_hash', None)
        return user_copy

    @staticmethod
    def get_all(page=1, limit=20, role=None, account_status=None):
        """Retrieve paginated users for admin management."""
        filters = {}
        if role:
            filters['role'] = role
        if account_status:
            filters['account_status'] = account_status

        skip = (page - 1) * limit
        collection = UserModel.collection()
        cursor = collection.find(filters).sort('created_at', -1).skip(skip).limit(limit)
        items = [UserModel.sanitize_user(u) for u in cursor]
        total = collection.count_documents(filters)

        return {
            'items': items,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit if total > 0 else 1
            }
        }

    @staticmethod
    def update_status(user_id, status):
        """Update account status of a user (e.g. ACTIVE, SUSPENDED)."""
        try:
            result = UserModel.collection().update_one(
                {'_id': ObjectId(user_id)},
                {
                    '$set': {
                        'account_status': status,
                        'updated_at': datetime.datetime.now(datetime.timezone.utc)
                    }
                }
            )
            return result.modified_count > 0 or result.matched_count > 0
        except Exception:
            return False

    @staticmethod
    def update_role(user_id, role):
        """Update role of a user (e.g. student, admin)."""
        try:
            result = UserModel.collection().update_one(
                {'_id': ObjectId(user_id)},
                {
                    '$set': {
                        'role': role,
                        'updated_at': datetime.datetime.now(datetime.timezone.utc)
                    }
                }
            )
            return result.modified_count > 0 or result.matched_count > 0
        except Exception:
            return False

