"""
安全模块：API 访问令牌认证中间件

认证策略：
- 通过环境变量 APP_ACCESS_TOKEN 配置访问令牌（部署到公网时必须配置）
- 未配置令牌（默认）→ 认证关闭，兼容本地开发环境
- 已配置令牌 → 所有请求必须携带 `Authorization: Bearer <token>` 或 `X-API-Token: <token>`
- 使用 hmac.compare_digest 进行常量时间比较，防止时序攻击
"""
import hmac

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from core.config import Config


class TokenAuthMiddleware(BaseHTTPMiddleware):
    """访问令牌认证中间件"""

    def __init__(self, app):
        super().__init__(app)
        self.access_token = (Config.APP_ACCESS_TOKEN or "").strip()

    async def dispatch(self, request, call_next):
        # 未配置令牌 → 认证关闭（本地开发模式）
        if not self.access_token:
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        api_token = request.headers.get("X-API-Token", "")

        token = ""
        if auth_header.lower().startswith("bearer "):
            token = auth_header[7:].strip()
        elif api_token:
            token = api_token.strip()

        # 常量时间比较，避免通过响应时间差异枚举令牌
        if not token or not hmac.compare_digest(token, self.access_token):
            return JSONResponse(
                status_code=401,
                content={"code": 401, "message": "未授权：请提供有效的访问令牌"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        return await call_next(request)
