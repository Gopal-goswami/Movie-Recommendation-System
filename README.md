# 🎬 Premium OTT Movie Recommendation System
### 🚀 CODTECH IT SOLUTIONS INTERNSHIP - TASK 2

A full-stack, real-time movie streaming and recommendation platform built as a **simple project** during my internship at **CodTech IT Solutions**. 

This application features a complete user authentication gateway and a seamless content delivery layout, using a **MySQL database** to handle user security profiles as well as store the structured 100-movie blockbuster catalog.

---

## 🛠️ Core Internship Project Features

- **MySQL Authentication System:** A dedicated relational user framework that handles user registration and login flows securely.
- **Structured Movie Datastore:** Fully handles a catalog of 100 movies with custom attributes (`name`, `genre`, `poster_url`, `video_url`) directly pulled from live API mappings inside MySQL.
- **Dynamic Hybrid Matrix Recommendation:** Computes user interest profiles and content similarities instantly using `scikit-learn`'s Cosine Similarity Matrix.
- **Flawless UI Container Swapping:** Fully state-driven routing using Streamlit's internal session states (`st.session_state`), switching streaming titles seamlessly without breaking active sessions.
- **Embedded Zero-Error Video Player:** Patched with high-speed working universal and blockbuster movie trailers, bypassing any standard third-party embedding block restrictions.
- **Secure Configuration Management:** Fully protected from API keys and database password leaks on GitHub via isolated `.gitignore` layers.

---

## 🧱 Technology Stack Used

- **Database Engine:** MySQL Server (Handles User Authentication and Movie Inventory Storage)
- **Frontend UI:** Streamlit (Custom Premium Dark Theme CSS layout)
- **Backend API:** FastAPI & Uvicorn (High-performance Async routing)
- **Data Engineering:** Pandas & NumPy
- **Machine Learning Layer:** Scikit-Learn (Cosine Pairwise Similarity Matrix)
- **Security Framework:** Bcrypt (Secure salted password hashing for authentication data)

---

## 📂 Project Structure

```text
├── db_config.py          # Centralized Secrets Management (Database Passwords & API Keys) [GIT-IGNORED]
├── main.py               # FastAPI Backend & Live Matrix Recommendation Engine
├── app.py                # Streamlit Premium OTT Web Frontend & Authentication System
├── setup_populate.py     # Automation Script to Initialize DB and Populate 100 Blockbuster Metadata
├── requirements.txt      # Automated Pip Dependencies Manifest
└── .gitignore            # Security filters ensuring raw credentials stay hidden
