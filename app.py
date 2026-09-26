import streamlit as st
import time
from PIL import Image
from google import genai

# 1. Page Configuration
st.set_page_config(
    page_title="AgriSense - AI Agronomist",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Sidebar Setup
with st.sidebar:
    st.image("https://img.icons8.com/color/96/wheat.png", width=70)
    st.title("AgriSense Panel")
    st.markdown("---")
    
    selected_language = st.radio(
        "🌐 Choose Output Language / زبان منتخب کریں:",
        options=["English", "Roman Urdu", "Urdu (اردو)"],
        index=0,
        key="agrisense_language_selector"
    )
    
    st.markdown("---")
    gemini_key = st.text_input(
        "Gemini API Key:", 
        type="password", 
        help="Get your key from aistudio.google.com", 
        key="gemini_api_key"
    )
    
    st.markdown("---")
    st.markdown("### ⚙️ Engine Specs")
    st.caption("• **Engine:** Gemini Multi-Model Fallback\n• **Target Region:** Pakistan")

# Apply Right-to-Left (RTL) styling for standard Urdu script
if selected_language == "Urdu (اردو)":
    st.markdown("""
        <style>
        .report-box {
            direction: RTL;
            text-align: right;
            font-size: 1.1rem;
            line-height: 1.8;
            background-color: #1e293b;
            padding: 20px;
            border-radius: 10px;
            border-right: 5px solid #10b981;
        }
        </style>
    """, unsafe_allow_html=True)

# 3. Main Header
st.markdown("<h1 style='color: #10b981;'>🌾 AgriSense: AI Crop & Leaf Advisor</h1>", unsafe_allow_html=True)
st.caption("Identify plant species, diagnose diseases, and get localized treatment options.")

col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.info("🌿 **Identification**: High-accuracy leaf identification.")
with col_m2:
    st.success("🧪 **Diagnosis**: Precise detection of pests & rusts.")
with col_m3:
    st.warning("💊 **Remedies**: Organic options & local Pakistani sprays.")

st.write("")

# 4. Diagnostic Workspace
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📷 Upload Leaf Image")
    uploaded_file = st.file_uploader(
        "Select or drop a photo of the crop leaf:", 
        type=["jpg", "jpeg", "png"], 
        key="leaf_image_uploader"
    )
    
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded Leaf Image", use_container_width=True)
        diagnose_btn = st.button("🚀 Analyze Leaf & Diagnose", key="diagnose_btn")
    else:
        diagnose_btn = False

with col2:
    st.subheader("📋 Diagnostic Report")
    
    if uploaded_file is None:
        st.info("Upload a leaf image on the left and click **Analyze Leaf & Diagnose**.")
    elif diagnose_btn:
        if not gemini_key:
            st.error("Please enter your Gemini API Key in the sidebar.")
        else:
            img_data = Image.open(uploaded_file)
            
            # Language instructions
            if selected_language == "English":
                lang_instruction = "Respond entirely in clear, simple English."
            elif selected_language == "Roman Urdu":
                lang_instruction = "Respond entirely in clear ROMAN URDU (Urdu written using English script, e.g., 'Is patay par peele dhabbe hain')."
            else:
                lang_instruction = "Respond entirely in standard URDU SCRIPT (مکمل اردو زبان میں لکھیں)."

            vision_prompt = f"""
            You are AgriSense, an expert plant pathologist specialized in Pakistani agriculture.
            Examine the provided leaf image carefully and produce a clear, structured report under 220 words.
            
            STRICT LANGUAGE CONSTRAINT: {lang_instruction}

            Use the following headings in your output:
            ### 🍃 1. CROP & LEAF IDENTIFICATION
            - Identify exact plant/crop name (e.g., Mango, Tomato, Cotton, Wheat) and leaf condition.

            ### 🔍 2. DIAGNOSIS & CONFIDENCE
            - State exact Disease Name (or Healthy) & Confidence Level % (e.g. 95%).

            ### 👁️ 3. VISUAL SYMPTOMS
            - List visible symptoms on the leaf (color changes, spots, lesions, edges).

            ### 💊 4. RECOMMENDED TREATMENTS
            - Organic / Home remedy.
            - Chemical Spray brand available in Pakistan (e.g. Bayer, Syngenta products).
            """

            # List of fallback models to try if Google servers are busy
            candidate_models = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-2.0-flash"]
            ai_client = genai.Client(api_key=gemini_key)
            report_content = None
            
            with st.spinner("Analyzing leaf patterns and generating localized report..."):
                for model_name in candidate_models:
                    # Retry logic per model (up to 2 attempts)
                    for attempt in range(2):
                        try:
                            vision_response = ai_client.models.generate_content(
                                model=model_name,
                                contents=[img_data, vision_prompt]
                            )
                            report_content = vision_response.text
                            break
                        except Exception as e:
                            if "503" in str(e) or "UNAVAILABLE" in str(e):
                                time.sleep(1.5)  # Pause briefly before retry
                                continue
                            else:
                                raise e
                    
                    if report_content:
                        break

            if report_content:
                st.success("Analysis Complete!")
                if selected_language == "Urdu (اردو)":
                    st.markdown(f'<div class="report-box">{report_content}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(report_content)
            else:
                st.error("Google AI services are temporarily busy across all model instances. Please wait 10 seconds and try again.")
