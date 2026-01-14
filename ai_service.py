import streamlit as st
import json
from pathlib import Path

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

def get_ai_explanation(question, options, correct_answer, question_id):
    """Get AI explanation for a question answer."""
    # Check cache first
    cached = get_cached_content("explanations", question_id)
    if cached: 
        return cached

    max_retries = min(len(API_KEYS) + 2, 6)  # Try shifting keys first
    for attempt in range(max_retries):
        try:
            configure_genai()  # Ensure current key is set
            import google.generativeai as genai
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"""
            Bạn là chuyên gia AWS SAA-C03. Nhiệm vụ của bạn là phân tích câu hỏi trắc nghiệm này để giải thích cho học viên.
    
            **Câu hỏi:**
            {question}
    
            **Các lựa chọn:**
            {options}
    
            **Đáp án đúng:** {correct_answer}
    
            **Yêu cầu Output (Rất quan trọng):**
            - **TUYỆT ĐỐI KHÔNG** có lời chào mở đầu (VD: "Chào bạn", "Tôi là chuyên gia...").
            - **TUYỆT ĐỐI KHÔNG** có lời chúc hay kết luận xã giao ở cuối (VD: "Chúc thi tốt", "Hy vọng giúp ích...").
            - Chỉ tập trung vào nội dung chuyên môn cô đọng.
    
            **Cấu trúc phân tích:**
            1. **🎯 Phân tích Yêu cầu:** Xác định từ khóa (keywords) và mục tiêu của đề bài.
            2. **✅ Giải thích đáp án đúng:** Tại sao nó đáp ứng tốt nhất yêu cầu (về kỹ thuật, chi phí, best practice)?
            3. **❌ Giải thích đáp án sai:** Lí do từng đáp án còn lại không phù hợp.
            4. **💡 Mẹo nhớ nhanh:** Mapping từ khóa <-> Dịch vụ.
            """
            response = model.generate_content(prompt)
            text = response.text
            # Save to cache
            save_cached_content("explanations", question_id, text)
            return text
        except Exception as e:
            if "429" in str(e):
                # Rotate key and retry
                rotate_key()
                continue 
            return f"⚠ Không thể tải phân tích từ AI. Lỗi: {str(e)}"
    
    return "⚠ Không thể tải phân tích từ AI sau nhiều lần thử."

def get_ai_theory(question, options, question_id):
    """Get AI theory explanation for AWS concepts in question."""
    # Check cache first
    cached = get_cached_content("theories", question_id)
    if cached: 
        return cached

    max_retries = min(len(API_KEYS) + 2, 6)
    for attempt in range(max_retries):
        try:
            configure_genai()
            import google.generativeai as genai
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"""
            Bạn là từ điển sống về AWS. Hãy giải thích ngắn gọn các **Dịch vụ** hoặc **Khái niệm** AWS xuất hiện trong văn bản sau:
    
            **Ngữ cảnh (Câu hỏi & Đáp án):**
            {question}
            {options}
    
            **Yêu cầu Output:**
            - Chỉ tập trung vào CÁC KHÁI NIỆM/DỊCH VỤ (VD: AWS Lambda, IOPS, Consistency Model...).
            - Với mỗi khái niệm: Đưa ra định nghĩa 1 dòng và Use Case chính 1 dòng.
            - Không giải thích câu hỏi, không phân tích đúng sai.
            - Trình bày dạng danh sách Markdown sạch sẽ.
            """
            response = model.generate_content(prompt)
            text = response.text
            # Save to cache
            save_cached_content("theories", question_id, text)
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
