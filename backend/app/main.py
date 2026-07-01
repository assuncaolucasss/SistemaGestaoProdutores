import traceback

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from app.models import *
from app.models.base import create_db_and_tables
from app.api.routes.auth import router as auth_router
from app.api.routes.produtores import router as produtores_router
from app.api.routes.fomentos import router as fomentos_router
from app.api.routes.submissoes import router as submissoes_router
from app.api.routes.usuarios import router as usuarios_router
from app.api.routes.formulario import router as formulario_router

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://sistema-gestao-produtores.vercel.app",
    "https://sistemagestaoprodutores.onrender.com",
]

fastapi_app = FastAPI(
    title="Fomentos Agrícolas - Canaã dos Carajás",
    redirect_slashes=False,
)

def add_cors_headers(request: Request, response: JSONResponse):
    origin = request.headers.get("origin")
    if origin in origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
    return response

@fastapi_app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    erros = []
    for erro in exc.errors():
        campo = " → ".join(str(c) for c in erro["loc"] if c not in ("body",))
        mensagem = erro["msg"].replace("Value error, ", "")
        erros.append({"campo": campo, "mensagem": mensagem})

    response = JSONResponse(
        status_code=422,
        content={"detail": "Erro de validação", "erros": erros},
    )
    return add_cors_headers(request, response)

@fastapi_app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    response = JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )
    return add_cors_headers(request, response)

@fastapi_app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    traceback.print_exc()
    response = JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor"},
    )
    return add_cors_headers(request, response)

@fastapi_app.on_event("startup")
def on_startup():
    create_db_and_tables()
    print("✅ Banco conectado com sucesso")

@fastapi_app.get("/")
def root():
    return {"message": "API Fomentos Agrícolas online"}

fastapi_app.include_router(auth_router)
fastapi_app.include_router(produtores_router)
fastapi_app.include_router(fomentos_router)
fastapi_app.include_router(submissoes_router)
fastapi_app.include_router(usuarios_router)
fastapi_app.include_router(formulario_router)

app = CORSMiddleware(
    app=fastapi_app,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
