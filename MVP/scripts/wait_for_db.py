import os
import sys
import time
from urllib.parse import urlparse

from sqlalchemy import create_engine, text


def main():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL não definido; pulando espera do banco.")
        return

    parsed = urlparse(database_url)
    if parsed.scheme.startswith("sqlite"):
        return

    timeout_seconds = int(os.getenv("DB_WAIT_TIMEOUT", "90"))
    start = time.time()
    last_error = None

    while time.time() - start < timeout_seconds:
        try:
            engine = create_engine(database_url, pool_pre_ping=True)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("Banco disponível.")
            return
        except Exception as exc:
            last_error = exc
            print("Aguardando banco de dados...")
            time.sleep(3)

    print(f"Banco indisponível após {timeout_seconds}s: {last_error}", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
