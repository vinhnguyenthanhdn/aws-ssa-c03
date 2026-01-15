import streamlit as st
import json
import io
from pathlib import Path
from translations import get_text
# Force refresh for Streamlit Cloud - 2026-01-15


try:
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
    HAS_GDRIVE_LIB = True
except ImportError:
    HAS_GDRIVE_LIB = False

# Configure Gemini Keys
API_KEYS = []
if "GOOGLE_API_KEYS" in st.secrets:
    API_KEYS = [k.strip() for k in st.secrets["GOOGLE_API_KEYS"].split(",")]
elif "GOOGLE_API_KEY" in st.secrets:
    API_KEYS = [st.secrets["GOOGLE_API_KEY"]]

LOCAL_CACHE_FILE = Path(__file__).parent / "ai_cache.json"
DRIVE_FILE_NAME = "aws_saa_c03_ai_cache.json"

def get_drive_service():
    """Authenticate and return Google Drive service."""
    if not HAS_GDRIVE_LIB: return None
    if "GDRIVE_CREDENTIALS" not in st.secrets: return None
    try:
        # Handle both dict and string format for secrets
        creds_val = st.secrets["GDRIVE_CREDENTIALS"]
        # Handle Streamlit AttrDict or JSON string
        creds_info = json.loads(creds_val) if isinstance(creds_val, str) else dict(creds_val)
        
        # Robust Private Key Fixer
        pk = creds_info.get("private_key", "")
        if pk:
            import re
            # Remove headers and whitespace
            clean_core = re.sub(r'-----[^-]+-----', '', pk).replace('\n', '').replace(' ', '').strip()
            
            # Pad if necessary
            missing_padding = len(clean_core) % 4
            if missing_padding:
                clean_core += '=' * (4 - missing_padding)
                             
            # Reconstruct Standard PEM
            fixed_pem = "-----BEGIN PRIVATE KEY-----\n"
            for i in range(0, len(clean_core), 64):
                fixed_pem += clean_core[i:i+64] + "\n"
            fixed_pem += "-----END PRIVATE KEY-----"
            
            creds_info["private_key"] = fixed_pem
            
        creds = Credentials.from_service_account_info(creds_info, scopes=['https://www.googleapis.com/auth/drive'])
        return build('drive', 'v3', credentials=creds)
    except Exception as e:
        print(f"Drive Auth Error: {e}")
        return None

def configure_genai():
    """Configure Google Generative AI with current API key."""
    import google.generativeai as genai
    if not API_KEYS: 
        return False
    
    # Ensure key index exists
    if "api_key_index" not in st.session_state:
        st.session_state.api_key_index = 0
    
    current_key = API_KEYS[st.session_state.api_key_index % len(API_KEYS)]
    genai.configure(api_key=current_key)
    return True

def rotate_key():
    """Rotate to next API key if rate limited."""
    if not API_KEYS: 
        return
    st.session_state.api_key_index = (st.session_state.api_key_index + 1) % len(API_KEYS)
    configure_genai()

def load_cache():
    """Load AI response cache from Drive or local fallback."""
    service = get_drive_service()
    
    # Fallback to local if Drive not available
    if not service:
        if not LOCAL_CACHE_FILE.exists(): return {"explanations": {}, "theories": {}}
        try: return json.loads(LOCAL_CACHE_FILE.read_text(encoding='utf-8'))
        except: return {"explanations": {}, "theories": {}}
    
    # Drive Logic
    try:
        folder_id = st.secrets.get("GDRIVE_FOLDER_ID")
        print(f"[DRIVE LOG] Start Load. Folder ID: {folder_id}")
        
        base_q = f"name = '{DRIVE_FILE_NAME}' and trashed = false"
        query = f"{base_q} and '{folder_id}' in parents" if folder_id else base_q
        print(f"[DRIVE LOG] Query: {query}")
        
        # Check for file existence
        results = service.files().list(q=query, spaces='drive', fields="files(id, name)").execute()
        files = results.get('files', [])
        print(f"[DRIVE LOG] Found files: {files}")
        
        if not files:
            # Try searching without parent if specific folder search failed (fallback)
            if folder_id:
                results = service.files().list(q=base_q, spaces='drive', fields="files(id, name)").execute()
                files = results.get('files', [])
                if files: st.toast("⚠ Tìm thấy Cache ở thư mục gốc (không phải thư mục chỉ định).")
            
            if not files:
                return {"explanations": {}, "theories": {}}
            
        # Download
        request = service.files().get_media(fileId=files[0]['id'])
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            
        fh.seek(0)
        return json.load(fh)
    except Exception as e:
        st.error(f"❌ Drive Load Error: {str(e)}")
        print(f"Drive Load Error: {e}")
        return {"explanations": {}, "theories": {}}

