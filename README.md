# 🎾 AceReserve Court Booking System

AceReserve is a web platform that allows users to book tennis courts online. The system digitalizes the entire process, supporting:

* User profiles
* Court reservations
* Management of courts, coaches, and services
* User reviews
* Loyalty program

---

## 🛠️ Technology Stack

The project is built using the following technologies:

* **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.13+)
* **Database & ORM:** [SQLModel](https://sqlmodel.tiangolo.com/) (SQLAlchemy + Pydantic)
* **Testing:** [Pytest](https://docs.pytest.org/) (AsyncIO support)
* **Code Quality:** [Black](https://github.com/psf/black) (Formatter), [Pylint](https://pylint.pycqa.org/) (Linter), [MyPy](http://mypy-lang.org/) (Type Checker)

---

## ✨ Key Features


1.  **Reservation System:**
    * Users can create, cancel and modify reservations.
    * Time slot validation and double booking prevention.
    * Price calculation based on time and extras chosen (rackets, balls, court lighting).
2.  **Court Management:** CRUD operations, availability checks, filtering by surface type and lighting.
3.  **Coaches and Services:** Coaches can create services; users can book sessions.
4.  **Loyalty Program:** Automatic point accumulation and level upgrade (Beginner, Silver, Gold, Platinum).

---

## 🚀 Installation & Setup

This project uses **[uv](https://docs.astral.sh/uv/)** for dependency management and virtual environments.

### 1. Prerequisites
Ensure you have `uv` installed. If not:
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone and Sync

```bash
# Clone the repository
git clone https://github.com/mirelanik/AceReserve.git
cd AceReserve

# Creates .venv and installs dependencies
uv sync
```

### 3. Environment Configuration

Create a .env file in the root directory. You can start by copying the example:

```bash
cp .env.example .env
```

**Required variables:**
- `SECRET_KEY` - JWT secret key (generate a secure random string)
- `DATABASE_URL` - Database connection string
- `FIRST_ADMIN_EMAIL` - Initial admin email
- `FIRST_ADMIN_PASSWORD` - Initial admin password

### 4. Activating the Virtual Environment (Optional)

If you need to activate the virtual environment manually:
```bash
# macOS/Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

Note: When using `uv run`, activation is automatic.

---

## ▶️ Running the Application

### Backend (API Server)
```bash
# Default port (8000)
uv run uvicorn src.main:app --reload

# Custom port
uv run uvicorn src.main:app --reload --port 8080
```

Server is available at: http://127.0.0.1:8000

Interactive documentation (Swagger UI): http://127.0.0.1:8000/docs

---

## 🧪 Running Tests

To run the test suite with pytest:

```bash
uv run pytest
```

To run with coverage report:

```bash
uv run pytest --cov=src
```

---

## 📂 Project Structure

```
AceReserve/
├── src/
│   ├── auth/           # Authentication logic, registration, and JWT tokens
│   ├── core/           # Database configurations and settings
│   ├── models/         # SQLModel classes (database tables)
│   ├── routers/        # API Endpoints (routers)
│   ├── services/       # Business logic (ReservationService, CourtService, etc.)
│   └── main.py         # FastAPI application entry point
├── tests/              # Test directory
│   ├── routers/        # API endpoint tests
│   ├── services/       # Business logic tests
│   └── conftest.py     # Pytest configurations and fixtures
├── pyproject.toml      
├── README.md           
└── uv.lock             
```