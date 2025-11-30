from __future__ import annotations

import os
import time
from io import BytesIO
from typing import Any, Dict, Optional

import requests
import streamlit as st
from PIL import Image
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# -----------------------------------------------------------------------------
# 1. CONFIGURATION & SETUP
# -----------------------------------------------------------------------------
DEFAULT_API_URL = "http://leaf-diseases-detect.vercel.app"
LOCAL_API_URL = "http://localhost:8000"
BACKEND_URL = os.getenv("LEAF_API_URL", DEFAULT_API_URL)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

st.set_page_config(
    page_title="FloraGuard AI",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# 2. MODERN UI STYLING (CSS)
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {background-color: #f8fafc;}
    .css-1r6slb0, .css-12oz5g7 {
        background-color: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
                    0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    h1, h2, h3 {
        color: #1e293b;
        font-family: 'Segoe UI', sans-serif;
    }
    .stButton>button {
        background-color: #22c55e;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #16a34a;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
    }
    [data-testid="stSidebar"] {background-color: #1e293b;}
    [data-testid="stSidebar"] * {color: #e2e8f0 !important;}
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 3. BACKEND + MOCK PREDICTION LOGIC
# -----------------------------------------------------------------------------
def _optimize_image(image: Image.Image) -> bytes:
    """Convert uploads to optimized JPEG bytes for the backend."""
    buffer = BytesIO()
    image.convert("RGB").save(buffer, format="JPEG", quality=90)
    return buffer.getvalue()


def get_disease_explanation(disease_name: str, symptoms: list, causes: list) -> Optional[str]:
    """Get detailed explanation about the disease using Groq AI API with fallback."""
    
    # Fallback disease database for when API is unavailable
    disease_info = {
        "early blight": "Early Blight is a common fungal disease caused by Alternaria solani that affects tomatoes, potatoes, and other plants. It creates dark spots with concentric rings (target-like pattern) on older leaves first, then spreads upward. The disease thrives in warm, humid conditions (75-85°F) with alternating wet and dry periods. Spores spread through wind, rain splash, and contaminated tools. To prevent Early Blight: rotate crops every 2-3 years, remove infected plant debris, water at the base of plants (avoid wetting leaves), ensure good air circulation, and apply fungicides preventively during humid weather.",
        
        "late blight": "Late Blight is a devastating disease caused by Phytophthora infestans that can destroy entire crops within days. It causes water-soaked gray-green spots that turn brown/black, often with white fuzzy growth underneath leaves in humid conditions. This disease spreads rapidly in cool, wet weather (50-80°F). Spores travel by wind for miles. Prevention: use certified disease-free seeds, avoid overhead irrigation, destroy infected plants immediately, apply copper-based fungicides preventively, and plant resistant varieties when available.",
        
        "powdery mildew": "Powdery Mildew appears as white or gray powdery patches on leaf surfaces, stems, and sometimes fruits. Unlike most fungal diseases, it thrives in warm, dry conditions with high humidity (not wet leaves). The fungus weakens plants by blocking photosynthesis and stealing nutrients. Prevention: ensure good air circulation, avoid overcrowding plants, water at soil level, remove infected leaves promptly, and apply sulfur or potassium bicarbonate sprays. Neem oil also helps control mild infections.",
        
        "leaf spot": "Leaf Spot diseases are caused by various fungi and bacteria, creating spots of different colors (brown, black, tan) on leaves. Spots may have yellow halos and can merge to kill entire leaves. The pathogens survive in plant debris and spread through water splash and wind. Prevention: practice crop rotation, remove fallen leaves, avoid overhead watering, space plants for air circulation, and apply copper fungicides when symptoms first appear.",
        
        "rust": "Rust diseases are caused by fungi that produce orange, yellow, or brown powdery pustules on leaf undersides. Severely infected leaves turn yellow and drop. Rust fungi need living plant tissue to survive and often require two different host plants to complete their life cycle. Prevention: remove infected leaves, improve air circulation, avoid wetting foliage, apply fungicides at first sign, and destroy alternate host plants nearby.",
        
        "bacterial spot": "Bacterial Spot causes small, water-soaked spots that turn brown with yellow halos. Unlike fungal spots, bacterial lesions often look greasy or angular. The bacteria spread through rain splash, irrigation water, and contaminated tools. They enter through wounds or natural openings. Prevention: use disease-free seeds, avoid working with wet plants, sanitize tools, rotate crops, and apply copper sprays preventively. Remove severely infected plants.",
        
        "mosaic virus": "Mosaic Virus causes mottled light and dark green patterns on leaves, leaf curling, stunted growth, and reduced yields. Viruses cannot be cured once a plant is infected. They spread through aphids, contaminated tools, and infected seeds. Prevention: control aphid populations, remove infected plants immediately, sanitize tools with 10% bleach solution, use virus-resistant varieties, and avoid tobacco products near tomato family plants.",
        
        "brown spot": "Brown Spot is a fungal disease causing circular brown lesions with gray centers on leaves. It commonly affects rice, soybeans, and other crops. The fungus survives in infected seeds and plant debris. It spreads in warm, humid conditions through wind and rain. Prevention: use certified disease-free seeds, maintain proper plant nutrition (especially potassium), avoid excessive nitrogen, ensure good drainage, and apply fungicides during susceptible growth stages.",
        
        "septoria": "Septoria Leaf Spot creates small circular spots with dark borders and tan/gray centers, often with tiny black dots (fruiting bodies) visible. It starts on lower leaves and moves upward. The fungus overwinters in plant debris and spreads through water splash. Prevention: mulch around plants, stake tomatoes to keep leaves off ground, water at base, remove lower leaves, practice 2-3 year rotation, and apply fungicides preventively in wet weather.",
        
        "anthracnose": "Anthracnose causes dark, sunken lesions on leaves, stems, and fruits. On leaves, spots may have concentric rings. On fruits, it creates sunken, circular rotten spots. The fungus thrives in warm, wet conditions and spreads through rain splash and contaminated seeds. Prevention: use disease-free seeds, avoid overhead irrigation, harvest fruits before overripe, remove plant debris, rotate crops, and apply fungicides during flowering and fruit development.",
        
        "healthy": "Great news! Your plant appears healthy with no signs of disease. To maintain plant health: water consistently at the soil level, ensure proper spacing for air circulation, monitor regularly for early signs of problems, maintain balanced nutrition, practice crop rotation, and remove any dead or yellowing leaves promptly."
    }
    
    # Try to match disease name with database (case-insensitive partial match)
    disease_lower = disease_name.lower()
    for key, info in disease_info.items():
        if key in disease_lower or disease_lower in key:
            return info
    
    # Try Groq API if no match found and API key exists
    if GROQ_API_KEY:
        try:
            client = Groq(api_key=GROQ_API_KEY)
            
            prompt = f"""Provide a concise but informative explanation (2-3 short paragraphs) about the plant disease "{disease_name}".
            
Known symptoms: {', '.join(symptoms) if symptoms else 'Not specified'}
Possible causes: {', '.join(causes) if causes else 'Not specified'}

Cover:
1. What this disease is and how it damages plants
2. How it spreads and favorable conditions
3. Key prevention tips

Keep it simple and farmer-friendly. No markdown formatting."""
            
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=400,
            )
            
            return completion.choices[0].message.content
        except Exception:
            pass
    
    # Generate basic explanation from provided symptoms and causes
    if symptoms or causes:
        explanation = f"{disease_name} is a plant disease that requires attention. "
        if symptoms:
            explanation += f"Common symptoms include: {', '.join(symptoms)}. "
        if causes:
            explanation += f"This condition is typically caused by: {', '.join(causes)}. "
        explanation += "Monitor your plants closely, remove affected parts, ensure good air circulation, and consider applying appropriate treatments as recommended above."
        return explanation
    
    return None


def call_backend(image: Image.Image, filename: str, endpoint: str) -> Dict[str, Any]:
    """Send the leaf image to the FastAPI service and return its JSON payload."""
    payload = _optimize_image(image)
    files = {"file": (filename or "leaf.jpg", payload, "image/jpeg")}
    response = requests.post(
        f"{endpoint.rstrip('/')}/disease-detection-file",
        files=files,
        timeout=90,
    )
    response.raise_for_status()
    data = response.json()
    data["status"] = "Infected" if data.get("disease_detected") else "Healthy"
    data.setdefault("remedy", "See treatment recommendations below.")
    return data


def analyze_with_groq(image: Image.Image) -> Dict[str, Any]:
    """Analyze leaf image directly using Groq AI API."""
    import base64
    
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not set. Please add it to your .env file.")
    
    # Convert image to base64
    buffer = BytesIO()
    image.convert("RGB").save(buffer, format="JPEG", quality=85)
    base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")
    
    client = Groq(api_key=GROQ_API_KEY)
    
    prompt = """Analyze this leaf image for diseases. Return ONLY a valid JSON object with this exact structure:
{
    "disease_detected": true or false,
    "disease_name": "name of disease or null if healthy",
    "disease_type": "fungal/bacterial/viral/pest/nutrient deficiency/healthy",
    "severity": "mild/moderate/severe/none",
    "confidence": number between 0-100,
    "symptoms": ["list", "of", "observed", "symptoms"],
    "possible_causes": ["list", "of", "causes"],
    "treatment": ["list", "of", "treatment", "recommendations"]
}

If the image is not a plant leaf, set disease_type to "invalid_image"."""
    
    completion = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    }
                ]
            }
        ],
        temperature=0.3,
        max_tokens=1024,
    )
    
    # Parse the response
    import json
    import re
    
    response_text = completion.choices[0].message.content.strip()
    
    # Clean up response - remove markdown code blocks if present
    if response_text.startswith('```'):
        response_text = re.sub(r'^```json?\n?', '', response_text)
        response_text = re.sub(r'\n?```$', '', response_text)
    
    # Try to find JSON in response
    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
    if json_match:
        response_text = json_match.group()
    
    data = json.loads(response_text)
    data["status"] = "Infected" if data.get("disease_detected") else "Healthy"
    data["analysis_timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
    data["source"] = "Direct AI Analysis"
    
    return data


# -----------------------------------------------------------------------------
# 4. APP LAYOUT
# -----------------------------------------------------------------------------
if "result" not in st.session_state:
    st.session_state["result"] = None
    st.session_state["has_result"] = False

# Sidebar controls
with st.sidebar:
    st.title("🌿 FloraGuard AI")
    st.markdown("---")
    mode = st.radio("Detection Mode", ["Live API", "Direct AI"], index=0)
    if mode == "Live API":
        st.info("Using **deployed API** for analysis")
    else:
        st.info("Using **Groq AI directly** (requires API key)")

    st.write("### Settings")
    st.markdown("**AI Model:** Llama 4 Scout Vision")
    st.caption("Meta's multimodal model via Groq API")

    api_choice = st.selectbox(
        "API Endpoint",
        ["Production", "Local"],
        index=0 if BACKEND_URL == DEFAULT_API_URL else 1,
    )
    api_url = DEFAULT_API_URL if api_choice == "Production" else LOCAL_API_URL
    st.caption(f"Active endpoint: {api_url}")

    st.markdown("---")
    st.write("Developed by Abduulsamad Jamali, Shoaib Lashaari")

# Main Content
col1, col2 = st.columns([1, 1])

with col1:
    st.title("🌿 FloraGuard AI")
    st.write("Upload a leaf image to detect diseases instantly.")

    uploaded_file = st.file_uploader("Choose a leaf image...", type=["jpg", "png", "jpeg"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        if st.button("🔍 Analyze Leaf"):
            with st.spinner("Scanning leaf patterns..."):
                try:
                    if mode == "Live API":
                        result = call_backend(image, uploaded_file.name, api_url)
                    else:
                        result = analyze_with_groq(image)

                    st.session_state["result"] = result
                    st.session_state["has_result"] = True
                except requests.HTTPError as http_err:
                    st.error(
                        f"API error: {http_err.response.status_code} — {http_err.response.text}"
                    )
                    st.session_state["has_result"] = False
                except requests.RequestException as req_err:
                    st.error(f"Network issue: {req_err}")
                    st.session_state["has_result"] = False
                except Exception as exc:
                    st.error(f"Unexpected failure: {exc}")
                    st.session_state["has_result"] = False
    else:
        st.info("👆 Please upload an image to begin.")

with col2:
    st.write("")

    if st.session_state.get("has_result") and st.session_state.get("result"):
        res = st.session_state["result"]
        
        # Check if image is invalid (not a plant leaf)
        if res.get("disease_type") == "invalid_image":
            st.markdown(
                """
                <div style="padding: 24px; border-radius: 12px; background-color: #fef2f2;
                             border: 2px solid #fecaca; text-align: center;">
                    <p style="font-size: 48px; margin: 0;">⚠️</p>
                    <h2 style="color: #dc2626; margin: 10px 0;">Invalid Image</h2>
                    <p style="color: #991b1b; font-size: 1.1rem; margin-bottom: 0;">
                        This doesn't appear to be a plant leaf image.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            
            st.markdown("### 📋 What to do")
            st.warning("Please upload a clear image of a plant leaf for accurate disease detection.")
            
            st.markdown("### ✅ Tips for best results")
            tips = [
                "📸 Take a close-up photo of the leaf",
                "💡 Ensure good lighting (natural light works best)",
                "🎯 Focus on the affected area of the leaf",
                "🖼️ Avoid blurry or dark images",
                "🌿 Include only the leaf, not the whole plant"
            ]
            for tip in tips:
                st.markdown(
                    f"""
                    <div style="padding: 10px 14px; margin-bottom: 8px; border-radius: 8px;
                                background-color: #f0fdf4; border-left: 4px solid #22c55e; color: #166534;">
                        {tip}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            # Normal disease detection results
            status = res.get("status", "Healthy")
            status_color = "#166534" if status == "Healthy" else "#991b1b"
            bg_color = "#dcfce7" if status == "Healthy" else "#fee2e2"
            border_color = "#86efac" if status == "Healthy" else "#fca5a5"
            confidence = res.get("confidence", 0)

            st.markdown(
                f"""
                <div style="padding: 20px; border-radius: 10px; background-color: {bg_color};
                             border: 1px solid {border_color};">
                    <h2 style="color: {status_color}; margin:0;">{res.get('disease_name', 'Unknown')}</h2>
                    <p style="margin:5px 0 0 0; color: #374151;">Confidence: <strong>{confidence}%</strong></p>
                    <p style="margin:2px 0 0 0; color: #475569;">Severity: <strong>{res.get('severity', 'n/a')}</strong></p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # --- Symptoms Section ---
            symptoms = res.get("symptoms") or []
            if symptoms:
                st.markdown("### 🩺 Observed Symptoms")
                for symptom in symptoms:
                    st.markdown(
                        f"""
                        <div style="padding: 10px 14px; margin-bottom: 8px; border-radius: 8px;
                                    background-color: #fef3c7; border-left: 4px solid #f59e0b; color: #92400e;">
                            {symptom}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            # --- Possible Causes Section ---
            causes = res.get("possible_causes") or []
            if causes:
                st.markdown("### ❓ Why This Happens")
                for cause in causes:
                    st.markdown(
                        f"""
                        <div style="padding: 10px 14px; margin-bottom: 8px; border-radius: 8px;
                                    background-color: #e0e7ff; border-left: 4px solid #6366f1; color: #3730a3;">
                            {cause}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            # --- Treatment Section ---
            st.markdown("### 💊 Recommended Treatment")
            treatment = res.get("treatment") or [res.get("remedy", "No treatment data supplied.")]
            for tip in treatment:
                st.info(tip)

            # --- AI Disease Explanation Section ---
            disease_name = res.get("disease_name", "")
            if disease_name:
                st.markdown("### 📖 About This Disease")
                
                # Cache explanation in session state
                explanation_key = f"explanation_{disease_name}"
                
                if explanation_key not in st.session_state:
                    with st.spinner("Loading disease information..."):
                        explanation = get_disease_explanation(
                            disease_name,
                            res.get("symptoms", []),
                            res.get("possible_causes", [])
                        )
                        st.session_state[explanation_key] = explanation
                else:
                    explanation = st.session_state[explanation_key]
                
                if explanation:
                    st.markdown(
                        f"""
                        <div style="padding: 16px; border-radius: 10px; background-color: #ecfdf5;
                                    border: 1px solid #6ee7b7; color: #065f46; line-height: 1.7; font-size: 0.95rem;">
                            {explanation}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            st.markdown("### 📈 Analysis Details")
            st.progress(int(min(max(confidence, 0), 100)))

            with st.expander("View Technical Details"):
                st.json(
                    {
                        "Model": "Llama 4 Scout 17B Vision (Groq)",
                        "Mode": mode,
                        "API Endpoint": api_url if mode == "Live API" else "Direct Groq API",
                        "Disease Type": res.get("disease_type"),
                        "Analysis Timestamp": res.get("analysis_timestamp"),
                        "Source": res.get("source", "API"),
                    }
                )
    else:
        st.markdown(
            """
            <div style="text-align: center; color: #94a3b8; padding: 50px;">
                <p style="font-size: 40px; margin-bottom: 10px;">🍃</p>
                <p>Results will appear here after analysis.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

# -----------------------------------------------------------------------------
# 5. FOOTER
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #64748b; font-size: 0.8rem;">
        FloraGuard AI • Plant Disease Detector • Python 3.11 • Streamlit • FastAPI
        Contributers : Abduulsamad Jamali, Shoaib Lashaari
    </div>
    """,
    unsafe_allow_html=True,
)
