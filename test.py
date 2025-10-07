# check_db_enum.py
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# !!! مهم: این را با رشته اتصال واقعی خود جایگزین کنید !!!
DATABASE_URL = "postgresql+asyncpg://Pharma_user:Mehr3223@localhost:5432/Pharma_DB"


async def check_enums():
    """Connects to the DB and queries for user-defined enum types."""
    engine = create_async_engine(DATABASE_URL)

    query = text("""
        SELECT
            t.typname AS enum_name,
            e.enumlabel AS enum_value
        FROM
            pg_type t
        JOIN
            pg_enum e ON t.oid = e.enumtypid
        JOIN
            pg_catalog.pg_namespace n ON n.oid = t.typnamespace
        WHERE
            n.nspname = 'public' -- Adjust if you use a different schema
        ORDER BY
            t.typname, e.enumsortorder;
    """)

    async with engine.connect() as connection:
        result = await connection.execute(query)
        rows = result.fetchall()

        if not rows:
            print("No custom enum types found in the 'public' schema.")
            return

        print("=" * 40)
        print("Custom Enum Types in Database:")
        print("=" * 40)
        current_enum = None
        for row in rows:
            enum_name, enum_value = row
            if enum_name != current_enum:
                current_enum = enum_name
                print(f"\n--- ENUM: {current_enum} ---")
            print(f"  - '{enum_value}'")
        print("\n" + "=" * 40)

    await engine.dispose()


if __name__ == "__main__":
    print("Connecting to the database to inspect enums...")
    asyncio.run(check_enums())
    print("Inspection complete.")
