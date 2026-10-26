import os

import psycopg
from dotenv import load_dotenv

# Lê o arquivo .env e deixa a NOVA_DATABASE_URL disponível.
load_dotenv()

# Abre a conexão com o banco. O "with" fecha tudo sozinho no final.
with psycopg.connect(os.environ["NOVA_DATABASE_URL"]) as conn:
    # Pergunta a versão do PostgreSQL e quais tabelas existem.
    version = conn.execute("SELECT version()").fetchone()[0]
    tables = conn.execute(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = 'public' ORDER BY table_name"
    ).fetchall()

print(version)
print("Tabelas:", [name for (name,) in tables])