import streamlit as st
import json
import time
from pathlib import Path

import os

# Import custom modules
from app_config import setup_page_config, inject_seo, hide_streamlit_branding, load_custom_css
from ai_service import init_ai_session_state, get_ai_explanation, get_ai_theory
from ui_components import (
    render_page_header, render_question_header, render_question_card,
    render_answer_feedback, render_auto_scroll_script, render_ai_explanation,
    render_ai_theory, render_navigation_buttons, render_language_selector,
    render_footer
)
from quiz_parser import parse_markdown_file

# Setup page configuration
setup_page_config()
inject_seo()
hide_streamlit_branding()
load_custom_css()

@st.cache_data
def load_data(mtime):
    """Handles file loading logic. Cache invalidated if mtime changes."""
    fpath = Path(__file__).parent / "SAA_C03.md"
    if fpath.exists():
        content = fpath.read_text(encoding='utf-8')
        return parse_markdown_file(content)
    return None

def init_session_state(localS):
    """Initialize all session state variables."""
    # Load state from Local Storage/URL if session is fresh
    if 'data_loaded' not in st.session_state:
        # Restore Index from URL Query Params
        try:
            qp = st.query_params
            q_idx = int(qp.get("q", 1)) - 1
            st.session_state.current_index = max(0, q_idx)
        except:
            st.session_state.current_index = 0
             
        # Restore Answers from Local Storage
        try:
            saved_ans = localS.getItem("saa_c03_user_answers")
            if saved_ans:
                st.session_state.user_answers = json.loads(saved_ans)
        except:
            pass
            
        st.session_state.data_loaded = True

    # Ensure Session State Initialization
    if 'current_index' not in st.session_state: 
        st.session_state.current_index = 0
    if 'user_answers' not in st.session_state: 
        st.session_state.user_answers = {}
    if 'question_order' not in st.session_state: 
        st.session_state.question_order = []
    if 'active_ai_section' not in st.session_state:
        st.session_state.active_ai_section = None  # Can be 'theory', 'explanation', or None
    if 'language' not in st.session_state:
        st.session_state.language = 'vi'  # Default to Vietnamese
    
    # Initialize AI session state
    init_ai_session_state()

def handle_navigation(idx_ptr, total_indices, total_questions):
    """Handle navigation button clicks."""
    def on_prev():
        if st.session_state.current_index > 0:
            st.session_state.current_index -= 1
            st.query_params["q"] = str(st.session_state.current_index + 1)
            st.rerun()
    
    def on_next():
        if st.session_state.current_index < total_questions - 1:
            st.session_state.current_index += 1
            st.query_params["q"] = str(st.session_state.current_index + 1)
            st.rerun()
    
    def on_jump(new_idx):
        st.session_state.current_index = new_idx
        st.query_params["q"] = str(st.session_state.current_index + 1)
        st.rerun()
    
    render_navigation_buttons(idx_ptr, total_indices, on_prev, on_next, on_jump)

def get_current_question_index(questions):
    """Determine current question index."""
    indices = st.session_state.question_order
    idx_ptr = st.session_state.current_index
    real_idx = indices[idx_ptr]
    
    return indices, idx_ptr, real_idx

def render_question_form(q, localS):
    """Render the question form and handle submissions."""
    # Get language for AI generation (User preference)
    ai_lang = st.session_state.get('language', 'vi')
    
    # UI always in English
    from translations import get_text
    t = lambda key: get_text('en', key)
    
    with st.form(key=f"q_{q['id']}"):
        user_ch = []
        
        # Render options
        if q['is_multiselect']:
            for opt in q['options']:
                if st.checkbox(opt):
                    user_ch.append(opt.split('.')[0])
        else:
            sel = st.radio(t('select_answer'), q['options'], index=None, label_visibility="collapsed")
            if sel:
                user_ch.append(sel.split('.')[0])
        
        
        # Action buttons
        f1, f2, f3 = st.columns([1, 1, 1])
        
        with f1:
            theory_req = st.form_submit_button(t('btn_theory'), use_container_width=True)
        with f2:
            explain_req = st.form_submit_button(t('btn_explain'), use_container_width=True)
        with f3:
            sub = st.form_submit_button(t('btn_submit'), type="primary", use_container_width=True)
    
    # Handle answer submission
    if sub and user_ch:
        ans = "".join(sorted(user_ch))
        st.session_state.user_answers[q['id']] = ans
        localS.setItem("saa_c03_user_answers", json.dumps(st.session_state.user_answers))
    
    # Create cache keys that include language (so user can switch lang and get new content)
    theory_cache_key = f"{q['id']}_{ai_lang}"
    explanation_cache_key = f"{q['id']}_{ai_lang}"
    
    # Handle theory request
    if theory_req:
        with st.spinner(t('loading_theory')):
            start_time = time.time()
            if theory_cache_key not in st.session_state.theories:
                # Not cached - fetch from AI
                opts_text = "\n".join(q['options'])
                st.session_state.theories[theory_cache_key] = get_ai_theory(q['question'], opts_text, q['id'], ai_lang)
            
            # Ensure minimum 2s loading time for UX consistency
            elapsed = time.time() - start_time
            if elapsed < 2.0:
                time.sleep(2.0 - elapsed)
                
        # Set active section to theory, hide explanation
        st.session_state.active_ai_section = 'theory'
    
    # Handle explanation request
    if explain_req:
        with st.spinner(t('loading_explanation')):
            start_time = time.time()
            if explanation_cache_key not in st.session_state.explanations:
                # Not cached - fetch from AI
                opts_text = "\n".join(q['options'])
                explanation = get_ai_explanation(q['question'], opts_text, q['correct_answer'], q['id'], ai_lang)
                st.session_state.explanations[explanation_cache_key] = explanation
            
            # Ensure minimum 2s loading time for UX consistency
            elapsed = time.time() - start_time
            if elapsed < 2.0:
                time.sleep(2.0 - elapsed)
                
        # Set active section to explanation, hide theory
        st.session_state.active_ai_section = 'explanation'
    
    return theory_req, explain_req

