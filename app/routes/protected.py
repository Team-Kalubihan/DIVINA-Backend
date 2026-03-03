from flask import Blueprint, request, jsonify
from app import db
from app.models.user import User, VerificationStatus
from app.models.user_preferences import UserDivePreferences
from app.utils.jwt_helper import jwt_required

protected_bp = Blueprint("protected", __name__)


def dive_operator_approved(f):
    """Decorator that requires the user to be an approved dive operator."""
    from functools import wraps
    @wraps(f)
    @jwt_required
    def decorated(*args, **kwargs):
        user = request.current_user
        if not user.is_dive_operator:
            return jsonify({"error": "Dive operator access required"}), 403
        if not user.is_approved:
            return jsonify({
                "error": "Your dive operator account has not been approved yet.",
                "verification_status": user.verification_status,
            }), 403
        return f(*args, **kwargs)
    return decorated


@protected_bp.route("/profile", methods=["GET"])
@jwt_required
def get_profile():
    return jsonify({"profile": request.current_user.to_dict()}), 200


@protected_bp.route("/profile", methods=["PUT"])
@jwt_required
def update_profile():
    data = request.get_json() or {}
    user = request.current_user

    new_first_name = (data.get("first_name") or "").strip()
    new_last_name  = (data.get("last_name")  or "").strip()
    new_email      = (data.get("email")      or "").strip().lower()

    if new_first_name:
        if len(new_first_name) < 2:
            return jsonify({"error": "First name must be at least 2 characters"}), 400
        user.first_name = new_first_name

    if new_last_name:
        if len(new_last_name) < 2:
            return jsonify({"error": "Last name must be at least 2 characters"}), 400
        user.last_name = new_last_name

    if new_email and new_email != user.email:
        if "@" not in new_email:
            return jsonify({"error": "Invalid email address"}), 400
        if User.query.filter_by(email=new_email).first():
            return jsonify({"error": "Email already registered"}), 409
        user.email = new_email

    db.session.commit()
    return jsonify({"message": "Profile updated", "user": user.to_dict()}), 200


@protected_bp.route("/change-password", methods=["POST"])
@jwt_required
def change_password():
    data = request.get_json() or {}
    user = request.current_user
    current_password = data.get("current_password")
    new_password = data.get("new_password")

    if not current_password or not new_password:
        return jsonify({"error": "current_password and new_password are required"}), 400
    if not user.check_password(current_password):
        return jsonify({"error": "Current password is incorrect"}), 401
    if len(new_password) < 6:
        return jsonify({"error": "New password must be at least 6 characters"}), 400

    user.set_password(new_password)
    db.session.commit()
    return jsonify({"message": "Password changed successfully"}), 200


@protected_bp.route("/dashboard", methods=["GET"])
@jwt_required
def dashboard():
    user = request.current_user
    return jsonify({
        "message": f"Welcome, {user.full_name}!",  
        "user_id": user.id,
        "role": user.role,
    }), 200


@protected_bp.route("/operator/dashboard", methods=["GET"])
@dive_operator_approved
def operator_dashboard():
    user = request.current_user
    return jsonify({
        "message": f"Welcome, {user.full_name}!",  
        "verified_at": user.verified_at.isoformat() if user.verified_at else None,
        "documents": [doc.to_dict() for doc in user.documents],
    }), 200


# ---------------------------------------------------------------------------
# DIVE PREFERENCES
# ---------------------------------------------------------------------------

@protected_bp.route("/profile/preferences", methods=["GET"])
@jwt_required
def get_preferences():
    prefs = request.current_user.dive_preferences
    if not prefs:
        return jsonify({"error": "Dive preferences not set"}), 404
    return jsonify({"preferences": prefs.to_dict()}), 200


@protected_bp.route("/profile/preferences", methods=["PUT"])
@jwt_required
def update_preferences():
    user = request.current_user
    data = request.get_json() or {}

    prefs = user.dive_preferences
    if not prefs:
        prefs = UserDivePreferences(user_id=user.id)
        db.session.add(prefs)

    if "skill_level" in data:
        sl = int(data["skill_level"])
        if sl < 1 or sl > 5:
            return jsonify({"error": "skill_level must be 1–5"}), 400
        prefs.skill_level = sl
    if "preferred_marine_life" in data:
        ml = data["preferred_marine_life"]
        prefs.preferred_marine_life = ",".join(ml) if isinstance(ml, list) else str(ml)
    if "photography_priority" in data:
        pp = float(data["photography_priority"])
        if pp < 0 or pp > 10:
            return jsonify({"error": "photography_priority must be 0–10"}), 400
        prefs.photography_priority = pp
    if "depth_preference" in data:
        prefs.depth_preference = float(data["depth_preference"])
    if "max_travel_distance" in data:
        prefs.max_travel_distance = float(data["max_travel_distance"])
    if "requires_rental" in data:
        prefs.requires_rental = bool(data["requires_rental"])
    if "requires_nitrox" in data:
        prefs.requires_nitrox = bool(data["requires_nitrox"])
    if "requires_training" in data:
        prefs.requires_training = bool(data["requires_training"])
    if "is_tech_diver" in data:
        prefs.is_tech_diver = bool(data["is_tech_diver"])
    if "preferred_price_level" in data:
        pl = data["preferred_price_level"]
        if pl is not None:
            pl = int(pl)
            if pl < 1 or pl > 4:
                return jsonify({"error": "preferred_price_level must be 1–4"}), 400
        prefs.preferred_price_level = pl

    db.session.commit()
    return jsonify({"message": "Preferences updated", "preferences": prefs.to_dict()}), 200