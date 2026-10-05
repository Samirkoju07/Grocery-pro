# 🛒 Grocery POS – Nepal Supermarket Management System

A production-grade, full-featured grocery and supermarket management system built for the Nepal market.

## Technology Stack

### Backend
| Technology | Version | Purpose |
|---|---|---|
| Python | 3.12+ | Core language |
| FastAPI | 0.115+ | REST API framework |
| SQLAlchemy | 2.x | ORM |
| PostgreSQL | 16 | Primary database |
| Alembic | 1.14+ | Database migrations |
| Pydantic v2 | 2.10+ | Data validation |
| Redis | 7 | Caching, sessions |
| JWT | — | Authentication |

### Desktop POS
| Technology | Purpose |
|---|---|
| Tauri 1.x | Desktop shell |
| React 18 | UI framework |
| TypeScript | Type safety |
| Vite 6 | Build tool |
| Tailwind CSS 3 | Styling |
| TanStack Query | Server state |
| Zustand | Client state |
| React Hook Form + Zod | Forms & validation |

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) 24+
- [Docker Compose](https://docs.docker.com/compose/) v2.x
- [Node.js](https://nodejs.org/) 20+ (for desktop POS development)
- [Rust](https://rustup.rs/) stable (for Tauri)

---

## Quick Start

### 1. Clone the repository
```bash
git clone <repo-url>
cd grocery-pos
```

### 2. Set up environment variables
```bash
# Root .env (PostgreSQL, Redis passwords, etc.)
cp .env.example .env

# Backend .env (app secrets, CORS, etc.)
cp backend/.env.example backend/.env
```

> **⚠ Important:** Edit both `.env` files and replace all `CHANGE_ME` placeholders with real credentials.

### 3. Start all services

**Windows (PowerShell):**
```powershell
.\scripts\start-dev.ps1
```

**Linux / macOS:**
```bash
bash scripts/start-dev.sh
```

**Or manually:**
```bash
docker compose up --build -d
```

### 4. Verify services

| Service | URL |
|---|---|
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| API Health (liveness) | http://localhost:8000/health |
| API Health (readiness) | http://localhost:8000/api/v1/health |

---

## Development

### Backend

```bash
# Enter backend container
docker compose exec backend bash

# Run migrations
docker compose exec backend alembic upgrade head

# Run tests
docker compose exec backend pytest tests/ -v

# Or via script
.\scripts\run-tests.ps1

# Create a new migration
.\scripts\migrate.ps1 -Action revision -Message "add_products_table"
```

### Desktop POS

```bash
cd desktop-pos
npm install

# Web dev mode (no Tauri shell)
npm run dev

# Full Tauri dev (requires Rust)
npm run tauri:dev
```

---

## Project Structure

```
grocery-pos/
├── backend/                    # FastAPI Python backend
│   ├── app/
│   │   ├── api/v1/             # REST API endpoints (versioned)
│   │   ├── core/               # Config, logging, security
│   │   ├── db/                 # SQLAlchemy session, Redis client
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── schemas/            # Pydantic v2 schemas
│   │   ├── services/           # Business logic layer
│   │   ├── repositories/       # Data access layer
│   │   ├── middleware/         # Custom middleware
│   │   ├── workers/            # Background tasks (Celery)
│   │   └── main.py             # Application factory
│   ├── alembic/                # Database migrations
│   ├── tests/                  # pytest test suite
│   ├── Dockerfile
│   └── requirements.txt
│
├── desktop-pos/                # Tauri + React desktop app
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── pages/              # Route-level page components
│   │   ├── layouts/            # Layout wrappers
│   │   ├── hooks/              # Custom React hooks
│   │   ├── services/           # API client, integrations
│   │   ├── stores/             # Zustand state stores
│   │   ├── types/              # TypeScript type definitions
│   │   ├── utils/              # Utility functions
│   │   └── lib/                # Shared libraries
│   └── src-tauri/              # Tauri Rust backend
│
├── docker/
│   └── postgres/init.sql       # DB initialization
├── scripts/                    # Dev utility scripts
├── docs/                       # Documentation
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Module Roadmap

| Module | Status |
|---|---|
| Authentication & JWT | 🔜 Next |
| Company / Branch / POS Counter | 🔜 Planned |
| Users / Roles / Permissions | 🔜 Planned |
| Product / Category / Brand / Unit | 🔜 Planned |
| Barcode Management | 🔜 Planned |
| Inventory & Batch/Expiry | 🔜 Planned |
| Purchase & Supplier | 🔜 Planned |
| Customer / Khata | 🔜 Planned |
| POS Billing | 🔜 Planned |
| Payments (NPR, eSewa, Khalti, Fonepay, Card) | 🔜 Planned |
| Sales Return / Refund | 🔜 Planned |
| Cash Drawer | 🔜 Planned |
| Expenses | 🔜 Planned |
| Reports & Analytics | 🔜 Planned |
| Audit Logs | 🔜 Planned |
| Promotions | 🔜 Planned |
| Offline POS Foundation | 🔜 Planned |
| Multi-branch Support | 🔜 Planned |

---

## Nepal-Specific Features

- **Currency:** NPR (Nepalese Rupee)
- **Calendar:** Bikram Sambat (BS) & AD dates
- **Tax:** PAN/VAT configurable (13% VAT)
- **Payments:** eSewa, Khalti, Fonepay, Card, Bank Transfer, Customer Credit (Khata)
- **Hardware:** Thermal printer, Cash drawer, Barcode scanner
- **Weight-based products**
- **Offline POS capability**

---

## License

Proprietary – All rights reserved.
