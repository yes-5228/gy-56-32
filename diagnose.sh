#!/bin/bash
set -euo pipefail

PASS=0
FAIL=0
WARN=0

ok()   { echo "  ✅ $1"; ((PASS++)); }
fail() { echo "  ❌ $1"; ((FAIL++)); }
warn() { echo "  ⚠️  $1"; ((WARN++)); }

echo "========================================="
echo "  容器构建端到端诊断工具"
echo "========================================="

echo -e "\n━━━ [1/6] 容器运行状态 ━━━"
RUNNING_BACKEND=$(docker compose ps -q backend 2>/dev/null | xargs -r docker inspect -f '{{.State.Running}}' 2>/dev/null || echo "false")
RUNNING_FRONTEND=$(docker compose ps -q frontend 2>/dev/null | xargs -r docker inspect -f '{{.State.Running}}' 2>/dev/null || echo "false")

if [ "$RUNNING_BACKEND" = "true" ]; then
    ok "backend 容器运行中"
else
    fail "backend 容器未运行"
fi

if [ "$RUNNING_FRONTEND" = "true" ]; then
    ok "frontend 容器运行中"
else
    fail "frontend 容器未运行"
fi

HEALTH_BACKEND=$(docker compose ps --format json 2>/dev/null | python3 -c "
import sys, json
for line in sys.stdin:
    obj = json.loads(line)
    if 'backend' in obj.get('Service',''):
        print(obj.get('Health','unknown'))
        break
" 2>/dev/null || echo "unknown")

if [ "$HEALTH_BACKEND" = "healthy" ]; then
    ok "backend 健康检查: healthy"
elif [ "$RUNNING_BACKEND" = "true" ]; then
    warn "backend 健康检查: $HEALTH_BACKEND (可能仍在启动中)"
fi

echo -e "\n━━━ [2/6] 依赖安装状态 ━━━"
if [ "$RUNNING_BACKEND" = "true" ]; then
    DEPS=$(docker compose exec -T backend pip list 2>/dev/null | grep -cE "Django|djangorestframework|django-cors-headers|gunicorn" || echo "0")
    if [ "$DEPS" -ge 4 ]; then
        ok "后端 Python 依赖安装完整 ($DEPS/4)"
    else
        fail "后端 Python 依赖不完整 ($DEPS/4)"
    fi
else
    warn "后端容器未运行，跳过依赖检查"
fi

if [ "$RUNNING_FRONTEND" = "true" ]; then
    if docker compose exec -T frontend test -d node_modules/vue 2>/dev/null; then
        ok "前端 Vue 依赖已安装"
    else
        fail "前端 Vue 依赖缺失"
    fi
else
    warn "前端容器未运行，跳过依赖检查"
fi

echo -e "\n━━━ [3/6] 数据库迁移状态 ━━━"
if [ "$RUNNING_BACKEND" = "true" ]; then
    MIG_OUTPUT=$(docker compose exec -T backend python manage.py showmigrations 2>/dev/null || echo "")
    PENDING=$(echo "$MIG_OUTPUT" | grep -c "\[ \]" || true)
    APPLIED=$(echo "$MIG_OUTPUT" | grep -c "\[X\]" || true)

    if [ "$PENDING" -eq 0 ] && [ "$APPLIED" -gt 0 ]; then
        ok "所有迁移已应用 ($APPLIED 个)"
    elif [ "$PENDING" -gt 0 ]; then
        fail "存在 $PENDING 个未应用的迁移"
        echo "$MIG_OUTPUT" | grep "\[ \]" | sed 's/^/      /'
    else
        fail "无法获取迁移状态"
    fi
else
    warn "后端容器未运行，跳过迁移检查"
fi

echo -e "\n━━━ [4/6] 演示数据检查 ━━━"
if [ "$RUNNING_BACKEND" = "true" ]; then
    DATA_OUTPUT=$(docker compose exec -T backend python -c "
import django; django.setup()
from apps.attractions.models import Attraction
from apps.routes.models import TravelRoute, RouteStop
from apps.bookings.models import Booking
from apps.notifications.models import TravelNotice
counts = {
    'attractions': Attraction.objects.count(),
    'routes': TravelRoute.objects.count(),
    'stops': RouteStop.objects.count(),
    'bookings': Booking.objects.count(),
    'notices': TravelNotice.objects.count(),
}
for k, v in counts.items():
    print(f'{k}={v}')
" 2>/dev/null || echo "")

    if [ -n "$DATA_OUTPUT" ]; then
        ATTRACTIONS=$(echo "$DATA_OUTPUT" | grep "attractions=" | cut -d= -f2)
        ROUTES=$(echo "$DATA_OUTPUT" | grep "routes=" | cut -d= -f2)
        STOPS=$(echo "$DATA_OUTPUT" | grep "stops=" | cut -d= -f2)
        BOOKINGS=$(echo "$DATA_OUTPUT" | grep "bookings=" | cut -d= -f2)
        NOTICES=$(echo "$DATA_OUTPUT" | grep "notices=" | cut -d= -f2)

        [ "${ATTRACTIONS:-0}" -ge 4 ]  && ok "景点数据: $ATTRACTIONS (期望 >= 4)"  || warn "景点数据: ${ATTRACTIONS:-0} (期望 >= 4)"
        [ "${ROUTES:-0}" -ge 1 ]       && ok "线路数据: $ROUTES (期望 >= 1)"       || warn "线路数据: ${ROUTES:-0} (期望 >= 1)"
        [ "${STOPS:-0}" -ge 3 ]        && ok "停靠点: $STOPS (期望 >= 3)"          || warn "停靠点: ${STOPS:-0} (期望 >= 3)"
        [ "${BOOKINGS:-0}" -ge 2 ]     && ok "报名记录: $BOOKINGS (期望 >= 2)"     || warn "报名记录: ${BOOKINGS:-0} (期望 >= 2)"
        [ "${NOTICES:-0}" -ge 2 ]      && ok "出行通知: $NOTICES (期望 >= 2)"      || warn "出行通知: ${NOTICES:-0} (期望 >= 2)"
    else
        fail "无法获取演示数据"
    fi
else
    warn "后端容器未运行，跳过数据检查"
fi

echo -e "\n━━━ [5/6] 健康检查 API ━━━"
HEALTH_BODY=$(curl -sf http://localhost:8000/api/health/ 2>/dev/null || echo "")
if [ -n "$HEALTH_BODY" ]; then
    HEALTH_STATUS=$(echo "$HEALTH_BODY" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','unknown'))" 2>/dev/null || echo "parse_error")
    if [ "$HEALTH_STATUS" = "ok" ]; then
        ok "后端健康检查: $HEALTH_STATUS"
        echo "      详细信息: $HEALTH_BODY" | python3 -m json.tool 2>/dev/null | sed 's/^/      /' || echo "      $HEALTH_BODY"
    else
        fail "后端健康检查: $HEALTH_STATUS"
        echo "$HEALTH_BODY" | python3 -m json.tool 2>/dev/null | sed 's/^/      /' || echo "      $HEALTH_BODY"
    fi
else
    fail "后端健康检查端点不可达 (http://localhost:8000/api/health/)"
fi

FRONT_CODE=$(curl -sf -o /dev/null -w "%{http_code}" http://localhost:5173/ 2>/dev/null || echo "000")
if [ "$FRONT_CODE" = "200" ]; then
    ok "前端页面可访问 (HTTP $FRONT_CODE)"
elif [ "$FRONT_CODE" = "000" ]; then
    fail "前端页面不可达"
else
    warn "前端页面返回 HTTP $FRONT_CODE"
fi

echo -e "\n━━━ [6/6] 业务 API 抽查 ━━━"
ROUTE_RESP=$(curl -sf http://localhost:8000/api/routes/ 2>/dev/null || echo "")
if [ -n "$ROUTE_RESP" ]; then
    ROUTE_COUNT=$(echo "$ROUTE_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d) if isinstance(d,list) else 0)" 2>/dev/null || echo "?")
    if [ "$ROUTE_COUNT" != "?" ] && [ "$ROUTE_COUNT" -ge 1 ]; then
        ok "线路 API 返回 $ROUTE_COUNT 条数据"
    else
        warn "线路 API 返回 $ROUTE_COUNT 条 (期望 >= 1)"
    fi
else
    fail "线路 API 不可达 (http://localhost:8000/api/routes/)"
fi

ATTRACT_RESP=$(curl -sf http://localhost:8000/api/attractions/ 2>/dev/null || echo "")
if [ -n "$ATTRACT_RESP" ]; then
    ATTRACT_COUNT=$(echo "$ATTRACT_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d) if isinstance(d,list) else 0)" 2>/dev/null || echo "?")
    if [ "$ATTRACT_COUNT" != "?" ] && [ "$ATTRACT_COUNT" -ge 4 ]; then
        ok "景点 API 返回 $ATTRACT_COUNT 条数据"
    else
        warn "景点 API 返回 $ATTRACT_COUNT 条 (期望 >= 4)"
    fi
else
    fail "景点 API 不可达 (http://localhost:8000/api/attractions/)"
fi

echo ""
echo "========================================="
echo "  诊断结果汇总"
echo "========================================="
echo "  ✅ 通过: $PASS"
echo "  ❌ 失败: $FAIL"
echo "  ⚠️  警告: $WARN"
echo ""

if [ "$FAIL" -gt 0 ]; then
    echo "  🔧 快速修复命令:"
    echo "     完全重建:  docker compose down -v && docker compose up --build"
    echo "     仅重启:    docker compose restart"
    echo "     查看日志:  docker compose logs -f backend"
    echo ""
    exit 1
elif [ "$WARN" -gt 0 ]; then
    echo "  ℹ️  有警告项，部分功能可能未就绪，请检查上方输出。"
    echo ""
    exit 0
else
    echo "  🎉 所有检查通过，系统运行正常！"
    echo ""
    exit 0
fi
