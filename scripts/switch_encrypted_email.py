from pathlib import Path

models = Path("app/models.py")
content = models.read_text()

if "from app.crypto.encryption import" not in content:
    content = (
        "from app.crypto.encryption import encrypt_field, decrypt_field, blind_index\n"
        + content
    )

old = 'email = Column(String(255), unique=True, index=True, nullable=False)'

new = '''_encrypted_email = Column("encrypted_email", String(500))
    email_index = Column(String(64), unique=True, index=True)

    @property
    def email(self):
        return decrypt_field(self._encrypted_email)

    @email.setter
    def email(self, value):
        self._encrypted_email = encrypt_field(value)
        self.email_index = blind_index(value) if value else None'''

if old in content:
    content = content.replace(old, new, 1)
elif '_encrypted_email = Column(' not in content:
    raise SystemExit("Не знайдено колонку email у моделі User")

models.write_text(content)

auth = Path("app/auth.py")
content = auth.read_text()

if "from app.crypto.encryption import blind_index" not in content:
    content = (
        "from app.crypto.encryption import blind_index\n"
        + content
    )

content = content.replace(
    "User.email == email",
    "User.email_index == blind_index(email)"
)

auth.write_text(content)

print("Модель User оновлено")
print("Авторизацію оновлено")
