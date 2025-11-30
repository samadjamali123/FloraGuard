# 🌿 FloraGuard AI - Plant Disease Detection System

An AI-powered plant disease detection system featuring a dual-interface architecture: a FastAPI backend service and an interactive Streamlit web application. Built with Meta's Llama 4 Scout Vision model via Groq API, this system provides disease identification, severity assessment, and treatment recommendations.

## 🎯 Key Features

- **🔍 Disease Detection**: Identifies plant diseases across multiple categories (fungal, bacterial, viral, pest-related, nutrient deficiencies)
- **📊 Severity Assessment**: Classification of disease severity levels (mild, moderate, severe)
- **📈 Confidence Scoring**: Provides confidence percentages (0-100%)
- **💡 Treatment Recommendations**: Actionable treatment protocols tailored to specific diseases
- **📋 Symptom Analysis**: Visual symptom identification with possible causes
- **🖼️ Image Validation**: Automatically detects and rejects non-plant images
- **📖 Disease Information**: Built-in disease database with detailed explanations

## 🏗️ Project Structure

```
Plant Disease Analyzer/
├── main.py                    # Streamlit Web Application (FloraGuard AI)
├── app.py                     # FastAPI Backend Service
├── utils.py                   # Utility functions & cached detector
├── test_api.py               # API testing script
├── requirements.txt          # Python dependencies
├── Leaf Disease/
│   ├── main.py               # Core LeafDiseaseDetector class
│   └── config.py             # Application configuration
└── Media/                    # Sample test images
    └── brown-spot-4 (1).jpg
```

### Components

