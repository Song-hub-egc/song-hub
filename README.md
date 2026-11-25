# SongHub — Music & Audio Dataset Platform

**SongHub** is a modular web platform for managing, exploring, previewing, and downloading **music and audio datasets** (alongside image and UVL feature-model datasets). Built as an evolution of [uvlhub.io](https://www.uvlhub.io/) (originally developed by DiversoLab) by **Group 1** for *Evolution and Configuration Management (EGC 2025/2026)* at the University of Seville (ETSII).

> 📄 Full project documentation and team metrics are available in [`docs/Documento_del_Proyecto.md`](docs/Documento_del_Proyecto.md).

---

## Key Features

- **Audio & Multimodal Datasets (`audiodataset`, `imagedataset`, `dataset`):** Upload, browse, preview (including integrated audio playback), version, and download datasets under a unified `BaseDataset` architecture.
- **Two-Factor Authentication & Active Sessions (`auth`):** Account registration/recovery, 2FA verification, and active session tracking with remote session revocation.
- **Dataset Comments:** Interactive comment threads on dataset pages with CRUD operations and author/role-based permissions.
- **Download Cart (`cart`):** Select multiple datasets and export them together in a bulk ZIP archive while tracking download metrics.
- **Trending Datasets (`explore`):** Discovery of the most viewed and downloaded datasets.
- **Fakenodo & Webhooks (`fakenodo`, `webhook`):** Simulated Zenodo service for local DOI generation and webhook state synchronization without external dependencies.

---

## Architecture & Tech Stack

SongHub follows a modular 3-tier architecture organized into isolated domain modules under `app/modules/`:

- **Backend:** Python 3.12 · Flask · SQLAlchemy · Alembic · Gunicorn
- **Frontend:** Jinja2 templates · HTML / CSS · Bootstrap
- **Database:** MariaDB
- **Testing & QA:** `pytest` (unit & integration) · `Selenium` (E2E UI) · `Locust` (load testing) · `black` · `isort` · `flake8`
- **DevOps & CI/CD:** Docker & Docker Compose (`web`, `db`, `nginx`, `selenium-hub`, `selenium-chrome`) · GitHub Actions (`CI_pytest`, `CI_lint`, `CI_sonarqube`, `CI_codacy`, `CI_commits`, `CD_dockerhub`, `CD_render`) · `rosemary` CLI

---

## Quick Start (Docker)

1. Copy the example environment file and configure your variables:
   ```bash
   cp .env.docker.example .env
   ```
2. Build and start the development stack (`web`, `db`, `nginx`, and `selenium`):
   ```bash
   docker compose -f docker/docker-compose.dev.yml up --build
   ```
3. Once running, open `http://localhost` in your browser.

---

## Team (Group 1 — EGC 2025/2026)

- Daniel del Castillo Piñero
- Miguel Ángel Gómez Vela
- Diego Manzanos Anento
- Pablo Pérez Gaspar
- Rares Nicolae Petre
- Jesús Villalba Fernández
