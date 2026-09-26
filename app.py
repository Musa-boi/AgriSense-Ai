import streamlit as st
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
    st.caption("• **Engine:** Gemini 3.8 Flash\n• **Target Region:** Pakistan")

# Right-to-Left styling for Urdu Script
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

# 4. Workspace
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
            try:
                img_data = Image.open(uploaded_file)
                
                # Format prompt instructions based on user selection
                if selected_language == "English":
                    lang_instruction = "Respond entirely in clear, simple English."
                elif selected_language == "Roman Urdu":
                    lang_instruction = "Respond entirely in clear ROMAN URDU (Urdu written in Latin script, e.g., 'Is patay par peele dhabbe hain')."
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

                ai_client = genai.Client(api_key=gemini_key)
                
                with st.spinner("Analyzing leaf patterns using Gemini 3.8 Vision..."):
                    response = ai_client.models.generate_content(
                        model="gemini-3.8-flash",
                        contents=[img_data, vision_prompt]
                    )

                report_content = response.text

                st.success("Analysis Complete!")
                if selected_language == "Urdu (اردو)":
                    st.markdown(f'<div class="report-box">{report_content}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(report_content)

            except Exception as e:
                st.error(f"Error processing leaf image: {str(e)}")
