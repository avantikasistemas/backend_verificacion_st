from fastapi import Request, HTTPException, status
from Config.jwt_config import verify_token
from functools import wraps

async def verify_jwt_middleware(request: Request, call_next):
    """
    Middleware para verificar JWT en todas las peticiones excepto login.
    """
    # Rutas que no requieren autenticación
    public_paths = ["/api/login", "/docs", "/openapi.json", "/redoc", "/api/docs", "/api/openapi.json", "/api/redoc"]
    
    # Verificar si la ruta es pública
    if any(request.url.path.startswith(path) for path in public_paths):
        return await call_next(request)
    
    # Solo aplicar middleware a rutas que comienzan con /api/
    # Esto permite que las rutas estáticas y del frontend pasen sin verificación
    if not request.url.path.startswith("/api/"):
        return await call_next(request)
    
    # Obtener token del header Authorization
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se proporcionó token de autenticación",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = auth_header.split(" ")[1]
    
    try:
        payload = verify_token(token)
        # Agregar información del usuario al request
        request.state.user = payload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    response = await call_next(request)
    return response


def require_auth(func):
    """
    Decorador para requerir autenticación en endpoints específicos.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = kwargs.get('request')
        if not request:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Request no encontrado"
            )
        
        # Verificar si ya se validó en el middleware
        if not hasattr(request.state, 'user'):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No autenticado"
            )
        
        return await func(*args, **kwargs)
    
    return wrapper
