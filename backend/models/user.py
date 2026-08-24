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
            'created_at': datetime.datetime.utcnow(),
            'updated_at': datetime.datetime.utcnow()
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
                        'updated_at': datetime.datetime.utcnow()
                    }
                }
            )
            return True
        except:
            return False
