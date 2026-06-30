# Baufest-AI-Repo-Test

Este repositorio incluye una aplicación **FastAPI** en la carpeta `backend` que implementa un flujo básico de autenticación con **JWT**.

## Características

- Endpoint para autenticar al usuario fijo `admin` con la contraseña `admin123`
- Emisión de `access_token` con expiración de **300 segundos**
- Endpoint para refrescar el token usando un `refresh_token`
- Gestión de dependencias con **Poetry**
- Hashing de contraseñas con **passlib[bcrypt]** y `bcrypt >=3.2,<4.0`
- Archivos `Dockerfile` y `docker-compose.yml` para despliegue con Docker

## Estructura

```text
.
├── backend
│   ├── app
│   │   └── main.py
│   ├── Dockerfile
│   ├── poetry.lock
│   └── pyproject.toml
└── docker-compose.yml
```

## Requisitos

- Python 3.12+
- Poetry 2+
- Docker y Docker Compose (opcional)

## Uso local con Poetry

```bash
cd backend
export JWT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
export ADMIN_USERNAME="admin"
export ADMIN_PASSWORD_HASH='$2b$12$kXf36UAup8oGZcwbLPoWF.uRZVSogsi4wqP8D0TGrZkXYSywGGsk6'
poetry install
poetry run uvicorn app.main:app --reload
```

La API quedará disponible en `http://127.0.0.1:8000`.

## Obtener token

```bash
curl -X POST http://127.0.0.1:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

Respuesta esperada:

```json
{
  "access_token": "<jwt>",
  "refresh_token": "<jwt>",
  "token_type": "bearer",
  "expires_in": 300
}
```

## Refrescar token

```bash
curl -X POST http://127.0.0.1:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<jwt>"}'
```

Respuesta esperada:

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "expires_in": 300
}
```

## Uso con Docker

Desde la raíz del proyecto:

```bash
export JWT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
export ADMIN_USERNAME="admin"
export ADMIN_PASSWORD_HASH='$2b$12$kXf36UAup8oGZcwbLPoWF.uRZVSogsi4wqP8D0TGrZkXYSywGGsk6'
docker compose up --build
```

Luego podrás consumir la API en `http://127.0.0.1:8000`.

El valor de `ADMIN_PASSWORD_HASH` del ejemplo corresponde a la contraseña `admin123` generada con `passlib[bcrypt]`.

## Endpoints disponibles

- `GET /` - verificación simple del servicio
- `POST /auth/token` - autenticación y emisión de tokens
- `POST /auth/refresh` - generación de un nuevo access token a partir del refresh token
