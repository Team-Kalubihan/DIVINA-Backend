# DIVINA Backend — Implementation Guide

This guide walks you through setting up and integrating the DIVINA Backend API into your project.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Installation](#2-installation)
3. [Configuration](#3-configuration)
4. [Running the Server](#4-running-the-server)
5. [Integrating Authentication](#5-integrating-authentication)
6. [Working with Stores & Bookings](#6-working-with-stores--bookings)
7. [Using the Weather API](#7-using-the-weather-api)
8. [Using Species Identification](#8-using-species-identification)
9. [Frontend Integration Examples](#9-frontend-integration-examples)
10. [Deployment](#10-deployment)

---

## 1. Prerequisites

- **Python** ≥ 3.12
- **uv** — fast Python package manager ([install guide](https://docs.astral.sh/uv/getting-started/installation/))
- **Git**
- A free API key from [WeatherAPI.com](https://www.weatherapi.com/signup.aspx)

---

## 2. Installation

```bash
# Clone the repository
git clone https://github.com/Team-Kalubihan/DIVINA-Backend.git
cd DIVINA-Backend

# Install all dependencies with uv
uv sync
```

This installs Flask, SQLAlchemy, the DIVINA Classifier model, and all other dependencies defined in `pyproject.toml`.

---

## 3. Configuration

Create a `.env` file in the project root:

```env
# Flask
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# JWT
JWT_SECRET_KEY=your-jwt-secret-here
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=604800

# Database
DATABASE_URL=sqlite:///app.db

# Weather API (https://www.weatherapi.com)
FREE_WEATHER_API_KEY=your-weatherapi-key-here
```

### Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FLASK_ENV` | ❌ | `development` | `development` or `production` |
| `SECRET_KEY` | ✅ | `dev-secret-key` | Flask secret key |
| `JWT_SECRET_KEY` | ✅ | `dev-jwt-secret` | JWT signing key |
| `JWT_ACCESS_TOKEN_EXPIRES` | ❌ | `3600` | Access token TTL in seconds (1 hour) |
| `JWT_REFRESH_TOKEN_EXPIRES` | ❌ | `604800` | Refresh token TTL in seconds (7 days) |
| `DATABASE_URL` | ❌ | `sqlite:///app.db` | SQLAlchemy database URI |
| `FREE_WEATHER_API_KEY` | ✅ | — | WeatherAPI.com API key |

---

## 4. Running the Server

```bash
# Using uv
uv run python run.py

# Or activate the venv and run directly
source .venv/bin/activate
python run.py
```

The server starts at `http://localhost:5000`. The SQLite database and tables are created automatically on first run.

### Verify It's Running

```bash
curl http://localhost:5000/api/weather/current?q=Cebu
```

---

## 5. Integrating Authentication

The API uses JWT (JSON Web Tokens) for authentication. The flow is:

### Step 1 — Register a User

```bash
curl -X POST http://localhost:5000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "password": "secret123",
    "is_dive_operator": false
  }'
```

The response includes `access_token` and `refresh_token`.

### Step 2 — Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "secret123"
  }'
```

### Step 3 — Use the Access Token

Pass the token in the `Authorization` header for protected routes:

```bash
curl http://localhost:5000/api/profile \
  -H "Authorization: Bearer eyJ..."
```

### Step 4 — Refresh When Expired

Access tokens expire after 1 hour by default. Use the refresh token to get a new pair:

```bash
curl -X POST http://localhost:5000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "eyJ..."}'
```

### Dive Operator Registration

Dive operators must upload verification documents during signup using multipart form data:

```bash
curl -X POST http://localhost:5000/api/auth/signup \
  -F "first_name=Maria" \
  -F "last_name=Santos" \
  -F "email=maria@blueseadivers.com" \
  -F "password=secret123" \
  -F "is_dive_operator=true" \
  -F "bir_document=@/path/to/bir.pdf" \
  -F "certification_document=@/path/to/cert.pdf"
```

An admin must then approve the operator before they can create stores.

---

## 6. Working with Stores & Bookings

### Creating a Store (Dive Operator)

After an operator is approved by an admin:

```bash
curl -X POST http://localhost:5000/api/stores \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Blue Sea Divers",
    "description": "PADI certified dive center",
    "contact_number": "+63-912-345-6789",
    "address": "Mactan, Cebu",
    "latitude": 10.3157,
    "longitude": 123.9750
  }'
```

### Adding a Dive Schedule

```bash
curl -X POST http://localhost:5000/api/stores/1/schedules \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Morning Reef Dive",
    "description": "Explore the coral reef",
    "date": "2025-07-15",
    "start_time": "08:00",
    "end_time": "11:00",
    "price": 1500.00,
    "max_slots": 10
  }'
```

### Booking a Dive (Regular User)

```bash
curl -X POST http://localhost:5000/api/bookings \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{
    "schedule_id": 1,
    "slots": 2,
    "notes": "First time diving!",
    "coupon_code": "SUMMER2025"
  }'
```

### Browsing Stores (No Auth Required)

```bash
# List all stores
curl http://localhost:5000/api/stores

# Get stores for map view
curl http://localhost:5000/api/stores/map

# Get store details with schedules
curl http://localhost:5000/api/stores/1
```

---

## 7. Using the Weather API

Weather endpoints are public (no authentication needed) and powered by [WeatherAPI.com](https://www.weatherapi.com/). Make sure `FREE_WEATHER_API_KEY` is set in your `.env`.

### Current Weather

```bash
# By city name
curl "http://localhost:5000/api/weather/current?q=Cebu"

# By coordinates
curl "http://localhost:5000/api/weather/current?q=10.3157,123.9750"
```

### Marine Weather (for Dive Planning)

The marine endpoint returns wave height, swell data, water temperature, and tide information — critical data for safe dive planning.

```bash
# 1-day marine forecast with tides
curl "http://localhost:5000/api/weather/marine?q=Cebu&days=1&tides=yes"

# 3-day forecast without tides
curl "http://localhost:5000/api/weather/marine?q=Cebu&days=3&tides=no"
```

**Key marine data points for dive planning:**

| Field | What It Tells You |
|-------|-------------------|
| `water_temp_c` | Water temperature — wetsuit selection |
| `sig_ht_mt` | Significant wave height — surface conditions |
| `swell_ht_mt` | Swell height — underwater current indicator |
| `swell_period_secs` | Swell period — longer = calmer conditions |
| `vis_km` | Visibility — relates to underwater visibility |
| `tides` | Tide times & heights — affects dive site access and currents |

---

## 8. Using Species Identification

The `/api/identify` endpoint lets users photograph marine life and get species information. It uses a VGG16 model for classification and queries iNaturalist for species data.

### Identify a Species

```bash
curl -X POST http://localhost:5000/api/identify \
  -F "image=@clownfish.jpg"
```

**Successful response:**

```json
{
  "classification": {
    "class_id": 42,
    "label": "clownfish",
    "confidence": 0.92
  },
  "species": {
    "id": 48313,
    "name": "Amphiprioninae",
    "common_name": "Clownfishes",
    "rank": "subfamily",
    "observations_count": 45230,
    "wikipedia_url": "http://en.wikipedia.org/wiki/Clownfish",
    "photo_url": "https://inaturalist-open-data.s3.amazonaws.com/photos/12345/medium.jpg",
    "iconic_taxon_name": "Actinopterygii"
  }
}
```

**Supported image formats:** JPG, JPEG, PNG, WEBP

**Tips for best results:**
- Use clear, well-lit photos
- Center the subject in the frame
- Avoid heavily cropped or blurry images
- The model returns `"Unknown"` if confidence is below the threshold

---

## 9. Frontend Integration Examples

### JavaScript (Fetch API)

#### Authentication

```javascript
// Login
const loginResponse = await fetch('http://localhost:5000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'john@example.com',
    password: 'secret123'
  })
});
const { access_token, refresh_token } = await loginResponse.json();

// Authenticated request
const profile = await fetch('http://localhost:5000/api/profile', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
```

#### Weather

```javascript
const weather = await fetch(
  'http://localhost:5000/api/weather/current?q=Cebu'
);
const data = await weather.json();
console.log(`Temperature: ${data.current.temp_c}°C`);
console.log(`Condition: ${data.current.condition.text}`);
```

#### Marine Weather

```javascript
const marine = await fetch(
  'http://localhost:5000/api/weather/marine?q=Cebu&days=3&tides=yes'
);
const data = await marine.json();

data.forecast.forecastday.forEach(day => {
  console.log(`Date: ${day.date}`);
  console.log(`Water temp: ${day.hour[0].water_temp_c}°C`);
  console.log(`Wave height: ${day.hour[0].sig_ht_mt}m`);
});
```

#### Species Identification

```javascript
const formData = new FormData();
formData.append('image', fileInput.files[0]);

const result = await fetch('http://localhost:5000/api/identify', {
  method: 'POST',
  body: formData
});
const data = await result.json();

if (data.species) {
  console.log(`Species: ${data.species.common_name}`);
  console.log(`Scientific name: ${data.species.name}`);
  console.log(`Confidence: ${(data.classification.confidence * 100).toFixed(1)}%`);
} else {
  console.log('Could not identify species');
}
```

### Python (requests)

```python
import requests

BASE_URL = "http://localhost:5000/api"

# Login
session_data = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "john@example.com",
    "password": "secret123"
}).json()
token = session_data["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Get weather
weather = requests.get(f"{BASE_URL}/weather/current", params={"q": "Cebu"}).json()
print(f"Temperature: {weather['current']['temp_c']}°C")

# Get marine weather
marine = requests.get(f"{BASE_URL}/weather/marine", params={
    "q": "Cebu", "days": 3, "tides": "yes"
}).json()

# Identify species
with open("clownfish.jpg", "rb") as f:
    result = requests.post(f"{BASE_URL}/identify", files={"image": f}).json()
print(f"Species: {result['species']['common_name']}")

# Book a dive
booking = requests.post(f"{BASE_URL}/bookings", headers=headers, json={
    "schedule_id": 1,
    "slots": 2
}).json()
```

---

## 10. Deployment

### Production Environment

1. Set environment to production:

   ```env
   FLASK_ENV=production
   ```

2. Use strong, unique values for `SECRET_KEY` and `JWT_SECRET_KEY`.

3. For production databases, update `DATABASE_URL`:

   ```env
   DATABASE_URL=postgresql://user:pass@host:5432/divina
   ```

4. Run with a production WSGI server:

   ```bash
   uv add gunicorn
   uv run gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app('production')"
   ```

### Notes

- The VGG16 model weights are downloaded automatically on first run (~528 MB).
- The SQLite database is created at `instance/app.db` on first startup.
- File uploads (dive operator documents) are stored in the `uploads/` directory.
- The iNaturalist API is rate-limited to 60 requests/minute — the identify endpoint makes 1 request per call.
- WeatherAPI.com free tier allows up to 1,000,000 calls/month.
- The recommendation engine fetches live marine weather for each dive site at request time, so recommendation calls may take a few seconds depending on the number of sites.
