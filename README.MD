# 旅游线路规划系统

Django + Vue 的旅游线路规划系统，覆盖景点路线设计、费用预算、报名成团和出行通知。项目按前后端模块拆分，后端提供 REST API，前端提供运营工作台界面。

## 功能模块

- 景点库：维护城市、类型、游玩时长、票价和亮点信息。
- 线路设计：组合多日景点停靠点，展示基础费用、门票合计、导游费和预计总价。
- 报名成团：新增报名、统计已报名人数、展示最低成团进度。
- 出行通知：按线路发布集合提醒、天气提示、物品清单和行程变更。

## 目录结构

```text
backend/
  apps/
    attractions/      景点模块
    routes/           线路与预算模块
    bookings/         报名成团模块
    notifications/    出行通知模块
  travel_planner/     Django 项目配置
frontend/
  src/api/            API 请求封装
  src/components/     通用组件
  src/pages/          独立业务页面
  src/styles/         全局样式
docker-compose.yml
```

## Docker 启动

```bash
docker compose up --build
```

如果后端镜像在 `pip install -r requirements.txt` 阶段失败，通常是容器内访问 PyPI 超时或被网络策略拦截。后端 Dockerfile 默认使用清华 PyPI 镜像，也可以改用其他源：

```bash
docker compose build backend --build-arg PIP_INDEX_URL=https://pypi.org/simple --build-arg PIP_TRUSTED_HOST=pypi.org
docker compose up
```

启动后访问：

- 前端：http://localhost:5173
- 后端健康检查：http://localhost:8000/api/health/
- API 示例：http://localhost:8000/api/routes/

后端容器启动时会自动执行数据库迁移并写入示例数据。

## 本地开发

后端：

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py seed_demo
python manage.py runserver 127.0.0.1:8000
```

前端：

```bash
cd frontend
npm install
npm run dev
```

## API 概览

- `GET/POST /api/attractions/`
- `GET/POST /api/routes/`
- `GET/POST /api/bookings/`
- `GET/POST /api/notifications/`
- `GET /api/health/`
