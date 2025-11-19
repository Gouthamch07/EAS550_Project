# Global Food & Nutrition Explorer

This is the group project for EAS 550: Data Models and Query Languages, submitted by Akash Ankush Kamble, Nidhi Rajani, and Goutham Chengalvala.

## Project Overview

The "Global Food & Nutrition Explorer" is a database application designed to ingest, clean, and structure the vast Open Food Facts dataset. Our goal is to transform this raw, complex data into a normalized relational database, making it accessible for nutritional analysis and consumer insights.

This repository contains the complete pipeline for Phase 1, which focuses on building a robust and secure database foundation.

## Phase 1: Database Foundation (OLTP)

### Core Technologies
- **Containerization:** Docker & Docker Compose
- **Database:** PostgreSQL 15
- **Data Ingestion & Logic:** Python 3, Pandas, SQLAlchemy
- **Version Control:** Git & GitHub

### How to Run the Pipeline

**Prerequisites:**
- Docker Desktop installed and running.
- Python 3.8+ and `pip` installed.

**Step 1: Clone the Repository**
```bash
git clone https://github.com/Gouthamch07/EAS550_Project.git
cd EAS550_Project
```

**Step 2: Set Up the Python Environment**
It is recommended to use a virtual environment.
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Step 3: Launch the Database**
This command will start the PostgreSQL and pgAdmin containers. On the first run, it will automatically create the database schema and security roles by executing the files in the `sql/` directory.
```bash
docker-compose -f docker/docker-compose.yml up -d
```

**Step 4: Run the Data Ingestion Script**
This script will download the raw data, clean it, and populate the running database.
```bash
python scripts/ingest_data.py
```

The pipeline is now complete! The database `food_nutrition_db` is fully populated and ready for querying.

### Accessing the Database

You can connect to the database using any standard SQL client or the included pgAdmin interface.

- **pgAdmin URL:** `http://localhost:8080`
- **Email:** `admin@food-nutrition.com`
- **Password:** `admin`

**Server Connection Details:**
- **Host:** `food_nutrition_db`
- **Port:** `5432`
- **Database:** `food_nutrition_db`
- **Username/Password:** Use the `postgres` superuser, `analyst_user`, or `app_service_user` credentials.

If you need a video demonstration of the setup process, please refer to the following link: [Video Demonstration](https://youtu.be/WSvt6auAOsg)