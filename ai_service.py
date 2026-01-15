import streamlit as st
import json
from pathlib import Path
from translations import get_text

# Configure Gemini Keys
API_KEYS = []
if "GOOGLE_API_KEYS" in st.secrets:
    API_KEYS = [k.strip() for k in st.secrets["GOOGLE_API_KEYS"].split(",")]
elif "GOOGLE_API_KEY" in st.secrets:
    API_KEYS = [st.secrets["GOOGLE_API_KEY"]]

CACHE_FILE = Path(__file__).parent / "ai_cache.json"

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
    """Load AI response cache from disk."""
    if not CACHE_FILE.exists():
        return {"explanations": {}, "theories": {}}
    try:
        return json.loads(CACHE_FILE.read_text(encoding='utf-8'))
    except:
        return {"explanations": {}, "theories": {}}

def save_cache(data):
    """Save AI response cache to disk."""
    try:
        CACHE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    except Exception as e:
        print(f"Error saving cache: {e}")

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
