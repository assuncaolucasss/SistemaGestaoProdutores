import sys
import traceback

try:
    from fastapi import FastAPI, Request
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.exceptions import RequestValidationError
    from fastapi.responses import JSONResponse

    from app.models import *
    from app.models.base import create_db_and_tables
    from app.api.routes.auth import router as auth_router
    from app.api.routes.produtores import router as produtores_router
    from app.api.routes.fomentos import router as fomentos_router
    from app.api.routes.submissoes import router as submissoes_router
    from app.api.routes.usuarios import router as usuarios_router
    from app.api.routes.formulario import router as formulario_router

    app = FastAPI(title="Fomentos Agrícolas - Canaã dos Carajás")

    origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://sistema-gestao-produtores.vercel.app",
        "https://sistemagestaoprodutores.onrender.com",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        erros = []
        for erro in exc.errors():
            campo = " → ".join(str(c) for c in erro["loc"] if c not in ("body",))
            mensagem = erro["msg"].replace("Value error, ", "")
            erros.append({"campo": campo, "mensagem": mensagem})

        return JSONResponse(
            status_code=422,
            content={"detail": "Erro de validação", "erros": erros},
        )

    @app.on_event("startup")
    def on_startup():
        try:
            create_db_and_tables()
            print("✅ Banco conectado com sucesso")
        except Exception as e:
            print("❌ ERRO NO STARTUP:")
            traceback.print_exc()
            raise e

    @app.get("/")
    def root():
        return {"message": "API Fomentos Agrícolas online"}

    app.include_router(auth_router)
    app.include_router(produtores_router)
    app.include_router(fomentos_router)
    app.include_router(submissoes_router)
    app.include_router(usuarios_router)
    app.include_router(formulario_router)

    print("✅ App carregado com sucesso")

except Exception:
    print("❌ ERRO CRÍTICO NA INICIALIZAÇÃO:")
    traceback.print_exc()
    sys.exit(1)
