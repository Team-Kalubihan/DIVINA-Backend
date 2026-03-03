"""
Recommendation routes
    GET /api/recommend/sites?lat=<float>&lng=<float>   - get ranked dive sites
    GET /api/recommend/shops?lat=<float>&lng=<float>   - get ranked dive shops
"""
import os
from flask import Blueprint, request, jsonify
from divina_recommender.engine import RecommenderEngine

from app.models.dive_site import DiveSite
from app.models.store import Store
from app.utils.jwt_helper import jwt_required
from app.utils.recommender_service import build_recommender_sites, build_recommender_shops

recommend_bp = Blueprint("recommend", __name__)


def _parse_coords():
    lat = request.args.get("lat")
    lng = request.args.get("lng")
    if lat is None or lng is None:
        return None, None, jsonify({"error": "lat and lng query parameters are required"}), 400
    try:
        return float(lat), float(lng), None, None
    except (ValueError, TypeError):
        return None, None, jsonify({"error": "Invalid lat or lng values"}), 400


@recommend_bp.route("/recommend/sites", methods=["GET"])
@jwt_required
def recommend_sites():
    user = request.current_user
    prefs = user.dive_preferences
    if not prefs:
        return jsonify({"error": "Set your dive preferences first via PUT /api/profile/preferences"}), 400

    lat, lng, err, code = _parse_coords()
    if err:
        return err, code

    db_sites = DiveSite.query.filter_by(is_active=True).all()
    if not db_sites:
        return jsonify({"recommendations": [], "total": 0}), 200

    api_key = os.getenv("FREE_WEATHER_API_KEY")
    rec_sites = build_recommender_sites(db_sites, lat, lng, api_key)
    rec_user = prefs.to_recommender_obj()

    engine = RecommenderEngine()
    results = engine.recommend(rec_sites, rec_user)

    return jsonify({"total": len(results), "recommendations": results}), 200


@recommend_bp.route("/recommend/shops", methods=["GET"])
@jwt_required
def recommend_shops():
    user = request.current_user
    prefs = user.dive_preferences
    if not prefs:
        return jsonify({"error": "Set your dive preferences first via PUT /api/profile/preferences"}), 400

    lat, lng, err, code = _parse_coords()
    if err:
        return err, code

    db_sites = DiveSite.query.filter_by(is_active=True).all()
    stores = Store.query.filter(
        Store.is_active == True,
        Store.latitude != None,
        Store.longitude != None,
    ).all()

    if not stores:
        return jsonify({"recommendations": [], "total": 0}), 200

    api_key = os.getenv("FREE_WEATHER_API_KEY")
    rec_sites = build_recommender_sites(db_sites, lat, lng, api_key)
    rec_shops = build_recommender_shops(stores, lat, lng)
    rec_user = prefs.to_recommender_obj()

    engine = RecommenderEngine()
    results = engine.recommend_shops(rec_shops, rec_user, rec_sites)

    return jsonify({"total": len(results), "recommendations": results}), 200