def save_cache(data):
    """Save AI response cache to Drive or local fallback."""
    service = get_drive_service()
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    
    # Fallback to local
    if not service:
        try: LOCAL_CACHE_FILE.write_text(json_str, encoding='utf-8')
        except: pass
        return

    # Drive Logic
    try:
        print(f"[DRIVE LOG] Start Save. Data size: {len(json_str)} bytes")
        fh = io.BytesIO(json_str.encode('utf-8'))
        media = MediaIoBaseUpload(fh, mimetype='application/json')
        
        folder_id = st.secrets.get("GDRIVE_FOLDER_ID")
        print(f"[DRIVE LOG] Folder ID: {folder_id}")
        
        base_q = f"name = '{DRIVE_FILE_NAME}' and trashed = false"
        query = f"{base_q} and '{folder_id}' in parents" if folder_id else base_q
        
        # Check for file
        results = service.files().list(q=query, spaces='drive', fields="files(id)").execute()
        files = results.get('files', [])
        print(f"[DRIVE LOG] Existing files found: {files}")
        
        if files:
            # Update existing
            print(f"[DRIVE LOG] Updating file ID: {files[0]['id']}")
            service.files().update(fileId=files[0]['id'], media_body=media).execute()
        else:
            # Create new
            print(f"[DRIVE LOG] Creating new file in folder: {folder_id}")
            metadata = {'name': DRIVE_FILE_NAME}
            if folder_id:
                metadata['parents'] = [folder_id]
                
            new_file = service.files().create(body=metadata, media_body=media, fields='id').execute()
            print(f"[DRIVE LOG] Created new file ID: {new_file.get('id')}")
    except Exception as e:
        st.error(f"❌ Drive Save Error: {str(e)}")
        print(f"Drive Save Error: {e}")

def get_cached_content(category, key):
    """Retrieve cached AI response."""
    data = load_cache()
    return data.get(category, {}).get(key)

def save_cached_content(category, key, value):
    """Save AI response to cache."""
    data = load_cache()
    if category not in data: 
        data[category] = {}
    data[category][key] = value
    save_cache(data)

def get_ai_explanation(question, options, correct_answer, question_id, lang="vi"):
    """Get AI explanation for a question answer."""
    # Check cache first
    cache_key = f"{question_id}_{lang}"
    cached = get_cached_content("explanations", cache_key)
    if cached: 
        return cached

    max_retries = min(len(API_KEYS) + 2, 6)  # Try shifting keys first
    for attempt in range(max_retries):
        try:
            configure_genai()  # Ensure current key is set
            import google.generativeai as genai
            model = genai.GenerativeModel('gemini-3-flash-preview')
            
            # Build prompt using translations
            t = lambda key: get_text(lang, key)
            prompt = f"""
            {t('ai_expert_intro')}
    
            {t('ai_question_label')}
            {question}
    
            {t('ai_options_label')}
            {options}
    
            {t('ai_correct_answer_label')} {correct_answer}
    
            {t('ai_output_requirements')}
            {t('ai_no_greeting')}
            {t('ai_no_conclusion')}
            {t('ai_focus_content')}
    
            {t('ai_structure_label')}
            {t('ai_structure_1')}
            {t('ai_structure_2')}
            {t('ai_structure_3')}
            {t('ai_structure_4')}
            """
            response = model.generate_content(prompt, stream=True)
            text = ""
            for chunk in response:
                if chunk.candidates and chunk.candidates[0].content.parts:
                    text += chunk.text
            
            if not text:
                return "⚠ AI trả về phản hồi rỗng (Stream Mode). Vui lòng thử lại."

            # Save to cache
            save_cached_content("explanations", cache_key, text)
            return text
        except Exception as e:
            if "429" in str(e):
                # Rotate key and retry
                rotate_key()
                continue 
            return f"⚠ Không thể tải phân tích từ AI. Lỗi: {str(e)}"
    
    return "⚠ Không thể tải phân tích từ AI sau nhiều lần thử."

def get_ai_theory(question, options, question_id, lang="vi"):
    """Get AI theory explanation for AWS concepts in question."""
    # Check cache first
    cache_key = f"{question_id}_{lang}"
    cached = get_cached_content("theories", cache_key)
    if cached: 
        return cached

    max_retries = min(len(API_KEYS) + 2, 6)
    for attempt in range(max_retries):
        try:
            configure_genai()
            import google.generativeai as genai
            model = genai.GenerativeModel('gemini-3-flash-preview')
            
            # Build prompt using translations
            t = lambda key: get_text(lang, key)
            prompt = f"""
            {t('ai_theory_intro')} 
            
            {t('ai_theory_header')}
    
            {t('ai_theory_context')}
            {question}
            {options}
    
            {t('ai_theory_requirements')}
            {t('ai_theory_req_1')}
            {t('ai_theory_req_2')}
            {t('ai_theory_req_3')}
            {t('ai_theory_req_4')}
            """
            response = model.generate_content(prompt, stream=True)
            text = ""
            for chunk in response:
                if chunk.candidates and chunk.candidates[0].content.parts:
                    text += chunk.text
            
            if not text:
                return "⚠ AI trả về phản hồi rỗng (Stream Mode). Vui lòng thử lại."

            # Save to cache
            save_cached_content("theories", cache_key, text)
            return text
        except Exception as e:
            if "429" in str(e):
                rotate_key()
                continue
            return f"⚠ Lỗi tải lý thuyết: {str(e)}"
    
    return "⚠ Không thể tải lý thuyết sau nhiều lần thử."

def init_ai_session_state():
    """Initialize AI-related session state."""
    if "api_key_index" not in st.session_state: 
        st.session_state.api_key_index = 0
    if "theories" not in st.session_state: 
        st.session_state.theories = {}
    if "explanations" not in st.session_state: 
        st.session_state.explanations = {}
