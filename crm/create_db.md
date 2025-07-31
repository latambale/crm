Create Clean DB:

rm crm.db

# Or manually delete via File Explorer
Delete Alembic migration files (keep env.py, script.py.mako, etc., but delete versions/*):

rm alembic/versions/*
Recreate migration:

alembic revision --autogenerate -m "Initial schema"
alembic upgrade head