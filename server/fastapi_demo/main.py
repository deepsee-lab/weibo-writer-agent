import uvicorn
from fastapi import FastAPI
from loguru import logger
from apps.demo.views import router as demo_router

app = FastAPI(
    description="api文档: demo"
)

app.include_router(demo_router)


@app.get("/")
def index():
    logger.info("index")
    return "index"


if __name__ == '__main__':
    uvicorn.run(app="main:app", reload=True, host="0.0.0.0", port=8081)
