from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path


APP_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = APP_DIR / "data"
DEFAULT_DB_PATH = DATA_DIR / "dixy_clone.db"


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    address TEXT NOT NULL,
    bonus_balance INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    icon TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    name TEXT NOT NULL,
    subtitle TEXT NOT NULL,
    unit TEXT NOT NULL,
    price REAL NOT NULL,
    old_price REAL,
    rating REAL NOT NULL,
    badges TEXT NOT NULL DEFAULT '',
    accent_color TEXT NOT NULL,
    image_emoji TEXT NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS promos (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    accent_color TEXT NOT NULL,
    tag TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS favorites (
    user_id INTEGER NOT NULL REFERENCES users(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    PRIMARY KEY (user_id, product_id)
);

CREATE TABLE IF NOT EXISTS cart_items (
    user_id INTEGER NOT NULL REFERENCES users(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    PRIMARY KEY (user_id, product_id)
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    address TEXT NOT NULL,
    comment TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    total REAL NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_items (
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    price REAL NOT NULL,
    PRIMARY KEY (order_id, product_id)
);
"""


SEED_CATEGORIES = [
    (1, "Скидки", "🔥"),
    (2, "Овощи", "🥬"),
    (3, "Молоко", "🥛"),
    (4, "Готовое", "🍱"),
    (5, "Сладкое", "🍫"),
    (6, "Напитки", "🥤"),
]

SEED_PRODUCTS = [
    (1, 1, "Круассан сливочный", "Свежая выпечка к завтраку", "1 шт", 79.9, 119.9, 4.8, "Хит,Утро", "#ffd166", "🥐", 30),
    (2, 2, "Авокадо Hass", "Спелый, мягкий, для тостов", "1 шт", 139.9, None, 4.7, "Новинка", "#80ed99", "🥑", 18),
    (3, 3, "Молоко фермерское 3.2%", "Без сухого молока", "930 мл", 99.9, 129.9, 4.9, "Кешбэк 5%", "#caf0f8", "🥛", 42),
    (4, 4, "Боул с курицей терияки", "Готовый обед за 2 минуты", "280 г", 219.9, 259.9, 4.6, "Обед", "#f4a261", "🍱", 20),
    (5, 5, "Шоколад тёмный 70%", "Без лишнего сахара", "90 г", 114.9, 149.9, 4.8, "Скидка дня", "#cdb4db", "🍫", 24),
    (6, 6, "Лимонад тархун", "Освежающий вкус детства", "500 мл", 69.9, 89.9, 4.5, "2=3", "#90e0ef", "🥤", 50),
    (7, 2, "Томаты черри", "Сладкие, для салатов", "250 г", 159.9, None, 4.7, "Фермеры", "#ff6b6b", "🍅", 26),
    (8, 3, "Йогурт греческий", "Белок и натуральный состав", "140 г", 58.9, None, 4.9, "Фитнес", "#a8dadc", "🥣", 36),
    (9, 4, "Сэндвич с индейкой", "Для перекуса в дороге", "190 г", 174.9, 209.9, 4.4, "В дорогу", "#f7b267", "🥪", 16),
    (10, 5, "Миндаль в карамели", "Хрустящий снек", "120 г", 189.9, 229.9, 4.8, "Премиум", "#dda15e", "🌰", 14),
    (11, 6, "Сок апельсиновый", "100% juice", "1 л", 149.9, 199.9, 4.7, "Витамины", "#ffb703", "🍊", 34),
    (12, 1, "Кофе капучино", "Готовый напиток", "250 мл", 109.9, 139.9, 4.6, "Бодрое утро", "☕", 28),
]

SEED_PROMOS = [
    (1, "Собери корзину недели", "До -35% на любимые продукты каждый день", "#ff385c", "Горячее"),
    (2, "Экспресс-доставка", "Привезем за 30 минут в пределах района", "#06d6a0", "30 мин"),
    (3, "Карта лояльности", "Копите бонусы и тратьте их на новые заказы", "#118ab2", "Бонусы"),
]


def get_connection(db_path: str | Path | None = None) -> sqlite3.Connection:
    path = Path(db_path) if db_path else DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


@contextmanager
def managed_connection(db_path: str | Path | None = None) -> sqlite3.Connection:
    connection = get_connection(db_path)
    try:
        yield connection
    finally:
        connection.close()


def initialize_database(db_path: str | Path | None = None) -> None:
    with managed_connection(db_path) as connection:
        connection.executescript(SCHEMA)
        _seed_if_needed(connection)
        connection.commit()


def _seed_if_needed(connection: sqlite3.Connection) -> None:
    user_exists = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if user_exists:
        return

    connection.execute(
        """
        INSERT INTO users (id, name, phone, address, bonus_balance)
        VALUES (1, 'Анна Смирнова', '+7 999 123-45-67', 'Москва, ул. Лесная, 18', 420)
        """
    )
    connection.executemany(
        "INSERT INTO categories (id, name, icon) VALUES (?, ?, ?)",
        SEED_CATEGORIES,
    )
    connection.executemany(
        """
        INSERT INTO products (
            id, category_id, name, subtitle, unit, price, old_price,
            rating, badges, accent_color, image_emoji, stock
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        SEED_PRODUCTS,
    )
    connection.executemany(
        "INSERT INTO promos (id, title, description, accent_color, tag) VALUES (?, ?, ?, ?, ?)",
        SEED_PROMOS,
    )
