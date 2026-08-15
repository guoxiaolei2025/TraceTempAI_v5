"""
日志工具模块

提供每日轮转的日志文件 Handler：
- 每日生成独立的日志文件（<prefix>-YYYY-MM-DD.log）
- 跨天自动切换文件，无需重启进程
- 自动清理超过保留天数的历史日志
- 线程安全（支持 FastAPI 异步 + 后台任务线程并发写入）
"""

import os
import logging
import threading
from datetime import datetime, timedelta


class DailyFileHandler(logging.Handler):
    """
    每日独立日志文件 Handler

    按日期生成日志文件名：<prefix>-YYYY-MM-DD.log
    跨天时自动切换到新文件，并在每次切换后清理超过保留天数的历史文件。
    """

    def __init__(self, log_dir="logs", prefix="app", encoding="utf-8", backup_days=30):
        super().__init__()
        self.log_dir = log_dir
        self.prefix = prefix
        self.encoding = encoding
        self.backup_days = backup_days
        self._lock = threading.Lock()
        self._stream = None
        self._current_date = None
        self._last_cleanup_date = None
        os.makedirs(self.log_dir, exist_ok=True)

    @staticmethod
    def _today() -> str:
        return datetime.now().strftime("%Y-%m-%d")

    def _filepath(self, date_str: str) -> str:
        return os.path.join(self.log_dir, f"{self.prefix}-{date_str}.log")

    def _ensure_stream(self):
        """确保当前流对应今天的日志文件，跨天时自动切换。"""
        today = self._today()
        if self._stream is None or self._current_date != today:
            if self._stream is not None:
                try:
                    self._stream.flush()
                    self._stream.close()
                except OSError:
                    pass
            self._current_date = today
            self._stream = open(self._filepath(today), "a", encoding=self.encoding)
        return self._stream

    def _cleanup_old_logs(self):
        """清理超过保留天数的历史日志文件。"""
        try:
            cutoff = (datetime.now() - timedelta(days=self.backup_days)).strftime("%Y-%m-%d")
            prefix_len = len(self.prefix)
            for filename in os.listdir(self.log_dir):
                # 仅匹配 <prefix>-YYYY-MM-DD.log 格式的文件
                if not filename.startswith(self.prefix + "-") or not filename.endswith(".log"):
                    continue
                date_part = filename[prefix_len + 1:-4]
                if len(date_part) != 10 or date_part[4] != "-" or date_part[7] != "-":
                    continue
                if date_part < cutoff:
                    try:
                        os.remove(os.path.join(self.log_dir, filename))
                    except OSError:
                        pass
        except OSError:
            pass

    def emit(self, record: logging.LogRecord):
        try:
            msg = self.format(record)
            with self._lock:
                stream = self._ensure_stream()
                stream.write(msg + "\n")
                stream.flush()
                # 跨天切换后清理一次旧日志
                if self._last_cleanup_date != self._current_date:
                    self._last_cleanup_date = self._current_date
                    self._cleanup_old_logs()
        except Exception:
            self.handleError(record)

    def close(self):
        with self._lock:
            if self._stream is not None:
                try:
                    self._stream.flush()
                    self._stream.close()
                except OSError:
                    pass
                self._stream = None
        super().close()
