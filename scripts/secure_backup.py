import sqlite3
import tempfile
from pathlib import Path
from datetime import datetime, timezone

from app.crypto.encryption import get_fernet

DB = Path("/app_code/data/dean_office.db")
BACKUPS = DB.parent / "backups"


def main():
    BACKUPS.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        snapshot = Path(tmp) / "snapshot.db"

        with sqlite3.connect(DB) as source:
            with sqlite3.connect(snapshot) as target:
                source.backup(target)

        with sqlite3.connect(snapshot) as check:
            assert check.execute(
                "PRAGMA integrity_check"
            ).fetchone()[0] == "ok"

        plaintext = snapshot.read_bytes()

        filename = "dean_" + datetime.now(
            timezone.utc
        ).strftime("%Y%m%d_%H%M%S") + ".db.enc"

        output = BACKUPS / filename
        output.write_bytes(get_fernet().encrypt(plaintext))
        output.chmod(0o600)

        restored = get_fernet().decrypt(output.read_bytes())
        restore_path = Path(tmp) / "restored.db"
        restore_path.write_bytes(restored)

        with sqlite3.connect(restore_path) as check:
            integrity = check.execute(
                "PRAGMA integrity_check"
            ).fetchone()[0]
            users = check.execute(
                "SELECT COUNT(*) FROM users"
            ).fetchone()[0]

        assert integrity == "ok"

        print("Зашифрований бекап:", filename)
        print("Цілісність:", integrity)
        print("Користувачів:", users)
        print("Відновлення: OK")
        print("STATUS: OK")


if __name__ == "__main__":
    main()
