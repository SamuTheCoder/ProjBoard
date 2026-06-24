from fastapi import FastAPI
from routes.auth_routes import router as auth_router
from routes.user_routes import router as user_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(user_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
