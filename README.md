# API-Performance-Modernization

API Performance Modernization
Tools Used

Java: Spring Boot for API Gateway
Python: FastAPI for User Service
Docker: Containerization of services, Redis, and ELK stack
Redis: Rate limiting
ELK Stack: Elasticsearch, Logstash, Kibana for observability
OpenTelemetry: Distributed tracing
GitHub Actions: CI/CD pipeline
Maven: Dependency management for Spring Boot
Pytest: Testing for FastAPI service

Aim
The project aims to build a modern, scalable microservice architecture with a Spring Boot API Gateway and a FastAPI User Service, incorporating rate limiting, observability with the ELK stack, distributed tracing via OpenTelemetry, and automated CI/CD pipelines using GitHub Actions.
Introduction
This project implements a high-performance, microservice-based backend system. The Spring Boot Gateway handles routing and rate limiting, while the FastAPI User Service manages user-related operations. The system is containerized using Docker, with Redis for rate limiting, ELK stack for logging and observability, and OpenTelemetry for distributed tracing. Continuous integration and deployment are automated via GitHub Actions.
Dataset
No external dataset is used. The project focuses on API interactions, with sample endpoints returning demo data (e.g., {"user": "demo-user"}).
Method
Phase 1: API Gateway Setup
The Spring Boot Gateway serves as the entry point, routing requests to microservices and enforcing rate limiting using Redis.

Routing: Configures routes to the User Service for /user/** paths.
Rate Limiting: Implements Redis-based rate limiting with a replenish rate of 10 requests and a burst capacity of 20.

Implementation:

Tools Used: Spring Boot, Redis, Java
Configuration (application.yml):server:
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


Code Example (GatewayApplication.java):@SpringBootApplication
public class GatewayApplication {
    public static void main(String[] args) {
        SpringApplication.run(GatewayApplication.class, args);
    }
}



Phase 2: User Service Development
The FastAPI User Service handles user-related endpoints, with OpenTelemetry instrumentation for distributed tracing.

Endpoints: Provides a health check (/) and a user info endpoint (/user/info).
Tracing: Integrates OpenTelemetry for monitoring API performance.

Implementation:

Tools Used: FastAPI, Python, OpenTelemetry
Code Example (main.py):from fastapi import FastAPI
from app.routes import user_router
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

app = FastAPI()
app.include_router(user_router, prefix="/user")
FastAPIInstrumentor().instrument_app(app)

@app.get("/")
def health():
    return {"status": "user service running"}


Code Example (user_router.py):from fastapi import APIRouter

router = APIRouter()

@router.get("/info")
def get_user():
    return {"user": "demo-user"}



Phase 3: Containerization and Observability
Docker Compose orchestrates the Gateway, User Service, Redis, and ELK stack (Elasticsearch, Logstash, Kibana) for observability.

Containerization: Each service runs in a separate Docker container.
Observability: ELK stack provides logging and visualization, accessible via Kibana on port 5601.

Implementation:

Tools Used: Docker, Elasticsearch, Logstash, Kibana
Docker Compose (docker-compose.yml):version: '3.9'
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



Phase 4: CI/CD Pipeline
GitHub Actions automates the build and test process for both the Gateway and User Service.

Build: Compiles the Spring Boot Gateway using Maven and installs Python dependencies for the User Service.
Test: Runs Pytest for the FastAPI service.

Implementation:

Tools Used: GitHub Actions, Maven, Pytest
CI Pipeline (ci.yml):name: CI Pipeline
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



Dependencies

Java: Spring Boot, Maven
Python: FastAPI, OpenTelemetry, Pytest
Docker: Docker Compose
Redis: Rate limiting
ELK Stack: Elasticsearch (7.9.2), Logstash (7.9.2), Kibana (7.9.2)

Results

Gateway: Successfully routes requests to the User Service on port 8080 with Redis-based rate limiting.
User Service: Provides functional endpoints (/user/info, /) with OpenTelemetry tracing.
Observability: ELK stack enables logging and visualization, accessible via Kibana on port 5601.
CI/CD: GitHub Actions pipeline builds and tests both services, ensuring deployment reliability.
Containerization: All services run seamlessly in Docker containers, with dependencies managed via Docker Compose.

Conclusion
The API Performance Modernization project delivers a scalable, observable, and maintainable microservice architecture. By combining Spring Boot, FastAPI, Redis, ELK stack, and OpenTelemetry, it achieves robust routing, rate limiting, and distributed tracing. The Dockerized setup and automated CI/CD pipeline ensure easy deployment and consistent performance, making it a modern solution for high-performance API systems.
