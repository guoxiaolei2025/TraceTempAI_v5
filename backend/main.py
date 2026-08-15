import sys
from pathlib import Path

src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import Config
from core.security import TokenAuthMiddleware
from api.v1 import router as api_router
from utils.logger import DailyFileHandler

os.makedirs(Config.LOG_DIR, exist_ok=True)
os.makedirs("outputs", exist_ok=True)
os.makedirs("outputs/reports", exist_ok=True)


def setup_logging():
    """
    配置日志：每日独立文件 + 控制台输出，并将 uvicorn 访问日志接入同一管道。

    - 每日文件：logs/<prefix>-YYYY-MM-DD.log，跨天自动切换，自动清理旧文件
    - 通过 log_config=None 让 uvicorn 复用 root logger，使 HTTP 访问日志也写入每日文件
    """
    root_logger = logging.getLogger()
    # 清空已有 handlers，避免 reload 模式下模块重复导入导致日志重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        handler.close()

    log_format = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    file_handler = DailyFileHandler(
        log_dir=Config.LOG_DIR,
        prefix=Config.LOG_FILE_PREFIX,
        backup_days=Config.LOG_BACKUP_DAYS,
    )
    file_handler.setFormatter(log_format)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)

    root_logger.setLevel(getattr(logging, Config.LOG_LEVEL, logging.INFO))
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # 将 uvicorn 日志接入 root logger，避免被其默认 dictConfig 配置覆盖
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        u_logger = logging.getLogger(name)
        u_logger.handlers = []
        u_logger.propagate = True


setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="TraceTempAI API", description="温湿度智能监控分析系统 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "X-API-Token"],
)

# API 访问令牌认证：配置 APP_ACCESS_TOKEN 后自动启用
app.add_middleware(TokenAuthMiddleware)

# 安全说明：outputs/ 目录包含敏感报警数据与报告，不再以静态方式对外暴露，
# 所有下载均通过受认证保护的 /api 端点（/reports/download、/alarms/export-* 等）完成。

app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    logger.info("启动 TraceTempAI FastAPI 服务...")
    uvicorn.run(
        "main:app",
        host=Config.FASTAPI_SERVER_HOST,
        port=Config.FASTAPI_SERVER_PORT,
        reload=True,
        log_config=None,   # 复用 root logger 配置，使访问日志写入每日文件
        access_log=True,
    )