import datetime
import pymongo


class CategoryModel:
    @staticmethod
    def collection():
        import backend.db
        return backend.db.get_db().categories

    @staticmethod
    def setup_indexes():
        """Creates the necessary indexes for the categories collection."""
        col = CategoryModel.collection()
        col.create_index('slug', unique=True)
        col.create_index('is_active')

    @staticmethod
    def get_all_active():
        """Retrieve all active categories."""
        categories = list(CategoryModel.collection().find({'is_active': True}).sort('name', 1))
        for category in categories:
            category['_id'] = str(category['_id'])
        return categories

    @staticmethod
    def get_all():
        """Retrieve all categories (active and inactive) for admin inspection."""
        categories = list(CategoryModel.collection().find().sort('name', 1))
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

    @staticmethod
    def create_category(name, slug, description='', icon=''):
        """Creates a new category document."""
        slug = slug.lower().strip()
        doc = {
            'name': name.strip(),
            'slug': slug,
            'description': description.strip(),
            'icon': icon.strip(),
            'is_active': True,
            'created_at': datetime.datetime.now(datetime.timezone.utc),
            'updated_at': datetime.datetime.now(datetime.timezone.utc),
        }
        try:
            result = CategoryModel.collection().insert_one(doc)
            return str(result.inserted_id)
        except pymongo.errors.DuplicateKeyError:
            return None

    @staticmethod
    def update_category(slug, updates):
        """Updates fields of an existing category by slug."""
        updates['updated_at'] = datetime.datetime.now(datetime.timezone.utc)
        result = CategoryModel.collection().update_one(
            {'slug': slug},
            {'$set': updates}
        )
        return result.modified_count > 0 or result.matched_count > 0
