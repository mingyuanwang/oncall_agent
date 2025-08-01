# FastAPI/Flask 入口
from fastapi import FastAPI
from app.routes import query, train

app = FastAPI(title="Memory Agent Project")

# 注册路由
app.include_router(query.router, prefix="/api/v1")
app.include_router(train.router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 