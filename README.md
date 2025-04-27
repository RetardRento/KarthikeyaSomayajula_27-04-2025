# 📊 Store Monitoring System

> Assignment Submission for **LOOP**  
> Developed by: **Karthikeya Somayajula**

---

## 🚀 Project Overview

This project is a lightweight Store Monitoring system built with **FastAPI** and **PostgreSQL**.  
It allows generating and downloading reports based on store data via a clean API interface.

Designed for rapid deployment, easy testing, and clean modularity.

---

## 🛠️ Tech Stack

- **Backend:** FastAPI
- **Database:** PostgreSQL
- **ORM:** psycopg2
- **Testing:** Custom Python CLI (`test.py`)
- **Server:** Uvicorn

---

## 📦 Features

- 📈 Fetch and generate store reports on-demand
- 📥 Download generated reports easily
- 🔒 Secure database connection via `.env` file
- ⚡ Fast and lightweight architecture
- 🧩 Modular codebase (APIs and utilities separated)

---

## 📂 Project Structure

```
├── apis/         # API route handlers
├── utils/        # Utility functions (e.g., report generation, error handling)
├── main.py       # FastAPI application entry point
├── test.py       # CLI-based testing script
├── requirements.txt
├── .env          # Environment variables file (to be created manually)
└── README.md     # Project documentation
```

---

## 🏁 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/RetardRento/KarthikeyaSomayajula_27-04-2025
cd KarthikeyaSomayajula_27-04-2025
```

---

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

> ℹ️ **Note:**  
> Some miscellaneous packages (like for LightningAI setup) are included.  
> It's recommended to install all for smooth setup.

---

### 3. Setup Environment Variables

Create a `.env` file in the root directory with the following contents:

```env
user=your_username
password=your_password
host=your_host
port=your_port
dbname=your_database_name
```

---

### 4. Run the FastAPI Server

```bash
uvicorn main:app --reload
```

---

### 5. Test the API

In a new terminal, run the test script:

```bash
python test.py
```

Follow the on-screen options to send requests and download reports.

---

## 🧹 Good Practices

- ✅ Ensure your PostgreSQL database is running and accessible.
- ✅ Check your `.env` values before starting the server.
- ✅ (Optional) Use a Python virtual environment to isolate project dependencies.

---

## 📬 Contact

**Karthikeya Somayajula**  
karthik.somayajula12@gmail.com


