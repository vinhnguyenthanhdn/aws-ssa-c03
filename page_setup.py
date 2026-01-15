import streamlit as st
# Force refresh for Streamlit Cloud - 2026-01-15


def setup_page_config():
    """Configure Streamlit page settings and SEO."""
    # Early Page Config for faster initial render
    st.write('<style>div.block-container{padding-top:0rem;}</style>', unsafe_allow_html=True)
    st.set_page_config(
        page_title="AWS Certified Solutions Architect Associate (SAA-C03)", 
        page_icon="☁️", 
        layout="wide", 
        initial_sidebar_state="collapsed"
    )

def inject_seo():
    """Inject SEO meta tags."""
    st.markdown("""
        <script>
            document.title = "AWS Certified Solutions Architect Associate (SAA-C03)";
            
            // Add Meta Description
            var metaDesc = document.createElement('meta');
            metaDesc.name = "description";
            metaDesc.content = "Luyện thi chứng chỉ AWS Certified Solutions Architect Associate (SAA-C03) miễn phí với bộ câu hỏi trắc nghiệm đầy đủ, giải thích chi tiết từ AI và chế độ ôn tập thông minh.";
            document.getElementsByTagName('head')[0].appendChild(metaDesc);

            // Add Meta Keywords
            var metaKeywords = document.createElement('meta');
            metaKeywords.name = "keywords";
            metaKeywords.content = "AWS, SAA-C03, Solutions Architect, Exam Prep, Trắc nghiệm AWS, Cloud Computing, Luyện thi AWS miễn phí";
            document.getElementsByTagName('head')[0].appendChild(metaKeywords);
        </script>
    """, unsafe_allow_html=True)

def hide_streamlit_branding():
    """Hide Streamlit viewer badge and toolbar."""
    st.markdown("""
        <script>
            var observer = new MutationObserver(function(mutations) {
                var parentDoc = window.parent.document;
                if (parentDoc) {
                    var newStyle = parentDoc.createElement("style");
                    newStyle.innerHTML = `
                        ._viewerBadge_nim44_23, 
                        ._container_gzau3_1._viewerBadge_nim44_23, 
                        [class*="viewerBadge"], 
                        header[data-testid="stHeader"],
                        .stDeployButton,
                        [data-testid="stToolbar"] {
                            display: none !important;
                            visibility: hidden !important;
                        }
                    `;
                    parentDoc.head.appendChild(newStyle);
                }
            });
            observer.observe(window.parent.document.body, { childList: true, subtree: true });
            
            // Initial run
            try {
                var parentDoc = window.parent.document;
                if (parentDoc) {
                    var elements = parentDoc.querySelectorAll('._viewerBadge_nim44_23, [class*="viewerBadge"], [data-testid="stToolbar"]');
                    elements.forEach(el => el.style.display = 'none');
                    
                    // Inject style tag into parent for persistence
                    var style = parentDoc.createElement('style');
                    style.innerHTML = `
                        ._viewerBadge_nim44_23,
                        ._container_gzau3_1._viewerBadge_nim44_23,
                        [class*="viewerBadge"],
                        .stDeployButton,
                        [data-testid="stToolbar"] {
                            display: none !important;
                        }
                    `;
                    parentDoc.head.appendChild(style);
                }
            } catch (e) {
                console.log("Could not access parent document to hide Streamlit branding: " + e);
            }
        </script>
    """, unsafe_allow_html=True)

def load_custom_css():
    """Load custom CSS styles."""
    from pathlib import Path
    with open(Path(__file__).parent / "style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
