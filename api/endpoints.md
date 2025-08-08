# Smart Thermostat Automation System API Documentation

This document provides detailed information about the API endpoints available in the Django backend for the Smart Thermostat Automation System.

## Authentication Endpoints

### Register a New User
- **URL**: `/api/auth/register/`
- **Method**: `POST`
- **Auth Required**: No
- **Request Body**:
  ```json
  {
    "username": "example_user",
    "email": "user@example.com",
    "password": "securepassword123",
    "first_name": "John",
    "last_name": "Doe"
  }
  ```
- **Success Response**: `201 Created`
  ```json
  {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "id": 1,
      "username": "example_user",
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe"
    }
  }
  ```

### User Login
- **URL**: `/api/auth/login/`
- **Method**: `POST`
- **Auth Required**: No
- **Request Body**:
  ```json
  {
    "username": "example_user",
    "password": "securepassword123"
  }
  ```
- **Success Response**: `200 OK`
  ```json
  {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "id": 1,
      "username": "example_user",
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe"
    }
  }
  ```

### Get User Profile
- **URL**: `/api/auth/profile/`
- **Method**: `GET`
- **Auth Required**: Yes (Bearer Token)
- **Success Response**: `200 OK`
  ```json
  {
    "id": 1,
    "user": {
      "id": 1,
      "username": "example_user",
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe"
    },
    "phone": "1234567890",
    "company": "Example Company",
    "role": "manager",
    "created_at": "2025-06-03T01:15:30Z",
    "updated_at": "2025-06-03T01:15:30Z"
  }
  ```

### Update User Profile
- **URL**: `/api/auth/profile/`
- **Method**: `PUT`
- **Auth Required**: Yes (Bearer Token)
- **Request Body**:
  ```json
  {
    "phone": "9876543210",
    "company": "Updated Company",
    "role": "admin"
  }
  ```
- **Success Response**: `200 OK`
  ```json
  {
    "id": 1,
    "user": {
      "id": 1,
      "username": "example_user",
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe"
    },
    "phone": "9876543210",
    "company": "Updated Company",
    "role": "admin",
    "created_at": "2025-06-03T01:15:30Z",
    "updated_at": "2025-06-03T01:20:45Z"
  }
  ```

### Refresh Token
- **URL**: `/api/auth/token/refresh/`
- **Method**: `POST`
- **Auth Required**: No
- **Request Body**:
  ```json
  {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
  ```
- **Success Response**: `200 OK`
  ```json
  {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
  ```

## Property Endpoints

### List Properties
- **URL**: `/api/properties/`
- **Method**: `GET`
- **Auth Required**: Yes (Bearer Token)
- **Success Response**: `200 OK`
  ```json
  {
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "name": "Beach House",
        "address": "123 Ocean Drive",
        "city": "Miami",
        "state": "FL",
        "zip_code": "33139",
        "country": "USA",
        "user": 1,
        "created_at": "2025-06-03T01:30:00Z",
        "updated_at": "2025-06-03T01:30:00Z"
      }
    ]
  }
  ```

### Create Property
- **URL**: `/api/properties/`
- **Method**: `POST`
- **Auth Required**: Yes (Bearer Token)
- **Request Body**:
  ```json
  {
    "name": "Mountain Cabin",
    "address": "456 Pine Road",
    "city": "Aspen",
    "state": "CO",
    "zip_code": "81611",
    "country": "USA"
  }
  ```
- **Success Response**: `201 Created`
  ```json
  {
    "id": 2,
    "name": "Mountain Cabin",
    "address": "456 Pine Road",
    "city": "Aspen",
    "state": "CO",
    "zip_code": "81611",
    "country": "USA",
    "user": 1,
    "created_at": "2025-06-03T01:35:00Z",
    "updated_at": "2025-06-03T01:35:00Z"
  }
  ```

### Get Property Details
- **URL**: `/api/properties/{id}/`
- **Method**: `GET`
- **Auth Required**: Yes (Bearer Token)
- **Success Response**: `200 OK`
  ```json
  {
    "id": 1,
    "name": "Beach House",
    "address": "123 Ocean Drive",
    "city": "Miami",
    "state": "FL",
    "zip_code": "33139",
    "country": "USA",
    "user": 1,
    "created_at": "2025-06-03T01:30:00Z",
    "updated_at": "2025-06-03T01:30:00Z"
  }
  ```

