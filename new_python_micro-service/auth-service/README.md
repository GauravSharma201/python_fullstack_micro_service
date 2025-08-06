auth-service/
├── app/
│ ├── **init**.py
│ ├── main.py
│ ├── config.py
│ ├── database.py
│ ├── models/
│ │ ├── **init**.py
│ │ └── user.py
│ ├── schemas/
│ │ ├── **init**.py
│ │ ├── user.py
│ │ └── token.py
│ ├── auth/
│ │ ├── **init**.py
│ │ ├── jwt_handler.py
│ │ ├── jwt_bearer.py
│ │ └── password.py
│ ├── routers/
│ │ ├── **init**.py
│ │ └── auth.py
│ └── utils/
│ ├── **init**.py
│ └── security.py
├── alembic/
├── requirements.txt
├── .env
└── docker-compose.yml

## Installation Steps:

```bash
venv\Scripts\activate

pip install -r requirements.txt
```
