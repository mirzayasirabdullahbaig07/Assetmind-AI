import streamlit as st
from database.db import init_db, get_session
from database.seed import seed_database
from ai.assistant import ask_assetmind
from utils.ui_kit import inject_base_css, page_header, panel, empty_state, alert, section
import config

init_db()
seed_database()
inject_base_css()

st.markdown("""
<style>
/* Example question chips (buttons with key "ex_*") */
[class*="st-key-ex_"] button{
  width:100%; min-height:68px; justify-content:flex-start; text-align:left; border-radius:14px;
  background:#F8FAFC; border:1px solid #E2E8F0; color:#1E293B; font-weight:600; font-size:.86rem; padding:10px 14px;
  transition:all .2s ease;}
[class*="st-key-ex_"] button:hover{background:#EFF6FF; border-color:#93C5FD; color:#1E3A8A; transform:translateY(-3px);
  box-shadow:0 12px 22px -14px rgba(37,99,235,.55);}

/* Chat bubbles */
[data-testid="stChatMessage"]{border:1px solid #E2E8F0; border-radius:16px; background:#fff; padding:14px 18px;
  box-shadow:0 1px 2px rgba(15,23,42,.04); animation:amFadeUp .4s ease both;}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]){
  background:linear-gradient(135deg,#EFF6FF,#F0FDFA); border-color:#DBEAFE;}

/* Chat input */
[data-testid="stChatInput"]{border-radius:16px;}
</style>
""", unsafe_allow_html=True)

page_header(
    "ask", "Ask AssetMind",
    "Ask natural-language questions — every answer is grounded in real database results.",
    badge=config.COMPANY_NAME,
)

if not config.GROQ_API_KEY:
    alert("warning", "<b>GROQ_API_KEY is not configured.</b> Add it to your <code>.env</code> file to use this page.",
          html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

EXAMPLE_QUESTIONS = [
    "What assets need attention?",
    "Which department has the most maintenance issues?",
    "Which assets were repaired more than twice?",
    "How much did we spend on maintenance?",
    "Show me damaged chairs.",
    "Which laptops are under warranty?",
    "Which assets were replaced this year?",
    "How many assets are currently under repair?",
]

# ---------------------------------------------------------------- example chips
clicked_example = None
with panel("ask_examples", "Try asking", "ask"):
    cols = st.columns(4, gap="small")
    for i, q in enumerate(EXAMPLE_QUESTIONS):
        if cols[i % 4].button(q, key=f"ex_{i}", icon=":material/north_east:"):
            clicked_example = q

typed = st.chat_input("Ask about your assets, e.g. Which assets need attention?")
pending = clicked_example or (typed.strip() if typed else None)

# ---------------------------------------------------------------- conversation
st.write("")
head, clear_col = st.columns([5, 1], vertical_alignment="center")
with head:
    section("Conversation", "activity")
with clear_col:
    if st.session_state.chat_history and st.button("Clear", icon=":material/delete:", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

if not st.session_state.chat_history and not pending:
    with panel("ask_empty", "No questions yet", "ask"):
        empty_state("Pick an example above or type your own question below to get started.", "ask")

for entry in st.session_state.chat_history:
    with st.chat_message("user", avatar=":material/person:"):
        st.markdown(entry["question"])
    with st.chat_message("assistant", avatar=":material/smart_toy:"):
        if entry.get("error"):
            alert("danger", entry["error"])
        else:
            st.markdown(entry["answer"])
            if entry.get("function_used"):
                with st.expander(f"View raw database result (via `{entry['function_used']}`)"):
                    st.json(entry["raw_data"])

if pending:
    with st.chat_message("user", avatar=":material/person:"):
        st.markdown(pending)
    with st.chat_message("assistant", avatar=":material/smart_toy:"):
        session = get_session()
        try:
            with st.spinner("Checking the database..."):
                result = ask_assetmind(session, pending)
        finally:
            session.close()
    st.session_state.chat_history.append({"question": pending, **result})
    st.rerun()