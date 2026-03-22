# Mongo Ops

An app for accessing and viewing your MongoDB using your uri. 
Build on Next.js and fastapi by https://github.com/sup3rus3r.

## Features

- **Authentication System**
  - Session based authentication
  - JWT-based authentication for user sessions
  - API Key/Secret authentication 
  - NextAuth v5 integration with credentials provider
  - Encrypted credential transmission (AES-256-CBC)

- **Database**
  - MongoDB - async with Motor driver

- **Security**
  - End-to-end encryption for auth and websocket payloads
  - Rate limiting per user type (60/min users, 100/min API clients)
  - CORS middleware configured
  - JWT tokens with expiration

- **Modern Stack**
  - Next.js 16 with App Router
  - React 19
  - TypeScript
  - Tailwind CSS 4
  - FastAPI and WebSockets with async support
  - Pydantic v2 validation

## Project Structure

```
MONGO_OPD/
├── app/                 
│   ├── backend           # FastAPI backend
│   |   ├── .python-version           
│   |   ├── main.py           
│   |   ├── models           
│   |   ├── mongo             
│   |   ├── security           
│   |   ├── pyproject.toml  
│   |   └── uv.lock           
│   ├── frontend          # Nextjs frontend
│   |   ├── .env.local
│   |   ├── .gitignore
│   |   ├── .next
│   |   ├── app
│   │   │	├── api
│   │   │	├── favicon.ico
│   │   │	├── globals.css
│   │   │	├── layout.tsx
│   │   │	├── page.tsx
│   │   │	└── providers.tsx
│   |   ├── auth.ts
│   |   ├── components
│   |   ├── components.json
│   |   ├── config
│   |   ├── eslint.config.mjs
│   |   ├── hooks
│   |   ├── lib
│   |   ├── next-env.d.ts
│   |   ├── next.config.ts
│   |   ├── node_modules
│   |   ├── package-lock.json
│   |   ├── package.json
│   |   ├── postcss.config.mjs
│   |   ├── public
│   |   ├── tsconfig.json
│   |   └── types
│   └── package.json      # Python dependencies
├── docs/                 
│   ├── backend           # Overviews for backend services
│   |   ├── auth-token-layer.md           
│   |   ├── encription-layer.md           
│   |   ├── error-handling.md           
│   |   ├── models.md           
│   |   ├── mongo-layer.md            
│   |   └── mongo-websocket-layer.md  
│   ├── frontend          # WIll UPDATE THIS LATER
│   └── overview.md       # App Overview
└── README.md           
```

## Prerequisites

- **Node.js** 18+
- **Python** 3.12+
- **uv** (Python package manager) - [Install uv](https://docs.astral.sh/uv/getting-started/installation/)
- **MongoDB** (optional) - only if using MongoDB instead of SQLite

## Quick Start

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd nextapi
```

### 2. Install dependencies

```bash
# Install root dependencies (concurrently)
npm install

# Install frontend dependencies
cd frontend && npm install && cd ..

# Install backend dependencies
cd backend && uv sync && cd ..
```

### 3. Configure environment variables

#### Backend

| ENV | Format | Discription | Example |
| --- | --- | --- | --- |
| `ENCRYPTION_KEY` | 32 byte hex | Key for encripting api payload. | `tMh53JhX+NiHVfRnwAtopNJiCFSsA3qb8P8FNgYgiEU=`|
| `JWT_SECRET_KEY` | 32 byte hex | Key for encription jwt. | `tMh53JhX+NiHVfRnwAtopNJiCFSsA3qb8P8FNgYgiEU=`|
| `JWT_ALGORITHM` | jwt algorithm identifier  | Algorithm to use to encript jwt. | `HS256`|
| `EXPIRE_MINUTES` | Number of minutes  | Number of minutes until jst expire | `30`|
| `ALLOWED_ORIGINS` | host  | hosts allow to access api | `http://localhost:3000,http://localhost:3001`|

#### Frontend

| ENV | Format | Discription | Example |
| --- | --- | --- | --- |
| `AUTH_SECRET` | 32 byte hex | NextAuth secret. | `tMh53JhX+NiHVfRnwAtopNJiCFSsA3qb8P8FNgYgiEU=`|
| `AUTH_URL` | host | Base URL for all requests. | `http://localhost:3000`|
| `NEXT_PUBLIC_ENCRYPTION_KEY` | Same key as backends `ENCRYPTION_KEY` | Key to decript payload from api | `tMh53JhX+NiHVfRnwAtopNJiCFSsA3qb8P8FNgYgiEU=`|

---

### 4. Generate encryption keys

```bash
# Generate a 32-byte hex key for encryption
openssl rand -hex 32

# Generate a base64 secret for NextAuth
openssl rand -base64 32
```

**Important:** The `ENCRYPTION_KEY` (backend) and `NEXT_PUBLIC_ENCRYPTION_KEY` (frontend) must be identical for encrypted communication to work.

### 5. Run the development server

```bash
# From the root directory - runs both frontend and backend
npm run dev
```

This starts:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

## API Endpoints

### Public Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth` | Get session token |

### Websocket

- `ws/mongo`


## Authentication

### JWT Authentication 

Get session token form endpoint `auth`



## Environment Variables Reference

### Backend (`backend/.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ENCRYPTION_KEY` | Yes | - | 32-byte hex key for AES encryption |
| `JWT_SECRET_KEY` | Yes | - | Secret key for JWT signing |
| `JWT_ALGORITHM` | No | `HS256` | JWT algorithm |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | No | `30` | Token expiration time |
| `RATE_LIMIT_USER` | No | `60` | User requests per minute |
| `RATE_LIMIT_API_CLIENT` | No | `100` | API client requests per minute |
| `DATABASE_TYPE` | No | `sqlite` | Database type (`sqlite` or `mongo`) |
| `MONGO_URL` | No | `mongodb://localhost:27017` | MongoDB connection URL |
| `MONGO_DB_NAME` | No | `learning_scheduler` | MongoDB database name |

### Frontend (`frontend/.env.local`)

| Variable | Required | Description |
|----------|----------|-------------|
| `AUTH_SECRET` | Yes | NextAuth.js secret for session encryption |
| `AUTH_URL` | Yes | Base URL of your application |
| `NEXT_PUBLIC_ENCRYPTION_KEY` | Yes | Must match backend `ENCRYPTION_KEY` |

## Scripts

### Root

```bash
npm run dev    # Run frontend + backend concurrently
npm run api    # Run backend only
```

### Frontend (`frontend/`)

```bash
npm run dev    # Development server
npm run build  # Production build
npm run start  # Production server
npm run lint   # Run ESLint
```

### Backend (`backend/`)

```bash
uv run uvicorn main:app --reload  # Development server
uv run uvicorn main:app           # Production server
```

## Tech Stack

### Frontend
- Next.js 16.1.4
- React 19.2.3
- NextAuth 5.0.0-beta
- TypeScript 5
- Tailwind CSS 4
- crypto-js (client-side encryption)

### Backend
- FastAPI 0.128+
- SQLAlchemy 2.0+
- Motor 3.7+ (MongoDB async driver)
- Pydantic 2.0+
- python-jose (JWT)
- bcrypt (password hashing)
- PyCryptodome (AES encryption)
- slowapi (rate limiting)

## To Do
 - Document frontend
 - Create interface to perform CRUD functions on selected collection

## License

GNU

## Contact

For questions or feedback, please contact:

    Name:   Gabriella Govender
    Email: gabb3rw0cky@gmail.com
    GitHub: github.com/gabb3rw0cky
