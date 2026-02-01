# TikTok Ads AI Agent 🤖

An intelligent, CLI-based agent designed to streamline the creation of TikTok Ad campaigns using Google Gemini AI for expert guidance and error handling.

## 🌟 Features

- **Intelligent Error Handling**: Uses Google Gemini Pro to translate complex OAuth and API errors into human-readable advice and actionable steps.
- **Rule-Based Validation**: Enforces TikTok business rules (e.g., character limits, mandatory music for Conversions) before submission.
- **Mock Integration**: Fully simulated TikTok Ads API and OAuth2 flow for risk-free testing and development.
- **Interactive CLI**: A user-friendly command-line interface with real-time feedback.
- **Expert Persona**: The agent adopts specific personas (OAuth Expert, Ads Expert) depending on the context of the interaction.

## 🛠️ Tech Stack

- **Python 3.10+**
- **Google Generative AI SDK**: Powering the intelligence layer with Gemini 1.5 Flash.
- **Pydantic/Schema Validation**: For robust internal data integrity.
- **Dotenv**: For secure environment variable management.

## 🚀 Getting Started

### Prerequisites

- Python installed on your machine.
- A **Google Gemini API Key** (get one at [Google AI Studio](https://aistudio.google.com/)).

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/tiktok-ads-ai-agent.git
   cd tiktok-ads-ai-agent
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

Create a `.env` file in the root directory and add your credentials:

```text
GOOGLE_API_KEY=your_gemini_api_key_here
TIKTOK_CLIENT_ID=test_client_id
TIKTOK_CLIENT_SECRET=test_client_secret
GEMINI_MODEL=models/gemini-flash-latest
```

### Usage

Run the agent:
```bash
python agent.py
```

## 📊 Logical Workflow

```mermaid
graph TD
    Start([Start Agent]) --> InitLLM[Initialize Gemini LLM]
    InitLLM --> Auth[Mock OAuth Authentication]
    
    Auth -- Failure --> LLM_Auth[Gemini Explains Auth Error]
    LLM_Auth --> End([Exit])
    
    Auth -- Success --> CollectData{Collect Input Data}
    
    CollectData --> Val_Name[Validate Campaign Name]
    Val_Name -- Valid --> Val_Obj[Validate Objective]
    
    Val_Obj -- Valid --> Val_Music{Objective == Conversions?}
    
    Val_Music -- Yes --> ReqMusic[Force Music Upload/Select]
    Val_Music -- No --> OptMusic[Optional Music]
    
    ReqMusic --> Submit[Submit to Mock API]
    OptMusic --> Submit
    
    Submit -- API Error --> LLM_Error[Gemini Explains API Error]
    LLM_Error -- Retryable? --> Retry{Retry?}
    Retry -- Yes --> CollectData
    
    Submit -- Success --> LLM_Summary[Gemini Summarizes Payload]
    LLM_Summary --> Display[Display Final JSON]
    Display --> End
```

## 🧪 Testing Scenarios

Try these inputs to see the AI agent in action:
- **Validation**: Enter a 1-character campaign name to trigger local validation.
- **Geo-Block**: Name your campaign "India Promo" to see the AI explain a simulated regional restriction.
- **Music Requirement**: Choose "Conversions" and try to skip music to see the business rule enforcement.
