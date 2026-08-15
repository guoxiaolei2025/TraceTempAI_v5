# TraceTempAI v5

温湿度智能监控分析系统 - 基于 FastAPI + Vue 3 的前后端分离架构

## 项目概述

TraceTempAI 是一个面向医学实验室场景的温湿度智能监控分析系统，用于监控和分析各学科（科室）的温湿度报警数据。系统从第三方 369 平台 API 采集设备温湿度报警数据，进行多维度统计分析、AI 深度分析和 Word 报告生成。

### 版本演进

| 版本 | 架构 | 主要变化 |
|------|------|----------|
| v2 | Streamlit | 初始版本，基础 AI 调用 |
| v3 | Streamlit | 功能增强 |
| v4 | FastAPI + Vue 3 | 架构迁移，新增多维度图表、AI 深度分析、多格式导出 |
| v5 | FastAPI + Vue 3 | AI 质量评分、多模型故障转移、安全加固、报告优化 |

### 核心特性

- **学科管理**：支持所有医学实验室学科配置，每个学科独立 API Key 管理
- **报警数据采集**：从 369 平台 API 实时获取设备温湿度报警数据（自动重试 + 分页）
- **多维度趋势分析**：报警类型、设备分布、24小时趋势、星期规律、月度分布共 5 个 ECharts 图表
- **AI 深度分析**：报警概况总结、设备规律分析、类型分析、改善建议、处理评价五大板块
- **AI 多模型故障转移**：主模型（通义千问）失败自动切换备用模型（DeepSeek）
- **AI 输出质量监控**：自动评分（格式合规/内容充实度/建议质量/专业性）+ 用户反馈收集
- **Word 报告生成**：支持月度回顾报告和环境失控纠正报告，按设备类型自动拆分
- **多格式导出**：JSON、Excel（多工作表）、TXT、Word 四种格式
- **后台任务管理**：异步报告生成，前端轮询任务状态，支持批量下载 ZIP
- **安全防护**：API Key 环境变量管理、路径遍历防护、CORS 白名单

---

## 项目结构

```
TraceTempAI_v5/
├── README.md                       # 项目说明文档
├── .gitignore                      # Git 忽略规则
├── requirements.txt                # 统一依赖清单（后端 Python + 前端 Node）
├── start_all.bat                   # 一键启动前后端服务（Windows）
├── stop_all.bat                    # 停止所有服务（Windows）
│
├── backend/                        # FastAPI 后端
│   ├── main.py                     # 应用入口（CORS、静态文件、路由注册）
│   ├── .env                        # 实际环境变量（敏感信息，不纳入版本控制）
│   ├── .env.example                # 环境变量配置模板
│   ├── api/
│   │   └── v1.py                   # API 路由（14 个端点）
│   ├── config/
│   │   └── departments.json        # 学科配置文件
│   ├── models/
│   │   └── schemas.py             # Pydantic 数据模型
│   ├── services/
│   │   └── __init__.py            # 业务逻辑服务层（AlarmService/ReportService/DepartmentService）
│   ├── src/
│   │   ├── core/
│   │   │   ├── config.py           # 全局配置管理（环境变量加载）
│   │   │   ├── data_collector.py   # 369 平台 API 数据采集器
│   │   │   ├── department_manager.py # 学科配置管理器
│   │   │   ├── report_generator.py # Word 报告生成器（48 KB，核心模块）
│   │   │   ├── task_manager.py     # 后台异步任务管理器
│   │   │   ├── ai_analyzer.py      # AI 深度分析器（多模型故障转移）
│   │   │   └── ai_quality_scorer.py # AI 输出质量自动评分
│   │   └── utils/
│   │       ├── excel_exporter.py   # Excel 导出工具（含图表）
│   │       └── prompt_loader.py    # 提示词文件加载器
│   ├── prompts/
│   │   ├── deep_analysis_system.txt  # AI 系统提示词
│   │   └── deep_analysis_template.txt # AI 用户消息模板
│   ├── outputs/                    # 导出文件输出目录（运行时生成）
│   │   └── reports/               # 生成的 Word 报告文件
│   └── logs/                       # 日志目录（运行时生成）
│
├── frontend/                       # Vue 3 前端
│   ├── index.html                  # 入口 HTML
│   ├── package.json                # Node 依赖配置
│   ├── vite.config.js              # Vite 构建配置（含 API 代理）
│   ├── jsconfig.json               # 路径别名配置（@ → src/）
│   └── src/
│       ├── main.js                 # Vue 应用入口
│       ├── App.vue                 # 根组件
│       ├── api/
│       │   └── temperature-humidity.js  # API 接口封装（Axios）
│       ├── store/
│       │   └── temperature-humidity.js  # Pinia 状态管理
│       └── views/
│           └── alarm/
│               └── TemperatureHumidity/
│                   ├── index.vue           # 主页面容器（标签切换）
│                   └── components/
│                       ├── QueryPanel.vue        # 学科选择 + 日期查询
│                       ├── StatusAlert.vue       # 处理状态统计提醒
│                       ├── TrendAnalysisTab.vue   # 多维度趋势图表
│                       ├── AiReportTab.vue       # AI 深度分析展示
│                       ├── ReportPanel.vue       # 报告类型选择 + 生成
│                       └── TaskList.vue          # 任务列表 + 下载
│
├── docs/                           # 项目文档
│   ├── 2026-08-15-腾讯轻量云服务器部署指南.md
│   ├── 2026-08-15-风险规则与测试修改记录.md
│   ├── 温湿度智能监控分析需求文档v2.docx
│   ├── 温湿度监控报警数据处理流程对比报告v6.docx
│   ├── 温湿度失控场景风险评估表（最终版）.xlsx
│   ├── 24小时温湿度监控月度回顾表.doc
│   └── 环境失控纠正报告.doc
│
└── venv/                           # Python 虚拟环境（不纳入版本控制）
```

