# 容器构建诊断流程

## 总览

本文档整理了旅游线路规划系统的容器构建全流程诊断方法，覆盖四大核心阶段：
**依赖安装 → 数据库迁移 → 演示数据写入 → 健康检查**

---

## 一、依赖安装阶段诊断

### 1.1 后端依赖（Python）

**构建配置**：[backend/Dockerfile](file:///Users/yurik/Desktop/trae_label_project/SOLO_DOG_10_2/solo_dog_10_32/gy-56/backend/Dockerfile#L1-L23)

**依赖清单**：[backend/requirements.txt](file:///Users/yurik/Desktop/trae_label_project/SOLO_DOG_10_2/solo_dog_10_32/gy-56/backend/requirements.txt#L1-L4)

| 依赖包 | 版本 | 用途 |
|--------|------|------|
| Django | 5.0.6 | Web 框架 |
| djangorestframework | 3.15.1 | REST API 框架 |
| django-cors-headers | 4.3.1 | CORS 跨域支持 |
| gunicorn | 22.0.0 | WSGI 生产服务器 |

**构建流程**：
```
第 14-18 行：升级 pip/setuptools/wheel → 安装 requirements.txt
```

**常见问题与诊断**：

| 问题现象 | 可能原因 | 诊断命令 | 解决方案 |
|----------|----------|----------|----------|
| `pip install` 超时 | 网络访问 PyPI 受限 | `docker compose build backend --progress=plain` | 切换镜像源：清华/阿里云/官方 |
| 包版本冲突 | 依赖隐式依赖不兼容 | 检查构建日志中 `ERROR: ResolutionImpossible` | 锁定间接依赖版本 |
| `No such file or directory` | requirements.txt 缺失 | `ls backend/requirements.txt` | 确认文件存在且位于构建上下文 |
| 架构不兼容 | ARM 机器构建 amd64 镜像 | `docker buildx ls` | 使用 `--platform linux/amd64` 或原生构建 |

**切换 PyPI 镜像源**：
```bash
# 使用官方源
docker compose build backend \
  --build-arg PIP_INDEX_URL=https://pypi.org/simple \
  --build-arg PIP_TRUSTED_HOST=pypi.org

# 使用阿里云镜像
docker compose build backend \
  --build-arg PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple \
  --build-arg PIP_TRUSTED_HOST=mirrors.aliyun.com
```

**验证依赖安装成功**：
```bash
# 进入容器检查已安装包
docker compose exec backend pip list | grep -E "Django|rest|cors|gunicorn"

# 验证 Django 可导入
docker compose exec backend python -c "import django; print(django.get_version())"
```

---

### 1.2 前端依赖（Node.js）

**构建配置**：[frontend/Dockerfile](file:///Users/yurik/Desktop/trae_label_project/SOLO_DOG_10_2/solo_dog_10_32/gy-56/frontend/Dockerfile#L1-L11)

**依赖清单**：[frontend/package.json](file:///Users/yurik/Desktop/trae_label_project/SOLO_DOG_10_2/solo_dog_10_32/gy-56/frontend/package.json#L11-L15)

| 依赖包 | 版本 | 用途 |
|--------|------|------|
| vue | 3.4.27 | 前端框架 |
| vite | 5.2.12 | 构建工具/开发服务器 |
| @vitejs/plugin-vue | 5.0.5 | Vue 3 单文件组件支持 |

**构建流程**：
```
第 6 行：npm install（基于 package.json + package-lock.json）
```

**常见问题与诊断**：

| 问题现象 | 可能原因 | 诊断命令 | 解决方案 |
|----------|----------|----------|----------|
| `npm install` 卡住 | npm 源访问慢 | 构建时设置 `--network=host` 观察 | 配置 npm registry 镜像 |
| lockfile 版本不匹配 | lockfile 与 npm 版本冲突 | 检查日志中的 `EBADENGINE` 警告 | 重新生成 `package-lock.json` |
| EACCES 权限错误 | node_modules 目录权限 | `ls -la frontend/node_modules` | 清理后重新安装，或使用 `--unsafe-perm` |

**使用国内 npm 镜像**：
在 `frontend/Dockerfile` 中修改：
```dockerfile
RUN npm config set registry https://registry.npmmirror.com && npm install
```

**验证依赖安装成功**：
```bash
# 检查 node_modules 完整性
docker compose exec frontend ls node_modules/vue/package.json

# 验证 Vite 可执行
docker compose exec frontend npx vite --version
```

---

## 二、数据库迁移阶段诊断

### 2.1 迁移架构总览

**迁移依赖链**（按执行顺序）：
```
attractions → routes → bookings
           ↘ routes → notifications
```

| 迁移文件 | 依赖 | 创建的模型 |
|----------|------|------------|
| [attractions/0001_initial.py](file:///Users/yurik/Desktop/trae_label_project/SOLO_DOG_10_2/solo_dog_10_32/gy-56/backend/apps/attractions/migrations/0001_initial.py#L14-L29) | 无 | Attraction |
| [routes/0001_initial.py](file:///Users/yurik/Desktop/trae_label_project/SOLO_DOG_10_2/solo_dog_10_32/gy-56/backend/apps/routes/migrations/0001_initial.py#L15-L60) | attractions → 0001 | TravelRoute, RouteStop |
| [bookings/0001_initial.py](file:///Users/yurik/Desktop/trae_label_project/SOLO_DOG_10_2/solo_dog_10_32/gy-56/backend/apps/bookings/migrations/0001_initial.py#L15-L32) | routes → 0001 | Booking |
| [notifications/0001_initial.py](file:///Users/yurik/Desktop/trae_label_project/SOLO_DOG_10_2/solo_dog_10_32/gy-56/backend/apps/notifications/migrations/0001_initial.py#L15-L31) | routes → 0001 | TravelNotice |

**启动时执行入口**：[backend/Dockerfile 第 23 行](file:///Users/yurik/Desktop/trae_label_project/SOLO_DOG_10_2/solo_dog_10_32/gy-56/backend/Dockerfile#L23-L23)
```bash
python manage.py migrate --noinput
```

### 2.2 诊断步骤

**步骤 1：检查迁移是否执行**
```bash
# 查看容器启动日志中迁移相关输出
docker compose logs backend | grep -i "migrate\|Running migrations"

# 检查 Django 迁移记录表
docker compose exec backend python manage.py showmigrations
```

**期望输出**（所有迁移标记为 `[X]`）：
```
attractions
 [X] 0001_initial
bookings
 [X] 0001_initial
notifications
 [X] 0001_initial
routes
 [X] 0001_initial
```

**步骤 2：检查表是否创建成功**
```bash
# 直接查询 SQLite（需先安装 sqlite3 或使用 Django ORM）
docker compose exec backend python -c "
import django
django.setup()
from django.db import connection
tables = connection.introspection.table_names()
for t in sorted(tables):
    if not t.startswith('django_') and not t.startswith('auth_'):
        print(f'  ✓ {t}')
"
```

**期望存在的业务表**：
- `attractions_attraction`
- `routes_travelroute`
- `routes_routestop`
- `bookings_booking`
- `notifications_travelnotice`

**步骤 3：检查数据库文件权限**
```bash
# 数据库路径配置：settings.py 第 59 行
docker compose exec backend ls -la /app/data/

# 确认 SQLite 文件可读写
docker compose exec backend python -c "
import sqlite3
conn = sqlite3.connect('/app/data/db.sqlite3')
cursor = conn.execute('SELECT COUNT(*) FROM attractions_attraction')
print(f'DB is writable, attractions count: {cursor.fetchone()[0]}')
conn.close()
"
```

### 2.3 常见问题排查

| 问题 | 症状 | 根因 | 修复方法 |
|------|------|------|----------|
| 迁移卡住无输出 | 日志停在 `Operations to perform:` | SQLite 文件锁或磁盘只读 | 检查 volume 挂载权限，重启容器 |
| `No migrations to apply` | 新表未创建 | 迁移文件未被 Django 发现 | 确认 `INSTALLED_APPS` 包含对应 app |
| `django_migrations` 表损坏 | 报错 `relation does not exist` | 手动删除了系统表 | 清空 volume 重新执行：`docker volume rm gy-56_backend-data` |
| 外键约束失败 | `FOREIGN KEY constraint failed` | 迁移顺序错误或数据不一致 | 使用 `migrate --fake` 修正记录或清空重建 |

---

## 三、演示数据写入阶段诊断

### 3.1 数据写入流程

**命令定义**：[apps/routes/management/commands/seed_demo.py](file:///Users/yurik/Desktop/trae_label_project/SOLO_DOG_10_2/solo_dog_10_32/gy-56/backend/apps/routes/management/commands/seed_demo.py#L1-L137)

**执行时机**：容器启动 CMD 第二阶段
```bash
python manage.py seed_demo
```

**写入数据清单**：

| 模型 | 数量 | 关键字段 | 幂等策略 |
|------|------|----------|----------|
| Attraction | 4 条 | 西湖苏堤/灵隐寺/宋城/夫子庙 | `update_or_create(name=...)` |
| TravelRoute | 1 条 | 杭州湖山文化 2 日游 | `update_or_create(title=...)` |
| RouteStop | 3 条 | Day1-苏堤, Day1-灵隐寺, Day2-宋城 | 先 delete 后 create |
| Booking | 2 条 | 李女士(3人)/王先生(2人) | `update_or_create(route+phone)` |
| TravelNotice | 2 条 | 集合通知/雨具提醒 | `update_or_create(route+title)` |

### 3.2 诊断步骤

**步骤 1：检查演示数据命令输出**
```bash
# 查看启动日志
docker compose logs backend | grep -A 20 "seed_demo\|Demo data"

# 手动重新执行（可重复执行，幂等安全）
docker compose exec backend python manage.py seed_demo --verbosity 2
```

**步骤 2：验证各表数据量**
```bash
docker compose exec backend python -c "
import django
django.setup()
from apps.attractions.models import Attraction
from apps.routes.models import TravelRoute, RouteStop
from apps.bookings.models import Booking
from apps.notifications.models import TravelNotice

print('=== 演示数据统计 ===')
print(f'景点数量:    {Attraction.objects.count()} (期望: 4)')
print(f'线路数量:    {TravelRoute.objects.count()} (期望: 1)')
print(f'停靠点数量:  {RouteStop.objects.count()} (期望: 3)')
print(f'报名记录:    {Booking.objects.count()} (期望: 2)')
print(f'出行通知:    {TravelNotice.objects.count()} (期望: 2)')
"
```

**步骤 3：验证 API 数据返回**
```bash
# 通过健康检查确认服务正常后调用业务 API
curl -s http://localhost:8000/api/attractions/ | python -m json.tool
curl -s http://localhost:8000/api/routes/ | python -m json.tool
```

**期望返回示例（线路 API）**：
```json
[
  {
    "id": 1,
    "title": "杭州湖山文化 2 日游",
    "city": "杭州",
    "days": 2,
    "stops_count": 3,
    "bookings_count": 2,
    "status": "forming"
  }
]
```

### 3.3 常见问题排查

| 问题 | 症状 | 根因 | 修复方法 |
|------|------|------|----------|
| 数据为空 | API 返回 `[]` | 迁移未执行先运行 seed | 先执行 `migrate` 再 `seed_demo` |
| `ProgrammingError` | 报错 `table does not exist` | 同上 | 同上 |
| 停靠点重复 | RouteStop 数量 > 3 | 旧容器数据残留 | 手动清理或删除 volume 重建 |
| 日期异常 | travel_date 显示错误 | 时区配置问题 | 确认 `TIME_ZONE = 'Asia/Shanghai'`（settings.py 第 64 行） |
| 中文乱码 | 数据写入后显示乱码 | SQLite 编码或终端编码 | SQLite 默认 UTF-8，检查终端 `LANG=zh_CN.UTF-8` |

**重置演示数据（完全清空后重新写入）**：
```bash
# 方法 1：删除 volume（最彻底）
docker compose down -v
docker compose up --build

# 方法 2：使用 Django flush（保留系统表）
docker compose exec backend python manage.py flush --noinput
docker compose exec backend python manage.py migrate --noinput
docker compose exec backend python manage.py seed_demo
```

---

## 四、健康检查阶段诊断

### 4.1 当前健康检查实现

**健康检查端点**：[travel_planner/urls.py 第 8-84 行](file:///Users/yurik/Desktop/trae_label_project/SOLO_DOG_10_2/solo_dog_10_32/gy-56/backend/travel_planner/urls.py#L8-L84)

**访问路径**：`GET /api/health/`

**三层级联检查**：

| 检查项 | 检测内容 | 通过条件 |
|--------|----------|----------|
| `database` | 执行 `SELECT 1` 验证数据库连通性 | 查询成功 |
| `migrations` | 检查 5 张核心业务表是否存在 | 所有表存在：`attractions_attraction`、`routes_travelroute`、`routes_routestop`、`bookings_booking`、`notifications_travelnotice` |
| `demo_data` | 检查 5 类演示数据数量是否达标 | attractions>=4, routes>=1, stops>=3, bookings>=2, notices>=2 |

检查具有级联跳过逻辑：上一层失败则下一层标记 `skipped`，避免无效报错。

**健康时响应**（HTTP 200）：
```json
{
    "status": "ok",
    "service": "travel-planner",
    "checks": {
        "database": "ok",
        "migrations": "ok",
        "demo_data": "ok"
    }
}
```

**不健康时响应**（HTTP 503）：
```json
{
    "status": "unhealthy",
    "service": "travel-planner",
    "checks": {
        "database": "ok",
        "migrations": "missing tables: bookings_booking",
        "demo_data": "skipped"
    }
}
```

### 4.2 完整健康检查诊断流程

**层次 1：基础连通性检查**
```bash
# TCP 端口是否监听
nc -zv localhost 8000

# HTTP 响应码
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:8000/api/health/

# 响应体内容
curl -s http://localhost:8000/api/health/ | python -m json.tool
```

**期望输出**：
```json
{
    "status": "ok",
    "service": "travel-planner",
    "checks": {
        "database": "ok",
        "migrations": "ok",
        "demo_data": "ok"
    }
}
```

**层次 2：服务深度健康检查**
```bash
# 1. 数据库连接检查
docker compose exec backend python -c "
import django
django.setup()
from django.db import connection
cursor = connection.cursor()
cursor.execute('SELECT 1')
print('DB Connection: OK')
cursor.close()
"

# 2. 迁移状态检查
docker compose exec backend python manage.py showmigrations

# 3. 数据完整性检查（演示数据，5 类全部检查）
docker compose exec backend python -c "
import django
django.setup()
from apps.attractions.models import Attraction
from apps.routes.models import TravelRoute, RouteStop
from apps.bookings.models import Booking
from apps.notifications.models import TravelNotice
counts = {
    '景点(>=4)': Attraction.objects.count(),
    '线路(>=1)': TravelRoute.objects.count(),
    '停靠点(>=3)': RouteStop.objects.count(),
    '报名(>=2)': Booking.objects.count(),
    '通知(>=2)': TravelNotice.objects.count(),
}
for label, cnt in counts.items():
    print(f'  {label}: {cnt}')
"

# 4. Gunicorn worker 状态
docker compose exec backend ps aux | grep gunicorn
```

**层次 3：前端代理连通性检查**
```bash
# 前端容器是否能访问后端
docker compose exec frontend wget -qO- http://backend:8000/api/health/

# 前端开发服务器代理配置（Vite 代理）
curl -s -o /dev/null -w "Frontend Status: %{http_code}\n" http://localhost:5173
```

### 4.3 Docker Compose 健康检查与启动顺序

编排文件 [docker-compose.yml](file:///Users/yurik/Desktop/trae_label_project/SOLO_DOG_10_2/solo_dog_10_32/gy-56/docker-compose.yml) 已配置健康检查和启动依赖：**后端健康检查通过后前端才启动**，避免前端先起来报错。

**后端健康检查**（基于 Python urllib，镜像内不需要额外安装 curl）：
```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health/')"]
  interval: 5s
  timeout: 3s
  retries: 12
  start_period: 15s
```

**前端启动依赖**（等待后端 healthy）：
```yaml
depends_on:
  backend:
    condition: service_healthy
```

**前端健康检查**（使用 alpine 自带的 wget）：
```yaml
healthcheck:
  test: ["CMD", "wget", "-qO-", "http://localhost:5173/"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 10s
```

**启动顺序时序**：
```
backend 容器启动
  ├─ 15s start_period（等待 migrate + seed_demo 执行）
  ├─ 每 5s 探测 /api/health/（HTTP 503→重试, HTTP 200→通过）
  └─ 连续通过后标记为 healthy
       ↓
frontend 容器才启动
  └─ npm run dev → Vite 监听 5173
```

**查看健康状态**：
```bash
docker compose ps
docker compose logs backend | grep -i "migrate\|seed\|gunicorn\|Starting"
```

### 4.4 常见问题排查

| 问题 | 症状 | 根因 | 修复方法 |
|------|------|------|----------|
| Connection refused | `curl: (7) Failed to connect` | gunicorn 未启动或绑定错误 | 检查 CMD 命令，确认 `--bind 0.0.0.0:8000` |
| 502 Bad Gateway | 前端代理报错 | 后端未就绪或已崩溃 | 检查后端日志 `docker compose logs backend` |
| 响应超时 | curl 长时间无响应 | gunicorn worker 卡死 | 重启容器或增加 worker 数量 |
| CORS 错误 | 浏览器控制台跨域报错 | `CORS_ALLOWED_ORIGINS` 配置缺失 | 确认 settings.py 第 72-76 行，容器环境设置 `CORS_ALLOW_ALL_ORIGINS=1` |

---

## 五、端到端诊断脚本

以下是一键诊断脚本，按顺序执行上述所有检查：

项目根目录已提供可直接运行的诊断脚本 [diagnose.sh](file:///Users/yurik/Desktop/trae_label_project/SOLO_DOG_10_2/solo_dog_10_32/gy-56/diagnose.sh)，所有检查项跑完后统一给出汇总。脚本已设置可执行权限，**直接运行即可，不要从文档手动复制**。

**使用方式**：
```bash
cd /Users/yurik/Desktop/trae_label_project/SOLO_DOG_10_2/solo_dog_10_32/gy-56
./diagnose.sh
```

**6 步检查内容**：

| 步骤 | 检查维度 | 具体内容 |
|------|----------|----------|
| 1/6 | 容器状态 | backend/frontend 是否 running、Docker 报告的健康状态 |
| 2/6 | 依赖安装 | 后端 4 个 Python 包是否都存在、前端 node_modules/vue 是否存在 |
| 3/6 | 迁移状态 | 4 个 app 的迁移是否全部 `[X]`，无 pending |
| 4/6 | 演示数据 | 5 类数据（景点/线路/停靠点/报名/通知）数量是否达标 |
| 5/6 | 健康检查 API | 调用 `/api/health/`，检查 HTTP 200 + status=ok，并输出 checks 详情 |
| 6/6 | 业务 API 抽查 | 调用 `/api/routes/` 和 `/api/attractions/`，检查返回条数是否达标 |

**输出示例**：
```
=========================================
  容器构建端到端诊断工具
=========================================

━━━ [1/6] 容器运行状态 ━━━
  ✅ backend 容器运行中
  ✅ frontend 容器运行中
  ✅ backend 健康检查: healthy
...
━━━ [6/6] 业务 API 抽查 ━━━
  ✅ 线路 API 返回 1 条数据
  ✅ 景点 API 返回 4 条数据

=========================================
  诊断结果汇总
=========================================
  ✅ 通过: 12
  ❌ 失败: 0
  ⚠️  警告: 0

  🎉 所有检查通过，系统运行正常！
```

**退出码**：
- `0`：全部通过 或 仅有警告
- `1`：存在失败项（方便 CI/脚本化判断）


---

## 六、快速修复清单

| 场景 | 一键修复命令 |
|------|--------------|
| 完全重建（清空数据） | `docker compose down -v && docker compose up --build` |
| 仅后端重建（保留数据） | `docker compose up -d --build backend` |
| 重新执行迁移 | `docker compose exec backend python manage.py migrate --noinput` |
| 重新写入演示数据 | `docker compose exec backend python manage.py seed_demo` |
| 查看实时日志 | `docker compose logs -f backend` |
| 进入后端容器调试 | `docker compose exec backend bash` |

---

## 七、关键文件索引

| 文件 | 作用 |
|------|------|
| [docker-compose.yml](file:///Users/yurik/Desktop/trae_label_project/SOLO_DOG_10_2/solo_dog_10_32/gy-56/docker-compose.yml) | 服务编排 + 健康检查 + 启动依赖 |
| [backend/Dockerfile](file:///Users/yurik/Desktop/trae_label_project/SOLO_DOG_10_2/solo_dog_10_32/gy-56/backend/Dockerfile) | 后端镜像构建 + 启动命令 |
| [backend/requirements.txt](file:///Users/yurik/Desktop/trae_label_project/SOLO_DOG_10_2/solo_dog_10_32/gy-56/backend/requirements.txt) | Python 依赖清单 |
| [backend/travel_planner/settings.py](file:///Users/yurik/Desktop/trae_label_project/SOLO_DOG_10_2/solo_dog_10_32/gy-56/backend/travel_planner/settings.py) | Django 配置（DB/CORS/时区） |
| [backend/travel_planner/urls.py](file:///Users/yurik/Desktop/trae_label_project/SOLO_DOG_10_2/solo_dog_10_32/gy-56/backend/travel_planner/urls.py) | URL 路由 + 健康检查端点 |
| [backend/apps/routes/management/commands/seed_demo.py](file:///Users/yurik/Desktop/trae_label_project/SOLO_DOG_10_2/solo_dog_10_32/gy-56/backend/apps/routes/management/commands/seed_demo.py) | 演示数据写入命令 |
| [frontend/Dockerfile](file:///Users/yurik/Desktop/trae_label_project/SOLO_DOG_10_2/solo_dog_10_32/gy-56/frontend/Dockerfile) | 前端镜像构建 |
| [frontend/package.json](file:///Users/yurik/Desktop/trae_label_project/SOLO_DOG_10_2/solo_dog_10_32/gy-56/frontend/package.json) | Node 依赖与脚本 |
| [diagnose.sh](file:///Users/yurik/Desktop/trae_label_project/SOLO_DOG_10_2/solo_dog_10_32/gy-56/diagnose.sh) | 端到端诊断脚本 |
