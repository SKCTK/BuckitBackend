# Finance Hack API

[![Docker Image Build and Push](https://github.com/AzureAIDevHackathon/Backend/actions/workflows/docker-build-and-test-validation.yml/badge.svg)](https://github.com/AzureAIDevHackathon/Backend/actions/workflows/docker-build-and-test-validation.yml)

## Getting Started

### Docker Setup (Recommended)

1. Sign up for Docker on [Docker Hub](https://hub.docker.com/repositories/chitangchin)
2. Download and install [Docker Desktop](https://docs.docker.com/get-started/get-docker/)

3. Start Docker Desktop and ensure it's running (look for the Docker icon in your system tray/menu bar)
   
4. setup
```
git clone https://github.com/AzureAIDevHackathon/Backend.git
cd backend
code . -r
git checkout dev
```

5. rename env.sample to .env

Heres the secret you want to paste into .env:
```
SECRET_KEY=yaybycydye
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
SA_PASSWORD=azureaihack2025!

# Database configuration
DB_USER=sa
DB_PASSWORD=azureaihack2025!
DB_SERVER=localhost
DB_PORT=1433
DB_NAME=FinancialBudgetApp
```

6. run:
```
docker compose up -d --build
```

7. goto: localhost:8080/docs

---

### Local Backend Setup

1. Create a virtual environment

```
python -m venv .venv
```

2. Activate the virtual environment

In windows: 

Powershell terminal:
```
.venv\Scripts\Activate.ps1
```

Bash terminal:
```
source .venv/Scripts/activate
```


In Linux, macOS

```
source .venv/bin/activate
```

3. Upgrading pip

```
python -m pip install --upgrade pip
```

4. Installing packages

```
pip install -r requirements.txt
```

5. Running the server

The server will run on:

```
localhost:8080
```
---

See [routes_documentation.md](routes_documentation.md) for the complete API documentation and workflow explanation.
