from fastapi import FastAPI

from app.routers import categories, products, notes, users, reviews

app = FastAPI(
    title="API Интернет-магазин",
    version="0.1.0",
)

app.include_router(categories.router)
app.include_router(products.router)
app.include_router(notes.router)
app.include_router(users.router)
app.include_router(reviews.router)

@app.get("/")
async def root():
    """
    Root endpoint.
    """
    return {"message": "Welcome to API!"}