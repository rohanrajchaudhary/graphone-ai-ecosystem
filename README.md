# GraphOne AI Ecosystem Intelligence Platform

An automated AI ecosystem intelligence platform that discovers, extracts, enriches, validates, and presents structured information about AI startups, products, research papers, jobs, and news.

## 🚀 Live Demo

https://graphone-ai-ecosystem-1.onrender.com/

## 🎯 Problem

AI ecosystem information is distributed across multiple websites and changes rapidly. Manually collecting and maintaining reliable data about startups, products, research papers, jobs, and AI news is time-consuming and difficult to scale.

GraphOne automates this process through a scalable web crawling, LLM extraction, entity resolution, validation, and freshness pipeline.

## 💡 Solution

The platform follows an automated pipeline:

Web Sources
→ Crawling
→ Data Acquisition
→ LLM Extraction
→ Normalization
→ Entity Resolution
→ Validation
→ Structured Dataset
→ Interactive Dashboard

## ✨ Key Features

- Automated AI ecosystem data acquisition
- Research paper discovery and extraction
- Startup and product data collection
- AI news and job monitoring
- LLM-powered structured information extraction
- Multi-tier extraction and fallback strategy
- Deterministic entity linking and deduplication
- Data validation and quality checks
- Large-scale dataset generation
- Interactive web dashboard
- Search and filtering
- Research paper browsing
- API-powered frontend
- Production deployment

## 🏗️ Architecture

```text
                    ┌──────────────────────┐
                    │     Web Sources      │
                    │ News • Jobs • Papers │
                    │ Startups • Products  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Data Acquisition   │
                    │ Crawlers / Fetchers  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   LLM Extraction     │
                    │ Structured Entities  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Entity Resolution    │
                    │ Deduplication        │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Validation & Quality  │
                    │ Checks / Normalizing │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Structured JSON Data │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ FastAPI Backend      │
                    │ REST API             │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ React Dashboard      │
                    │ Search • Research    │
                    └──────────────────────┘