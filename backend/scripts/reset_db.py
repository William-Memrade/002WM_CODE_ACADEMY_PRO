import asyncio
import sys
import os
import importlib
import pkgutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.db.session import engine
from app.models.base import Base

import app.models

for loader, module_name, is_pkg in pkgutil.walk_packages(app.models.__path__, app.models.__name__ + '.'):
    importlib.import_module(module_name)

async def reset_db():
    async with engine.begin() as conn:
        print('Executing CASCADE schema drop...')
        await conn.execute(text('DROP SCHEMA public CASCADE'))
        await conn.execute(text('CREATE SCHEMA public'))
        await conn.execute(text('GRANT ALL ON SCHEMA public TO postgres'))
        await conn.execute(text('GRANT ALL ON SCHEMA public TO public'))
        print('Creating all tables...')
        await conn.run_sync(Base.metadata.create_all)
    print('Database reset complete.')
    
if __name__ == '__main__':
    asyncio.run(reset_db())
