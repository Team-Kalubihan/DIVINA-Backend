import math
import os
import requests as http_requests

from divina_recommender.models import DiveSite as RecDiveSite, DiveShop as RecDiveShop


WEATHER_API_BASE = "https://api.weatherapi.com/v1"


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lng / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def fetch_weather_for_site(lat: float, lng: float, api_key: str | None) -> dict:
    """Fetch marine weather for coordinates. Returns defaults on failure."""
    defaults = {
        "water_visibility": 10.0,
        "wave_height": 1.0,
        "current_speed": 0.5,
        "wind_speed": 10.0,
        "water_temperature": 20.0,
        "rain_probability": 0.0,
    }
    if not api_key:
        return defaults
    try:
        resp = http_requests.get(
            f"{WEATHER_API_BASE}/marine.json",
            params={"key": api_key, "q": f"{lat},{lng}", "days": 1},
            timeout=10,
        )
        if resp.status_code != 200:
            return defaults
        data = resp.json()
        hour = data["forecast"]["forecastday"][0]["hour"][0]
        current = data.get("current", {})
        return {
            "water_visibility": float(hour.get("vis_km", defaults["water_visibility"])),
            "wave_height": float(hour.get("sig_ht_mt", defaults["wave_height"])),
            "current_speed": float(hour.get("swell_ht_mt", defaults["current_speed"])),
            "wind_speed": float(current.get("wind_kph", defaults["wind_speed"])),
            "water_temperature": float(hour.get("water_temp_c", defaults["water_temperature"])),
            "rain_probability": float(hour.get("chance_of_rain", 0)) / 100.0,
        }
    except Exception:
        return defaults


def build_recommender_sites(db_sites, user_lat: float, user_lng: float, api_key: str | None) -> list[RecDiveSite]:
    """Convert DB DiveSite rows into recommender DiveSite objects with live weather."""
    rec_sites = []
    for site in db_sites:
        weather = fetch_weather_for_site(site.latitude, site.longitude, api_key)
        distance = haversine_km(user_lat, user_lng, site.latitude, site.longitude)
        rec_dict = site.to_recommender_dict(weather, distance)
        rec_sites.append(RecDiveSite.from_dict(rec_dict))
    return rec_sites


def build_recommender_shops(stores, user_lat: float, user_lng: float) -> list[RecDiveShop]:
    """Convert DB Store rows into recommender DiveShop objects."""
    rec_shops = []
    for store in stores:
        distance = haversine_km(user_lat, user_lng, store.latitude, store.longitude) if store.latitude and store.longitude else 50.0
        rec_shops.append(RecDiveShop.from_dict({
            "id": str(store.id),
            "name": store.name,
            "rating": store.rating or 4.0,
            "price_level": store.price_level or 2,
            "has_rental": store.has_rental,
            "has_nitrox": store.has_nitrox,
            "has_training": store.has_training,
            "is_tech_friendly": store.is_tech_friendly,
            "dive_sites": [str(s.id) for s in store.dive_sites],
            "distance_km": distance,
        }))
    return rec_shops
