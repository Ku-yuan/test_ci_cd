"""
FastAPI 应用测试模块

这个模块包含对 FastAPI 应用的自动化测试。
测试是 CI/CD 流程中非常重要的一环，确保代码更改不会破坏现有功能。

使用 pytest + httpx 进行异步 API 测试：
- pytest: Python 最流行的测试框架
- httpx: 支持异步的 HTTP 客户端
- ASGITransport: 允许直接测试 ASGI 应用，无需启动真正的服务器
"""

import pytest
from httpx import ASGITransport, AsyncClient

import src.app.main as main_module

# 导入我们的 FastAPI 应用实例
from src.app.main import app, items_db

# ============================================
# pytest fixture - 测试夹具
# ============================================
# fixture 是 pytest 的核心概念，用于：
# 1. 设置测试环境（setup）
# 2. 提供测试所需的资源
# 3. 测试后清理（teardown）


@pytest.fixture
def clear_db():
    """
    清理数据库的 fixture

    在每个测试前后清空模拟数据库。
    这确保每个测试都在干净的环境中运行，
    测试之间不会相互影响。

    使用 yield 关键字：
    - yield 之前的代码在测试前执行（setup）
    - yield 之后的代码在测试后执行（teardown）
    """
    # Setup: 测试前清空数据库并重置 ID
    items_db.clear()
    main_module.next_id = 1  # 重置 ID 计数器
    # 将控制权交给测试函数
    yield
    # Teardown: 测试后再次清空，保持环境干净
    items_db.clear()
    main_module.next_id = 1


@pytest.fixture
async def client():
    """
    创建异步测试客户端的 fixture

    ASGITransport 允许我们直接与 ASGI 应用通信，
    无需启动真正的 HTTP 服务器，测试速度更快。

    async with 确保客户端在使用后正确关闭。
    """
    # 创建 ASGI 传输层，直接连接到 FastAPI 应用
    transport = ASGITransport(app=app)
    # 创建异步客户端
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


# ============================================
# 测试用例
# ============================================
# 每个测试函数以 test_ 开头，pytest 会自动发现并执行


class TestRootEndpoint:
    """
    根路径端点测试类

    测试 GET / 端点的功能。
    使用类来组织相关的测试用例是一个好习惯。
    """

    async def test_root_returns_welcome_message(self, client: AsyncClient):
        """
        测试根路径返回欢迎消息

        这是一个基本的冒烟测试（smoke test），
        验证 API 是否能正常响应。
        """
        # 发送 GET 请求
        response = await client.get("/")

        # 断言状态码为 200（成功）
        assert response.status_code == 200
        # 断言响应内容包含预期的消息
        assert response.json() == {"message": "欢迎使用 FastAPI CI/CD 示例 API！"}


class TestHealthEndpoint:
    """
    健康检查端点测试类

    健康检查在生产环境中非常重要，
    用于监控系统和负载均衡器判断服务是否可用。
    """

    async def test_health_check_returns_ok(self, client: AsyncClient):
        """测试健康检查端点返回正常状态"""
        response = await client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"message": "服务运行正常"}


class TestItemsEndpoints:
    """
    商品相关端点测试类

    测试完整的 CRUD（创建、读取、更新、删除）操作。
    """

    async def test_get_items_empty_database(
        self,
        client: AsyncClient,
        clear_db,  # 使用 fixture 确保数据库为空
    ):
        """
        测试在空数据库时获取商品列表

        预期结果：返回空列表
        """
        response = await client.get("/items")

        assert response.status_code == 200
        assert response.json() == []

    async def test_create_item_success(self, client: AsyncClient, clear_db):
        """
        测试成功创建商品

        验证：
        1. 返回状态码 201（已创建）
        2. 返回的数据与提交的数据一致
        """
        # 准备测试数据
        item_data = {
            "name": "测试商品",
            "price": 99.99,
            "description": "这是一个测试商品",
        }

        # 发送 POST 请求创建商品
        response = await client.post("/items", json=item_data)

        # 验证响应
        assert response.status_code == 201
        response_data = response.json()
        assert response_data["name"] == item_data["name"]
        assert response_data["price"] == item_data["price"]
        assert response_data["description"] == item_data["description"]

    async def test_create_and_get_item(self, client: AsyncClient, clear_db):
        """
        测试创建商品后能正确获取

        这是一个集成测试，验证 POST 和 GET 端点协同工作。
        """
        # 创建商品
        item_data = {"name": "测试商品", "price": 50.0}
        await client.post("/items", json=item_data)

        # 获取商品列表
        response = await client.get("/items")

        assert response.status_code == 200
        items = response.json()
        assert len(items) == 1
        assert items[0]["name"] == "测试商品"

    async def test_get_item_not_found(self, client: AsyncClient, clear_db):
        """
        测试获取不存在的商品返回 404

        错误处理测试同样重要，确保 API 正确处理异常情况。
        """
        response = await client.get("/items/999")

        assert response.status_code == 404
        assert "未找到" in response.json()["detail"]

    async def test_delete_item_success(self, client: AsyncClient, clear_db):
        """
        测试成功删除商品

        步骤：
        1. 先创建一个商品
        2. 删除该商品
        3. 验证删除成功
        """
        # 创建商品
        item_data = {"name": "待删除商品", "price": 10.0}
        await client.post("/items", json=item_data)

        # 删除商品（ID 为 1，因为是第一个创建的）
        response = await client.delete("/items/1")

        assert response.status_code == 200
        assert "已成功删除" in response.json()["message"]

    async def test_delete_item_not_found(self, client: AsyncClient, clear_db):
        """测试删除不存在的商品返回 404"""
        response = await client.delete("/items/999")

        assert response.status_code == 404


class TestDataValidation:
    """
    数据验证测试类

    测试 Pydantic 的数据验证功能。
    确保无效数据被正确拒绝。
    """

    async def test_create_item_invalid_data(self, client: AsyncClient, clear_db):
        """
        测试提交无效数据时返回 422

        422 Unprocessable Entity 表示请求格式正确，
        但由于语义错误（数据验证失败）无法处理。
        """
        # 缺少必填字段 'name'
        invalid_data = {"price": 99.99}

        response = await client.post("/items", json=invalid_data)

        # Pydantic 验证失败会返回 422
        assert response.status_code == 422

    async def test_create_item_wrong_type(self, client: AsyncClient, clear_db):
        """
        测试提交错误类型的数据

        price 应该是数字，传入字符串应该失败。
        """
        invalid_data = {
            "name": "测试商品",
            "price": "不是数字",  # 应该是 float
        }

        response = await client.post("/items", json=invalid_data)

        assert response.status_code == 422


# ============================================
# 运行测试说明
# ============================================
#
# 使用 uv 运行测试：
#   uv run pytest
#
# 显示详细输出：
#   uv run pytest -v
#
# 运行特定测试文件：
#   uv run pytest tests/test_main.py
#
# 运行特定测试类：
#   uv run pytest tests/test_main.py::TestItemsEndpoints
#
# 运行特定测试方法：
#   uv run pytest tests/test_main.py::TestItemsEndpoints::test_create_item_success
#
# 显示覆盖率报告（需要安装 pytest-cov）：
#   uv run pytest --cov=src
