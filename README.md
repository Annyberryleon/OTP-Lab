# OTP Authentication Lab

A hands-on DevOps and cybersecurity laboratory for building, containerizing, testing, monitoring, and deploying a secure OTP authentication service.

The project demonstrates practical experience with Python, Flask, Redis, Docker, Docker Compose, Prometheus, Grafana, GitHub Actions, and GitHub Container Registry.

## Project Overview

OTP-Lab is a small authentication API that generates and verifies six-digit One-Time Passwords (OTPs).

The application includes security controls such as:

- OTP expiration
- Maximum verification attempts
- API rate limiting
- Secure random OTP generation
- Constant-time OTP comparison
- Authentication event logging
- Automated testing
- Health checks
- Prometheus metrics
- Grafana monitoring
- Containerized deployment
- CI/CD with GitHub Actions
- Docker image publishing to GitHub Container Registry

The project is designed as a practical DevOps portfolio laboratory rather than a production banking authentication system.

## Architecture

The application runs as a multi-container Docker Compose stack.

```text
Client
  |
  | HTTP
  v
OTP-Lab
Flask + Gunicorn
  |
  +------------------+
  |                  |
  v                  v
Redis             Prometheus
Rate Limiting     Metrics
                     |
                     v
                  Grafana
                  Dashboard
```

## Docker Compose Services

The application stack contains four services:

| Service | Purpose | Port |
|---|---|---:|
| `otp-lab` | Flask OTP API running with Gunicorn | 5000 |
| `redis` | Rate-limiting storage | 6379 |
| `prometheus` | Metrics collection | 9090 |
| `grafana` | Metrics visualization and dashboards | 3000 |

Docker named volumes are used to persist Prometheus and Grafana data.
## Technology Stack

- Python 3.13
- Flask
- Gunicorn
- Redis
- Flask-Limiter
- Prometheus
- Grafana
- Docker
- Docker Compose
- Git
- GitHub
- GitHub Actions
- GitHub Container Registry
- Pytest

## OTP Security Flow

The OTP authentication process follows these steps:

1. A client requests an OTP from the `/otp/generate` endpoint.
2. The application generates a cryptographically secure six-digit OTP using Python `secrets`.
3. An expiration time is created using `OTP_EXPIRY_SECONDS`.
4. The OTP is returned to the client for laboratory testing.
5. The client submits the OTP to `/otp/verify`.
6. The application checks whether the OTP has expired.
7. The application checks whether the maximum failed attempts have been reached.
8. The submitted OTP is compared using `secrets.compare_digest()`.
9. Successful verification increments the success metric and invalidates the stored OTP.
10. Failed verification attempts are logged without recording the actual OTP.
11. Excessive failed attempts are blocked.
12. Prometheus records authentication events for Grafana monitoring.

### Security Controls

| Control | Implementation |
|---|---|
| Secure OTP generation | Python `secrets` module |
| OTP length | 6 digits |
| OTP expiration | Configurable through environment variables |
| Maximum attempts | Configurable through environment variables |
| Constant-time comparison | `secrets.compare_digest()` |
| API rate limiting | Flask-Limiter + Redis |
| Authentication logging | Application log file |
| Sensitive data protection | OTP values are not written to logs |
| Monitoring | Prometheus + Grafana |
## API Endpoints

### Health Check

```http
GET /health
```

Returns the health status of the application.

### Generate OTP

```http
GET /otp/generate
```

Generates a six-digit OTP and returns its expiration time.

### Verify OTP

```http
POST /otp/verify
```

Accepts a JSON payload containing the OTP:

```json
{
  "otp": "123456"
}
```

### Prometheus Metrics

```http
GET /metrics
```

Exposes application metrics for Prometheus.
## Local Deployment

### Prerequisites

Before running OTP-Lab locally, install:

- Docker Desktop
- Git

Docker Desktop should be running before starting the application.

### Clone the Repository

```bash
git clone https://github.com/Annyberryleon/OTP-Lab.git
cd OTP-Lab
```

### Configure Environment Variables

Create a `.env` file in the project root with the required configuration:

```text
OTP_EXPIRY_SECONDS=300
MAX_ATTEMPTS=5
REDIS_HOST=localhost
```

### Start the Application

Build and start the Docker Compose stack:

```bash
docker compose up -d --build
```

Check the running containers:

```bash
docker compose ps
```

### Access Services

- OTP API: `http://localhost:5000`
- Health check: `http://localhost:5000/health`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`

### Stop the Application

```bash
docker compose down
```
## Testing

OTP-Lab includes automated tests using Pytest.

The test suite covers:

- OTP generation
- Six-digit OTP format
- OTP expiration
- Successful OTP verification
- Invalid OTP verification
- Maximum failed verification attempts
- Authentication logging

### Run Tests Locally

Run the test suite directly using the Python virtual environment:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## Monitoring

OTP-Lab exposes application metrics through the `/metrics` endpoint.

Prometheus collects these metrics every 5 seconds.

Grafana uses Prometheus as its data source to visualize authentication activity.

### Prometheus

Prometheus is available at:

```text
http://localhost:9090
```

The Prometheus configuration uses the OTP-Lab container as its scrape target:

```yaml
global:
  scrape_interval: 5s

scrape_configs:
  - job_name: "otp-lab"
    static_configs:
      - targets: ["otp-lab:5000"]
```
### Grafana

Grafana is available at:

```text
http://localhost:3000
```

The Grafana dashboard is named **OTP Lab Monitoring**.

The dashboard tracks:

- OTP Generations
- Successful OTP Verifications
- Failed OTP Verifications
- Expired OTP Attempts
- Blocked OTP Attempts

Prometheus and Grafana data are stored using Docker named volumes so monitoring data persists when containers are recreated.

## CI/CD

GitHub Actions automatically runs the test suite and builds and publishes the Docker image to GitHub Container Registry when changes are pushed to the `main` branch.

The CI/CD pipeline includes:

- Repository checkout
- Python environment setup
- Dependency installation
- Automated Pytest execution
- Docker image build
- GitHub Container Registry authentication
- Docker image publishing

## Docker Image

The application image is published to GitHub Container Registry.

```text
ghcr.io/annyberryleon/otp-lab:latest
```

## Portfolio Skills Demonstrated

- Python application development
- REST API development
- Authentication security controls
- Redis-based rate limiting
- Automated testing
- Docker containerization
- Docker Compose orchestration
- Prometheus monitoring
- Grafana dashboards
- Git version control
- GitHub Actions CI/CD
- GitHub Container Registry
- Infrastructure and deployment troubleshooting
