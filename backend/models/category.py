import datetime


class CategoryModel:
    @staticmethod
    def collection():
        import backend.db
        return backend.db.get_db().categories

    @staticmethod
    def get_all_active():
        """Retrieve all active categories."""
        categories = list(CategoryModel.collection().find({'is_active': True}).sort('name', 1))
        # Convert ObjectId to string for JSON serialization
        for category in categories:
            category['_id'] = str(category['_id'])
        return categories

    @staticmethod
    def get_by_slug(slug):
        """Retrieve a category by its slug."""
        category = CategoryModel.collection().find_one({'slug': slug})
        if category:
            category['_id'] = str(category['_id'])
        return category

    @staticmethod
    def is_valid(slug):
        """Check if a category slug exists and is active."""
        return CategoryModel.collection().count_documents({'slug': slug, 'is_active': True}) > 0
