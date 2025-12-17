"""
FastAPI 主应用模块

这是应用的入口文件，定义了 FastAPI 应用实例和路由。
FastAPI 是一个现代、快速（高性能）的 Web 框架，用于构建 API。

主要特点：
- 快速：基于 Starlette 和 Pydantic，性能非常高
- 快速编码：提高开发速度约 200% 到 300%
- 更少的 bug：减少约 40% 的人为错误
- 直观：强大的编辑器支持，自动补全无处不在
- 简单：设计易于使用和学习
- 简短：最小化代码重复
- 健壮：生产可用的代码，自动生成交互式文档
- 基于标准：基于 OpenAPI 和 JSON Schema
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# ============================================
# 创建 FastAPI 应用实例
# ============================================
# title: API 文档中显示的标题
# description: API 的详细描述
# version: API 版本号
# docs_url: Swagger UI 文档的 URL 路径
# redoc_url: ReDoc 文档的 URL 路径
app = FastAPI(
    title="FastAPI CI/CD 示例",
    description="一个用于学习 GitHub Actions CI/CD 流程的示例项目",
    version="0.1.0",
    docs_url="/docs",  # Swagger UI 文档地址
    redoc_url="/redoc",  # ReDoc 文档地址
)


# ============================================
# Pydantic 数据模型定义
# ============================================
# Pydantic 模型用于：
# 1. 请求体的数据验证
# 2. 响应数据的序列化
# 3. 自动生成 API 文档中的 Schema


class Item(BaseModel):
    """
    商品数据模型

    Pydantic 会自动验证传入的数据类型，
    如果类型不匹配会返回详细的错误信息。

    Attributes:
        name: 商品名称，必填字段
        price: 商品价格，必须为正数
        description: 商品描述，可选字段，默认为 None
    """

    name: str  # 必填的字符串字段
    price: float  # 必填的浮点数字段
    description: str | None = None  # 可选字段，使用 Python 3.10+ 的类型语法


class Message(BaseModel):
    """
    通用消息响应模型

    用于返回简单的文本消息响应。
    """

    message: str


# ============================================
# 模拟数据库 - 使用字典存储数据
# ============================================
# 在实际项目中，这里会连接真正的数据库（如 PostgreSQL、MySQL 等）
# 这里为了演示简单，使用内存中的字典
items_db: dict[int, Item] = {}
# 用于生成自增 ID
next_id: int = 1


# ============================================
# 路由定义 - API 端点
# ============================================


@app.get("/", response_model=Message)
async def root():
    """
    根路径端点

    这是 API 的根路径，返回欢迎信息。
    可以用来检测 API 是否正常运行。

    Returns:
        dict: 包含欢迎消息的字典

    使用方式：
        GET /
    """
    return {"message": "欢迎使用 FastAPI CI/CD 示例 API！"}


@app.get("/health", response_model=Message)
async def health_check():
    """
    健康检查端点

    用于检测服务是否正常运行。
    在 CI/CD 流程中，这个端点常用于：
    - 容器健康检查
    - 负载均衡器的健康探测
    - 监控系统的存活检测

    Returns:
        dict: 健康状态信息
    """
    return {"message": "服务运行正常"}


@app.get("/items", response_model=list[Item])
async def get_items():
    """
    获取所有商品列表

    返回数据库中存储的所有商品。

    Returns:
        list[Item]: 商品列表

    使用方式：
        GET /items
    """
    return list(items_db.values())


@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int):
    """
    根据 ID 获取单个商品

    路径参数 {item_id} 会自动解析为整数类型。
    如果商品不存在，返回 404 错误。

    Args:
        item_id: 商品的唯一标识符

    Returns:
        Item: 商品信息

    Raises:
        HTTPException: 当商品不存在时返回 404

    使用方式：
        GET /items/1
    """
    # 检查商品是否存在
    if item_id not in items_db:
        # 抛出 HTTP 异常，FastAPI 会自动转换为 JSON 响应
        raise HTTPException(status_code=404, detail=f"商品 ID {item_id} 未找到")
    return items_db[item_id]


@app.post("/items", response_model=Item, status_code=201)
async def create_item(item: Item):
    """
    创建新商品

    请求体中的 JSON 数据会自动验证并转换为 Item 对象。
    Pydantic 会确保数据类型正确，如果不正确会返回 422 错误。

    Args:
        item: 要创建的商品数据（从请求体自动解析）

    Returns:
        Item: 创建成功的商品信息

    使用方式：
        POST /items
        Content-Type: application/json
        {
            "name": "商品名称",
            "price": 99.99,
            "description": "商品描述（可选）"
        }
    """
    global next_id
    # 将商品添加到数据库
    items_db[next_id] = item
    # ID 自增
    next_id += 1
    return item


@app.delete("/items/{item_id}", response_model=Message)
async def delete_item(item_id: int):
    """
    删除指定商品

    根据 ID 删除商品，如果商品不存在则返回 404 错误。

    Args:
        item_id: 要删除的商品 ID

    Returns:
        dict: 删除成功的消息

    Raises:
        HTTPException: 当商品不存在时返回 404

    使用方式：
        DELETE /items/1
    """
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail=f"商品 ID {item_id} 未找到")
    # 从数据库中删除商品
    del items_db[item_id]
    return {"message": f"商品 ID {item_id} 已成功删除"}


@app.get("/test", response_model=Message)
async def test():
    return {"message": "test"}


# ============================================
# 启动说明
# ============================================
# 运行此应用的方式：
#
# 1. 使用 uv 安装依赖：
#    uv sync
#
# 2. 启动开发服务器：
#    uv run uvicorn src.app.main:app --reload
#
# 3. 访问 API 文档：
#    - Swagger UI: http://localhost:8000/docs
#    - ReDoc: http://localhost:8000/redoc
#
# --reload 参数会在代码修改时自动重启服务器
