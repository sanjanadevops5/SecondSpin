import datetime
from bson.objectid import ObjectId
import pymongo


class ReportModel:
    STATUSES = ['OPEN', 'REVIEWING', 'RESOLVED', 'DISMISSED']
    TARGET_TYPES = ['PRODUCT', 'USER']

    VALID_TRANSITIONS = {
        'OPEN': ['REVIEWING', 'RESOLVED', 'DISMISSED'],
        'REVIEWING': ['RESOLVED', 'DISMISSED'],
        'RESOLVED': [],
        'DISMISSED': [],
    }

    @staticmethod
    def collection():
        import backend.db
        return backend.db.get_db().reports

    @staticmethod
    def setup_indexes():
        """Creates the necessary indexes for the reports collection."""
        col = ReportModel.collection()
        col.create_index([('reporter_id', pymongo.ASCENDING), ('status', pymongo.ASCENDING)])
        col.create_index([('target_type', pymongo.ASCENDING), ('target_id', pymongo.ASCENDING)])
        col.create_index('status')
        col.create_index('created_at')

    @staticmethod
    def has_active_report(reporter_id, target_type, target_id):
        """Returns True if the reporter already has an OPEN or REVIEWING report for this target."""
        count = ReportModel.collection().count_documents({
            'reporter_id': reporter_id,
            'target_type': target_type,
            'target_id': target_id,
            'status': {'$in': ['OPEN', 'REVIEWING']}
        })
        return count > 0

    @staticmethod
    def create_report(reporter_id, target_type, target_id, reason, description=''):
        """Creates a new report document with status OPEN."""
        doc = {
            'reporter_id': reporter_id,
            'target_type': target_type,
            'target_id': target_id,
            'reason': reason.strip(),
            'description': description.strip(),
            'status': 'OPEN',
            'created_at': datetime.datetime.now(datetime.timezone.utc),
            'updated_at': datetime.datetime.now(datetime.timezone.utc),
            'resolved_at': None,
            'resolved_by': None,
        }
        result = ReportModel.collection().insert_one(doc)
        return str(result.inserted_id)

    @staticmethod
    def get_by_id(report_id):
        """Retrieves a report by string ID."""
        try:
            report = ReportModel.collection().find_one({'_id': ObjectId(report_id)})
            if report:
                report['_id'] = str(report['_id'])
            return report
        except Exception:
            return None

    @staticmethod
    def search_reports(status=None, target_type=None, page=1, limit=20):
        """Paginated report retrieval with status and target_type filters."""
        filters = {}
        if status:
            filters['status'] = status
        if target_type:
            filters['target_type'] = target_type

        skip = (page - 1) * limit
        col = ReportModel.collection()
        cursor = col.find(filters).sort('created_at', -1).skip(skip).limit(limit)
        items = list(cursor)
        for item in items:
            item['_id'] = str(item['_id'])
        total = col.count_documents(filters)

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
    def is_valid_transition(current_status, new_status):
        """Check if report status transition is allowed."""
        return new_status in ReportModel.VALID_TRANSITIONS.get(current_status, [])

    @staticmethod
    def update_status(report_id, new_status, admin_id=None):
        """Update report status and set resolution metadata if terminal."""
        now = datetime.datetime.now(datetime.timezone.utc)
        updates = {
            'status': new_status,
            'updated_at': now,
        }
        if new_status in ['RESOLVED', 'DISMISSED']:
            updates['resolved_at'] = now
            updates['resolved_by'] = admin_id

        try:
            result = ReportModel.collection().update_one(
                {'_id': ObjectId(report_id)},
                {'$set': updates}
            )
            return result.modified_count > 0 or result.matched_count > 0
        except Exception:
            return False
