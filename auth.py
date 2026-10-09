from __future__ import annotations
import os
import bcrypt
import streamlit as st

def _expected() -> str:
    return os.getenv("APP_PASSWORD_CHANGE_ME", "").strip()

def password_matches(password: str, expected: str) -> bool:
    if expected.startswith("$2"):
        return bcrypt.checkpw(password.encode("utf-8"), expected.encode("utf-8"))
    return password == expected

def require_login() -> None:
    if st.session_state.get("gv_auth_ok"):
        return
    expected = _expected()
    if not expected:
        st.error("Не задан APP_PASSWORD_CHANGE_ME в окружении.")
        st.stop()
    st.markdown("## Вход")
    st.caption("Локальная защита доступа к развёрнутому экземпляру.")
    pwd = st.text_input("Пароль", type="password")
    if st.button("Войти", type="primary"):
        if password_matches(pwd, expected):
            st.session_state["gv_auth_ok"] = True
            st.rerun()
        st.error("Неверный пароль.")
    st.stop()
