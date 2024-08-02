import uvicorn
from loguru import logger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps.demo.views import router as demo_router

app = FastAPI(
    title="FastAPI",
    description="FastAPI",
    version="0.0.1",
    docs_url="/docs",
    redoc_url="/redoc",
)
# 允许所有来源
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许访问的源列表
    allow_credentials=True,  # 支持 cookies 跨域
    allow_methods=["*"],  # 允许的请求方法
    allow_headers=["*"],  # 允许的请求头
)

app.include_router(demo_router)


@app.get("/")
def index():
    logger.info("index")
    return "index"


if __name__ == '__main__':
    uvicorn.run(app="main:app", reload=True, host="0.0.0.0", port=8081)