---

## 快速开始

### 环境要求

| 依赖 | 最低版本 | 说明 |
|------|----------|------|
| Python | 3.9+ | 后端运行环境 |
| Node.js | 18+ | 前端开发环境 |
| npm | 9+ | 前端包管理器 |

### 一键启动（Windows，推荐）

```bash
# 在项目根目录双击或在命令行运行
start_all.bat
```

脚本将自动执行：
1. 创建/激活 Python 虚拟环境
2. 安装后端依赖
3. 检查并创建 `.env` 配置文件
4. 启动 FastAPI 后端服务（端口 8000）
5. 启动 Vue 前端开发服务（端口 5173）

### 手动启动

#### 1. 后端配置与启动

```bash
# 进入后端目录
cd backend

# 创建虚拟环境（仅首次）
python -m venv venv

# 激活虚拟环境
# Windows:
call venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate

# 安装依赖（依赖清单位于项目根目录）
pip install -r ../requirements.txt

# 配置环境变量
copy .env.example .env
# 编辑 .env 文件，填入您的 API Key
```

启动后端服务：

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. 前端配置与启动

```bash
# 新开命令行窗口，进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

#### 3. 停止服务

```bash
# 双击或在命令行运行
stop_all.bat
```

### 访问应用

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端页面 | http://localhost:5173 | Vue 3 用户界面 |
| 后端 API | http://localhost:8000 | FastAPI 服务 |
| API 文档 | http://localhost:8000/docs | Swagger UI 自动生成 |
| 静态文件 | http://localhost:8000/outputs/ | 生成的报告和导出文件 |

---

## 技术栈

### 后端

| 技术 | 版本 | 用途 |
|------|------|------|
| FastAPI | ≥0.100.0 | Web 框架 |
| Uvicorn | ≥0.20.0 | ASGI 服务器 |
| Pydantic | ≥2.0.0 | 数据验证与序列化 |
| python-dotenv | ≥1.0.0 | 环境变量管理 |
| requests | ≥2.30.0 | HTTP 客户端 |
| python-docx | ≥1.1.0 | Word 文档生成 |
| openpyxl | ≥3.1.0 | Excel 文件处理 |
| pandas | ≥2.0.0 | 数据分析处理 |

### 前端

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue 3 | ^3.4.21 | 前端框架（Composition API） |
| Vite | ^5.2.8 | 构建工具 |
| Element Plus | ^2.6.3 | UI 组件库 |
| Pinia | ^2.1.7 | 状态管理 |
| Axios | ^1.6.8 | HTTP 客户端 |
| ECharts | ^5.5.0 | 数据可视化图表 |
| Sass | ^1.72.0 | CSS 预处理器 |

---

## API 接口

### 通用响应格式

```json
{
  "code": 0,
  "message": "success",
  "data": { ... }
}
```

- `code: 0` 表示成功，非 0 表示失败
- `message` 为操作结果描述
- `data` 为响应数据

### 基础接口

| 方法 | 路径 | 参数 | 说明 |
|------|------|------|------|
| GET | `/api/` | - | 服务健康检查 |
| GET | `/api/departments` | - | 获取所有学科列表 |

### 报警数据接口

| 方法 | 路径 | 参数 | 说明 |
|------|------|------|------|
| GET | `/api/alarms/temperature-humidity` | `start_date`, `end_date`, `dept_id`(可选) | 查询温湿度报警数据 |
| POST | `/api/alarms/analyze` | `{start_date, end_date, alarm_data, dept_id}` | AI 分析报警数据 |

### 导出接口

| 方法 | 路径 | 请求体 | 说明 |
|------|------|------|------|
| POST | `/api/alarms/export` | `{alarm_data, analysis_result, date_range}` | 导出完整数据（JSON） |
| POST | `/api/alarms/export-excel` | `{alarm_data}` | 导出图表数据（Excel） |
| POST | `/api/alarms/export-ai-txt` | `{analysis_data}` | 导出 AI 分析（TXT） |
| POST | `/api/alarms/export-ai-word` | `{analysis_data}` | 导出 AI 分析（Word） |

### 报告接口

| 方法 | 路径 | 参数/请求体 | 说明 |
|------|------|------|------|
| POST | `/api/reports/generate` | `{report_type, start_date, end_date, dept_id}` | 创建报告生成任务 |
| GET | `/api/reports/tasks` | - | 获取所有任务列表 |
| GET | `/api/reports/tasks/{task_id}` | - | 查询任务状态与进度 |
| GET | `/api/reports/download/{file_id}` | - | 下载单个报告文件 |
| POST | `/api/reports/download-batch` | `{file_ids}` | 批量下载（ZIP 打包） |

### AI 反馈接口

| 方法 | 路径 | 请求体 | 说明 |
|------|------|------|------|
| POST | `/api/alarms/ai-feedback` | `{rating, comment, timestamp, quality_score}` | 提交 AI 分析反馈评分 |

---

## 主要功能详解

### 1. 报警数据查询

- 按学科 + 日期范围查询温湿度报警数据（默认显示上一月数据）
- 学科选择：必须选择学科后才能查询，支持 32 个医学实验室学科
- 实时显示处理状态统计（已处理 / 未处理数量）
- 设备报警详情列表展示

### 2. 数据趋势分析

| 图表 | 类型 | 说明 |
|------|------|------|
| 报警类型占比 | 饼图 | 温度/湿度/温湿度/未知报警的分布比例 |
| 各设备报警分布 | 柱状图 | 各设备报警次数排名（TOP 20） |
| 24 小时报警分布 | 堆叠柱状图 | 一天内每小时各类型报警趋势 |
| 星期报警分布 | 堆叠柱状图 | 一周各天的报警规律 |
| 月度日期分布 | 堆叠柱状图 | 一个月内每天各类型报警规律 |

### 3. AI 深度分析

AI 深度分析包含五大板块：

| 板块 | 内容 |
|------|------|
| 报警概况总结 | 总报警次数、处理完成率、环比变化趋势 |
| 设备报警规律 | TOP3 报警设备、重点关注设备、报警高峰时段 |
| 报警类型分析 | 各类型报警占比、风险评估 |
| 改善建议 | 按优先级排序的智能改善建议 |
| 处理评价 | 对现有处理措施的评价和建议 |

**AI 架构特点：**
- **多模型故障转移**：主模型（qwen3.6-flash）→ 备用模型（deepseek-chat）
- **统一 API 格式**：使用 OpenAI 兼容接口，易于扩展
- **质量评分**：自动对 AI 输出进行四维度评分（格式合规 30% / 内容充实度 30% / 建议质量 20% / 专业性 20%）
- **用户反馈**：支持用户对 AI 分析进行星级评分和文字评论

### 4. 报告生成

| 报告类型 | 说明 |
|----------|------|
| 月度回顾报告 | 月度温湿度监控数据汇总分析，包含趋势图表和统计信息 |
| 纠正报告 | 环境失控事件的纠正措施报告，按设备类型自动拆分 |

**报告内容包含：**
- 报警概况与统计
- 风险评估表（冰箱温度 / 环境温度 / 环境湿度三大类 20+ 场景）
- AI 生成的原因分析、影响评估、纠正措施
- AI 不可用时自动降级至规则引擎

**任务管理：**
- 后台异步生成（线程池）
- 实时进度追踪（0-100%）
- 超时控制（1 小时）
- 前端自动轮询（2 秒间隔）
- 单文件下载 + 批量 ZIP 下载
- 过期任务自动清理

### 5. 多格式导出

| 格式 | 内容 | 适用场景 |
|------|------|----------|
| JSON | 完整报警数据和 AI 分析结果 | 数据备份、二次处理 |
| Excel | 图表源数据（多工作表） | 数据分析、统计报告 |
| TXT | AI 分析报告（纯文本） | 快速查看、邮件正文 |
| Word | AI 分析报告（格式化文档） | 正式报告、存档 |

---

## 配置说明

### 学科配置 (`backend/config/departments.json`)

学科配置使用 `api_key_env` 指定环境变量名，API Key 从环境变量读取，确保密钥安全：

```json
{
  "departments": [
    {
      "id": "infection",
      "name": "感染中心常规PCR室",
      "api_key_env": "DEPARTMENT_INFECTION_API_KEY",
      "rules": {
        "uncontrol_threshold_minutes": 30,
        "allow_time_merge": true,
        "merge_gap_hours": 2,
        "importance_order": ["temperature", "humidity"]
      }
    }
  ]
}
```

| 配置项 | 说明 |
|--------|------|
| `id` | 学科唯一标识符 |
| `name` | 学科中文名称 |
| `api_key_env` | 环境变量名，对应 `.env` 中的 API Key |
| `rules.uncontrol_threshold_minutes` | 失控判定阈值（分钟） |
| `rules.allow_time_merge` | 是否允许时间合并 |
| `rules.merge_gap_hours` | 合并间隔（小时） |
| `rules.importance_order` | 报警类型重要性排序 |

### 环境变量 (`backend/.env`)

```env
# ========== 369平台 API 配置 ==========
API_KEY=your_default_api_key_here
API_BASE_URL=https://cloudapi.369clouds.com/openapi

