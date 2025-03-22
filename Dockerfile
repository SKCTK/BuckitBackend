FROM python:3.12
WORKDIR /app

# Install ODBC dependencies and Microsoft ODBC Driver 17
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        gnupg2 \
        lsb-release \
        unixodbc \
        unixodbc-dev && \
    # Add Microsoft repository with proper key
    curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/microsoft-keyring.gpg] https://packages.microsoft.com/debian/$(lsb_release -rs)/prod $(lsb_release -cs) main" > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17 && \
    # Clean up
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

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