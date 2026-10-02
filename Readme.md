# Credit Risk Data Engineering & Analytics Platform

## Overview

An end-to-end data engineering project that transforms approximately 2.26 million Lending Club loan records into a structured analytical data warehouse.

The project demonstrates a complete data pipeline covering data ingestion, data-quality validation, cleaning, transformation, MySQL staging, dimensional data modeling, warehouse loading, reconciliation, and SQL-based business analytics.

---

## Business Objective

The objective is to build a reliable analytical data platform that enables lending-related analysis such as:

- Loan portfolio volume
- Loan funding
- Charge-off rates
- Credit-risk patterns
- Interest and principal collections
- Outstanding principal
- Geographic funding distribution
- Origination trends

---

## Architecture

```text
Lending Club Raw CSV
        ↓
Python + Pandas
        ↓
Data Validation
        ↓
Data Cleaning & Transformation
        ↓
MySQL Staging
        ↓
ETL Processing
        ↓
MySQL Data Warehouse
        ↓
Star Schema
        ↓
SQL Analytics
        ↓
Power BI