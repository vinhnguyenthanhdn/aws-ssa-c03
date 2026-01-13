import streamlit as st
import random
from pathlib import Path
from quiz_parser import parse_markdown_file

st.set_page_config(page_title="SAA-C03 Prep", page_icon="☁️", layout="wide", initial_sidebar_state="expanded")

# Load CSS
with open(Path(__file__).parent / "style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def load_data():
    """Handles file loading logic."""
    fpath = Path(__file__).parent / "SAA_C03.md"
    if fpath.exists():
        return fpath.read_text(encoding='utf-8')
    return None

def main():
    if 'current_index' not in st.session_state:
        st.session_state.update({'current_index': 0, 'user_answers': {}, 'random_mode': False, 'question_order': []})

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        content = load_data()
        if not content:
            uploaded = st.file_uploader("Upload .md file", type=["md"])
            if uploaded: content = uploaded.getvalue().decode("utf-8")
            else: st.stop()
            
        questions = parse_markdown_file(content)
        total = len(questions)
        
        # Init order
        if len(st.session_state.question_order) != total:
            st.session_state.question_order = list(range(total))
            
        st.markdown(f"**Total Qs:** {total} | **Done:** {len(st.session_state.user_answers)}")
        st.progress(min(len(st.session_state.user_answers) / total, 1.0))
        st.divider()
        
        # Tools
        search = st.text_input("🔍 Search")
        c1, c2 = st.columns(2)
        if c1.button("🔀 Shuffle"):
            st.session_state.random_mode = True
            random.shuffle(st.session_state.question_order)
            st.session_state.current_index = 0
            st.rerun()
        if c2.button("🔄 Reset"):
            st.session_state.random_mode = False
            st.session_state.question_order = list(range(total))
            st.session_state.current_index = 0
            st.session_state.user_answers = {}
            st.rerun()
            
        if st.button("Jump to Q#"):
            q_jump = st.number_input("Q#", 1, total, 1) # This UI flow is a bit odd in streamlined version, keeping simple
            st.session_state.current_index = q_jump - 1
            st.rerun()

    # Main Logic
    indices = st.session_state.question_order
    is_search = False
    
    if search:
        indices = [i for i in st.session_state.question_order if search.lower() in questions[i]['question'].lower() or search in questions[i]['id']]
        if not indices: st.warning("No matches"); st.stop()
        if 'search_query' not in st.session_state or st.session_state.search_query != search:
            st.session_state.search_query = search; st.session_state.search_idx = 0
        idx_ptr = st.session_state.search_idx if st.session_state.search_idx < len(indices) else 0
        real_idx = indices[idx_ptr]
        is_search = True
    else:
        idx_ptr = st.session_state.current_index
        real_idx = indices[idx_ptr]

    q = questions[real_idx]
    
    # UI Render
    st.markdown(f"""
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <span class="question-number">{idx_ptr+1}</span>
                <span style="font-size: 1.5rem; font-weight: 700; color: #232f3e;">Question #{q['id']}</span>
                <span class="meta-tag topic-tag">📚 Topic {q['topic']}</span>
            </div>
            <span style="font-size: 0.875rem; color: #64748b; font-weight: 500;">{idx_ptr+1} of {len(indices)}</span>
        </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown(f'<div class="question-card"><div class="question-text">{q["question"].replace(chr(10), "<br>")}</div></div>', unsafe_allow_html=True)
        
        # Show multi-select hint
        if q['is_multiselect']:
            st.markdown('<p style="color: #ff9900; font-weight: 600; font-size: 0.875rem; margin-bottom: 0.5rem;">📌 Select all that apply</p>', unsafe_allow_html=True)
        
        with st.form(key=f"q_{q['id']}"):
            user_ch = []
            if q['is_multiselect']:
                for opt in q['options']:
                    if st.checkbox(opt): user_ch.append(opt.split('.')[0])
            else:
                sel = st.radio("Select your answer:", q['options'], index=None, label_visibility="collapsed")
                if sel: user_ch.append(sel.split('.')[0])
            
            sub = st.form_submit_button("✓ Submit Answer")
            
        ans = st.session_state.user_answers.get(q['id'])
        if sub and user_ch:
            ans = "".join(sorted(user_ch))
            st.session_state.user_answers[q['id']] = ans
            
        if ans:
            correct = ans == (q['correct_answer'] or "")
            if correct:
                st.markdown(f'''
                    <div class="success-msg">
                        <span style="margin-left: 0.5rem;">Correct! You answered: <strong>{ans}</strong></span>
                    </div>
                ''', unsafe_allow_html=True)
            else:
                st.markdown(f'''
                    <div class="error-msg">
                        <span style="margin-left: 0.5rem;">Incorrect. You answered: <strong>{ans}</strong></span>
                    </div>
                ''', unsafe_allow_html=True)
            
            with st.expander("Discussion", expanded=True):
                st.markdown(f"**Official:** <span class='highlight-answer'>{q['correct_answer']}</span>", unsafe_allow_html=True)
                if q['suggested_answer_text']: st.info(q['suggested_answer_text'])
                if q['discussion_link']: st.markdown(f"[Link]({q['discussion_link']})")

    # Nav
    c1, _, c2 = st.columns([1, 2, 1])
    if c1.button("⬅️"):
        if is_search and st.session_state.search_idx > 0: st.session_state.search_idx -= 1; st.rerun()
        elif not is_search and st.session_state.current_index > 0: st.session_state.current_index -= 1; st.rerun()
    if c2.button("➡️"):
        if is_search and st.session_state.search_idx < len(indices)-1: st.session_state.search_idx += 1; st.rerun()
        elif not is_search and st.session_state.current_index < len(questions)-1: st.session_state.current_index += 1; st.rerun()

if __name__ == "__main__":
    main()
