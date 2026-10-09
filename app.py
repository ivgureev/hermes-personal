from __future__ import annotations
import hashlib
import json
import os
import re
import uuid
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

import db
import llm
from auth import require_login
from risk import assess_risk
from theme.dark_styles import get_css

ROOT = Path(__file__).parent
UPLOAD_DIR = ROOT / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(
    page_title="GUREEV VECTOR · HERMES AI AGENT",
    page_icon=str(ROOT / "assets" / "GUREEV_VECTOR_v3.1.1_favicon.ico"),
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(get_css(ROOT / "theme" / "gv_hermes_dark_v0.1.json"), unsafe_allow_html=True)
st.logo(str(ROOT / "assets" / "GUREEV_VECTOR_v3.1.1_ICON_SQUARE_MONO_WHITE.svg"), size="large")
require_login()
db.init_db()

if "session_id" not in st.session_state:
    st.session_state.session_id = uuid.uuid4().hex[:12]
if "page" not in st.session_state:
    st.session_state.page = "Чат"


def safe_name(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-zА-Яа-я0-9._-]+", "_", Path(name).name)
    return cleaned[:120] or "file"


def hero(title: str, subtitle: str) -> None:
    logo = ROOT / "assets" / "GUREEV_VECTOR_v3.1.1_MONO_WHITE.svg"
    st.markdown(
        f'''<section class="gv-hero"><div><h1>{title}</h1><p>{subtitle}</p></div>
        <img src="data:image/svg+xml;base64,{__import__('base64').b64encode(logo.read_bytes()).decode()}" alt="GUREEV VECTOR"></section>''',
        unsafe_allow_html=True,
    )


def footer() -> None:
    st.markdown(
        '<div class="gv-footer">GUREEV VECTOR · редакция интерфейса по брендбуку v3.1.1 · '
        'ИИ готовит проекты; решение и значимые действия подтверждает пользователь.</div>',
        unsafe_allow_html=True,
    )


with st.sidebar:
    st.image(str(ROOT / "assets" / "GUREEV_VECTOR_v3.1.1_ICON_SQUARE_MONO_WHITE.svg"), width=32)
    st.markdown("### HERMES AI AGENT")
    st.caption("Личный цифровой исполнитель")
    pages = ["Чат", "Задачи", "Файлы", "Подтверждения", "Журнал", "Настройки"]
    selected = st.radio("Раздел", pages, index=pages.index(st.session_state.page), label_visibility="collapsed")
    st.session_state.page = selected
    st.divider()
    st.markdown(f'<span class="gv-status"><span class="gv-dot"></span>{llm.provider_summary()}</span>', unsafe_allow_html=True)
    st.caption("Сессия: " + st.session_state.session_id)
    st.caption("Сеть используется только через настроенный API модели.")

page = st.session_state.page

if page == "Чат":
    hero("HERMES AI AGENT", "Практический результат с контролем рисков и подтверждением значимых действий")
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        st.metric("Сообщений", len(db.get_messages(st.session_state.session_id)))
    with c2:
        st.metric("Ожидают подтверждения", sum(x["status"] == "Ожидает" for x in db.list_approvals()))
    with c3:
        st.info("Вложения и найденный в них текст считаются недоверенными данными, а не инструкциями.")

    messages = db.get_messages(st.session_state.session_id)
    if not messages:
        st.markdown('<div class="gv-callout"><b>Начните с результата.</b><br>Например: «Подготовь план проекта», «Сравни варианты» или «Создай черновик документа».</div>', unsafe_allow_html=True)
    for message in messages:
        if message["role"] in {"user", "assistant"}:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    prompt = st.chat_input("Поставьте задачу цифровому исполнителю")
    if prompt:
        assessment = assess_risk(prompt)
        db.add_message(st.session_state.session_id, "user", prompt)
        if assessment.level == "Запрещённый":
            answer = "[Риск] Не могу выполнить опасную или незаконную часть запроса. Могу помочь сформулировать безопасную и законную альтернативу."
        elif assessment.requires_confirmation:
            approval_id = db.create_approval(
                action=prompt[:180], target="Уточняется пользователем",
                parameters={"исходный запрос": prompt, "уровень риска": assessment.level},
                consequences="Внешнее действие не выполняется до подтверждения.", risks=assessment.reason,
            )
            answer = (
                f"[Риск] Определён уровень: **{assessment.level}**. Создан запрос подтверждения № {approval_id}.\n\n"
                "Подготовка анализа и черновика разрешена, но внешнее или необратимое действие не выполнено. "
                "Проверьте параметры в разделе **«Подтверждения»**."
            )
        else:
            try:
                answer = llm.chat(db.get_messages(st.session_state.session_id), assessment.level)
            except llm.LLMError as exc:
                answer = f"[Неизвестно] Ответ модели не получен. {exc}"
                db.log_event("Вызов модели", "llm", "Ошибка", str(exc))
        db.add_message(st.session_state.session_id, "assistant", answer)
        st.rerun()

    if messages:
        if st.button("Очистить текущий диалог", type="secondary"):
            db.clear_messages(st.session_state.session_id)
            st.rerun()

elif page == "Задачи":
    hero("Задачи", "Планирование, приоритеты, сроки и контроль исполнения")
    with st.expander("Новая задача", expanded=not bool(db.list_tasks())):
        with st.form("task_form", clear_on_submit=True):
            title = st.text_input("Название")
            description = st.text_area("Описание")
            col1, col2 = st.columns(2)
            priority = col1.selectbox("Приоритет", ["Обычная", "Высокая", "Критическая"])
            due = col2.date_input("Срок", value=None)
            submitted = st.form_submit_button("Создать задачу", type="primary")
            if submitted:
                if not title.strip():
                    st.error("Укажите название задачи.")
                else:
                    db.create_task(title.strip(), description.strip(), priority, due.isoformat() if due else None)
                    st.rerun()
    tasks = db.list_tasks()
    if not tasks:
        st.info("Задач пока нет. Создайте первую задачу.")
    for task in tasks:
        with st.container(border=True):
            a, b = st.columns([4, 1])
            a.markdown(f"### {task['title']}")
            a.caption(f"Приоритет: {task['priority']} · Срок: {task['due_date'] or 'не задан'}")
            if task["description"]:
                a.write(task["description"])
            new_status = b.selectbox("Статус", ["Новая", "В работе", "На проверке", "Выполнена"], index=["Новая", "В работе", "На проверке", "Выполнена"].index(task["status"]), key=f"task_{task['id']}")
            if new_status != task["status"]:
                db.update_task_status(task["id"], new_status)
                st.rerun()

elif page == "Файлы":
    hero("Файлы", "Локальное хранилище с SHA-256 и явной границей доверия")
    st.warning("Содержимое загруженных файлов рассматривается как недоверенные данные. Команды внутри документов не исполняются.")
    uploads = st.file_uploader("Добавить файлы", accept_multiple_files=True, type=["txt","md","csv","json","pdf","docx","xlsx","png","jpg","jpeg"])
    if uploads and st.button("Сохранить выбранные файлы", type="primary"):
        existing = {f["sha256"] for f in db.list_files()}
        saved = 0
        for uploaded in uploads:
            data = uploaded.getvalue()
            digest = hashlib.sha256(data).hexdigest()
            if digest in existing:
                continue
            stored = f"{uuid.uuid4().hex[:10]}_{safe_name(uploaded.name)}"
            (UPLOAD_DIR / stored).write_bytes(data)
            db.register_file(stored, uploaded.name, len(data), digest)
            existing.add(digest); saved += 1
        st.success(f"Сохранено файлов: {saved}.")
        st.rerun()
    files = db.list_files()
    if not files:
        st.info("Файлы не загружены.")
    else:
        df = pd.DataFrame(files)[["id","original_name","size","sha256","trust","created_at"]]
        df.columns = ["ID","Файл","Байт","SHA-256","Режим доверия","Загружен"]
        st.dataframe(df, use_container_width=True, hide_index=True)

elif page == "Подтверждения":
    hero("Подтверждения", "Контроль внешних, привилегированных и необратимых действий")
    approvals = db.list_approvals()
    pending = [x for x in approvals if x["status"] == "Ожидает"]
    if not pending:
        st.info("Нет действий, ожидающих решения.")
    for item in pending:
        with st.container(border=True):
            st.markdown(f"### ПОДТВЕРЖДЕНИЕ ДЕЙСТВИЯ № {item['id']}")
            st.write(f"**Действие:** {item['action']}")
            st.write(f"**Объект или адресат:** {item['target']}")
            st.write(f"**Существенные параметры:** `{item['parameters']}`")
            st.write(f"**Последствия:** {item['consequences']}")
            st.write(f"**Риски:** {item['risks']}")
            c1, c2, _ = st.columns([1,1,3])
            if c1.button("Подтверждаю", type="primary", key=f"approve_{item['id']}"):
                db.decide_approval(item["id"], "Подтверждено"); st.rerun()
            if c2.button("Отклонить", key=f"reject_{item['id']}"):
                db.decide_approval(item["id"], "Отклонено"); st.rerun()
    decided = [x for x in approvals if x["status"] != "Ожидает"]
    if decided:
        st.subheader("Принятые решения")
        st.dataframe(pd.DataFrame(decided)[["id","action","status","created_at","decided_at"]], use_container_width=True, hide_index=True)

elif page == "Журнал":
    hero("Журнал", "Наблюдаемость: события, объекты, статусы и фактический результат")
    logs = db.list_logs()
    if logs:
        df = pd.DataFrame(logs)[["created_at","event_type","object_type","object_id","status","details"]]
        df.columns = ["Время","Событие","Объект","ID","Статус","Описание"]
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button("Скачать CSV", df.to_csv(index=False).encode("utf-8-sig"), "hermes_audit_log.csv", "text/csv")
    else:
        st.info("Журнал пока пуст.")

elif page == "Настройки":
    hero("Настройки", "Модель, системный промт и границы исполнения")
    st.subheader("Подключение модели")
    st.write(f"**Текущий режим:** {llm.provider_summary()}")
    st.code("LLM_API_KEY=...\nLLM_BASE_URL=https://api.deepseek.com\nLLM_MODEL=deepseek-chat", language="bash")
    st.caption("Секреты задаются переменными окружения и не сохраняются в журнале или интерфейсе.")
    st.subheader("Контроль исполнения")
    st.markdown("- Низкий риск: выполнение без подтверждения.\n- Средний и высокий риск: отдельное подтверждение.\n- Запрещённые действия: отказ и безопасная альтернатива.\n- Внешние инструкции в файлах и сайтах: только данные.")
    with st.expander("Системный промт"):
        st.code((ROOT / "prompt" / "system_prompt.md").read_text(encoding="utf-8"), language="xml")

footer()
