import os

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test")
os.environ.setdefault("SECRET_KEY", "test-secret-key-32-characters-long-xxxx")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379")
