import logging
import threading
import time
import traceback
from enum import Enum
from typing import Dict, Callable, Any, Optional, List
from dataclasses import dataclass
import uuid

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """
    任务状态枚举
    
    定义任务的各种状态
    """
    PENDING = "待处理"
    PROCESSING = "处理中"
    COMPLETED = "已完成"
    FAILED = "失败"

@dataclass
class Task:
    """
    任务数据结构
    
    包含任务的基本信息、状态、进度和结果
    """
    task_id: str
    name: str
    status: TaskStatus
    progress: int
    result: Any = None
    error: str = None
    created_at: float = None
    started_at: float = None
    completed_at: float = None
    department: str = None
    report_type: str = None
    report_format: str = None

class TaskManager:
    """
    后台任务管理器
    
    负责管理后台任务的创建、执行、状态跟踪和结果缓存
    使用线程池实现异步任务执行，不阻塞前端
    """
    
    def __init__(self):
        """
        初始化任务管理器
        """
        self.tasks: Dict[str, Task] = {}
        self.lock = threading.Lock()
        self.max_tasks = 100
        self.task_timeout = 3600  # 1小时超时
        self._timeout_timers: Dict[str, threading.Timer] = {}
    
    def create_task(self, name: str, func: Callable, *args, **kwargs) -> str:
        """
        创建并启动后台任务
        
        Args:
            name: 任务名称
            func: 要执行的函数
            *args, **kwargs: 函数参数
        
        Returns:
            str: 任务ID
        """
        # 检查任务数量限制
        if len(self.tasks) >= self.max_tasks:
            # 清理已完成的旧任务
            self._cleanup_old_tasks()
        
        task_id = str(uuid.uuid4())
        task = Task(
            task_id=task_id,
            name=name,
            status=TaskStatus.PENDING,
            progress=0,
            created_at=time.time(),
            department=kwargs.get('department'),
            report_type=kwargs.get('report_type'),
            report_format=kwargs.get('report_format')
        )
        
        with self.lock:
            self.tasks[task_id] = task
        
        # 启动后台线程执行任务
        thread = threading.Thread(
            target=self._execute_task,
            args=(task_id, func, args, kwargs),
            daemon=True
        )
        thread.start()
        
        # 启动超时定时器
        self._start_timeout_timer(task_id)
        
        return task_id
    
    def _execute_task(self, task_id: str, func: Callable, args: tuple, kwargs: dict):
        """
        在后台线程中执行任务
        
        Args:
            task_id: 任务ID
            func: 要执行的函数
            args: 函数位置参数
            kwargs: 函数关键字参数
        """
        try:
            # 更新任务状态为处理中
            self.update_task_status(task_id, TaskStatus.PROCESSING)
            with self.lock:
                if task_id in self.tasks:
                    self.tasks[task_id].started_at = time.time()
            logger.info("任务 %s 开始执行", task_id)
            
            # 执行任务函数
            result = func(*args, **kwargs)
            
            # 更新任务状态为已完成
            self.update_task_result(task_id, result)
            logger.info("任务 %s 执行完成", task_id)
            
        except Exception as e:
            # 任务失败，记录详细错误信息
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            logger.error("任务 %s 执行失败: %s", task_id, error_msg)
            self.update_task_error(task_id, error_msg)
        finally:
            # 取消超时定时器
            self._cancel_timeout_timer(task_id)
    
    def _start_timeout_timer(self, task_id: str):
        """
        启动任务超时定时器
        
        Args:
            task_id: 任务ID
        """
        def on_timeout():
            self._on_task_timeout(task_id)
        
        timer = threading.Timer(self.task_timeout, on_timeout)
        timer.daemon = True
        with self.lock:
            self._timeout_timers[task_id] = timer
        timer.start()
        logger.debug("任务 %s 超时定时器已启动（%s 秒）", task_id, self.task_timeout)
    
    def _cancel_timeout_timer(self, task_id: str):
        """
        取消任务超时定时器
        
        Args:
            task_id: 任务ID
        """
        with self.lock:
            timer = self._timeout_timers.pop(task_id, None)
        if timer:
            timer.cancel()
            logger.debug("任务 %s 超时定时器已取消", task_id)
    
    def _on_task_timeout(self, task_id: str):
        """
        任务超时处理回调
        
        Args:
            task_id: 任务ID
        """
        with self.lock:
            task = self.tasks.get(task_id)
            if task and task.status in (TaskStatus.PENDING, TaskStatus.PROCESSING):
                task.status = TaskStatus.FAILED
                task.error = f"任务执行超时（超过 {self.task_timeout} 秒）"
                task.completed_at = time.time()
                logger.warning("任务 %s 已超时并被标记为失败", task_id)
        # 清理定时器引用
        with self.lock:
            self._timeout_timers.pop(task_id, None)
    
    def update_task_status(self, task_id: str, status: TaskStatus) -> bool:
        """
        更新任务状态
        
        Args:
            task_id: 任务ID
            status: 新状态
        
        Returns:
            bool: 是否更新成功
        """
        with self.lock:
            if task_id in self.tasks:
                self.tasks[task_id].status = status
                return True
        return False
    
    def update_task_progress(self, task_id: str, progress: int) -> bool:
        """
        更新任务进度
        
        Args:
            task_id: 任务ID
            progress: 进度值（0-100）
        
        Returns:
            bool: 是否更新成功
        """
        with self.lock:
            if task_id in self.tasks:
                self.tasks[task_id].progress = max(0, min(100, progress))
                return True
        return False
    
    def update_task_result(self, task_id: str, result: Any) -> bool:
        """
        更新任务结果
        
        Args:
            task_id: 任务ID
            result: 任务结果
        
        Returns:
            bool: 是否更新成功
        """
        with self.lock:
            if task_id in self.tasks:
                self.tasks[task_id].result = result
                self.tasks[task_id].status = TaskStatus.COMPLETED
                self.tasks[task_id].progress = 100
                self.tasks[task_id].completed_at = time.time()
                return True
        return False
    
    def update_task_error(self, task_id: str, error: str) -> bool:
        """
        更新任务错误
        
        Args:
            task_id: 任务ID
            error: 错误信息
        
        Returns:
            bool: 是否更新成功
        """
        with self.lock:
            if task_id in self.tasks:
                self.tasks[task_id].error = error
                self.tasks[task_id].status = TaskStatus.FAILED
                self.tasks[task_id].completed_at = time.time()
                return True
        return False
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        获取任务信息
        
        Args:
            task_id: 任务ID
        
        Returns:
            Task: 任务对象，如果不存在则返回None
        """
        with self.lock:
            return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> Dict[str, Task]:
        """
        获取所有任务
        
        Returns:
            Dict[str, Task]: 任务字典
        """
        with self.lock:
            return self.tasks.copy()
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """
        根据状态获取任务列表
        
        Args:
            status: 任务状态
        
        Returns:
            List[Task]: 任务列表
        """
        with self.lock:
            return [task for task in self.tasks.values() if task.status == status]
    
    def delete_task(self, task_id: str) -> bool:
        """
        删除任务
        
        Args:
            task_id: 任务ID
        
        Returns:
            bool: 是否删除成功
        """
        with self.lock:
            if task_id in self.tasks:
                del self.tasks[task_id]
                return True
        return False
    
    def clear_completed_tasks(self, max_age: int = 3600) -> int:
        """
        清理已完成的任务
        
        Args:
            max_age: 任务最大保留时间（秒）
        
        Returns:
            int: 清理的任务数量
        """
        current_time = time.time()
        tasks_to_delete = []
        
        with self.lock:
            for task_id, task in self.tasks.items():
                if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                    if task.completed_at and (current_time - task.completed_at) > max_age:
                        tasks_to_delete.append(task_id)
            
            for task_id in tasks_to_delete:
                del self.tasks[task_id]
        
        return len(tasks_to_delete)
    
    def _cleanup_old_tasks(self):
        """
        清理旧任务（内部方法）
        """
        self.clear_completed_tasks(max_age=1800)  # 清理30分钟前的任务
    
    def get_task_count(self) -> Dict[str, int]:
        """
        获取任务统计信息
        
        Returns:
            Dict[str, int]: 各状态任务数量
        """
        with self.lock:
            status_counts = {}
            for status in TaskStatus:
                status_counts[status.value] = 0
            
            for task in self.tasks.values():
                status_counts[task.status.value] += 1
            
            return status_counts
    
    def cancel_task(self, task_id: str) -> bool:
        """
        取消任务
        
        Args:
            task_id: 任务ID
        
        Returns:
            bool: 是否取消成功
        """
        with self.lock:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                if task.status == TaskStatus.PENDING or task.status == TaskStatus.PROCESSING:
                    task.status = TaskStatus.FAILED
                    task.error = "任务已取消"
                    task.completed_at = time.time()
                    return True
        return False
    
    def get_active_tasks(self) -> List[Task]:
        """
        获取活动任务（待处理或处理中）
        
        Returns:
            List[Task]: 活动任务列表
        """
        with self.lock:
            return [
                task for task in self.tasks.values()
                if task.status in [TaskStatus.PENDING, TaskStatus.PROCESSING]
            ]
    
    def get_completed_tasks(self, limit: int = 10) -> List[Task]:
        """
        获取已完成的任务
        
        Args:
            limit: 返回的最大任务数量
        
        Returns:
            List[Task]: 已完成任务列表，按完成时间倒序排列
        """
        with self.lock:
            completed_tasks = [
                task for task in self.tasks.values()
                if task.status == TaskStatus.COMPLETED
            ]
            # 按完成时间倒序排列
            completed_tasks.sort(key=lambda x: x.completed_at or 0, reverse=True)
            return completed_tasks[:limit]
    
    def get_failed_tasks(self, limit: int = 10) -> List[Task]:
        """
        获取失败的任务
        
        Args:
            limit: 返回的最大任务数量
        
        Returns:
            List[Task]: 失败任务列表，按完成时间倒序排列
        """
        with self.lock:
            failed_tasks = [
                task for task in self.tasks.values()
                if task.status == TaskStatus.FAILED
            ]
            # 按完成时间倒序排列
            failed_tasks.sort(key=lambda x: x.completed_at or 0, reverse=True)
            return failed_tasks[:limit]