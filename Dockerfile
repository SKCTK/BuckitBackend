FROM python:3.12
WORKDIR /app

# Install ODBC dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    unixodbc \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy in the source code
COPY app ./app
EXPOSE 8080

# Setup an app user so the container doesn't run as the root user
RUN useradd app
USER app

# Update this line to point to the correct module path
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]