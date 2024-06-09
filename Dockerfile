# Stage 1: Build dependencies and export requirements.txt
FROM python:3.12-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && apt-get clean

# Set the working directory in the container
WORKDIR /app

# Copy only the files needed for installing dependencies
COPY pyproject.toml poetry.lock /app/

# Install project dependencies using Poetry and export to requirements.txt
RUN pip install poetry \
    && poetry export --without-hashes --format=requirements.txt > requirements.txt

# Stage 2: Copy application code and run Streamlit app
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt from the builder stage
COPY --from=builder /app/requirements.txt /app/

# Install project dependencies from requirements.txt
RUN pip install -r requirements.txt

# Copy the application code into the container
COPY . /app 

# Expose the port the app runs on
EXPOSE 8501

# Command to run the Streamlit app
CMD ["streamlit", "run", "recommendation_games/main.py"]