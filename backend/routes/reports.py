"""
Reports Blueprint — User Reporting System (Phase 8)
Allows authenticated users to report listings or users for trust & safety.
"""
from flask import Blueprint, request, g

from backend.responses import success_response, error_response
from backend.validation import validate_json
from backend.auth_middleware import jwt_required
from backend.models.report import ReportModel
from backend.models.product import ProductModel
from backend.models.user import UserModel

reports_bp = Blueprint('reports', __name__)

MAX_DESCRIPTION_LENGTH = 1000


# ---------------------------------------------------------------------------
# POST /api/v1/reports/
# ---------------------------------------------------------------------------
@reports_bp.route('/', methods=['POST'])
@jwt_required
@validate_json(required_fields=['target_type', 'target_id', 'reason'])
def create_report():
    """
    Submit a new report for a product or user.
    Reporter ID is derived from authenticated user context (JWT).
    """
    data = request.get_json()
    target_type = str(data.get('target_type', '')).upper().strip()
    target_id = str(data.get('target_id', '')).strip()
    reason = str(data.get('reason', '')).strip()
    description = str(data.get('description', '')).strip()

    # --- Validate target type ---
    if target_type not in ReportModel.TARGET_TYPES:
        return error_response(
            code='INVALID_TARGET_TYPE',
            message=f"Target type must be one of: {', '.join(ReportModel.TARGET_TYPES)}.",
            status_code=400,
        )

    if not reason or len(reason) > 100:
        return error_response(
            code='INVALID_REASON',
            message='Reason must be non-empty and at most 100 characters.',
            status_code=400,
        )

    if len(description) > MAX_DESCRIPTION_LENGTH:
        return error_response(
            code='DESCRIPTION_TOO_LONG',
            message=f'Description must be at most {MAX_DESCRIPTION_LENGTH} characters.',
            status_code=400,
        )

    # --- Validate target existence ---
    if target_type == 'PRODUCT':
        product = ProductModel.get_by_id(target_id)
        if not product:
            return error_response(
                code='NOT_FOUND',
                message='Reported product does not exist.',
                status_code=404,
            )
    elif target_type == 'USER':
        user = UserModel.get_by_id(target_id)
        if not user:
            return error_response(
                code='NOT_FOUND',
                message='Reported user does not exist.',
                status_code=404,
            )

    reporter_id = g.user_id

    # --- Anti-spam: check for duplicate open/reviewing report ---
    if ReportModel.has_active_report(reporter_id, target_type, target_id):
        return error_response(
            code='DUPLICATE_REPORT',
            message='You already have an open report for this target.',
            status_code=409,
        )

    report_id = ReportModel.create_report(
        reporter_id=reporter_id,
        target_type=target_type,
        target_id=target_id,
        reason=reason,
        description=description,
    )

    return success_response(
        data={'report_id': report_id, 'message': 'Report submitted successfully.'},
        status_code=201,
    )


# ---------------------------------------------------------------------------
# GET /api/v1/reports/<report_id>
# ---------------------------------------------------------------------------
@reports_bp.route('/<report_id>', methods=['GET'])
@jwt_required
def get_report(report_id):
    """
    Retrieve report details.
    Accessible by the reporter or an admin.
    """
    report = ReportModel.get_by_id(report_id)
    if not report:
        return error_response(
            code='NOT_FOUND',
            message='Report not found.',
            status_code=404,
        )

    # Check authorization: reporter or admin
    if report['reporter_id'] != g.user_id and getattr(g, 'user_role', 'student') != 'admin':
        return error_response(
            code='FORBIDDEN',
            message='You do not have permission to view this report.',
            status_code=403,
        )

    return success_response(data=report)
