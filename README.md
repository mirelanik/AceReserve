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
    * Time slot validation (prevents double booking).
    * Price calculation based on time and extras chosen (rackets, balls, court lighting).
2.  **Court Management:** CRUD operations, availability checks, filtering by surface type and lighting.
3.  **Coaches and Services:** Coaches can create services; clients can book sessions.
4.  **Loyalty Program:** Automatic point accumulation and level upgrade (Beginner, Silver, Gold, Platinum).

---

## 🚀 Installation and Setup

Follow the steps below to run the project locally.

### 1. Clone the Repository
```bash
git clone https://github.com/mirelanik/AceReserve.git
cd AceReserve
```

### 2. Create a Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Application

### Backend (API Server)
```bash
uvicorn src.main:app --reload
```

Server is available at: http://127.0.0.1:8000

Interactive documentation (Swagger UI): http://127.0.0.1:8000/docs

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