# ========== 学科 API Keys ==========
# 格式: DEPARTMENT_{学科ID}_API_KEY
DEPARTMENT_INFECTION_API_KEY=your_infection_api_key
DEPARTMENT_FLOWCYTOMETRY_API_KEY=your_flowcytometry_api_key
# ... 其他 30 个学科的 API Key

# ========== 大模型 AI 配置（主模型）==========
AI_API_KEY=your_dashscope_api_key_here
AI_API_URL=https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions
AI_MODEL=qwen3.6-flash
AI_TIMEOUT=300

# ========== 大模型 AI 配置（备用模型）==========
AI_FALLBACK_API_KEY=your_deepseek_api_key_here
AI_FALLBACK_API_URL=https://api.deepseek.com/chat/completions
AI_FALLBACK_MODEL=deepseek-chat

# ========== 系统配置 ==========
FASTAPI_SERVER_HOST=0.0.0.0
FASTAPI_SERVER_PORT=8000
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# ========== 安全配置 ==========
# 访问令牌：留空关闭认证（本地开发）；公网部署务必设置，所有 /api 请求须携带 Bearer Token
APP_ACCESS_TOKEN=
# 运行环境：development / production；生产环境隐藏异常详情
APP_ENV=development

# ========== 缓存配置 ==========
ENABLE_CACHE=true
CACHE_TTL=3600

