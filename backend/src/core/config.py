import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """
    配置管理类

    负责加载和管理系统配置信息，包括API密钥、系统参数等
    所有敏感信息通过环境变量管理，不硬编码在代码中
    """

    # 阿里云369平台API配置
    ALIBABA_API_URL = os.getenv("ALIBABA_API_URL", "https://cloudapi.369clouds.com/openapi")

    # AI模型API配置（主模型）
    AI_API_URL = os.getenv("AI_API_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions")
    AI_API_KEY = os.getenv("AI_API_KEY", "")
    AI_MODEL = os.getenv("AI_MODEL", "qwen3.6-flash")
    AI_TIMEOUT = int(os.getenv("AI_TIMEOUT", "300"))

    # AI模型API配置（备用模型，主模型失败时自动切换）
    AI_FALLBACK_API_URL = os.getenv("AI_FALLBACK_API_URL", "https://api.deepseek.com/chat/completions")
    AI_FALLBACK_API_KEY = os.getenv("AI_FALLBACK_API_KEY", "")
    AI_FALLBACK_MODEL = os.getenv("AI_FALLBACK_MODEL", "deepseek-chat")

    # 安全配置
    # 访问令牌：为空表示关闭认证（本地开发）；配置后所有 /api 请求必须携带 Bearer Token
    APP_ACCESS_TOKEN = os.getenv("APP_ACCESS_TOKEN", "")
    # 运行环境：development / production，生产环境隐藏异常详情避免信息泄露
    APP_ENV = os.getenv("APP_ENV", "development")

    # 应用配置
    STREAMLIT_SERVER_PORT = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))
    STREAMLIT_SERVER_ADDRESS = os.getenv("STREAMLIT_SERVER_ADDRESS", "localhost")
    FASTAPI_SERVER_HOST = os.getenv("FASTAPI_SERVER_HOST", "0.0.0.0")
    FASTAPI_SERVER_PORT = int(os.getenv("FASTAPI_SERVER_PORT", "8000"))

    # 日志配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    # 兼容保留：单文件日志路径（不再由 main.py 使用，保留以防外部引用）
    LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")
    # 每日轮转日志：目录 / 文件前缀 / 保留天数
    LOG_DIR = os.getenv("LOG_DIR", "logs")
    LOG_FILE_PREFIX = os.getenv("LOG_FILE_PREFIX", "app")
    LOG_BACKUP_DAYS = int(os.getenv("LOG_BACKUP_DAYS", "30"))

    # 缓存配置
    ENABLE_CACHE = os.getenv("ENABLE_CACHE", "true").lower() == "true"
    CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))

    # 学科配置文件路径
    DEPARTMENTS_CONFIG_PATH = os.getenv("DEPARTMENTS_CONFIG_PATH", "config/departments.json")

    # 代理配置（留空表示使用系统默认；设置为 'none' 表示禁用代理）
    PROXY_URL = os.getenv("PROXY_URL", "")
    NO_PROXY = os.getenv("NO_PROXY", "")
