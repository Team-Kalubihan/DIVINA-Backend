"""
Dive Site routes
    GET    /api/dive-sites                          - list all active dive sites (public)
    GET    /api/dive-sites/<id>                     - get dive site detail (public)
    POST   /api/dive-sites                          - create dive site (admin only)
    PUT    /api/dive-sites/<id>                     - update dive site (admin only)
    DELETE /api/dive-sites/<id>                     - deactivate dive site (admin only)

Store ↔ Site association
    POST   /api/stores/<id>/dive-sites              - link site to store (owner or admin)
    DELETE /api/stores/<id>/dive-sites/<site_id>    - unlink site from store (owner or admin)
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models.dive_site import DiveSite
from app.models.store import Store
from app.models.user import UserRole
from app.utils.jwt_helper import jwt_required

dive_sites_bp = Blueprint("dive_sites", __name__)


def _require_admin(user):
    if user.role != UserRole.ADMIN:
        return jsonify({"error": "Admin access required"}), 403
    return None


# ---------------------------------------------------------------------------
# DIVE SITE CRUD
# ---------------------------------------------------------------------------

@dive_sites_bp.route("/dive-sites", methods=["GET"])
def list_dive_sites():
    sites = DiveSite.query.filter_by(is_active=True).order_by(DiveSite.name).all()
    return jsonify({"total": len(sites), "dive_sites": [s.to_dict() for s in sites]}), 200


@dive_sites_bp.route("/dive-sites/<int:site_id>", methods=["GET"])
def get_dive_site(site_id):
    site = DiveSite.query.get(site_id)
    if not site or not site.is_active:
        return jsonify({"error": "Dive site not found"}), 404
    return jsonify({"dive_site": site.to_dict()}), 200


@dive_sites_bp.route("/dive-sites", methods=["POST"])
@jwt_required
def create_dive_site():
    err = _require_admin(request.current_user)
    if err:
        return err

    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name is required"}), 400

    latitude = data.get("latitude")
    longitude = data.get("longitude")
    if latitude is None or longitude is None:
        return jsonify({"error": "latitude and longitude are required"}), 400
    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid latitude or longitude"}), 400

    site = DiveSite(
        name=name,
        latitude=latitude,
        longitude=longitude,
        marine_biodiversity=float(data.get("marine_biodiversity", 5.0)),
        difficulty=int(data.get("difficulty", 3)),
        photography_score=float(data.get("photography_score", 5.0)),
        max_depth=float(data.get("max_depth", 20.0)),
        marine_life=(data.get("marine_life") or "").strip() if isinstance(data.get("marine_life"), str) else ",".join(data.get("marine_life", [])),
        crowd_level=float(data.get("crowd_level", 0.5)),
    )
    db.session.add(site)
    db.session.commit()
    return jsonify({"message": f"Dive site '{name}' created", "dive_site": site.to_dict()}), 201


@dive_sites_bp.route("/dive-sites/<int:site_id>", methods=["PUT"])
@jwt_required
def update_dive_site(site_id):
    err = _require_admin(request.current_user)
    if err:
        return err

    site = DiveSite.query.get(site_id)
    if not site:
        return jsonify({"error": "Dive site not found"}), 404

    data = request.get_json() or {}
    if data.get("name"):
        site.name = data["name"].strip()
    if "latitude" in data:
        site.latitude = float(data["latitude"])
    if "longitude" in data:
        site.longitude = float(data["longitude"])
    if "marine_biodiversity" in data:
        site.marine_biodiversity = float(data["marine_biodiversity"])
    if "difficulty" in data:
        site.difficulty = int(data["difficulty"])
    if "photography_score" in data:
        site.photography_score = float(data["photography_score"])
    if "max_depth" in data:
        site.max_depth = float(data["max_depth"])
    if "marine_life" in data:
        ml = data["marine_life"]
        site.marine_life = ml.strip() if isinstance(ml, str) else ",".join(ml)
    if "crowd_level" in data:
        site.crowd_level = float(data["crowd_level"])

    db.session.commit()
    return jsonify({"message": "Dive site updated", "dive_site": site.to_dict()}), 200


@dive_sites_bp.route("/dive-sites/<int:site_id>", methods=["DELETE"])
@jwt_required
def deactivate_dive_site(site_id):
    err = _require_admin(request.current_user)
    if err:
        return err

    site = DiveSite.query.get(site_id)
    if not site:
        return jsonify({"error": "Dive site not found"}), 404

    site.is_active = False
    db.session.commit()
    return jsonify({"message": f"Dive site '{site.name}' deactivated"}), 200


# ---------------------------------------------------------------------------
# STORE ↔ SITE ASSOCIATION
# ---------------------------------------------------------------------------

def _is_store_owner_or_admin(user, store):
    return user.role == UserRole.ADMIN or store.owner_id == user.id


@dive_sites_bp.route("/stores/<int:store_id>/dive-sites", methods=["POST"])
@jwt_required
def link_site_to_store(store_id):
    user = request.current_user
    store = Store.query.get(store_id)
    if not store:
        return jsonify({"error": "Store not found"}), 404
    if not _is_store_owner_or_admin(user, store):
        return jsonify({"error": "Access denied"}), 403

    data = request.get_json() or {}
    site_id = data.get("dive_site_id")
    if not site_id:
        return jsonify({"error": "dive_site_id is required"}), 400

    site = DiveSite.query.get(site_id)
    if not site or not site.is_active:
        return jsonify({"error": "Dive site not found"}), 404

    if site in store.dive_sites:
        return jsonify({"error": "Site already linked to this store"}), 409

    store.dive_sites.append(site)
    db.session.commit()
    return jsonify({"message": f"Site '{site.name}' linked to store '{store.name}'"}), 201


@dive_sites_bp.route("/stores/<int:store_id>/dive-sites/<int:site_id>", methods=["DELETE"])
@jwt_required
def unlink_site_from_store(store_id, site_id):
    user = request.current_user
    store = Store.query.get(store_id)
    if not store:
        return jsonify({"error": "Store not found"}), 404
    if not _is_store_owner_or_admin(user, store):
        return jsonify({"error": "Access denied"}), 403

    site = DiveSite.query.get(site_id)
    if not site or site not in store.dive_sites:
        return jsonify({"error": "Site not linked to this store"}), 404

    store.dive_sites.remove(site)
    db.session.commit()
    return jsonify({"message": f"Site '{site.name}' unlinked from store '{store.name}'"}), 200
