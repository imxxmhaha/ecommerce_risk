#!/bin/bash
set -euo pipefail

# 解析参数：-v 表示同时删除 mysql 数据卷（默认保留 mysql 数据）
REMOVE_MYSQL_VOLUME=false
for arg in "$@"; do
    case "$arg" in
        -v|--volumes) REMOVE_MYSQL_VOLUME=true ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="${SCRIPT_DIR}/docker-compose.yaml"

cd "${SCRIPT_DIR}"

echo "=========================================="
echo "  电商风控系统 - Docker 部署"
echo "=========================================="

if [ ! -f "${COMPOSE_FILE}" ]; then
  echo "未找到 docker-compose.yaml: ${COMPOSE_FILE}"
  exit 1
fi

echo ""
echo "==> [1/3] 检查 Docker Compose 配置..."
docker compose -f "${COMPOSE_FILE}" config >/dev/null
echo "    配置检查通过"

echo ""
echo "==> [2/3] 检查并清理已存在的服务（跳过 mysql）..."
if docker compose -f "${COMPOSE_FILE}" ps --all -q | grep -q .; then
  echo "    停止 backend 和 frontend 容器..."
  docker compose -f "${COMPOSE_FILE}" stop backend frontend 2>/dev/null || true
  docker compose -f "${COMPOSE_FILE}" rm -f backend frontend 2>/dev/null || true
else
  echo "    未检测到已存在的 Compose 服务"
fi

echo ""
echo "==> [3/3] 构建并启动 Docker 容器（排除 mysql）..."
docker compose -f "${COMPOSE_FILE}" up -d --build backend frontend

echo ""
echo "=========================================="
echo "  部署完成！"
echo "  前端: http://服务器IP:8080"
echo "  后端: http://服务器IP:9400"
echo "  数据库: 服务器IP:13307"
echo "=========================================="

echo ""
docker compose -f "${COMPOSE_FILE}" ps
