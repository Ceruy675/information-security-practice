#!/bin/bash

set -u

REPORT="project_check_report.txt"

{
echo "======================================"
echo " ЕЛЕКТРОННИЙ ДЕКАНАТ"
echo " ЗВІТ ПЕРЕВІРКИ ПРОЄКТУ"
echo "======================================"
date
echo

echo "1. ПЕРЕВІРКА ФАЙЛІВ"
for file in app/main.py app/models.py app/database.py app/security.py app/auth.py app/roles.py app/courses.py app/enrollments.py app/limiter.py app/sanitizer.py Dockerfile docker-compose.yml requirements.txt; do
    if [ -f "$file" ]; then
        echo "[OK] $file"
    else
        echo "[MISSING] $file"
    fi
done

echo
echo "2. ПЕРЕВІРКА DOCKER"
docker compose ps

echo
echo "3. ПЕРЕВІРКА API"
curl -s -o /dev/null -w "HTTP: %{http_code}\n" http://localhost:8000/

echo
echo "4. ПЕРЕВІРКА PYTHON"
docker compose exec -T api python -m compileall -q app
if [ $? -eq 0 ]; then
    echo "[OK] Python compilation"
else
    echo "[ERROR] Python compilation"
fi

echo
echo "5. ПЕРЕВІРКА БАЗИ ДАНИХ"
docker compose exec -T api python -c "from sqlalchemy import inspect; from app.database import engine; print(inspect(engine).get_table_names())"

echo
echo "6. ПЕРЕВІРКА МАРШРУТІВ"
docker compose exec -T api python -c "from app.main import app; [print(sorted(r.methods), r.path) for r in app.routes if hasattr(r, 'methods')]"

echo
echo "7. ПЕРЕВІРКА GIT"
git log --oneline -5
git status --short

echo
echo "8. АВТОМАТИЧНІ ТЕСТИ"
docker compose exec -T api python -m pytest tests/ -q

echo
echo "======================================"
echo " ПЕРЕВІРКУ ЗАВЕРШЕНО"
echo "======================================"
} 2>&1 | tee "$REPORT"
