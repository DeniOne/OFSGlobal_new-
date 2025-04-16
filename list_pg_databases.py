import asyncio
import asyncpg

async def list_databases():
    conn = None
    try:
        # Подключаемся к служебной базе postgres
        conn = await asyncpg.connect(
            user="postgres",
            password="postgres",
            database="postgres",
            host="localhost",
            port=5432,
            timeout=10.0
        )
        
        # Запрашиваем список баз данных
        databases = await conn.fetch("""
            SELECT datname FROM pg_database 
            WHERE datistemplate = false
            ORDER BY datname;
        """)
        
        print("Доступные базы данных:")
        for db in databases:
            print(f"- {db['datname']}")
            
    except Exception as e:
        print(f"Ошибка при запросе баз данных: {str(e)}")
    finally:
        if conn:
            await conn.close()
            print("Соединение закрыто")

# Запускаем асинхронную функцию
asyncio.run(list_databases()) 