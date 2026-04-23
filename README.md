# Identity Aggregation Service

## Overview

The Identity Aggregation Service is a RESTful API that generates enriched user profiles from a single input — a name — by aggregating and processing data from multiple external sources.

It has evolved into a **Queryable Intelligence Engine**, allowing clients to filter, segment, and analyze demographic data efficiently using both structured queries and natural language.

The system integrates multiple external APIs, validates and processes their responses, and stores normalized profiles for fast retrieval.

---

## Business Context

This service is designed for **Insighta Labs**, a demographic intelligence company.

Clients such as marketing teams, product teams, and growth analysts rely on this API to:

- Segment users
- Identify demographic patterns
- Query large datasets efficiently

---

## What It Does

Given a name, the service:

- Fetches gender data from Genderize
- Estimates age using Agify
- Determines nationality using Nationalize
- Validates and processes all responses
- Stores enriched profiles in a database
- Prevents duplicates via idempotent logic
- Enables advanced querying and search

---

## Core Capabilities

### 1. Advanced Filtering

**Endpoint:** `GET /api/profiles`

Supports combinable filters:

- `gender`
- `age_group`
- `country_id`
- `min_age`
- `max_age`
- `min_gender_probability`
- `min_country_probability`

**Example**

```

/api/profiles?gender=male&country_id=NG&min_age=25

```

All filters are **AND-combined** — results must satisfy every condition.

---

### 2. Sorting

- `sort_by` → `age | created_at | gender_probability`
- `order` → `asc | desc`

**Example**

```

/api/profiles?sort_by=age&order=desc

````

---

### 3. Pagination

- `page` (default: 1)
- `limit` (default: 10, max: 50)

**Response Format**

```json
{
  "status": "success",
  "page": 1,
  "limit": 10,
  "total": 2026,
  "data": [ ... ]
}
````

Pagination is applied after filtering and sorting.

---

### 4. Natural Language Search (Core Feature)

**Endpoint:** `GET /api/profiles/search?q=...`

Allows users to query using plain English.

**Example**

```
/api/profiles/search?q=young males from nigeria
```

---

### Supported Query Interpretations

| Query                                | Interpreted As                                |
| ------------------------------------ | --------------------------------------------- |
| `young males`                        | gender=male + min_age=16 + max_age=24         |
| `females above 30`                   | gender=female + min_age=30                    |
| `people from angola`                 | country_id=AO                                 |
| `adult males from kenya`             | gender=male + age_group=adult + country_id=KE |
| `male and female teenagers above 17` | age_group=teenager + min_age=17               |

---

### Parsing Rules

* Rule-based parsing only (no AI/LLMs)
* "young" → age range 16–24 (not stored as age_group)
* Multiple conditions are combined logically
* Pagination applies to search results

---

### Invalid Query Handling

If a query cannot be interpreted:

```json
{ "status": "error", "message": "Unable to interpret query" }
```

---

### 5. Query Validation

Invalid parameters return:

```json
{ "status": "error", "message": "Invalid query parameters" }
```

---

## API Endpoints

### Create Profile

**POST** `/api/profiles`

Creates or retrieves a profile (idempotent).

---

### List Profiles

**GET** `/api/profiles`

Supports filtering, sorting, and pagination.

---

### Search Profiles

**GET** `/api/profiles/search?q=...`

Natural language query interface.

---

### Delete Profile

**DELETE** `/api/profiles/{id}`

---

## Database Schema

| Field               | Type             | Notes                          |
| ------------------- | ---------------- | ------------------------------ |
| id                  | UUID v7          | Primary key                    |
| name                | VARCHAR (UNIQUE) | Person's name                  |
| gender              | VARCHAR          | male / female                  |
| gender_probability  | FLOAT            | Confidence score               |
| age                 | INT              | Exact age                      |
| age_group           | VARCHAR          | child, teenager, adult, senior |
| country_id          | VARCHAR(2)       | ISO code                       |
| country_name        | VARCHAR          | Full name                      |
| country_probability | FLOAT            | Confidence score               |
| created_at          | TIMESTAMP        | Auto-generated                 |

---

## Data Seeding

* Database is seeded with 2026 profiles
* Seeding is **idempotent** (no duplicates on re-run)

---

## Performance Considerations

* Handles datasets of 2000+ records efficiently
* Pagination prevents large payloads
* Query conditions are applied at the database level
* Avoids unnecessary full-table scans

---

## Error Handling

All errors follow:

```json
{ "status": "error", "message": "<error message>" }
```

| Status Code | Meaning                        |
| ----------- | ------------------------------ |
| 400         | Missing or empty parameter     |
| 422         | Invalid parameter type         |
| 404         | Profile not found              |
| 500 / 502   | Server or external API failure |

---

## Tech Stack

* Python
* FastAPI
* PostgreSQL
* SQLAlchemy
* httpx (async HTTP client)

---

## Base URL

```
https://backend.rclancing.dev
```

---

## Why This Project Matters

This system demonstrates real-world backend design by combining:

* Multi-source data aggregation
* Idempotent writes and race-condition handling
* Advanced query systems
* Rule-based natural language parsing
* Scalable API design

It reflects how production systems enable both **structured querying** and **human-friendly search interfaces**.

```