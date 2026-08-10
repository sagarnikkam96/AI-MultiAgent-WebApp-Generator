from fastapi import FastAPI
from routers.routes import router

app = FastAPI(title='Generated FastAPI Backend')

app.include_router(router)

@app.get('/')
async def read_root() -> dict[str, str]:
    return {'message': 'Generated backend is running'}
