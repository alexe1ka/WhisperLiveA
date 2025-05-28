COMPOSE=docker compose -f docker-compose.yaml

include .env

up-asr:
        $(COMPOSE)  -p  faster-uz up -d --force-recreate asr

up-asr-trt:
        $(COMPOSE) -p faster-uz-asr up --force-recreate asr-trt