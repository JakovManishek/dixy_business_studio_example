from __future__ import annotations

from pathlib import Path

import streamlit as st

from dixy_clone.db import DEFAULT_DB_PATH
from dixy_clone.services import GroceryService
from dixy_clone.ui import inject_styles, render_badges, section_title


PAGES = [
    ("home", "Главная", "🏠"),
    ("catalog", "Каталог", "🛒"),
    ("favorites", "Избранное", "❤️"),
    ("cart", "Корзина", "🧾"),
    ("profile", "Профиль", "👤"),
]


def get_service() -> GroceryService:
    return GroceryService(DEFAULT_DB_PATH)


def set_page(page: str) -> None:
    st.session_state["page"] = page


def initialize_state() -> None:
    st.session_state.setdefault("page", "home")
    st.session_state.setdefault("selected_category", None)
    st.session_state.setdefault("search_text", "")


def product_card(service: GroceryService, product: dict, compact: bool = False) -> None:
    st.markdown(
        f"""
        <div class="product-card">
            <div style="display:flex; gap:0.8rem; align-items:flex-start;">
                <div class="product-emoji" style="background:{product['accent_color']};">{product['image_emoji']}</div>
                <div style="flex:1;">
                    <div style="font-weight:700; font-size:1.02rem;">{product['name']}</div>
                    <div class="muted">{product['subtitle']}</div>
                    <div class="muted">{product['unit']} • ⭐ {product['rating']}</div>
                    <div class="price-row">
                        <span class="price-main">{product['price']:.1f} ₽</span>
                        {f"<span class='price-old'>{product['old_price']:.1f} ₽</span>" if product['old_price'] else ""}
                    </div>
                    <div class="badge-strip">{render_badges(product['badges'])}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    left, right = st.columns([1, 1])
    with left:
        fav_label = "Убрать из избранного" if product["is_favorite"] else "В избранное"
        if st.button(fav_label, key=f"fav_{product['id']}"):
            service.toggle_favorite(product["id"])
            st.rerun()
    with right:
        if st.button("В корзину", key=f"cart_{product['id']}", type="primary"):
            service.add_to_cart(product["id"])
            st.toast(f"{product['name']} добавлен в корзину")
            if compact:
                st.session_state["page"] = "cart"
            st.rerun()


def render_home(service: GroceryService) -> None:
    profile = service.get_profile()
    promos = service.list_promos()
    featured = service.list_featured_products()
    categories = service.list_categories()

    st.markdown(
        f"""
        <div class="hero-card">
            <div style="font-size:0.84rem; opacity:0.9;">Доставка за 30 минут</div>
            <div style="font-size:1.65rem; font-weight:800; margin-top:0.25rem;">Привет, {profile['name'].split()[0]}!</div>
            <div style="margin-top:0.35rem; max-width:220px;">Собрали персональные скидки, быстрый повтор заказов и бонусы в одном экране.</div>
            <div style="margin-top:0.9rem; padding:0.8rem; border-radius:20px; background:rgba(255,255,255,0.16);">
                <div style="font-size:0.8rem;">Бонусный баланс</div>
                <div style="font-size:1.55rem; font-weight:800;">{profile['bonus_balance']} баллов</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    section_title("Подборка", "Категории", "Короткий путь к ежедневной корзине")
    category_columns = st.columns(3)
    for index, category in enumerate(categories):
        with category_columns[index % 3]:
            if st.button(f"{category['icon']} {category['name']}", key=f"cat_{category['id']}"):
                st.session_state["selected_category"] = category["id"]
                st.session_state["page"] = "catalog"
                st.rerun()

    section_title("Выгода", "Акции и предложения")
    for promo in promos:
        st.markdown(
            f"""
            <div class="promo-card" style="background:linear-gradient(135deg, {promo['accent_color']}18 0%, #ffffff 100%);">
                <div class="badge-pill">{promo['tag']}</div>
                <div style="font-size:1.1rem; font-weight:700; margin-top:0.5rem;">{promo['title']}</div>
                <div class="muted" style="margin-top:0.25rem;">{promo['description']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    section_title("Сегодня выгодно", "Популярное со скидкой")
    for product in featured:
        product_card(service, product)


def render_catalog(service: GroceryService) -> None:
    categories = service.list_categories()
    selected_category = st.session_state.get("selected_category")
    search_text = st.text_input(
        "Поиск",
        value=st.session_state.get("search_text", ""),
        placeholder="Например, молоко или авокадо",
    )
    st.session_state["search_text"] = search_text

    category_options = {0: "Все"}
    category_options.update({category["id"]: f"{category['icon']} {category['name']}" for category in categories})
    selected = st.selectbox(
        "Категория",
        options=list(category_options.keys()),
        index=list(category_options.keys()).index(selected_category) if selected_category in category_options else 0,
        format_func=lambda value: category_options[value],
    )
    only_discounted = st.toggle("Только со скидкой", value=False)
    category_filter = selected or None
    products = service.list_products(
        search=search_text,
        category_id=category_filter,
        only_discounted=only_discounted,
    )

    section_title("Каталог", "Соберите корзину", f"Найдено товаров: {len(products)}")
    if not products:
        st.info("По выбранным фильтрам ничего не найдено.")
        return
    for product in products:
        product_card(service, product)


def render_favorites(service: GroceryService) -> None:
    favorites = service.list_favorites()
    section_title("Избранное", "Ваши быстрые покупки", "Любимые товары в один тап")
    if not favorites:
        st.info("Пока пусто. Добавьте товары из каталога или главной страницы.")
        return
    for product in favorites:
        product_card(service, product)


def render_cart(service: GroceryService) -> None:
    items = service.list_cart_items()
    summary = service.cart_summary()
    section_title("Корзина", "Проверьте заказ", f"Позиций: {summary['items_count']}")

    if not items:
        st.info("Корзина пока пустая. Добавьте пару товаров из каталога.")
        return

    for item in items:
        st.markdown(
            f"""
            <div class="checkout-card">
                <div style="display:flex; gap:0.8rem; align-items:center;">
                    <div class="product-emoji" style="background:{item['accent_color']};">{item['image_emoji']}</div>
                    <div style="flex:1;">
                        <div style="font-weight:700;">{item['name']}</div>
                        <div class="muted">{item['subtitle']}</div>
                        <div class="muted">{item['unit']}</div>
                    </div>
                    <div style="font-weight:700;">{item['line_total']:.1f} ₽</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        minus, qty, plus = st.columns([1, 1, 1])
        with minus:
            if st.button("−", key=f"minus_{item['product_id']}"):
                service.set_cart_quantity(item["product_id"], item["quantity"] - 1)
                st.rerun()
        with qty:
            st.markdown(
                f"<div style='text-align:center; padding-top:0.6rem; font-weight:700;'>{item['quantity']} шт</div>",
                unsafe_allow_html=True,
            )
        with plus:
            if st.button("+", key=f"plus_{item['product_id']}"):
                service.set_cart_quantity(item["product_id"], item["quantity"] + 1)
                st.rerun()

    st.markdown(
        f"""
        <div class="checkout-card">
            <div style="display:flex; justify-content:space-between;"><span>Товары</span><strong>{summary['subtotal']:.1f} ₽</strong></div>
            <div style="display:flex; justify-content:space-between;"><span>Ваша выгода</span><strong style="color:#d7263d;">-{summary['discount']:.1f} ₽</strong></div>
            <div style="display:flex; justify-content:space-between;"><span>Доставка</span><strong>{summary['delivery_fee']:.1f} ₽</strong></div>
            <hr style="border:none; border-top:1px solid #f1e7db; margin:0.85rem 0;">
            <div style="display:flex; justify-content:space-between; font-size:1.2rem;"><span>Итого</span><strong>{summary['total']:.1f} ₽</strong></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    profile = service.get_profile()
    with st.form("checkout_form", clear_on_submit=False):
        address = st.text_input("Адрес доставки", value=profile["address"])
        comment = st.text_area("Комментарий курьеру", placeholder="Код домофона, пожелания по доставке")
        payment_method = st.selectbox("Оплата", ["Картой онлайн", "При получении", "Бонусами и картой"])
        submitted = st.form_submit_button("Оформить заказ", type="primary")

    if submitted:
        order_id = service.create_order(address=address, comment=comment, payment_method=payment_method)
        st.success(f"Заказ №{order_id} оформлен. Скоро передадим его в сборку.")
        st.rerun()


def render_profile(service: GroceryService) -> None:
    profile = service.get_profile()
    orders = service.list_orders()
    section_title("Профиль", profile["name"], profile["phone"])

    stats = st.columns(3)
    metric_specs = [
        ("Баллы", str(profile["bonus_balance"])),
        ("Избранное", str(profile["favorites_count"])),
        ("Заказы", str(profile["orders_count"])),
    ]
    for column, (label, value) in zip(stats, metric_specs):
        with column:
            st.markdown(
                f"""
                <div class="stat-card">
                    <div class="muted">{label}</div>
                    <div class="metric-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        f"""
        <div class="checkout-card">
            <div class="muted">Основной адрес</div>
            <div style="font-weight:700; margin-top:0.3rem;">{profile['address']}</div>
            <div class="muted" style="margin-top:0.5rem;">Текущая сумма корзины: {profile['cart_total']:.1f} ₽</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    section_title("История", "Последние заказы")
    if not orders:
        st.info("Заказов пока нет. Оформите первый из корзины.")
        return

    for order in orders:
        st.markdown(
            f"""
            <div class="order-card">
                <div style="display:flex; justify-content:space-between; gap:0.6rem;">
                    <div>
                        <div style="font-weight:700;">Заказ №{order['id']}</div>
                        <div class="muted">{order['created_at']}</div>
                    </div>
                    <div style="font-weight:700;">{order['total']:.1f} ₽</div>
                </div>
                <div class="muted" style="margin-top:0.4rem;">{order['positions']} позиции • {order['payment_method']}</div>
                <div class="muted" style="margin-top:0.2rem;">{order['address']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_navigation() -> None:
    st.markdown("<div class='sticky-nav'><div class='nav-caption'>Навигация</div>", unsafe_allow_html=True)
    columns = st.columns(len(PAGES))
    current_page = st.session_state["page"]
    for column, (page_key, label, icon) in zip(columns, PAGES):
        with column:
            button_type = "primary" if page_key == current_page else "secondary"
            if st.button(f"{icon}", key=f"nav_{page_key}", type=button_type):
                set_page(page_key)
                st.rerun()
            st.caption(label)
    st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    st.set_page_config(
        page_title="Dixy Mobile Clone",
        page_icon="🛍️",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    initialize_state()
    inject_styles()
    service = get_service()

    st.markdown("<div class='mobile-shell'>", unsafe_allow_html=True)
    page = st.session_state["page"]
    if page == "home":
        render_home(service)
    elif page == "catalog":
        render_catalog(service)
    elif page == "favorites":
        render_favorites(service)
    elif page == "cart":
        render_cart(service)
    elif page == "profile":
        render_profile(service)
    st.markdown("</div>", unsafe_allow_html=True)
    render_navigation()


if __name__ == "__main__":
    if not Path(DEFAULT_DB_PATH).exists():
        DEFAULT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    main()
