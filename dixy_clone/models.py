from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Category:
    id: int
    name: str
    icon: str


@dataclass(frozen=True)
class Product:
    id: int
    category_id: int
    name: str
    subtitle: str
    unit: str
    price: float
    old_price: float | None
    rating: float
    badges: str
    accent_color: str
    image_emoji: str
    stock: int

    @property
    def discount_percent(self) -> int:
        if not self.old_price or self.old_price <= self.price:
            return 0
        return int(round((1 - self.price / self.old_price) * 100))