def main():
    # Import here to avoid module load errors
    from streamlit_local_storage import LocalStorage
    
    # Initialize Local Storage
    localS = LocalStorage()
    init_session_state(localS)
    
    # Load questions
    fpath = Path(__file__).parent / "SAA_C03.md"
    mtime = os.path.getmtime(fpath) if fpath.exists() else 0
    questions = load_data(mtime)
    from translations import get_text
    
    if questions is None:
        # UI English
        st.header(get_text('en', 'settings'))
        uploaded = st.file_uploader(get_text('en', 'upload_file'), type=["md"])
        if uploaded:
            content = uploaded.getvalue().decode("utf-8")
            questions = parse_markdown_file(content)
        else:
            st.stop()
    total = len(questions)
    
    # Init question order
    if len(st.session_state.question_order) != total:
        st.session_state.question_order = list(range(total))
    
    # Render UI headers
    render_language_selector()  # Add language selector at the top
    render_page_header()
    
    # Check Drive Configuration
    if "GDRIVE_FOLDER_ID" not in st.secrets:
        st.warning("⚠️ **Lưu ý:** Bạn chưa cấu hình `GDRIVE_FOLDER_ID`. File cache đang được lưu trong bộ nhớ riêng của Bot (bạn sẽ không thấy trên Drive). Vui lòng thêm Folder ID vào Secrets.", icon="📂")
    
    # Get current question
    indices, idx_ptr, real_idx = get_current_question_index(questions)
    q = questions[real_idx]
    
    # Render question header
    render_question_header(idx_ptr, len(indices))
    
    with st.container():
        render_question_card(q["question"], q['is_multiselect'])
        
        # Render form and handle actions
        theory_req, explain_req = render_question_form(q, localS)
        
        # Display answer feedback
        ans = st.session_state.user_answers.get(q['id'])
        if ans:
            render_answer_feedback(ans, q['correct_answer'])
        
        # Render auto-scroll script
        render_auto_scroll_script()
        
        # Get current language for cache keys
        lang = st.session_state.get('language', 'vi')
        theory_cache_key = f"{q['id']}_{lang}"
        explanation_cache_key = f"{q['id']}_{lang}"
        
        # Only display one AI section at a time based on active_ai_section
        # Display AI explanation (only if active)
        if explanation_cache_key in st.session_state.explanations and st.session_state.active_ai_section == 'explanation':
            render_ai_explanation(
                q['id'],
                st.session_state.explanations[explanation_cache_key],
                q.get('discussion_link'),
                auto_scroll=explain_req
            )
        
        # Display AI theory (only if active)
        if theory_cache_key in st.session_state.theories and st.session_state.active_ai_section == 'theory':
            render_ai_theory(
                q['id'],
                st.session_state.theories[theory_cache_key],
                auto_scroll=theory_req
            )
    
    # Navigation
    handle_navigation(idx_ptr, len(indices), total)
    
    # Diagnostics
    with st.expander("🛠 System Diagnostics (Debug)"):
        if st.button("Test Reachability & Drive"):
            st.write("### 1. System Info")
            st.write(f"Streamlit Version: {st.__version__}")
            
            st.write("### 2. Google Drive Check")
            from ai_service import get_drive_service, HAS_GDRIVE_LIB
            
            st.write(f"- **Libraries Installed:** {'✅' if HAS_GDRIVE_LIB else '❌ (Missing google-api-python-client/google-auth)'}")
            has_secret = "GDRIVE_CREDENTIALS" in st.secrets
            st.write(f"- **[GDRIVE_CREDENTIALS]:** {'✅' if has_secret else '❌ (Missing in Secrets)'}")
            
            if not HAS_GDRIVE_LIB or not has_secret:
                st.error("Missing prerequisites. Cannot proceed.")
            else:
                try:
                    # Attempt manual auth for debugging
                    import json
                    from google.oauth2.service_account import Credentials
                    from googleapiclient.discovery import build
                    
                    creds_val = st.secrets["GDRIVE_CREDENTIALS"]
                    creds_info = json.loads(creds_val) if isinstance(creds_val, str) else dict(creds_val)
                    
                    # Advanced Private Key Analysis
                    pk = creds_info.get("private_key", "")
                    st.write("### 🔑 Private Key Analysis")
                    
                    # Normalize newlines
                    if "\\n" in pk:
                        pk = pk.replace("\\n", "\n")
                    
                    lines = pk.strip().split("\n")
                    st.write(f"- Total Lines: {len(lines)}")
                    
                    has_error = False
                    for i, line in enumerate(lines):
                        if "PRIVATE KEY" in line: continue
                        if len(line.strip()) == 0: continue
                        
                        # Base64 length check
                        if len(line) % 4 == 1:
                            st.error(f"❌ Line {i+1} corrupted: Length {len(line)} (Invalid Base64).")
                            st.code(line)
                            has_error = True
                    
                    if has_error:
                        st.warning("🔄 Attempting Auto-Repair (cleaning headers/whitespace)...")
                    
                    # Auto-Repair Strategy: Strip everything and rebuild
                    import re
                    clean_key = re.sub(r'-----[^-]+-----', '', pk).replace('\n', '').replace(' ', '').strip()
                    
                    if len(clean_key) % 4 != 0:
                        st.warning(f"Key length {len(clean_key)} requires padding. Auto-padding...")
                        clean_key += '=' * (4 - (len(clean_key) % 4))
                    
                    # Reconstruct Standard PEM
                    fixed_pem = "-----BEGIN PRIVATE KEY-----\n"
                    for i in range(0, len(clean_key), 64):
                        fixed_pem += clean_key[i:i+64] + "\n"
                    fixed_pem += "-----END PRIVATE KEY-----"
                    
                    creds_info["private_key"] = fixed_pem
                    st.code(fixed_pem, language="text") # Show fixed key to user
                    
                    # Retry Auth with Fixed Key
                    creds = Credentials.from_service_account_info(creds_info, scopes=['https://www.googleapis.com/auth/drive'])
                    service = build('drive', 'v3', credentials=creds)
                    st.success("✅ Auth Successful using Auto-Repaired Key!")
                    
                    # Folder Check
                    folder_id = st.secrets.get("GDRIVE_FOLDER_ID")
                    st.write(f"**Target Folder ID:** `{folder_id}`")
                    
                    if not folder_id:
                        st.error("No Folder ID provided.")
                    else:
                        # Check for Cache File Existence
                        DRIVE_FILE_NAME = "aws_saa_c03_ai_cache.json"
                        q = f"name = '{DRIVE_FILE_NAME}' and '{folder_id}' in parents and trashed = false"
                        results = service.files().list(q=q, fields="files(id, name)").execute()
                        files = results.get('files', [])
                        
                        if files:
                            file_id = files[0]['id']
                            st.success(f"✅ Found Cache File: `{files[0]['name']}` (ID: `{file_id}`)")
                            
                            # Write Test (Update)
                            st.write("Testing Write (Update) Permission...")
                            from googleapiclient.http import MediaIoBaseUpload
                            import io
                            import datetime
                            
                            # We just update the modification time or minimal content check
                            # But to be safe, let's just ready it. 
                            # Actually, let's try to read it first to preserve content, then write back?
                            # Or just try an update with same content?
                            # Simplest test is just checking we *can* find it. 
                            # If we want to test write, we need to be careful not to corrupt cache.
                            # Let's skipping actual write to avoid data loss in debug tool, 
                            # or just try to update 'description' metadata if possible? 
                            # Service accounts can update metadata.
                            
                            try:
                                new_desc = f"Last checked by SAA-C03 App at {datetime.datetime.now()}"
                                service.files().update(fileId=file_id, body={'description': new_desc}).execute()
                                st.success(f"✅ Write (Metadata Update) Success!")
                            except Exception as em:
                                st.error(f"❌ Write Failed: {em}")
                                
                        else:
                            st.warning(f"⚠ Cache file `{DRIVE_FILE_NAME}` not found in folder.")
                            st.info(f"**Action Required:** Please create an empty file named `{DRIVE_FILE_NAME}` in your Google Drive folder manually. The Service Account cannot create new files due to quota limits, but it can edit existing ones.")
                            
                            # Attempt Create (Will likely fail but good for confirmation)
                            if st.button("Attempt Force Create (Will likely fail)"):
                                try:
                                    test_content = b"{}"
                                    fh = io.BytesIO(test_content)
                                    media = MediaIoBaseUpload(fh, mimetype='application/json')
                                    meta = {'name': DRIVE_FILE_NAME, 'parents': [folder_id]}
                                    service.files().create(body=meta, media_body=media).execute()
                                except Exception as e:
                                    st.error(f"Expected Failure: {str(e)}")

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())

    # Render Footer
    render_footer()

if __name__ == "__main__":
    main()
