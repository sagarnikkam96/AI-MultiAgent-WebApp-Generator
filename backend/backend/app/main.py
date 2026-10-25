from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.connection import engine
from models.models import Base
Base.metadata.create_all(bind=engine)
from routers.routes import router

app = FastAPI(title='Generated FastAPI Backend')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=False, allow_methods=['*'], allow_headers=['*'])
app.include_router(router)

@app.get('/')
async def read_root() -> dict[str, str]:
    return {'message': 'Generated backend is running'}