| File | Description |
|------|-------------|
| `main.py` | Streamlit web app with modern UI, dual detection modes (Live API & Direct AI), disease explanations |
| `app.py` | FastAPI REST API with file upload endpoint, validation, and JSON responses |
| `utils.py` | Cached `LeafDiseaseDetector` instance, image-to-base64 conversion utilities |
| `Leaf Disease/main.py` | Core AI engine with `LeafDiseaseDetector` class and `DiseaseAnalysisResult` dataclass |
| `Leaf Disease/config.py` | `AppConfig` dataclass for centralized configuration management |
| `test_api.py` | Test script for API endpoints |

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- [Groq API Key](https://console.groq.com/)

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd "Plant Disease Analyzer"
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   # or
   .venv\Scripts\activate     # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   
   Create a `.env` file in the project root:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

### Running the Application

#### Option A: Streamlit Web Interface
```bash
streamlit run main.py --server.port 8501 --server.address 0.0.0.0
```
Access at: http://localhost:8501

#### Option B: FastAPI Backend
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

#### Option C: Both Services
```bash
# Terminal 1
uvicorn app:app --reload --port 8000

# Terminal 2
streamlit run main.py --server.port 8501
```

## 📡 API Reference

### FastAPI Endpoints

#### `GET /`
Root endpoint with API information.

**Response:**
```json
{
  "message": "Leaf Disease Detection API",
  "version": "1.0.0",
  "endpoints": {
    "disease_detection_file": "/disease-detection-file (POST, file upload)"
  }
}
```

#### `POST /disease-detection-file`
Upload an image for disease analysis.

**Request:**
- Content-Type: `multipart/form-data`
- Body: Image file (JPEG, PNG, WebP)
- Max Size: 10MB

**Response:**
```json
{
  "disease_detected": true,
  "disease_name": "Brown Spot Disease",
  "disease_type": "fungal",
  "severity": "moderate",
  "confidence": 87.3,
  "symptoms": ["Circular brown spots", "Yellow halos around lesions"],
  "possible_causes": ["High humidity", "Poor air circulation"],
  "treatment": ["Apply copper-based fungicide", "Remove affected leaves"],
  "analysis_timestamp": "2024-01-15T10:30:00+00:00"
}
```

**Invalid Image Response:**
```json
{
  "disease_detected": false,
  "disease_name": null,
  "disease_type": "invalid_image",
  "severity": "none",
  "confidence": 95,
  "symptoms": ["This image does not contain a plant leaf"],
  "possible_causes": ["Invalid image type uploaded"],
  "treatment": ["Please upload an image of a plant leaf for disease analysis"]
}
```

### Streamlit Features

The web interface offers two detection modes:

1. **Live API Mode**: Uses the deployed FastAPI backend
2. **Direct AI Mode**: Calls Groq API directly from the browser

Features include:
- Drag-and-drop image upload
- Real-time analysis with progress indicators
- Disease explanation with causes and prevention tips
- Technical details view
- Invalid image detection and user guidance

## 🧪 Testing

### Run API Tests
```bash
# Start the API server first
uvicorn app:app --reload --port 8000

# In another terminal
python test_api.py
```

### Test with cURL
```bash
curl -X POST "http://localhost:8000/disease-detection-file" \
  -H "accept: application/json" \
  -F "file=@Media/brown-spot-4 (1).jpg"
```

### Test Core Detection Engine
```bash
python "Leaf Disease/main.py"
```

### Test Utilities
```bash
python utils.py
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GROQ_API_KEY` | Groq API key | ✅ Yes | - |
| `LEAF_API_URL` | Backend API URL | No | `http://leaf-diseases-detect.vercel.app` |
| `MODEL_NAME` | AI model identifier | No | `meta-llama/llama-4-scout-17b-16e-instruct` |
| `MODEL_TEMPERATURE` | Response creativity (0.0-2.0) | No | `0.3` |
| `MAX_COMPLETION_TOKENS` | Max response tokens | No | `1024` |
| `MAX_UPLOAD_BYTES` | Max file upload size | No | `10485760` (10MB) |
| `LOG_LEVEL` | Logging level | No | `INFO` |

### Supported Image Formats
- JPEG/JPG
- PNG
- WebP
- BMP
- TIFF

## 🔬 Technical Details

### AI Model
- **Model**: Meta Llama 4 Scout 17B Vision Instruct
- **Provider**: Groq API
- **Temperature**: 0.3 (factual, consistent responses)
- **Max Tokens**: 1024

### Disease Categories Detected
- **Fungal**: Leaf spot, blight, rust, mildew, anthracnose
- **Bacterial**: Bacterial spot, wilt, canker
- **Viral**: Mosaic virus, leaf curl, yellowing
- **Pest-related**: Insect damage, mite infestations
- **Nutrient deficiency**: N, P, K, and micronutrient deficiencies
- **Healthy**: Confirms healthy plant leaves

### Built-in Disease Database
The system includes explanations for common diseases:
- Early Blight
- Late Blight
- Powdery Mildew
- Leaf Spot
- Rust
- Bacterial Spot
- Mosaic Virus
- Brown Spot
- Septoria
- Anthracnose

## 📦 Dependencies

```
groq>=0.31.0
python-dotenv>=1.0.0
typing-extensions>=4.8.0
fastapi>=0.116.1
uvicorn[standard]>=0.21.1
python-multipart>=0.0.6
requests>=2.31.0
streamlit>=1.20.0
Pillow>=10.0.0
```

## 🚀 Deployment

### Production API URL
The default production API is deployed at:
```
http://leaf-diseases-detect.vercel.app
```

### Deploy to Vercel
1. Push code to GitHub
2. Connect to Vercel
3. Add environment variable: `GROQ_API_KEY`

### Deploy to Streamlit Cloud
1. Push code to GitHub
2. Connect to [share.streamlit.io](https://share.streamlit.io/)
3. Add `GROQ_API_KEY` in Secrets

## 👥 Contributors

- Abduulsamad Jamali
- Shoaib Lashaari

## 📚 Resources

- [Groq API Documentation](https://console.groq.com/docs)
- [Meta Llama Models](https://ai.meta.com/llama/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
