from fastapi import FastAPI
from routes.auth_routes import router as auth_router
from routes.user_routes import router as user_router
from routes.project_routes import router as project_router
from routes.task_routes import router as task_routes
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(project_router)
app.include_router(task_routes)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
