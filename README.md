# Identity Aggregation Service

## Overview

The Identity Aggregation Service is a RESTful API that generates enriched user profiles from a single input — a name — by aggregating and processing data from multiple external sources.

Instead of relying on a single dataset, the service integrates with three independent APIs to infer demographic attributes such as gender, age, and nationality. The collected data is validated, transformed, and stored, allowing it to be retrieved efficiently through dedicated endpoints.

This project demonstrates core backend engineering concepts including multi-API orchestration, data persistence, idempotent operations, and structured API design.

---

## What It Does

Given a name, the service:

* Fetches gender data from Genderize
* Estimates age using Agify
* Determines likely nationality using Nationalize
* Applies classification logic (e.g., age grouping, highest-probability country)
* Stores the processed profile in a database
* Prevents duplicate records through idempotent handling
* Exposes endpoints to retrieve, filter, and delete stored profiles

---

## Key Features

* **Multi-Source Data Aggregation**
  Combines responses from multiple external APIs into a single structured profile

* **Data Persistence**
  Stores processed results in a relational database for reuse and querying

* **Idempotency Handling**
  Prevents duplicate records by checking existing entries and enforcing database constraints

* **Filtering & Querying**
  Supports querying profiles by gender, country, and age group

* **Robust Error Handling**
  Validates all external API responses and gracefully handles failures

* **Asynchronous Processing**
  Uses concurrent API calls to improve performance and responsiveness

---

## Why This Project Matters

This service is designed to reflect real-world backend patterns:

* Coordinating multiple external dependencies
* Ensuring data consistency under concurrent requests
* Designing clean and predictable APIs
* Handling partial failures without corrupting stored data

It moves beyond simple API consumption and demonstrates how to build a reliable data-processing service.

---

## Tech Stack

* Python
* FastAPI
* PostgreSQL
* httpx (async HTTP client)

---

## Base URL

```text
https://backend.rclancing.dev
```
