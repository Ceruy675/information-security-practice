from pathlib import Path

path = Path("app/auth.py")
code = path.read_text()

if "from app.audit.logger import log_event" not in code:
    code = "from app.audit.logger import log_event\n" + code

old = '''    if not user or not verify_password(
        form_data.password,
        user.hashed_password
    ):
        raise HTTPException('''

new = '''    if not user or not verify_password(
        form_data.password,
        user.hashed_password
    ):
        log_event(
            "login_failed", "failure",
            request.client.host if request.client else "unknown",
            username=email,
            http_method="POST",
            endpoint="/login",
            status_code=401,
        )
        raise HTTPException('''

if old in code:
    code = code.replace(old, new, 1)
elif '"login_failed"' not in code:
    raise SystemExit("Не знайдено блок перевірки пароля. Файл не змінено.")

old = '''    token = create_access_token('''

new = '''    log_event(
        "login_success", "success",
        request.client.host if request.client else "unknown",
        user_id=user.id,
        http_method="POST",
        endpoint="/login",
        status_code=200,
    )

    token = create_access_token('''

if old in code and '"login_success"' not in code:
    code = code.replace(old, new, 1)

path.write_text(code)
print("Логування авторизації додано")
