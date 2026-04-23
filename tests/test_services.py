from __future__ import annotations

import shutil
import unittest
from pathlib import Path
from uuid import uuid4

from dixy_clone.services import GroceryService


class GroceryServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.workspace_tmp_root = Path(__file__).resolve().parent.parent / ".test_tmp"
        self.workspace_tmp_root.mkdir(parents=True, exist_ok=True)
        self.db_path = self.workspace_tmp_root / f"{uuid4().hex}.sqlite3"
        self.service = GroceryService(self.db_path)

    def tearDown(self) -> None:
        if self.db_path.exists():
            self.db_path.unlink()
        if self.workspace_tmp_root.exists() and not any(self.workspace_tmp_root.iterdir()):
            shutil.rmtree(self.workspace_tmp_root, ignore_errors=True)

    def test_seeded_content_exists(self) -> None:
        categories = self.service.list_categories()
        products = self.service.list_products()
        promos = self.service.list_promos()

        self.assertGreaterEqual(len(categories), 6)
        self.assertGreaterEqual(len(products), 10)
        self.assertGreaterEqual(len(promos), 3)

    def test_toggle_favorite_adds_and_removes_product(self) -> None:
        state_after_add = self.service.toggle_favorite(1)
        favorites_after_add = self.service.list_favorites()
        state_after_remove = self.service.toggle_favorite(1)
        favorites_after_remove = self.service.list_favorites()

        self.assertTrue(state_after_add)
        self.assertEqual(len(favorites_after_add), 1)
        self.assertFalse(state_after_remove)
        self.assertEqual(len(favorites_after_remove), 0)

    def test_cart_summary_and_order_creation(self) -> None:
        self.service.add_to_cart(1, quantity=2)
        self.service.add_to_cart(3, quantity=1)

        summary = self.service.cart_summary()
        order_id = self.service.create_order(
            address="Test street 1",
            comment="Call in 5 minutes",
            payment_method="Card",
        )
        orders = self.service.list_orders()
        cart_items = self.service.list_cart_items()

        self.assertGreater(summary["total"], 0)
        self.assertEqual(order_id, orders[0]["id"])
        self.assertEqual(cart_items, [])

    def test_search_and_discount_filter(self) -> None:
        results = self.service.list_products(search="Hass")
        discounted = self.service.list_products(only_discounted=True)

        self.assertEqual(len(results), 1)
        self.assertTrue(all(item["discount_percent"] > 0 for item in discounted))


if __name__ == "__main__":
    unittest.main()