# ========== 代理配置 ==========
# 留空使用系统默认，设置为 'none' 禁用代理
PROXY_URL=none
NO_PROXY=
```

---

## 安全说明

### API Key 安全

- **不**将真实 API Key 直接写入 `departments.json`
- **必须**使用环境变量存储敏感的 API Key（通过 `api_key_env` 引用）
- `.env` 文件已添加到 `.gitignore`，不会纳入版本控制
- `.env.example` 为模板文件，不含真实密钥

### 访问令牌认证

- 通过环境变量 `APP_ACCESS_TOKEN` 配置访问令牌（公网部署务必设置）
- 配置后所有 `/api` 请求必须携带 `Authorization: Bearer <令牌>` 或 `X-API-Token: <令牌>`
- 前端首次打开页面时弹出「访问验证」面板，输入令牌后方可使用系统
- 令牌比较使用常量时间算法（`hmac.compare_digest`），防止时序攻击

### 路径遍历防护

文件下载接口内置路径遍历防护：
- 使用 `os.path.basename()` 提取纯文件名
- 使用 `os.path.realpath()` 解析真实路径
- 校验最终路径是否位于允许的目录范围内

### 信息泄露防护

- 生产环境（`APP_ENV=production`）下 API 错误响应隐藏异常详情，仅记录到服务端日志
- `outputs/` 导出目录不对外静态暴露，文件下载一律经认证的 API 端点
- AI 系统提示词内置防注入约束，报警数据中的指令不会被当作指令执行

### 传输安全

- 开发环境使用 HTTP
- CORS 中间件限制允许的前端域名
- 生产环境建议启用 HTTPS 并配置 CORS 白名单

---

## 架构设计

### 数据流

```
用户浏览器（Vue 3）
    │
    ├── GET/POST 请求 ──→ Vite Proxy ──→ FastAPI 后端（端口 8000）
    │                                         │
    │                                         ├── 369 平台 API（设备报警数据）
    │                                         ├── AI API（深度分析）
    │                                         │    ├── 主模型: 通义千问
    │                                         │    └── 备用: DeepSeek
    │                                         ├── 规则引擎（AI 降级）
    │                                         └── 文件导出（outputs/ 目录）
    │
    └──← 响应数据 / 文件下载
