# event-planner-llm
event-planner-llm/
├── main.py                   
├── requirements.txt          
├── .env                      
├── .streamlit/               
│   └── secrets.toml          
├── assets/                   
│   └── logo.png              
└── utils/                    
    └── image_processing.py   

How to Run the Application-
Prerequisites:
Before starting, make sure you have the following environment variables configured:

OPENROUTER_API_KEY - Your API key from OpenRouter

Note: Ensure your OpenRouter account has a positive credit balance or is using :free models.

Step 1: Initial Setup
Navigate to the project directory:

Bash

cd event-planner-llm
Create and activate a virtual environment:

PowerShell


python -m venv MACS
. .\MACS\Scripts\Activate.ps1
Install dependencies:

Bash

pip install -r requirements.txt
Step 2: Running Locally
Start the Streamlit development server:

Bash

streamlit run main.py
Open the web application:

The app will be available at: http://localhost:8501

Features
Multi-Modal Poster Parsing
Vision AI: Uses Qwen 2.5 VL or Gemini 3 Flash to "see" and interpret event posters.

Auto-Extraction: Instantly identifies Event Name, Date, Venue, and Pricing without manual entry.

Cloud Ready
Secrets Management: Fully integrated with Streamlit Cloud's encrypted secrets.

Optimized for Free Tier: Lightweight architecture that runs within the 1GB RAM limit.

Technical Architecture
Logic Flow
Input: User uploads a .jpg or .png event poster.

Processing: The image is converted to base64 and sent via LangChain to OpenRouter.

Inference: The LLM (Qwen/Mistral/Gemini) performs OCR and semantic analysis.

Output: Structured event details are displayed in a clean Markdown format.

API Configuration
For deployment, configure your secrets.toml as follows:

Ini, TOML

OPENROUTER_API_KEY = "sk-or-v1-your-key-here"
