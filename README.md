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
        - // const API_URL=http://localhost:8000
        - const API_URL = process.env.NEXT_PUBLIC_API_URL;
- Change it to this:
        - const API_URL=http://localhost:8000
        - // const API_URL = process.env.NEXT_PUBLIC_API_URL;

2.

- Make .env file in frontend folder
- Put this into it: NEXT_PUBLIC_API_URL=http://localhost:8000

### 4. Start frontend server

Development:
- npm run dev

Production:
- npm run build
- npm run start

## 🧠 Explanation of Approach

The system is designed as a document processing pipeline that automatically extracts, validates, and stores structured data from uploaded files.

---

### 🔄 1. Document Upload

The user uploads a document through the frontend.  
The file is sent to the backend API for processing.

---

### 📄 2. Data Extraction

The backend reads the uploaded file and uses an extraction service to convert unstructured document content into structured data (`extracted_data`).

This includes:
- Header information (supplier, dates, totals, etc.)
- Line items (product details, quantities, prices)

---

### 🧩 3. Data Mapping

Extracted data is mapped into database models:
- Header fields are stored in the `Document` model (table)
- Line items are stored in the `LineItem` model

---

### ✅ 4. Validation

The system validates extracted data using business rules:
- Required fields check
- Date validation
- Mathematical consistency (subtotal, total, line items)
- Duplicate document detection

If validation fails, errors are stored and the document is marked for review.

---

### 💾 5. Persistence

After validation:
- Valid documents are marked as `validated`
- Invalid documents are marked as `needs_review`
- All data is stored in PostgreSQL database

---

### 📊 6. Response

The backend returns:
- Extracted data
- Validation results
- Document status

This is displayed in the frontend for user review.

## 🤖 AI Tools Used

- ChatGPT - Used during the development of the backend and overall system to accelerate development
- Cursor - Used mainly for frontend productivity and css files

## 🔧 Improvements I Would Make

Although the core requirements are completed, several improvements would make the system more robust and user-friendly:

### 1. Document Preview
Add a preview of the uploaded document (PDF/Image) so users can visually compare the extracted data with the source.

### 2. Search & Filter on Dashboard
Enhance the dashboard with:
- Search by supplier, document number, or status  
- Filters (validated, needs_review, uploaded)   

### 3. Performance Optimizations
For large documents or batches: 
- Cache previous validation results  

### 4. Asynchronous Batch Processing
Improve the user experience for high-volume uploads:
- Move heavy OCR and extraction tasks to background workers.
- Implement WebSockets to provide real-time progress updates on the dashboard while documents are being processed.

## 📘 Documentation

Interactive API documentation is available at https://smartdocs-yy9e.onrender.com/docs#/