```

### 关键设计决策

| 决策 | 说明 |
|------|------|
| 前后端分离 | FastAPI (8000) + Vite Dev Server (5173)，Vite 代理解决跨域 |
| API Key 环境隔离 | 所有密钥存储在 `.env`，`departments.json` 仅存引用 |
| AI 多模型故障转移 | 主模型失败自动切换备用，确保服务可用性 |
| 异步报告生成 | 线程池后台执行，前端轮询，避免请求超时 |
| AI 降级机制 | AI 不可用时使用规则引擎 + 风险评估表生成内容 |
| 统一响应格式 | 所有接口使用 `{code, message, data}` 格式 |

---

## 开发指南

### 添加新功能

1. **后端路由**：在 `backend/api/v1.py` 中添加新的 endpoint
2. **业务逻辑**：在 `backend/services/__init__.py` 中实现服务方法
3. **数据模型**：在 `backend/models/schemas.py` 中定义 Pydantic 模型
4. **前端 API**：在 `frontend/src/api/temperature-humidity.js` 中添加调用方法
5. **状态管理**：在 `frontend/src/store/temperature-humidity.js` 中添加状态
6. **页面组件**：在 `frontend/src/views/` 中创建或修改 Vue 组件

### 目录规范

| 目录 | 职责 | 规则 |
|------|------|------|
| `api/` | API 路由定义 | 仅定义路由，不写业务逻辑 |
| `services/` | 业务逻辑层 | 向后端路由暴露统一接口 |
| `src/core/` | 核心模块 | 可独立复用的核心功能 |
| `src/utils/` | 工具模块 | 通用工具函数 |
| `models/` | 数据模型 | Pydantic 请求/响应模型 |
| `config/` | 配置文件 | JSON 配置文件 |
| `prompts/` | AI 提示词 | .txt 格式，按功能命名 |

### 导出功能扩展

导出功能位于 `backend/services/__init__.py`，主要方法：

- `export_alarm_data()` — JSON 格式
- `export_charts_excel()` — Excel 格式（多工作表）
- `export_ai_txt()` — TXT 格式
- `export_ai_word()` — Word 格式

### 添加新学科

1. 在 `backend/config/departments.json` 中添加学科配置，使用 `api_key_env` 引用环境变量
2. 在 `backend/.env` 中添加对应的 `DEPARTMENT_{ID}_API_KEY` 环境变量
3. 重启后端服务使配置生效

---

## 常见问题

### 后端相关

**Q: 学科选择显示无数据？**

A: 检查后端是否正常运行（访问 http://localhost:8000/api/departments 验证），确认 `.env` 文件中已配置正确的环境变量。

**Q: API 请求超时？**

A: 默认超时时间为 120 秒。如需调整可修改前端 `src/api/temperature-humidity.js` 中的 `timeout` 配置，以及后端 `AI_TIMEOUT` 环境变量。

**Q: AI 分析失败？**

A: 系统会自动故障转移到备用模型。检查主模型和备用模型的 API Key 是否均已正确配置。查看 `logs/app.log` 获取详细错误信息。

**Q: 导出功能无法下载文件？**

A: 检查后端 `outputs/` 目录是否有写入权限。

### 前端相关

**Q: 页面白屏或加载异常？**

A: 确保前端依赖已安装完整：`cd frontend && npm install`。检查浏览器控制台是否有网络请求错误。

**Q: 图表不显示？**

A: 确认已查询到报警数据，图表仅在数据加载完成后渲染。

**Q: 报告生成任务一直显示"处理中"？**

A: 检查后端日志确认任务是否超时（默认 1 小时超时）。可重启后端服务清理卡住的任务。

### 部署相关

**Q: 如何部署到生产环境？**

A: 完整步骤参见 `docs/2026-08-15-腾讯轻量云服务器部署指南.md`。简要流程：后端使用 `uvicorn` + `--host 0.0.0.0`，前端执行 `npm run build` 生成静态文件，使用 Nginx 部署并配置反向代理；公网部署请务必设置 `APP_ACCESS_TOKEN` 访问令牌。

**Q: 如何修改端口？**

A: 后端端口通过 `FASTAPI_SERVER_PORT` 环境变量配置，前端端口在 `vite.config.js` 中修改，同时需同步修改 Vite 代理目标地址。

---

## 更新日志

### v5.1.1 (2026-08-15) 安全加固

- ✅ 新增访问令牌认证（`APP_ACCESS_TOKEN`）：公网部署时所有 `/api` 请求须携带 Bearer Token，前端新增「访问验证」面板
- ✅ 移除 `/outputs` 静态目录暴露，导出文件下载一律经认证 API 端点
- ✅ 生产环境（`APP_ENV=production`）API 错误响应脱敏，隐藏内部路径等敏感信息
- ✅ AI 系统提示词增加防注入约束，避免报警数据中的指令被执行
- ✅ AI 反馈接口增加输入校验（评分范围、评论长度），防止日志污染

### v5.1.0 (2026-08-15)

- ✅ 依据《温湿度失控场景风险评估表（最终版）.xlsx》校准风险规则：霜层过厚拆分为「霜层低温（中低风险）/ 霜层高温（高风险）」两条场景
- ✅ 新增 `direction_keywords` 方向词匹配，场景需同时命中关键词与方向词才命中
- ✅ 修复抽屉破损被霜层场景错误截胡、JSON 与内置规则描述不一致、"中高风险"非法等级等问题
- ✅ 补充空调关机场景关键词（"关闭空调"、"空调关闭"）
- ✅ 新增 `tests/test_report_generator.py` 单元测试（45 个用例全部通过）
- ✅ 新增 `docs/2026-08-15-腾讯轻量云服务器部署指南.md` 部署文档

### v5.0.0

- ✅ 新增 AI 输出质量自动评分系统（四维度评分）
- ✅ 新增 AI 多模型故障转移（主模型 → 备用模型自动切换）
- ✅ 新增 AI 用户反馈收集（星级评分 + 评论记录）
- ✅ 新增路径遍历安全防护
- ✅ 优化报告生成流程和任务管理
- ✅ 修复中文文件名下载编码问题（RFC 5987）

### v4.0.0 (2026-05-05)

- ✅ 从 Streamlit 迁移至 FastAPI + Vue 3 前后端分离架构
- ✅ 添加多维度数据趋势分析图表（5 个 ECharts 图表）
- ✅ 新增 AI 深度分析功能（五大板块）
- ✅ 实现多种导出格式（JSON、Excel、TXT、Word）
- ✅ 优化学科管理和 API Key 安全配置
- ✅ 添加一键启动/停止脚本

---

## 许可证

Private - All Rights Reserved
