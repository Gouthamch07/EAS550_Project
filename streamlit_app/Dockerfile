FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (needed for psycopg2)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first (to leverage Docker cache)
COPY requirements.txt .

# Install Python dependencies during the BUILD phase
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY streamlit_app/ .

# Expose the port
EXPOSE 8501

# Healthcheck to ensure Streamlit is running
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Default command to run the app
CMD ["streamlit", "run", "home.py", "--server.port=8501", "--server.address=0.0.0.0"]