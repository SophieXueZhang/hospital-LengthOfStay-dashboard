# Streamlit Cloud Deployment Guide

## Setting up Secrets in Streamlit Cloud

To enable the RAG system on Streamlit Cloud, you need to configure the OpenAI API key:

1. Go to your Streamlit Cloud dashboard
2. Click on your app settings (gear icon)
3. Navigate to "Secrets" tab
4. Add the following configuration:

```toml
OPENAI_API_KEY = "sk-your-actual-openai-api-key-here"
```

5. Save the configuration
6. The app will automatically restart and the RAG system will be enabled

## Features Available After Configuration

- ✅ Paper-based medical insights
- 🔍 Evidence-based clinical analysis
- 💬 AI-powered patient consultation
- 📚 Medical literature search and recommendations

## Database

The app uses a lightweight SQLite database (8KB) containing sample medical papers covering:
- Anemia and length of stay
- Pneumonia treatment outcomes
- Asthma hospitalization patterns
- Diabetes complications
- Kidney disease management

## Troubleshooting

If you see "Basic AI assistant available (paper database not loaded)":
1. Check that the OPENAI_API_KEY is correctly set in Streamlit Cloud secrets
2. Verify the API key is valid and has sufficient credits
3. Wait 2-3 minutes for the app to restart after configuration changes