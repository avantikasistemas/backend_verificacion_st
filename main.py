from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Config.db import BASE, engine
from Middleware.get_json import JSONMiddleware
from Router.Verificacion import verificacion_router
from pathlib import Path

route = Path.cwd()
app = FastAPI()
app.title = "Avantika Módulo 5004"
app.version = "0.0.1"

app.add_middleware(JSONMiddleware)
app.add_middleware(
    CORSMiddleware,allow_origins=["*"],  # Permitir todos los orígenes; para producción, especifica los orígenes permitidos.
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos; puedes especificar los métodos permitidos.
    allow_headers=["*"],  # Permitir todos los encabezados; puedes especificar los encabezados permitidos.
)
app.include_router(verificacion_router)

BASE.metadata.create_all(bind=engine)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8007,
        reload=True
    )
