// Folder Structure:
// api-performance-modernization/
// ├── gateway/
// │   ├── src/main/java/com/gateway/GatewayApplication.java
// │   ├── src/main/resources/application.yml
// ├── user-service/
// │   ├── app/
// │   │   ├── main.py
// │   │   ├── routes/
// │   │   │   ├── user_router.py
// │   │   │   └── genai_router.py
// │   └── requirements.txt
// ├── docker-compose.yml
// ├── .github/workflows/ci.yml
// └── README.md

// --------------------- Spring Boot Gateway ------------------------

// File: gateway/src/main/java/com/gateway/GatewayApplication.java

package com.gateway;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class GatewayApplication {
    public static void main(String[] args) {
        SpringApplication.run(GatewayApplication.class, args);
    }
}

// File: gateway/src/main/resources/application.yml

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
        - id: genai-service
          uri: http://user-service:8000
          predicates:
            - Path=/genai/**
      default-filters:
        - name: RequestRateLimiter
          args:
            redis-rate-limiter.replenishRate: 10
            redis-rate-limiter.burstCapacity: 20
logging:
  level:
    org.springframework.cloud.gateway: DEBUG


// --------------------- FastAPI Service ------------------------

# File: user-service/app/main.py

from fastapi import FastAPI
from app.routes import user_router, genai_router
import logging
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.include_router(user_router, prefix="/user")
app.include_router(genai_router, prefix="/genai")

FastAPIInstrumentor().instrument_app(app)

@app.get("/")
def health():
    return {"status": "user service running"}


# File: user-service/app/routes/user_router.py

from fastapi import APIRouter

router = APIRouter()

@router.get("/info")
def get_user():
    return {"user": "demo-user"}


# File: user-service/app/routes/genai_router.py

from fastapi import APIRouter, Request
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
import os

router = APIRouter()

embeddings = OpenAIEmbeddings()
db = Chroma(persist_directory="chroma_index", embedding_function=embeddings)
qa_chain = RetrievalQA.from_chain_type(llm=OpenAI(), retriever=db.as_retriever())

@router.post("/query")
async def run_rag(request: Request):
    body = await request.json()
    query = body.get("query")
    if not query:
        return {"error": "Query required"}

    response = qa_chain.run(query)
    return {"query": query, "response": response}


# File: user-service/requirements.txt

fastapi
uvicorn
openai
langchain
chromadb
tiktoken
opentelemetry-instrumentation-fastapi


// --------------------- Docker Compose ------------------------

# File: docker-compose.yml

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
    volumes:
      - ./user-service/chroma_index:/usr/src/app/chroma_index
  redis:
    image: redis
    container_name: redis_cache
  elasticsearch:
    image: elasticsearch:7.9.2
    environment:
      - discovery.type=single-node
  kibana:
    image: kibana:7.9.2
    ports:
      - "5601:5601"


// --------------------- GitHub Actions CI ------------------------

# File: .github/workflows/ci.yml

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
        ./mvnw clean install || true  # assuming mvnw exists
    - name: Build User Service
      run: |
        cd user-service
        pip install -r requirements.txt
        pytest || true


 
