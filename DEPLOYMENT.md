# Streamlit Cloud Deployment Guide

## Prerequisites
✅ Your code is already pushed to GitHub: https://github.com/shashankshines/Antigravity.git

## Step-by-Step Deployment Instructions

### 1. Access Streamlit Cloud
- Go to [share.streamlit.io](https://share.streamlit.io)
- Sign in with your GitHub account (@shashankshines)

### 2. Deploy New App
- Click **"New app"** button
- Fill in the deployment form:
  - **Repository**: `shashankshines/Antigravity`
  - **Branch**: `master`
  - **Main file path**: `app.py`
  - **App URL** (optional): Choose a custom subdomain or use the auto-generated one

### 3. Configure Secrets
Before deploying, you need to add your API key:
- Click on **"Advanced settings"**
- In the **"Secrets"** section, add:
  ```toml
  GOOGLE_API_KEY = "your-actual-google-api-key"
  ```
- Replace `your-actual-google-api-key` with your real Google Gemini API key

### 4. Deploy
- Click **"Deploy!"**
- Streamlit Cloud will:
  - Clone your repository
  - Install dependencies from `requirements.txt`
  - Start your app
  - Provide you with a public URL

### 5. Post-Deployment Configuration
Once deployed, users will need to configure in the app's sidebar:
- **Google API Key** (if not using secrets)
- **SMTP Settings** for email sending:
  - SMTP Server
  - SMTP Port
  - Email Address
  - Email Password
- **Email Signature** (optional)

## Important Notes

### Security
- ⚠️ **Never commit API keys or passwords to git**
- Use Streamlit secrets for the Google API key
- SMTP credentials are configured per-user in the app UI

### App Features
Your AI Email Agent includes:
- AI-powered email composition using Google Gemini
- Smart subject line generation
- Professional/Personal tone adaptation
- Email signature support
- Undo send functionality (10-second window)
- Light/Dark theme support
- Modern macOS-inspired UI

### Monitoring
- Access your app dashboard at share.streamlit.io
- View logs, metrics, and manage deployments
- Update your app by pushing to GitHub (auto-deploys)

### Troubleshooting
If deployment fails:
1. Check the logs in Streamlit Cloud dashboard
2. Verify all dependencies in `requirements.txt` are correct
3. Ensure `GOOGLE_API_KEY` is set in secrets
4. Check that `app.py` runs locally without errors

## Repository Information
- **GitHub**: https://github.com/shashankshines/Antigravity.git
- **GitLab**: https://gitlab.com/shashankshines/antigravity.git
- **Main File**: app.py
- **Python Dependencies**: See requirements.txt

## Next Steps After Deployment
1. Test the deployed app with your Google API key
2. Share the public URL with users
3. Monitor usage and logs
4. Update code by pushing to GitHub (auto-redeploys)

---
**Deployment Date**: 2025-11-25
**Status**: Ready to Deploy ✅
