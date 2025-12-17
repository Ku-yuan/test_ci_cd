# FastAPI CI/CD 示例项目

这是一个用于学习 GitHub CI/CD 流程的 FastAPI 示例项目。

## 🚀 项目简介

这个项目演示了如何：
- 使用 **FastAPI** 构建 RESTful API
- 使用 **uv** 管理 Python 依赖和虚拟环境
- 使用 **pytest** 编写自动化测试
- 使用 **GitHub Actions** 实现 CI/CD 自动化

## 📁 项目结构

```
test_ci_cd/
├── .github/
│   └── workflows/
│       └── ci.yml          # GitHub Actions 工作流配置
├── src/
│   ├── __init__.py
│   └── app/
│       ├── __init__.py
│       └── main.py         # FastAPI 主应用
├── tests/
│   ├── __init__.py
│   └── test_main.py        # 测试文件
├── pyproject.toml          # 项目配置和依赖
└── README.md               # 项目说明
```

## 🛠️ 环境要求

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) - 现代 Python 包管理器

## 📦 安装 uv

```bash
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 🏃 快速开始

### 1. 克隆项目

```bash
git clone <你的仓库地址>
cd test_ci_cd
```

### 2. 安装依赖

```bash
# 安装生产依赖
uv sync

# 安装开发依赖（包含测试工具）
uv sync --dev
```

### 3. 运行应用

```bash
# 启动开发服务器
uv run uvicorn src.app.main:app --reload

# 或者指定端口
uv run uvicorn src.app.main:app --reload --port 8000
```

### 4. 访问 API 文档

启动服务后，打开浏览器访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🧪 运行测试

```bash
# 运行所有测试
uv run pytest

# 详细输出
uv run pytest -v

# 运行特定测试文件
uv run pytest tests/test_main.py

# 显示打印输出
uv run pytest -s
```

## 🔍 代码检查

```bash
# 检查代码风格
uv run ruff check src/ tests/

# 检查代码格式
uv run ruff format --check src/ tests/

# 自动修复问题
uv run ruff check --fix src/ tests/

# 自动格式化代码
uv run ruff format src/ tests/
```

## 🔄 CI/CD 流程

本项目使用 GitHub Actions 实现自动化 CI/CD，工作流包含以下阶段：

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  代码检查   │ -> │    测试     │ -> │    构建     │ -> │    部署     │
│   (Lint)    │    │   (Test)    │    │   (Build)   │    │  (Deploy)   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
     Ruff          pytest x 3版本       uv build         仅 main 分支
```

### 触发条件

- 推送到 `main` 或 `develop` 分支
- 创建 Pull Request 到 `main` 分支
- 手动触发（workflow_dispatch）

### 查看工作流状态

推送代码后，访问 GitHub 仓库的 "Actions" 标签页查看工作流执行状态。

## 📝 API 端点

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/` | 欢迎信息 |
| GET | `/health` | 健康检查 |
| GET | `/items` | 获取所有商品 |
| GET | `/items/{id}` | 获取单个商品 |
| POST | `/items` | 创建商品 |
| DELETE | `/items/{id}` | 删除商品 |

## 🎯 学习要点

### 1. GitHub Actions 基础

- **工作流 (Workflow)**: 自动化流程，由一个或多个作业组成
- **作业 (Job)**: 一组步骤，在同一个运行器上执行
- **步骤 (Step)**: 单个任务，可以是命令或动作 (Action)
- **动作 (Action)**: 可重用的代码单元

### 2. CI/CD 概念

- **持续集成 (CI)**: 频繁合并代码，自动运行测试
- **持续部署 (CD)**: 自动将通过测试的代码部署到生产环境

### 3. 最佳实践

- 使用矩阵策略在多个版本上测试
- 设置作业依赖确保执行顺序
- 使用环境保护规则控制部署
- 缓存依赖加速构建

## 📚 相关资源

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [uv 官方文档](https://docs.astral.sh/uv/)
- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [pytest 文档](https://docs.pytest.org/)

## 📄 许可证

MIT License
