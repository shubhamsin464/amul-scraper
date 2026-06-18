import os
import aiosqlite
import logging
from datetime import datetime
from .config import settings

logger = logging.getLogger(__name__)

from contextlib import asynccontextmanager

@asynccontextmanager
async def get_db():
    # Ensure data directory exists
    os.makedirs(os.path.dirname(settings.database_path), exist_ok=True)
    async with aiosqlite.connect(settings.database_path) as db:
        db.row_factory = aiosqlite.Row
        yield db

async def init_db():
    async with get_db() as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS pincodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pincode TEXT UNIQUE NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS state (
                product_id INTEGER,
                pincode_id INTEGER,
                is_available BOOLEAN,
                last_checked DATETIME,
                PRIMARY KEY (product_id, pincode_id),
                FOREIGN KEY(product_id) REFERENCES products(id),
                FOREIGN KEY(pincode_id) REFERENCES pincodes(id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS availability_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                pincode_id INTEGER,
                is_available BOOLEAN,
                timestamp DATETIME,
                FOREIGN KEY(product_id) REFERENCES products(id),
                FOREIGN KEY(pincode_id) REFERENCES pincodes(id)
            )
        """)
        await db.commit()
        logger.info("Database initialized.")

# -- Product CRUD --
async def add_product(url: str, name: str):
    async with get_db() as db:
        await db.execute("INSERT OR IGNORE INTO products (url, name) VALUES (?, ?)", (url, name))
        await db.commit()

async def get_products():
    async with get_db() as db:
        async with db.execute("SELECT id, url, name FROM products") as cursor:
            return await cursor.fetchall()

async def remove_product(product_id: int):
    async with get_db() as db:
        await db.execute("DELETE FROM state WHERE product_id = ?", (product_id,))
        await db.execute("DELETE FROM availability_log WHERE product_id = ?", (product_id,))
        await db.execute("DELETE FROM products WHERE id = ?", (product_id,))
        await db.commit()

# -- Pincode CRUD --
async def add_pincode(pincode: str):
    async with get_db() as db:
        await db.execute("INSERT OR IGNORE INTO pincodes (pincode) VALUES (?)", (pincode,))
        await db.commit()

async def remove_pincode(pincode: str):
    async with get_db() as db:
        cursor = await db.execute("SELECT id FROM pincodes WHERE pincode = ?", (pincode,))
        row = await cursor.fetchone()
        if row:
            pincode_id = row["id"]
            await db.execute("DELETE FROM state WHERE pincode_id = ?", (pincode_id,))
            await db.execute("DELETE FROM availability_log WHERE pincode_id = ?", (pincode_id,))
            await db.execute("DELETE FROM pincodes WHERE id = ?", (pincode_id,))
            await db.commit()

async def get_pincodes():
    async with get_db() as db:
        async with db.execute("SELECT id, pincode FROM pincodes") as cursor:
            return await cursor.fetchall()

# -- State & Logging --
async def update_state(product_id: int, pincode_id: int, is_available: bool) -> bool:
    """
    Updates the current state and returns True if the availability status *changed* from False to True.
    """
    now = datetime.now().isoformat()
    status_changed_to_available = False
    
    async with get_db() as db:
        # Check current state
        cursor = await db.execute(
            "SELECT is_available FROM state WHERE product_id = ? AND pincode_id = ?", 
            (product_id, pincode_id)
        )
        row = await cursor.fetchone()
        
        if row is None:
            # First time checking
            await db.execute(
                "INSERT INTO state (product_id, pincode_id, is_available, last_checked) VALUES (?, ?, ?, ?)",
                (product_id, pincode_id, is_available, now)
            )
            if is_available:
                status_changed_to_available = True
        else:
            prev_available = bool(row["is_available"])
            if not prev_available and is_available:
                status_changed_to_available = True
                
            await db.execute(
                "UPDATE state SET is_available = ?, last_checked = ? WHERE product_id = ? AND pincode_id = ?",
                (is_available, now, product_id, pincode_id)
            )
        
        # Always log the check to history
        await db.execute(
            "INSERT INTO availability_log (product_id, pincode_id, is_available, timestamp) VALUES (?, ?, ?, ?)",
            (product_id, pincode_id, is_available, now)
        )
        await db.commit()
        
    return status_changed_to_available

async def get_recent_logs(limit: int = 50):
    query = """
        SELECT l.id, p.name as product_name, p.url, c.pincode, l.is_available, l.timestamp 
        FROM availability_log l
        JOIN products p ON l.product_id = p.id
        JOIN pincodes c ON l.pincode_id = c.id
        ORDER BY l.timestamp DESC LIMIT ?
    """
    async with get_db() as db:
        async with db.execute(query, (limit,)) as cursor:
            return await cursor.fetchall()
