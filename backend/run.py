#!/usr/bin/env python3
"""
启动脚本 - 用于快速启动后端服务
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
