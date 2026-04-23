from __future__ import annotations

import streamlit as st


def inject_styles() -> None:
    st.markdown(
        """
        <style>
            :root {
                --surface: #fffaf5;
                --card: #ffffff;
                --ink: #1f2937;
                --muted: #6b7280;
                --accent: #ff385c;
                --accent-2: #0ead69;
                --line: #f1e7db;
            }

            .stApp {
                background:
                    radial-gradient(circle at top right, rgba(255, 56, 92, 0.12), transparent 28%),
                    linear-gradient(180deg, #fff9f0 0%, #fff6e9 42%, #fffdf9 100%);
            }

            .block-container {
                max-width: 430px;
                padding-top: 1rem;
                padding-bottom: 6rem;
                padding-left: 1rem;
                padding-right: 1rem;
            }

            h1, h2, h3, p, span, label, div {
                font-family: "Segoe UI", "Trebuchet MS", sans-serif;
                color: var(--ink);
            }

            .mobile-shell {
                background: rgba(255, 255, 255, 0.68);
                border: 1px solid rgba(255,255,255,0.7);
                box-shadow: 0 20px 50px rgba(226, 96, 54, 0.12);
                border-radius: 28px;
                padding: 0.9rem;
                backdrop-filter: blur(12px);
                margin-bottom: 1rem;
            }

            .hero-card,
            .promo-card,
            .product-card,
            .stat-card,
            .checkout-card,
            .order-card {
                border-radius: 24px;
                padding: 1rem;
                background: var(--card);
                border: 1px solid var(--line);
                box-shadow: 0 12px 30px rgba(46, 31, 12, 0.08);
                margin-bottom: 0.85rem;
            }

            .hero-card {
                background: linear-gradient(135deg, #ff385c 0%, #ff7b54 100%);
                color: white;
                border: none;
            }

            .hero-card * {
                color: white !important;
            }

            .section-label {
                font-size: 0.78rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                color: var(--muted);
                margin-bottom: 0.2rem;
            }

            .price-row {
                display: flex;
                align-items: baseline;
                gap: 0.55rem;
                margin-top: 0.3rem;
            }

            .price-main {
                font-size: 1.25rem;
                font-weight: 700;
                color: var(--ink);
            }

            .price-old {
                color: var(--muted);
                text-decoration: line-through;
                font-size: 0.92rem;
            }

            .badge-strip {
                display: flex;
                flex-wrap: wrap;
                gap: 0.35rem;
                margin-top: 0.55rem;
            }

            .badge-pill {
                display: inline-flex;
                border-radius: 999px;
                background: rgba(255, 56, 92, 0.1);
                color: #d7263d;
                padding: 0.18rem 0.55rem;
                font-size: 0.78rem;
                font-weight: 600;
            }

            .product-emoji {
                width: 56px;
                height: 56px;
                border-radius: 18px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.8rem;
                box-shadow: inset 0 0 0 1px rgba(255,255,255,0.45);
            }

            .sticky-nav {
                position: fixed;
                left: 50%;
                transform: translateX(-50%);
                bottom: 0.8rem;
                width: min(390px, calc(100vw - 1.5rem));
                background: rgba(255,255,255,0.92);
                backdrop-filter: blur(18px);
                border: 1px solid rgba(255,255,255,0.9);
                box-shadow: 0 12px 40px rgba(0,0,0,0.1);
                border-radius: 22px;
                padding: 0.6rem 0.8rem;
                z-index: 999999;
            }

            .nav-caption {
                font-size: 0.75rem;
                color: var(--muted);
                text-align: center;
                margin-top: -0.2rem;
                margin-bottom: 0.3rem;
            }

            .stButton > button, .stFormSubmitButton > button {
                width: 100%;
                border-radius: 18px;
                border: none;
                min-height: 2.8rem;
                font-weight: 600;
            }

            .metric-value {
                font-size: 1.4rem;
                font-weight: 700;
            }

            .muted {
                color: var(--muted);
                font-size: 0.92rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def section_title(eyebrow: str, title: str, subtitle: str | None = None) -> None:
    st.markdown(f"<div class='section-label'>{eyebrow}</div>", unsafe_allow_html=True)
    st.subheader(title)
    if subtitle:
        st.caption(subtitle)


def render_badges(badges: list[str]) -> str:
    return "".join(
        f"<span class='badge-pill'>{badge}</span>"
        for badge in badges
    )
