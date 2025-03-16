from fastapi import FastAPI
from .api.routes import auth_router
from .api.routes import user_routes
from .api.routes import transaction_routes

app = FastAPI()

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(user_routes.router, prefix="/users", tags=["users"])
app.include_router(transaction_routes.router, prefix="/transactions", tags=["transactions"])

@app.get("/")
async def root():
    return {"message": "Motha fuckin Backend"}
