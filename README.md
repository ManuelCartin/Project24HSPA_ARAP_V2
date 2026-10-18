# ARAP — Ardennes Racing Automotive Platform

## 24 Hours of Spa — NoSQL Academic Project

ARAP is a web-based racing analysis platform developed as part of an academic NoSQL project focused on the **24 Hours of Spa-Francorchamps**, held at the Spa-Francorchamps circuit in Belgium.

The platform aims to bring together racing telemetry, historical weather observations, circuit geometry, and vehicle performance data to support the analysis of endurance racing sessions.

## Project Scope

- **Racing Telemetry:** Analyze vehicle telemetry and session data.
- **Weather Data:** Collect historical meteorological observations from NOAA GHCNh to provide environmental context for racing analysis.
- **Circuit Geometry:** Represent circuit features and spatial information using GeoJSON and WebGIS technologies.
- **Vehicle Performance:** Organize vehicle specifications, setup information, and performance-related data.

## Technologies

- MongoDB
- Spring Boot
- Java
- REST API
- HTML5
- CSS3
- JavaScript
- GeoJSON
- WebGIS
- Python for weather data acquisition

## Architecture

```text
Meteorological Data (NOAA GHCNh)
                │
                ▼
       Data Acquisition
                │
                ▼
             MongoDB
                │
                ▼
      Spring Boot REST API
                │
                ▼
        ARAP Web Frontend
                │
                ├── Racing Telemetry
                ├── Weather Analysis
                ├── Circuit Geometry
                └── Vehicle Performance
```

## Data Sources

Meteorological data is sourced from NOAA's Global Historical Climatology Network hourly (GHCNh) dataset. The project uses station observations to explore the relationship between weather conditions and endurance racing analysis.

Raw source files are preserved separately from processed data to support traceability and data preparation for MongoDB.

## Project Objective

The objective of ARAP is to establish a data platform for organizing and analyzing the different sources of information involved in endurance racing, with a focus on the 24 Hours of Spa-Francorchamps.