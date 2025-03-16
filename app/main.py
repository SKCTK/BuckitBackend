from fastapi import FastAPI
from .api.routes import auth_router
from .api.routes import user_routes, transaction_routes
from .api.routes import bucket_routes, expenses_routes
from .api.routes import income_routes, financial_summary_routes
import uvicorn

app = FastAPI()

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(user_routes.router, prefix="/users", tags=["users"])
app.include_router(transaction_routes.router, prefix="/transactions", tags=["transactions"])
app.include_router(bucket_routes.router, prefix="/buckets", tags=["buckets"])
app.include_router(expenses_routes.router, prefix="/expenses", tags=["expenses"])
app.include_router(income_routes.router, prefix="/incomes", tags=["incomes"])
app.include_router(financial_summary_routes.router, prefix="/financial-summaries", tags=["financial-summaries"])

@app.get("/")
async def root():
    return {"message": "Im healthy 😎"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
