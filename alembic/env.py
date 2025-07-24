import os
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.user import User  # Required so Alembic detects the table
from database import Base     # Base used in your models

target_metadata = Base.metadata

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# ✅ Load .env file before anything else
load_dotenv()

# ✅ Alembic Config object
config = context.config

# ✅ Inject DATABASE_URL from .env file
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise Exception("DATABASE_URL not found in .env")

config.set_main_option("sqlalchemy.url", database_url)

# ✅ Logging setup
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# ✅ Offline migration config
def run_migrations_offline():
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

# ✅ Online migration config
def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

# ✅ Run either offline or online migration
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
