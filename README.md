# 📄 SmartDocs - Document Processing System

A full-stack application that extracts, validates, and stores structured data from uploaded documents.

---

# 🚀 Live Demo

https://smart-docs-five.vercel.app/

---

# ⚙️ Tech Stack

- Backend: FastAPI (Python)
- Frontend: Next.js (React)
- Database: PostgreSQL

---

## 🖥️ Local Setup

This project can be run locally with a FastAPI backend and a Next.js frontend.
U need to have Node.js and Python installed.

First of all, clone the project using: git clone https://github.com/harun20035/SmartDocs

---

## 🗄️ Database Setup

This project uses PostgreSQL as the database.

You need to create your own local or cloud database instance before running the backend.

---

### 1. Create a database

You can use one of the following options:

- Local PostgreSQL installation
- Cloud database (e.g. Supabase, Neon, Railway)

Create a new database, for example:

CREATE DATABASE smartdocs_db;

---

## 🔐 Environment Variables

To run the project locally, you must create your own `.env` file in the backend directory.

You can use the provided `.env.example` as a template.

---

### 1. Create a .env file

Create a .env file in the backend directory and add your database connection string:
DATABASE_URL=postgresql://username:password@localhost:5432/your_db_name

---

## 📦 Backend Setup

Follow these steps to run the backend locally.

---

### 1. Navigate to backend folder

cd your-project/backend or only cd backend

### 2. Create virtual environment

python -m venv venv (if you use VSCode you can do Ctrl + Shift + P and type > and select Python: Create environment)

You can activate (if not activated automatically) the environment using: venv\Scripts\activate

### 3. Install dependencies

pip install -r requirements.txt

### 4. Start backend server

uvicorn app.main:app --reload

If configured correctly, database tables will be created automatically on startup using SQLAlchemy models.

---

## 💻 Frontend Setup

Follow these steps to run the frontend locally.

---

### 1. Navigate to frontend folder

cd your-project/frontend or only cd frontend


### 2. Install dependencies

npm install

### 3. Change API URL to localhost

For this one you have 2 options:

1. 

- Go to every page.js file in frontend
- Find this piece of code: 
        // const API_URL=http://localhost:8000
        const API_URL = process.env.NEXT_PUBLIC_API_URL;
- Change it to this:
        const API_URL=http://localhost:8000
        // const API_URL = process.env.NEXT_PUBLIC_API_URL;

2.

- Make .env file in frontend folder
- Put this into it: NEXT_PUBLIC_API_URL=http://localhost:8000

### 4. Start frontend server

Development:
- npm run dev

Production:
- npm run build
- npm run start