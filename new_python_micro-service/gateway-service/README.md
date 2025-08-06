gateway-service/
├── app/
│ ├── **init**.py
│ ├── main.py
│ ├── config.py
│ ├── middleware/
│ │ ├── **init**.py
│ │ ├── auth_middleware.py
│ │ ├── rate_limiting.py
│ │ ├── logging_middleware.py --> (removed)
│ │ └── cors_middleware.py --> (removed)
│ ├── services/
│ │ ├── **init**.py
│ │ ├── service_discovery.py
│ │ ├── circuit_breaker.py
│ │ └── load_balancer.py --> (removed)
│ ├── routers/
│ │ ├── **init**.py
│ │ ├── gateway.py
│ │ └── health.py
│ ├── utils/
│ │ ├── **init**.py
│ │ ├── http_client.py
│ │ └── response_transformer.py --> (removed)
│ └── models/ --> (removed)
│ ├── **init**.py
│ └── gateway_models.py
├── requirements.txt
├── .env
└── docker-compose.yml

## Installation Steps:

```bash
venv\Scripts\activate

pip install -r requirements.txt
```