### Update Property
- **URL**: `/api/properties/{id}/`
- **Method**: `PUT`
- **Auth Required**: Yes (Bearer Token)
- **Request Body**:
  ```json
  {
    "name": "Updated Beach House",
    "address": "123 Ocean Drive",
    "city": "Miami Beach",
    "state": "FL",
    "zip_code": "33139",
    "country": "USA"
  }
  ```
- **Success Response**: `200 OK`
  ```json
  {
    "id": 1,
    "name": "Updated Beach House",
    "address": "123 Ocean Drive",
    "city": "Miami Beach",
    "state": "FL",
    "zip_code": "33139",
    "country": "USA",
    "user": 1,
    "created_at": "2025-06-03T01:30:00Z",
    "updated_at": "2025-06-03T01:40:00Z"
  }
  ```

### Delete Property
- **URL**: `/api/properties/{id}/`
- **Method**: `DELETE`
- **Auth Required**: Yes (Bearer Token)
- **Success Response**: `204 No Content`

## Thermostat Endpoints

### List Thermostats
- **URL**: `/api/thermostats/`
- **Method**: `GET`
- **Auth Required**: Yes (Bearer Token)
- **Success Response**: `200 OK`
  ```json
  {
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "name": "Living Room",
        "device_id": "nest123",
        "type": "NEST",
        "property": 1,
        "is_online": true,
        "last_temperature": 72.5,
        "last_updated": "2025-06-03T01:45:00Z",
        "api_key": "api_key_123",
        "ip_address": "192.168.1.100",
        "created_at": "2025-06-03T01:45:00Z",
        "updated_at": "2025-06-03T01:45:00Z"
      }
    ]
  }
  ```

### Create Thermostat
- **URL**: `/api/thermostats/`
- **Method**: `POST`
- **Auth Required**: Yes (Bearer Token)
- **Request Body**:
  ```json
  {
    "name": "Bedroom",
    "device_id": "nest456",
    "type": "NEST",
    "property": 1,
    "api_key": "api_key_456",
    "ip_address": "192.168.1.101"
  }
  ```
- **Success Response**: `201 Created`
  ```json
  {
    "id": 2,
    "name": "Bedroom",
    "device_id": "nest456",
    "type": "NEST",
    "property": 1,
    "is_online": false,
    "last_temperature": null,
    "last_updated": null,
    "api_key": "api_key_456",
    "ip_address": "192.168.1.101",
    "created_at": "2025-06-03T01:50:00Z",
    "updated_at": "2025-06-03T01:50:00Z"
  }
  ```

### Get Thermostat Details
- **URL**: `/api/thermostats/{id}/`
- **Method**: `GET`
- **Auth Required**: Yes (Bearer Token)
- **Success Response**: `200 OK`
  ```json
  {
    "id": 1,
    "name": "Living Room",
    "device_id": "nest123",
    "type": "NEST",
    "property": 1,
    "is_online": true,
    "last_temperature": 72.5,
    "last_updated": "2025-06-03T01:45:00Z",
    "api_key": "api_key_123",
    "ip_address": "192.168.1.100",
    "created_at": "2025-06-03T01:45:00Z",
    "updated_at": "2025-06-03T01:45:00Z"
  }
  ```

### Update Thermostat
- **URL**: `/api/thermostats/{id}/`
- **Method**: `PUT`
- **Auth Required**: Yes (Bearer Token)
- **Request Body**:
  ```json
  {
    "name": "Main Living Room",
    "api_key": "updated_api_key_123",
    "ip_address": "192.168.1.200"
  }
  ```
- **Success Response**: `200 OK`
  ```json
  {
    "id": 1,
    "name": "Main Living Room",
    "device_id": "nest123",
    "type": "NEST",
    "property": 1,
    "is_online": true,
    "last_temperature": 72.5,
    "last_updated": "2025-06-03T01:45:00Z",
    "api_key": "updated_api_key_123",
    "ip_address": "192.168.1.200",
    "created_at": "2025-06-03T01:45:00Z",
    "updated_at": "2025-06-03T01:55:00Z"
  }
  ```

### Delete Thermostat
- **URL**: `/api/thermostats/{id}/`
- **Method**: `DELETE`
- **Auth Required**: Yes (Bearer Token)
- **Success Response**: `204 No Content`

