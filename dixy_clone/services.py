from __future__ import annotations

from pathlib import Path
from typing import Any

from dixy_clone.db import initialize_database, managed_connection


DEFAULT_USER_ID = 1


class GroceryService:
    def __init__(self, db_path: str | Path | None = None, user_id: int = DEFAULT_USER_ID) -> None:
        self.db_path = db_path
        self.user_id = user_id
        initialize_database(self.db_path)

    def list_categories(self) -> list[dict[str, Any]]:
        with managed_connection(self.db_path) as connection:
            rows = connection.execute(
                "SELECT id, name, icon FROM categories ORDER BY id"
            ).fetchall()
        return [dict(row) for row in rows]

    def list_promos(self) -> list[dict[str, Any]]:
        with managed_connection(self.db_path) as connection:
            rows = connection.execute(
                "SELECT id, title, description, accent_color, tag FROM promos ORDER BY id"
            ).fetchall()
        return [dict(row) for row in rows]

    def list_products(
        self,
        search: str = "",
        category_id: int | None = None,
        only_discounted: bool = False,
        favorites_only: bool = False,
    ) -> list[dict[str, Any]]:
        query = """
            SELECT
                p.*,
                c.name AS category_name,
                CASE WHEN f.product_id IS NULL THEN 0 ELSE 1 END AS is_favorite
            FROM products p
            JOIN categories c ON c.id = p.category_id
            LEFT JOIN favorites f
                ON f.product_id = p.id AND f.user_id = ?
            WHERE 1 = 1
        """
        params: list[Any] = [self.user_id]

        if search:
            query += " AND (LOWER(p.name) LIKE ? OR LOWER(p.subtitle) LIKE ?)"
            like_pattern = f"%{search.lower()}%"
            params.extend([like_pattern, like_pattern])
        if category_id:
            query += " AND p.category_id = ?"
            params.append(category_id)
        if only_discounted:
            query += " AND p.old_price IS NOT NULL AND p.old_price > p.price"
        if favorites_only:
            query += " AND f.product_id IS NOT NULL"
        query += " ORDER BY p.id"

        with managed_connection(self.db_path) as connection:
            rows = connection.execute(query, params).fetchall()
        return [self._enrich_product(dict(row)) for row in rows]

    def get_product(self, product_id: int) -> dict[str, Any]:
        with managed_connection(self.db_path) as connection:
            row = connection.execute(
                """
                SELECT
                    p.*,
                    c.name AS category_name,
                    CASE WHEN f.product_id IS NULL THEN 0 ELSE 1 END AS is_favorite
                FROM products p
                JOIN categories c ON c.id = p.category_id
                LEFT JOIN favorites f
                    ON f.product_id = p.id AND f.user_id = ?
                WHERE p.id = ?
                """,
                (self.user_id, product_id),
            ).fetchone()
        if row is None:
            raise ValueError(f"Product {product_id} not found")
        return self._enrich_product(dict(row))

    def list_featured_products(self, limit: int = 4) -> list[dict[str, Any]]:
        products = self.list_products(only_discounted=True)
        return products[:limit]

    def toggle_favorite(self, product_id: int) -> bool:
        with managed_connection(self.db_path) as connection:
            existing = connection.execute(
                "SELECT 1 FROM favorites WHERE user_id = ? AND product_id = ?",
                (self.user_id, product_id),
            ).fetchone()
            if existing:
                connection.execute(
                    "DELETE FROM favorites WHERE user_id = ? AND product_id = ?",
                    (self.user_id, product_id),
                )
                connection.commit()
                return False

            connection.execute(
                "INSERT INTO favorites (user_id, product_id) VALUES (?, ?)",
                (self.user_id, product_id),
            )
            connection.commit()
            return True

    def list_favorites(self) -> list[dict[str, Any]]:
        return self.list_products(favorites_only=True)

    def add_to_cart(self, product_id: int, quantity: int = 1) -> None:
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        with managed_connection(self.db_path) as connection:
            existing = connection.execute(
                "SELECT quantity FROM cart_items WHERE user_id = ? AND product_id = ?",
                (self.user_id, product_id),
            ).fetchone()
            if existing:
                connection.execute(
                    "UPDATE cart_items SET quantity = quantity + ? WHERE user_id = ? AND product_id = ?",
                    (quantity, self.user_id, product_id),
                )
            else:
                connection.execute(
                    "INSERT INTO cart_items (user_id, product_id, quantity) VALUES (?, ?, ?)",
                    (self.user_id, product_id, quantity),
                )
            connection.commit()

    def set_cart_quantity(self, product_id: int, quantity: int) -> None:
        with managed_connection(self.db_path) as connection:
            if quantity <= 0:
                connection.execute(
                    "DELETE FROM cart_items WHERE user_id = ? AND product_id = ?",
                    (self.user_id, product_id),
                )
            else:
                connection.execute(
                    """
                    INSERT INTO cart_items (user_id, product_id, quantity)
                    VALUES (?, ?, ?)
                    ON CONFLICT(user_id, product_id)
                    DO UPDATE SET quantity = excluded.quantity
                    """,
                    (self.user_id, product_id, quantity),
                )
            connection.commit()

    def list_cart_items(self) -> list[dict[str, Any]]:
        with managed_connection(self.db_path) as connection:
            rows = connection.execute(
                """
                SELECT
                    ci.product_id,
                    ci.quantity,
                    p.name,
                    p.subtitle,
                    p.unit,
                    p.price,
                    p.old_price,
                    p.accent_color,
                    p.image_emoji
                FROM cart_items ci
                JOIN products p ON p.id = ci.product_id
                WHERE ci.user_id = ?
                ORDER BY ci.rowid DESC
                """,
                (self.user_id,),
            ).fetchall()
        items = [dict(row) for row in rows]
        for item in items:
            item["line_total"] = round(item["price"] * item["quantity"], 2)
        return items

    def cart_summary(self) -> dict[str, Any]:
        items = self.list_cart_items()
        subtotal = round(sum(item["line_total"] for item in items), 2)
        discount = round(
            sum(
                ((item["old_price"] or item["price"]) - item["price"]) * item["quantity"]
                for item in items
            ),
            2,
        )
        delivery_fee = 0.0 if subtotal >= 1500 or subtotal == 0 else 149.0
        total = round(subtotal + delivery_fee, 2)
        return {
            "items_count": sum(item["quantity"] for item in items),
            "subtotal": subtotal,
            "discount": discount,
            "delivery_fee": delivery_fee,
            "total": total,
        }

    def create_order(self, address: str, comment: str, payment_method: str) -> int:
        items = self.list_cart_items()
        if not items:
            raise ValueError("Cart is empty")

        summary = self.cart_summary()
        with managed_connection(self.db_path) as connection:
            cursor = connection.execute(
                """
                INSERT INTO orders (user_id, address, comment, payment_method, total)
                VALUES (?, ?, ?, ?, ?)
                """,
                (self.user_id, address, comment, payment_method, summary["total"]),
            )
            order_id = int(cursor.lastrowid)
            connection.executemany(
                """
                INSERT INTO order_items (order_id, product_id, quantity, price)
                VALUES (?, ?, ?, ?)
                """,
                [
                    (order_id, item["product_id"], item["quantity"], item["price"])
                    for item in items
                ],
            )
            connection.execute(
                "DELETE FROM cart_items WHERE user_id = ?",
                (self.user_id,),
            )
            connection.commit()
        return order_id

    def list_orders(self) -> list[dict[str, Any]]:
        with managed_connection(self.db_path) as connection:
            rows = connection.execute(
                """
                SELECT
                    o.id,
                    o.address,
                    o.comment,
                    o.payment_method,
                    o.total,
                    o.created_at,
                    COUNT(oi.product_id) AS positions
                FROM orders o
                LEFT JOIN order_items oi ON oi.order_id = o.id
                WHERE o.user_id = ?
                GROUP BY o.id
                ORDER BY o.id DESC
                """,
                (self.user_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_profile(self) -> dict[str, Any]:
        with managed_connection(self.db_path) as connection:
            user = connection.execute(
                "SELECT id, name, phone, address, bonus_balance FROM users WHERE id = ?",
                (self.user_id,),
            ).fetchone()
        if user is None:
            raise ValueError(f"User {self.user_id} not found")
        profile = dict(user)
        profile["favorites_count"] = len(self.list_favorites())
        profile["orders_count"] = len(self.list_orders())
        profile["cart_total"] = self.cart_summary()["total"]
        return profile

    @staticmethod
    def _enrich_product(product: dict[str, Any]) -> dict[str, Any]:
        old_price = product["old_price"]
        discount = 0
        if old_price and old_price > product["price"]:
            discount = int(round((1 - product["price"] / old_price) * 100))
        product["discount_percent"] = discount
        product["badges"] = [badge.strip() for badge in product["badges"].split(",") if badge.strip()]
        product["is_favorite"] = bool(product["is_favorite"])
        return product
