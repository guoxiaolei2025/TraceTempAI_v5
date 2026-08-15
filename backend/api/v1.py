from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from typing import Optional, Dict
import json
import os
import logging
from datetime import datetime

from models.schemas import ReportGenerateRequest
from services import AlarmService, ReportService, DepartmentService
from core.config import Config

logger = logging.getLogger(__name__)
router = APIRouter()

alarm_service = AlarmService()
report_service = ReportService()
dept_service = DepartmentService()

def success_response(data=None, message="success"):
    return {"code": 0, "message": message, "data": data}

def error_response(message, code=1, status_code=400):
    return JSONResponse(status_code=status_code, content={"code": code, "message": message})

def _safe_error_message(operation: str, exc: Exception) -> str:
    """
    生成安全的错误提示：
    - 开发环境（development）：附带异常详情，便于排查
    - 生产环境（production）：仅返回通用提示，避免泄露内部路径、API 地址等敏感信息
    """
    if Config.APP_ENV == "production":
        return f"{operation}失败，请稍后重试或联系管理员"
    return f"{operation}失败: {exc}"

@router.get("/")
async def root():
    return success_response({"message": "TraceTempAI API 服务已启动"})

@router.get("/departments")
async def get_departments():
    try:
        result = dept_service.get_all_departments()
        return success_response(result)
    except Exception as e:
        logger.error("获取学科列表失败: %s", e, exc_info=True)
        return error_response(_safe_error_message("获取学科列表", e))

@router.get("/alarms/temperature-humidity")
async def get_alarm_data(start_date: str, end_date: str, dept_id: Optional[str] = None):
    try:
        result = alarm_service.get_alarm_data(start_date, end_date, dept_id)
        return success_response(result)
    except ValueError as e:
        logger.warning("获取报警数据参数校验失败: %s", e)
        return error_response(str(e))
    except Exception as e:
        logger.error("获取报警数据失败: %s", e, exc_info=True)
        return error_response(_safe_error_message("获取报警数据", e))

@router.post("/alarms/analyze")
async def analyze_alarms(request_data: Dict):
    try:
        start_date = request_data.get("start_date", "")
        end_date = request_data.get("end_date", "")
        alarm_data = request_data.get("alarm_data", {})
        dept_id = request_data.get("dept_id")
        result = alarm_service.analyze_alarms(start_date, end_date, alarm_data, dept_id)
        return success_response(result)
    except Exception as e:
        logger.error("AI分析失败: %s", e, exc_info=True)
        return error_response(_safe_error_message("AI分析", e))

@router.post("/reports/generate")
async def generate_report(request: ReportGenerateRequest):
    try:
        task_id = report_service.generate_report(
            request.report_type,
            request.start_date,
            request.end_date,
            request.dept_id
        )
        return success_response({"task_id": task_id}, "报告生成任务已创建")
    except ValueError as e:
        logger.warning("创建报告任务参数校验失败: %s", e)
        return error_response(str(e))
    except Exception as e:
        logger.error("创建报告任务失败: %s", e, exc_info=True)
        return error_response(_safe_error_message("创建报告任务", e))

@router.get("/reports/tasks")
async def get_tasks():
    try:
        result = report_service.get_tasks()
        return success_response(result)
    except Exception as e:
        logger.error("获取任务列表失败: %s", e, exc_info=True)
        return error_response(_safe_error_message("获取任务列表", e))

@router.get("/reports/tasks/{task_id}")
async def get_task_status(task_id: str):
    try:
        result = report_service.get_task_status(task_id)
        return success_response(result)
    except ValueError as e:
        logger.warning("获取任务状态失败（任务不存在）: %s", e)
        return error_response(str(e), status_code=404)
    except Exception as e:
        logger.error("获取任务状态失败: %s", e, exc_info=True)
        return error_response(_safe_error_message("获取任务状态", e))

def _make_content_disposition(filename: str) -> str:
    """生成符合 RFC 5987 的 Content-Disposition 头，避免中文文件名显示异常"""
    from urllib.parse import quote
    ascii_filename = quote(filename, safe='')
    return f"attachment; filename*=utf-8''{ascii_filename}"

@router.get("/reports/download/{file_id}")
async def download_report(file_id: str):
    """
    下载报告文件

    包含路径遍历防护：对 file_id 进行安全校验，确保文件路径
    始终位于 outputs/reports 目录内，防止目录穿越攻击。

    Args:
        file_id: 文件名（仅允许纯文件名，禁止路径分隔符）

    Returns:
        FileResponse: 文件响应
    """
    try:
        import os
        safe_filename = os.path.basename(file_id)
        file_path = os.path.realpath(os.path.join("outputs/reports", safe_filename))
        base_dir = os.path.realpath("outputs/reports")
        if not file_path.startswith(base_dir + os.sep) or not os.path.isfile(file_path):
            return error_response(f"文件 {safe_filename} 不存在", status_code=404)
        return FileResponse(
            path=file_path, 
            filename=safe_filename, 
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": _make_content_disposition(safe_filename)}
        )
    except Exception as e:
        logger.error("下载报告失败: %s", e, exc_info=True)
        return error_response(_safe_error_message("下载报告", e))

