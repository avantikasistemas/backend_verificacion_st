from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from Config.db import BASE, engine
from Middleware.get_json import JSONMiddleware
from Middleware.auth_middleware import verify_jwt_middleware
from Router.Verificacion import verificacion_router
from Router.Inspeccion import inspeccion_router
from Router.Login import login_router
from pathlib import Path

route = Path.cwd()
app = FastAPI()
app.title = "Avantika Módulo 5004"
app.version = "0.0.1"

app.mount("/Uploads", StaticFiles(directory=f"{route}/Uploads"), name="Uploads")

# Middlewares en orden
app.add_middleware(JSONMiddleware)
app.middleware("http")(verify_jwt_middleware)  # Middleware de autenticación JWT
app.add_middleware(
    CORSMiddleware,allow_origins=["*"],  # Permitir todos los orígenes; para producción, especifica los orígenes permitidos.
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos; puedes especificar los métodos permitidos.
    allow_headers=["*"],  # Permitir todos los encabezados; puedes especificar los encabezados permitidos.
)

# Routers
app.include_router(login_router, prefix="/api")
app.include_router(verificacion_router, prefix="/api")
app.include_router(inspeccion_router, prefix="/api")

BASE.metadata.create_all(bind=engine)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8007,
        reload=True
    )
