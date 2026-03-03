# DIVINA Backend — API Reference

Base URL: `http://localhost:5000`

All endpoints are prefixed with `/api`. Authenticated routes require a JWT access token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

---

## Table of Contents

- [Authentication](#authentication)
- [User Profile](#user-profile)
- [Admin — Dive Operators](#admin--dive-operators)
- [Admin — Coupons](#admin--coupons)
- [Coupons](#coupons)
- [Stores](#stores)
- [Schedules](#schedules)
- [Bookings](#bookings)
- [Weather](#weather)
- [Species Identification](#species-identification)
- [Error Responses](#error-responses)

---

## Authentication

### POST `/api/auth/signup`

Register a new user. Dive operators must upload verification documents as multipart form data.

**Regular user (JSON):**

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "password": "secret123",
  "is_dive_operator": false
}
```

**Dive operator (multipart form):**

| Field | Type | Required |
|-------|------|----------|
| `first_name` | string | ✅ |
| `last_name` | string | ✅ |
| `email` | string | ✅ |
| `password` | string | ✅ |
| `is_dive_operator` | boolean | ✅ |
| `bir_document` | file | ✅ (operators) |
| `certification_document` | file | ✅ (operators) |

**Response** `201 Created`:

```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "role": "user"
  },
  "access_token": "eyJ...",
  "refresh_token": "eyJ..."
}
```

---

### POST `/api/auth/login`

**Request:**

```json
{
  "email": "john@example.com",
  "password": "secret123"
}
```

**Response** `200 OK`:

```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "role": "user"
  },
  "access_token": "eyJ...",
  "refresh_token": "eyJ..."
}
```

---

### POST `/api/auth/refresh`

Exchange a refresh token for a new token pair.

**Request:**

```json
{
  "refresh_token": "eyJ..."
}
```

**Response** `200 OK`:

```json
{
  "message": "Token refreshed",
  "access_token": "eyJ...",
  "refresh_token": "eyJ..."
}
```

---

### GET `/api/auth/me`

🔒 **Requires authentication**

Returns the currently authenticated user.

**Response** `200 OK`:

```json
{
  "user": {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "role": "user"
  }
}
```

---

### POST `/api/auth/logout`

🔒 **Requires authentication**

**Response** `200 OK`:

```json
{
  "message": "Logged out successfully"
}
```

---

## User Profile

### GET `/api/profile`

🔒 **Requires authentication**

**Response** `200 OK`:

```json
{
  "profile": {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "role": "user"
  }
}
```

---

### PUT `/api/profile`

🔒 **Requires authentication**

**Request:**

```json
{
  "first_name": "Johnny",
  "last_name": "Doe",
  "email": "johnny@example.com"
}
```

All fields are optional.

**Response** `200 OK`:

```json
{
  "message": "Profile updated",
  "user": { ... }
}
```

---

### POST `/api/change-password`

🔒 **Requires authentication**

**Request:**

```json
{
  "current_password": "secret123",
  "new_password": "newsecret456"
}
```

**Response** `200 OK`:

```json
{
  "message": "Password changed successfully"
}
```

---

### GET `/api/dashboard`

🔒 **Requires authentication**

**Response** `200 OK`:

```json
{
  "message": "Welcome to your dashboard",
  "user_id": 1,
  "role": "user"
}
```

---

### GET `/api/operator/dashboard`

🔒 **Requires authentication** (approved dive operator only)

**Response** `200 OK`:

```json
{
  "message": "Dive Operator Dashboard",
  "verified_at": "2025-01-15T10:30:00",
  "documents": [
    {
      "doc_type": "bir_document",
      "original_filename": "bir.pdf",
      "file_size": 204800
    }
  ]
}
```

---

## Admin — Dive Operators

All admin routes require the authenticated user to have the `admin` role.

### GET `/api/admin/dive-operators`

🔒 **Admin only**

| Query Param | Type | Default | Description |
|-------------|------|---------|-------------|
| `status` | string | `pending` | Filter: `pending`, `approved`, `rejected`, `all` |

**Response** `200 OK`:

```json
{
  "total": 3,
  "filter": "pending",
  "dive_operators": [
    {
      "id": 2,
      "first_name": "Maria",
      "last_name": "Santos",
      "email": "maria@blueseadivers.com",
      "verification_status": "pending"
    }
  ]
}
```

---

### GET `/api/admin/dive-operators/summary`

🔒 **Admin only**

**Response** `200 OK`:

```json
{
  "pending": 2,
  "approved": 5,
  "rejected": 1,
  "total": 8
}
```

---

### GET `/api/admin/dive-operators/<user_id>`

🔒 **Admin only**

**Response** `200 OK`:

```json
{
  "dive_operator": {
    "id": 2,
    "first_name": "Maria",
    "last_name": "Santos",
    "email": "maria@blueseadivers.com",
    "verification_status": "pending",
    "documents": [ ... ]
  }
}
```

---

### POST `/api/admin/dive-operators/<user_id>/approve`

🔒 **Admin only**

**Response** `200 OK`:

```json
{
  "message": "Dive operator approved",
  "dive_operator": { ... }
}
```

---

### POST `/api/admin/dive-operators/<user_id>/reject`

🔒 **Admin only**

**Request:**

```json
{
  "reason": "Documents are expired"
}
```

**Response** `200 OK`:

```json
{
  "message": "Dive operator rejected",
  "dive_operator": { ... }
}
```

---

### POST `/api/admin/dive-operators/<user_id>/reset`

🔒 **Admin only**

Resets verification status back to pending.

**Response** `200 OK`:

```json
{
  "message": "Dive operator reset to pending",
  "dive_operator": { ... }
}
```

---

## Admin — Coupons

### POST `/api/admin/coupons`

🔒 **Admin only**

**Request:**

```json
{
  "code": "SUMMER2025",
  "description": "Summer discount",
  "discount_type": "percentage",
  "discount_value": 15,
  "min_price": 500,
  "max_discount": 200,
  "scope": "global",
  "max_uses": 100,
  "uses_per_user": 1,
  "valid_from": "2025-06-01",
  "valid_until": "2025-08-31"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `code` | string | ❌ | Auto-generated if omitted |
| `discount_type` | string | ✅ | `percentage` or `fixed` |
| `discount_value` | number | ✅ | Discount amount |
| `scope` | string | ✅ | `global`, `store`, or `schedule` |
| `store_id` | integer | ❌ | Required if scope is `store` |
| `schedule_id` | integer | ❌ | Required if scope is `schedule` |
| `max_uses` | integer | ❌ | Total redemption limit |
| `uses_per_user` | integer | ✅ | Per-user redemption limit |
| `valid_from` | date | ❌ | Start date |
| `valid_until` | date | ❌ | Expiry date |

**Response** `201 Created`:

```json
{
  "message": "Coupon created",
  "coupon": { ... }
}
```

---

### POST `/api/admin/coupons/generate`

🔒 **Admin only** — Bulk generate coupons.

**Request:**

```json
{
  "count": 10,
  "prefix": "PROMO",
  "discount_type": "fixed",
  "discount_value": 100,
  "max_uses": 1,
  "valid_until": "2025-12-31"
}
```

**Response** `201 Created`:

```json
{
  "message": "10 coupons generated",
  "coupons": [ ... ],
  "codes": ["PROMO-ABC123", "PROMO-DEF456", ...]
}
```

---

### GET `/api/admin/coupons`

🔒 **Admin only**

| Query Param | Type | Description |
|-------------|------|-------------|
| `active` | boolean | Filter by active status |
| `type` | string | Filter by `percentage` or `fixed` |
| `scope` | string | Filter by `global`, `store`, or `schedule` |

**Response** `200 OK`:

```json
{
  "total": 5,
  "coupons": [ ... ]
}
```

---

### GET `/api/admin/coupons/<coupon_id>`

🔒 **Admin only**

**Response** `200 OK`:

```json
{
  "coupon": { ... },
  "redemptions": [ ... ]
}
```

---

### PUT `/api/admin/coupons/<coupon_id>`

🔒 **Admin only**

**Request** (all fields optional):

```json
{
  "discount_value": 20,
  "is_active": false,
  "valid_until": "2025-12-31"
}
```

**Response** `200 OK`:

```json
{
  "message": "Coupon updated",
  "coupon": { ... }
}
```

---

### DELETE `/api/admin/coupons/<coupon_id>`

🔒 **Admin only** — Deactivates the coupon (soft delete).

**Response** `200 OK`:

```json
{
  "message": "Coupon deactivated"
}
```

---

## Coupons

### POST `/api/coupons/validate`

🔒 **Requires authentication**

Validate a coupon code and preview the discount.

**Request:**

```json
{
  "code": "SUMMER2025",
  "schedule_id": 1
}
```

**Response** `200 OK`:

```json
{
  "valid": true,
  "code": "SUMMER2025",
  "discount_type": "percentage",
  "discount_value": 15,
  "original_price": 1000,
  "discount_amount": 150,
  "final_price": 850,
  "savings": 150
}
```

---

## Stores

### GET `/api/stores`

Public — no authentication required.

**Response** `200 OK`:

```json
{
  "total": 3,
  "stores": [
    {
      "id": 1,
      "name": "Blue Sea Divers",
      "description": "PADI certified dive center",
      "contact_number": "+63-912-345-6789",
      "address": "Mactan, Cebu",
      "latitude": 10.3157,
      "longitude": 123.9750,
      "is_active": true,
      "popularity": "popular"
    }
  ]
}
```

---

### GET `/api/stores/map`

Public — returns stores with coordinates for map rendering.

**Response** `200 OK`:

```json
{
  "total": 3,
  "stores": [
    {
      "id": 1,
      "name": "Blue Sea Divers",
      "latitude": 10.3157,
      "longitude": 123.9750
    }
  ]
}
```

---

### GET `/api/stores/<store_id>`

Public — returns store details with schedules.

**Response** `200 OK`:

```json
{
  "store": {
    "id": 1,
    "name": "Blue Sea Divers",
    "description": "...",
    "schedules": [ ... ]
  }
}
```

---

### POST `/api/stores`

🔒 **Approved dive operator only**

**Request:**

```json
{
  "name": "Blue Sea Divers",
  "description": "PADI certified dive center",
  "contact_number": "+63-912-345-6789",
  "address": "Mactan, Cebu",
  "latitude": 10.3157,
  "longitude": 123.9750
}
```

**Response** `201 Created`:

```json
{
  "message": "Store created",
  "store": { ... }
}
```

---

### PUT `/api/stores/<store_id>`

🔒 **Store owner or admin**

**Request** (all fields optional):

```json
{
  "name": "Updated Store Name",
  "description": "Updated description"
}
```

**Response** `200 OK`:

```json
{
  "message": "Store updated",
  "store": { ... }
}
```

---

### DELETE `/api/stores/<store_id>`

🔒 **Store owner or admin** — Deactivates the store (soft delete).

**Response** `200 OK`:

```json
{
  "message": "Store deactivated"
}
```

---

## Schedules

### GET `/api/stores/<store_id>/schedules`

Public.

| Query Param | Type | Description |
|-------------|------|-------------|
| `date` | string | Filter by date (`YYYY-MM-DD`) |

**Response** `200 OK`:

```json
{
  "store": "Blue Sea Divers",
  "total": 2,
  "schedules": [
    {
      "id": 1,
      "title": "Morning Dive",
      "description": "Beginner-friendly dive",
      "date": "2025-07-01",
      "start_time": "08:00",
      "end_time": "11:00",
      "price": 1500.00,
      "max_slots": 10,
      "booked_slots": 3,
      "status": "active"
    }
  ]
}
```

---

### POST `/api/stores/<store_id>/schedules`

🔒 **Store owner or admin**

**Request:**

```json
{
  "title": "Morning Dive",
  "description": "Beginner-friendly dive",
  "date": "2025-07-01",
  "start_time": "08:00",
  "end_time": "11:00",
  "price": 1500.00,
  "max_slots": 10
}
```

**Response** `201 Created`:

```json
{
  "message": "Schedule created",
  "schedule": { ... }
}
```

---

### PUT `/api/stores/<store_id>/schedules/<schedule_id>`

🔒 **Store owner or admin**

**Request** (all fields optional):

```json
{
  "title": "Updated Dive",
  "price": 2000.00
}
```

**Response** `200 OK`:

```json
{
  "message": "Schedule updated",
  "schedule": { ... }
}
```

---

### DELETE `/api/stores/<store_id>/schedules/<schedule_id>`

🔒 **Store owner or admin** — Cancels the schedule.

**Response** `200 OK`:

```json
{
  "message": "Schedule cancelled",
  "schedule": { ... }
}
```

---

## Bookings

### GET `/api/bookings`

🔒 **Requires authentication** — Admins see all bookings, users see their own.

| Query Param | Type | Description |
|-------------|------|-------------|
| `status` | string | Filter: `active` or `cancelled` |

**Response** `200 OK`:

```json
{
  "total": 2,
  "bookings": [
    {
      "id": 1,
      "schedule_id": 1,
      "slots": 2,
      "notes": "First time diving",
      "status": "active",
      "created_at": "2025-06-15T10:00:00"
    }
  ]
}
```

---

### GET `/api/bookings/my`

🔒 **Requires authentication**

Returns only the authenticated user's bookings.

**Response** `200 OK`:

```json
{
  "total": 1,
  "bookings": [ ... ]
}
```

---

### GET `/api/bookings/<booking_id>`

🔒 **Requires authentication**

**Response** `200 OK`:

```json
{
  "booking": {
    "id": 1,
    "schedule_id": 1,
    "slots": 2,
    "notes": "First time diving",
    "status": "active"
  }
}
```

---

### POST `/api/bookings`

🔒 **Requires authentication**

**Request:**

```json
{
  "schedule_id": 1,
  "slots": 2,
  "notes": "First time diving",
  "coupon_code": "SUMMER2025"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `schedule_id` | integer | ✅ | ID of the diving schedule |
| `slots` | integer | ✅ | Number of slots to book |
| `notes` | string | ❌ | Optional notes |
| `coupon_code` | string | ❌ | Coupon to apply |

**Response** `201 Created`:

```json
{
  "message": "Booking created",
  "booking": { ... },
  "coupon_applied": {
    "code": "SUMMER2025",
    "discount_amount": 150
  }
}
```

---

### DELETE `/api/bookings/<booking_id>`

🔒 **Requires authentication**

Cancels a booking.

**Response** `200 OK`:

```json
{
  "message": "Booking cancelled",
  "booking": { ... }
}
```

---

## Weather

Weather data is provided by [WeatherAPI.com](https://www.weatherapi.com/). No authentication required.

### GET `/api/weather/current`

Get real-time weather for a location.

| Query Param | Type | Required | Description |
|-------------|------|----------|-------------|
| `q` | string | ✅ | Location — city name, lat/lon, zip code, IP, etc. |

**Usage:**

```
GET /api/weather/current?q=Cebu
GET /api/weather/current?q=10.3157,123.9750
GET /api/weather/current?q=10001
```

**Response** `200 OK`:

```json
{
  "location": {
    "name": "Cebu",
    "region": "Central Visayas",
    "country": "Philippines",
    "lat": 10.32,
    "lon": 123.89,
    "tz_id": "Asia/Manila",
    "localtime": "2025-07-01 14:30"
  },
  "current": {
    "temp_c": 31.0,
    "temp_f": 87.8,
    "condition": {
      "text": "Partly cloudy",
      "icon": "//cdn.weatherapi.com/weather/64x64/day/116.png"
    },
    "wind_kph": 15.1,
    "wind_dir": "NE",
    "humidity": 70,
    "feelslike_c": 35.2,
    "vis_km": 10.0,
    "uv": 7.0
  }
}
```

---

### GET `/api/weather/marine`

Get marine and tidal weather forecast — essential for dive planning.

| Query Param | Type | Required | Default | Description |
|-------------|------|----------|---------|-------------|
| `q` | string | ✅ | — | Location (city, coordinates, etc.) |
| `days` | integer | ❌ | `1` | Forecast days (1–7) |
| `tides` | string | ❌ | `yes` | Include tide data (`yes` or `no`) |

**Usage:**

```
GET /api/weather/marine?q=Cebu&days=3
GET /api/weather/marine?q=10.3157,123.9750&days=1&tides=yes
```

**Response** `200 OK`:

```json
{
  "location": {
    "name": "Cebu",
    "region": "Central Visayas",
    "country": "Philippines",
    "lat": 10.32,
    "lon": 123.89,
    "tz_id": "Asia/Manila",
    "localtime": "2025-07-01 14:30"
  },
  "forecast": {
    "forecastday": [
      {
        "date": "2025-07-01",
        "day": {
          "maxtemp_c": 32.0,
          "mintemp_c": 26.0,
          "condition": {
            "text": "Partly cloudy"
          },
          "tides": [
            {
              "tide": [
                {
                  "tide_time": "2025-07-01 03:45",
                  "tide_height_mt": "0.30",
                  "tide_type": "LOW"
                },
                {
                  "tide_time": "2025-07-01 10:12",
                  "tide_height_mt": "1.50",
                  "tide_type": "HIGH"
                }
              ]
            }
          ]
        },
        "hour": [
          {
            "time": "2025-07-01 06:00",
            "temp_c": 27.5,
            "wind_kph": 12.0,
            "wind_dir": "E",
            "humidity": 80,
            "vis_km": 10.0,
            "sig_ht_mt": 0.5,
            "swell_ht_mt": 0.3,
            "swell_dir": "E",
            "swell_period_secs": 6.0,
            "water_temp_c": 28.5
          }
        ]
      }
    ]
  }
}
```

Key marine-specific fields in hourly data:

| Field | Type | Description |
|-------|------|-------------|
| `sig_ht_mt` | float | Significant wave height (meters) |
| `swell_ht_mt` | float | Swell height (meters) |
| `swell_dir` | string | Swell direction |
| `swell_period_secs` | float | Swell period (seconds) |
| `water_temp_c` | float | Water temperature (°C) |
| `water_temp_f` | float | Water temperature (°F) |

---

## Species Identification

### POST `/api/identify`

Upload an image to classify marine species using a VGG16 deep learning model, then fetch species information from [iNaturalist](https://www.inaturalist.org/).

**Request:** `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `image` | file | ✅ | Image file (jpg, jpeg, png, webp) |

**Usage (curl):**

```bash
curl -X POST http://localhost:5000/api/identify \
  -F "image=@photo.jpg"
```

**Response** `200 OK` (successful classification):

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

**Response** `200 OK` (low confidence):

```json
{
  "classification": {
    "class_id": -1,
    "label": "Unknown",
    "confidence": 0.0
  },
  "species": null,
  "message": "Could not confidently classify the image"
}
```

---

## Error Responses

All errors follow a consistent format:

```json
{
  "error": "Description of what went wrong"
}
```

| Status Code | Meaning |
|-------------|---------|
| `400` | Bad request — missing or invalid parameters |
| `401` | Unauthorized — missing or invalid JWT token |
| `403` | Forbidden — insufficient permissions |
| `404` | Not found — resource does not exist |
| `409` | Conflict — duplicate resource (e.g., email already registered) |
| `500` | Internal server error |
| `502` | Bad gateway — external API (weather, iNaturalist) unreachable |