@router.post("/alarms/export")
async def export_alarm_data(request_data: Dict):
    try:
        alarm_data = request_data.get("alarm_data", {})
        analysis_result = request_data.get("analysis_result", None)
        date_range = request_data.get("date_range", {})
        result = alarm_service.export_alarm_data(alarm_data, analysis_result, date_range)
        
        import os
        file_path = result["file_path"]
        if os.path.exists(file_path):
            return FileResponse(
                path=file_path, 
                filename=result["filename"], 
                media_type="application/octet-stream",
                headers={"Content-Disposition": _make_content_disposition(result["filename"])}
            )
        return success_response(result, "导出成功")
    except Exception as e:
        logger.error("导出数据失败: %s", e, exc_info=True)
        return error_response(_safe_error_message("导出数据", e))


@router.post("/alarms/export-excel")
async def export_charts_excel(request_data: Dict):
    try:
        alarm_data = request_data.get("alarm_data", {})
        result = alarm_service.export_charts_excel(alarm_data)
        
        import os
        file_path = result["file_path"]
        if os.path.exists(file_path):
            return FileResponse(
                path=file_path, 
                filename=result["filename"], 
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": _make_content_disposition(result["filename"])}
            )
        return success_response(result, "导出成功")
    except Exception as e:
        logger.error("导出Excel失败: %s", e, exc_info=True)
        return error_response(_safe_error_message("导出Excel", e))


@router.post("/alarms/export-ai-txt")
async def export_ai_txt(request_data: Dict):
    try:
        analysis_data = request_data.get("analysis_data", {})
        result = alarm_service.export_ai_txt(analysis_data)
        
        import os
        file_path = result["file_path"]
        if os.path.exists(file_path):
            return FileResponse(
                path=file_path, 
                filename=result["filename"], 
                media_type="text/plain",
                headers={"Content-Disposition": _make_content_disposition(result["filename"])}
            )
        return success_response(result, "导出成功")
    except Exception as e:
        logger.error("导出TXT失败: %s", e, exc_info=True)
        return error_response(_safe_error_message("导出TXT", e))


@router.post("/alarms/export-ai-word")
async def export_ai_word(request_data: Dict):
    try:
        analysis_data = request_data.get("analysis_data", {})
        result = alarm_service.export_ai_word(analysis_data)
        
        import os
        file_path = result["file_path"]
        abs_file_path = os.path.abspath(file_path)
        if os.path.exists(abs_file_path):
            return FileResponse(
                path=abs_file_path, 
                filename=result["filename"], 
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                headers={"Content-Disposition": _make_content_disposition(result["filename"])}
            )
        return error_response("文件不存在或已过期，请重新生成", status_code=404)
    except Exception as e:
        logger.error("导出Word失败: %s", e, exc_info=True)
        return error_response(_safe_error_message("导出Word", e))


@router.post("/alarms/ai-feedback")
async def submit_ai_feedback(request_data: Dict):
    """接收用户对 AI 分析的反馈评分"""
    try:
        rating = request_data.get("rating", 0)
        comment = request_data.get("comment", "")
        timestamp = request_data.get("timestamp", "")
        quality_score = request_data.get("quality_score", 0)

        # 输入校验，防止异常数据污染反馈日志文件
        if not isinstance(rating, (int, float)) or isinstance(rating, bool) or not (0 <= rating <= 5):
            return error_response("评分必须在 0-5 之间", status_code=400)
        if not isinstance(quality_score, (int, float)) or isinstance(quality_score, bool) or not (0 <= quality_score <= 100):
            return error_response("质量评分必须在 0-100 之间", status_code=400)
        if not isinstance(comment, str) or len(comment) > 1000:
            return error_response("评论内容过长或格式错误", status_code=400)
        if not isinstance(timestamp, str) or len(timestamp) > 40:
            return error_response("时间戳格式错误", status_code=400)

        feedback_record = {
            "time": timestamp or datetime.now().isoformat(),
            "rating": rating,
            "comment": comment,
            "quality_score": quality_score
        }

        # 追加写入 logs/ai_feedback.jsonl
        feedback_file = os.path.join("logs", "ai_feedback.jsonl")
        os.makedirs("logs", exist_ok=True)
        with open(feedback_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(feedback_record, ensure_ascii=False) + "\n")

        return success_response(None, "反馈已记录")
    except Exception as e:
        logger.error("提交反馈失败: %s", e, exc_info=True)
        return error_response(_safe_error_message("提交反馈", e))


@router.post("/reports/download-batch")
async def download_reports_batch(request_data: Dict):
    try:
        file_ids = request_data.get("file_ids", [])
        result = report_service.download_reports_batch(file_ids)
        
        import os
        file_path = result["file_path"]
        if os.path.exists(file_path):
            return FileResponse(
                path=file_path, 
                filename=result["filename"], 
                media_type="application/zip",
                headers={"Content-Disposition": _make_content_disposition(result["filename"])}
            )
        return error_response("打包失败", status_code=404)
    except Exception as e:
        logger.error("批量下载失败: %s", e, exc_info=True)
        return error_response(_safe_error_message("批量下载", e))