## Calendar Endpoints

### List Calendars
- **URL**: `/api/calendars/`
- **Method**: `GET`
- **Auth Required**: Yes (Bearer Token)
- **Success Response**: `200 OK`
  ```json
  {
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "name": "Airbnb Calendar",
        "type": "ICAL",
        "url": "https://www.airbnb.com/calendar/ical/12345.ics",
        "property": 1,
        "sync_frequency": "DAILY",
        "credentials": null,
        "last_synced": "2025-06-03T02:00:00Z",
        "created_at": "2025-06-03T02:00:00Z",
        "updated_at": "2025-06-03T02:00:00Z"
      }
    ]
  }
  ```

### Create Calendar
- **URL**: `/api/calendars/`
- **Method**: `POST`
- **Auth Required**: Yes (Bearer Token)
- **Request Body**:
  ```json
  {
    "name": "Google Calendar",
    "type": "GOOGLE",
    "url": null,
    "property": 1,
    "sync_frequency": "HOURLY",
    "credentials": "{\"client_id\": \"google_client_id\", \"client_secret\": \"google_client_secret\"}"
  }
  ```
- **Success Response**: `201 Created`
  ```json
  {
    "id": 2,
    "name": "Google Calendar",
    "type": "GOOGLE",
    "url": null,
    "property": 1,
    "sync_frequency": "HOURLY",
    "credentials": "{\"client_id\": \"google_client_id\", \"client_secret\": \"google_client_secret\"}",
    "last_synced": null,
    "created_at": "2025-06-03T02:05:00Z",
    "updated_at": "2025-06-03T02:05:00Z"
  }
  ```

## Schedule Endpoints

### List Schedules
- **URL**: `/api/schedules/`
- **Method**: `GET`
- **Auth Required**: Yes (Bearer Token)
- **Success Response**: `200 OK`
  ```json
  {
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "name": "Booking Schedule",
        "type": "BOOKING",
        "thermostat": 1,
        "occupied_temp": 72.0,
        "unoccupied_temp": 65.0,
        "pre_arrival_hours": 2,
        "is_active": true,
        "created_at": "2025-06-03T02:10:00Z",
        "updated_at": "2025-06-03T02:10:00Z"
      }
    ]
  }
  ```

### Create Schedule
- **URL**: `/api/schedules/`
- **Method**: `POST`
- **Auth Required**: Yes (Bearer Token)
- **Request Body**:
  ```json
  {
    "name": "Time-based Schedule",
    "type": "TIME",
    "thermostat": 1,
    "occupied_temp": 74.0,
    "unoccupied_temp": 68.0,
    "is_active": true
  }
  ```
- **Success Response**: `201 Created`
  ```json
  {
    "id": 2,
    "name": "Time-based Schedule",
    "type": "TIME",
    "thermostat": 1,
    "occupied_temp": 74.0,
    "unoccupied_temp": 68.0,
    "pre_arrival_hours": null,
    "is_active": true,
    "created_at": "2025-06-03T02:15:00Z",
    "updated_at": "2025-06-03T02:15:00Z"
  }
  ```

## Temperature Log Endpoints

### List Temperature Logs
- **URL**: `/api/temperature-logs/`
- **Method**: `GET`
- **Auth Required**: Yes (Bearer Token)
- **Success Response**: `200 OK`
  ```json
  {
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "thermostat": 1,
        "temperature": 72.5,
        "is_occupied": true,
        "timestamp": "2025-06-03T02:20:00Z"
      },
      {
        "id": 2,
        "thermostat": 1,
        "temperature": 73.0,
        "is_occupied": true,
        "timestamp": "2025-06-03T02:25:00Z"
      }
    ]
  }
  ```

## Authentication

All protected endpoints require a valid JWT token in the Authorization header:

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

To obtain a token, use the login or register endpoints. The token is valid for 24 hours. Use the refresh token endpoint to get a new access token when it expires.

## Error Responses

- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Missing or invalid authentication
- **403 Forbidden**: Authenticated but not authorized to access the resource
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

## Pagination

List endpoints return paginated results with the following structure:

```json
{
  "count": 100,
  "next": "http://example.com/api/items/?page=2",
  "previous": null,
  "results": [
    // items
  ]
}
```

You can specify the page size and page number using query parameters:

```
/api/items/?page=2&page_size=20
```
