from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class AlarmDataRequest(BaseModel):
    start_date: str = Field(description="开始日期 (YYYY-MM-DD)")
    end_date: str = Field(description="结束日期 (YYYY-MM-DD)")
    dept_id: Optional[str] = Field(default=None, description="学科ID")

class ReportGenerateRequest(BaseModel):
    report_type: str = Field(description="报告类型 (monthly_review 或 correction)")
    start_date: str = Field(description="开始日期 (YYYY-MM-DD)")
    end_date: str = Field(description="结束日期 (YYYY-MM-DD)")
    dept_id: Optional[str] = Field(default=None, description="学科ID")

class AnalyzeRequest(BaseModel):
    start_date: str = Field(description="开始日期")
    end_date: str = Field(description="结束日期")
    alarm_data: Dict = Field(description="报警数据")

class DepartmentResponse(BaseModel):
    id: str
    name: str

class AlarmDeviceResponse(BaseModel):
    device_name: str
    device_sn: str
    alarms: List[Dict]

class AlarmStatisticsResponse(BaseModel):
    total_alarms: int
    temperature_alarms: int
    humidity_alarms: int
    device_count: int

class AlarmDataResponse(BaseModel):
    total: int
    handled_count: int
    unhandled_count: int
    devices: List[AlarmDeviceResponse]
    statistics: AlarmStatisticsResponse

class TaskResponse(BaseModel):
    task_id: str
    name: str
    status: str
    progress: int
    created_at: Optional[float]
    started_at: Optional[float]
    completed_at: Optional[float]
    report_type: Optional[str]
    department: Optional[str]
    error: Optional[str]
    result: Optional[Dict]

class ApiResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Optional[Dict] = None