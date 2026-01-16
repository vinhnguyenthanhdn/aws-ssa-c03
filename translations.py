# Language Translation System
# This file contains all UI text translations for the app
# Force refresh for Streamlit Cloud - 2026-01-16 v2


LANGUAGES = {
    "vi": {
        "code": "vi",
        "name": "Tiếng Việt",
        "flag": "🇻🇳"
    },
    "en": {
        "code": "en",
        "name": "English",
        "flag": "🇺🇸"
    }
}

TRANSLATIONS = {
    "vi": {
        # Page Header
        "page_title": "AWS Certified Solutions Architect Associate (SAA-C03)",
        
        # Sidebar
        "settings": "⚙️ Cài Đặt",
        "total_qs": "Tổng số",
        "done": "Hoàn thành",
        "search": "🔍 Tìm kiếm",
        "shuffle": "🔀 Xáo trộn",
        "reset": "🔄 Làm mới",
        
        # Question
        "question": "Câu hỏi",
        "of": "trên",
        "select_all": "📌 Chọn tất cả các đáp án đúng",
        "select_answer": "Chọn câu trả lời của bạn:",
        
        # Buttons
        "btn_theory": "📖 Lý Thuyết",
        "btn_explain": "🤖 Giải Thích",
        "btn_submit": "✓ Gửi câu trả lời",
        "btn_previous": "⬅️ Trước",
        "btn_next": "Tiếp ➡️",
        "btn_go": "Đi",
        "go_to_question": "Đi đến Câu hỏi #",
        
        # Feedback
        "correct": "Đúng rồi! Bạn đã chọn:",
        "incorrect": "Sai rồi. Bạn đã chọn:",
        "no_matches": "Không tìm thấy kết quả",
        
        # AI Sections
        "ai_analysis_title": "🤖 Phân Tích (AI Teacher)",
        "ai_theory_title": "📖 Kiến Thức Nền (Concepts)",
        "see_discussion": "Xem thảo luận gốc trên ExamTopics",
        
        # Loading
        "loading_theory": "Đang tổng hợp kiến thức...",
        "loading_explanation": "Đang phân tích câu hỏi... (Gemini AI)",
        
        # Upload
        "upload_file": "Tải lên file .md",
        
        # AI Prompts
        "ai_expert_intro": "Bạn là chuyên gia AWS SAA-C03. Nhiệm vụ của bạn là phân tích câu hỏi trắc nghiệm này để giải thích cho học viên.",
        "ai_question_label": "**Câu hỏi:**",
        "ai_options_label": "**Các lựa chọn:**",
        "ai_correct_answer_label": "**Đáp án đúng:**",
        "ai_output_requirements": "**Yêu cầu Output (Rất quan trọng):**",
        "ai_no_greeting": "- **TUYỆT ĐỐI KHÔNG** có lời chào mở đầu (VD: \"Chào bạn\", \"Tôi là chuyên gia...\").",
        "ai_no_conclusion": "- **TUYỆT ĐỐI KHÔNG** có lời chúc hay kết luận xã giao ở cuối (VD: \"Chúc thi tốt\", \"Hy vọng giúp ích...\").",
        "ai_focus_content": "- Chỉ tập trung vào nội dung chuyên môn cô đọng.",
        "ai_structure_label": "**Cấu trúc phân tích:**",
        "ai_structure_1": "1. **🎯 Phân tích Yêu cầu:** Xác định từ khóa (keywords) và mục tiêu của đề bài.",
        "ai_structure_2": "2. **✅ Giải thích đáp án đúng:** Tại sao nó đáp ứng tốt nhất yêu cầu (về kỹ thuật, chi phí, best practice)?",
        "ai_structure_3": "3. **❌ Giải thích đáp án sai:** Lí do từng đáp án còn lại không phù hợp.",
        "ai_structure_4": "4. **💡 Mẹo nhớ nhanh:** Mapping từ khóa <-> Dịch vụ.",
        
        "ai_theory_intro": "Bạn là từ điển sống về AWS.",
        "ai_theory_header": "Dưới đây là các dịch vụ và khái niệm AWS xuất hiện trong câu hỏi:",
        "ai_theory_context": "**Ngữ cảnh (Câu hỏi & Đáp án):**",
        "ai_theory_requirements": "**Yêu cầu Output:**",
        "ai_theory_req_1": "- Chỉ tập trung vào CÁC KHÁI NIỆM/DỊCH VỤ (VD: AWS Lambda, IOPS, Consistency Model...).",
        "ai_theory_req_2": "- Với mỗi khái niệm: Đưa ra định nghĩa 1 dòng và Use Case chính 1 dòng.",
        "ai_theory_req_3": "- Không giải thích câu hỏi, không phân tích đúng sai.",
        "ai_theory_req_4": "- Trình bày dạng danh sách Markdown sạch sẽ.",
    },
    
    "en": {
        # Page Header
        "page_title": "AWS Certified Solutions Architect Associate (SAA-C03)",
        
        # Sidebar
        "settings": "⚙️ Settings",
        "total_qs": "Total",
        "done": "Done",
        "search": "🔍 Search",
        "shuffle": "🔀 Shuffle",
        "reset": "🔄 Reset",
        
        # Question
        "question": "Question",
        "of": "of",
        "select_all": "📌 Select all that apply",
        "select_answer": "Select your answer:",
        
        # Buttons
        "btn_theory": "📚 Theory",
        "btn_explain": "💡 Explain",
        "btn_submit": "✅ Submit",
        "btn_previous": "⬅️ Previous",
        "btn_next": "Next ➡️",
        "btn_go": "🚀",
        "go_to_question": "Go to Question #",
        
        # Feedback
        "correct": "Correct! You answered:",
        "incorrect": "Incorrect. You answered:",
        "no_matches": "No matches found",
        
        # AI Sections
        "ai_analysis_title": "🤖 Analysis",
        "ai_theory_title": "📖 Background Knowledge (Concepts)",
        "see_discussion": "See original discussion on ExamTopics",
        
        # Loading
        "loading_theory": "Compiling knowledge...",
        "loading_explanation": "Analyzing question...",
        
        # Upload
        "upload_file": "Upload .md file",
        
        # AI Prompts
        "ai_expert_intro": "You are an AWS SAA-C03 expert. Your task is to analyze this multiple-choice question to explain it to students.",
        "ai_question_label": "**Question:**",
        "ai_options_label": "**Options:**",
        "ai_correct_answer_label": "**Correct Answer:**",
        "ai_output_requirements": "**Output Requirements (Very Important):**",
        "ai_no_greeting": "- **ABSOLUTELY NO** opening greetings (e.g., \"Hello\", \"I am an expert...\").",
        "ai_no_conclusion": "- **ABSOLUTELY NO** closing wishes or social conclusions (e.g., \"Good luck\", \"Hope this helps...\").",
        "ai_focus_content": "- Focus only on concise technical content.",
        "ai_structure_label": "**Analysis Structure:**",
        "ai_structure_1": "1. **🎯 Requirement Analysis:** Identify keywords and objectives of the question.",
        "ai_structure_2": "2. **✅ Explain Correct Answer:** Why it best meets requirements (technically, cost-wise, best practice)?",
        "ai_structure_3": "3. **❌ Explain Wrong Answers:** Reasons why each remaining option is unsuitable.",
        "ai_structure_4": "4. **💡 Quick Tips:** Mapping keywords <-> Services.",
        
        "ai_theory_intro": "You are a living AWS dictionary.",
        "ai_theory_header": "Below are AWS services and concepts that appear in the question:",
        "ai_theory_context": "**Context (Question & Answers):**",
        "ai_theory_requirements": "**Output Requirements:**",
        "ai_theory_req_1": "- Focus only on CONCEPTS/SERVICES (e.g., AWS Lambda, IOPS, Consistency Model...).",
        "ai_theory_req_2": "- For each concept: Provide a one-line definition and one-line main Use Case.",
        "ai_theory_req_3": "- Do not explain the question, do not analyze right or wrong.",
        "ai_theory_req_4": "- Present as a clean Markdown list.",
    }
}

def get_text(lang_code, key):
    """Get translated text for a given language and key."""
    return TRANSLATIONS.get(lang_code, TRANSLATIONS["vi"]).get(key, key)

def get_available_languages():
    """Return list of available languages."""
    return LANGUAGES
