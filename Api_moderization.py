// Project: API Performance Modernization

// Folder Structure:
// api-performance-modernization/
// ├── gateway/                        # Spring Boot API Gateway
// │   ├── src/main/java/com/gateway
// │   ├── application.yml
// ├── user-service/                  # FastAPI Microservice
// │   ├── app/
// │   │   ├── main.py
// │   │   ├── routes/
// │   │   ├── services/
// │   │   └── utils/
// │   └── requirements.txt
// ├── docker-compose.yml             # Containers for services, Redis, ELK
// ├── .github/workflows/ci.yml       # GitHub Actions Workflow
// └── README.md

// --- Spring Boot Gateway (Java) ---
// src/main/java/com/gateway/GatewayApplication.java

@SpringBootApplication
public class GatewayApplication {
    public static void main(String[] args) {
        SpringApplication.run(GatewayApplication.class, args);
    }
}

// application.yml
server:
  port: 8080
spring:
  application:
    name: gateway-service
  cloud:
    gateway:
      routes:
        - id: user-service
          uri: http://user-service:8000
          predicates:
            - Path=/user/**
      default-filters:
        - name: RequestRateLimiter
          args:
            redis-rate-limiter.replenishRate: 10
            redis-rate-limiter.burstCapacity: 20

// --- FastAPI User Service (Python) ---
// app/main.py

from fastapi import FastAPI
from app.routes import user_router
import logging
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

app = FastAPI()
app.include_router(user_router, prefix="/user")
FastAPIInstrumentor().instrument_app(app)

@app.get("/")
def health():
    return {"status": "user service running"}

// app/routes/user_router.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/info")
def get_user():
    return {"user": "demo-user"}

// --- Docker Compose ---
// docker-compose.yml
version: '3.9'
services:
  gateway:
    build: ./gateway
    ports:
      - "8080:8080"
    depends_on:
      - user-service
  user-service:
    build: ./user-service
    ports:
      - "8000:8000"
  redis:
    image: redis
  elasticsearch:
    image: elasticsearch:7.9.2
    environment:
      - discovery.type=single-node
  logstash:
    image: logstash:7.9.2
  kibana:
    image: kibana:7.9.2
    ports:
      - "5601:5601"

// --- GitHub Actions ---
// .github/workflows/ci.yml
name: CI Pipeline
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    services:
      docker:
        image: docker:19.03.12
    steps:
    - uses: actions/checkout@v2
    - name: Build Gateway
      run: |
        cd gateway
        ./mvnw clean install
    - name: Build User Service
      run: |
        cd user-service
        pip install -r requirements.txt
        pytest

