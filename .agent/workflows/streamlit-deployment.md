---
description: Deploy updates to Streamlit Cloud
---

# Streamlit Cloud Deployment Plan

## Overview
This workflow guides you through deploying the latest changes to Streamlit Cloud after pushing code to GitLab.

## Prerequisites
- Code changes pushed to GitLab repository
- Streamlit Cloud account connected to your GitLab repository
- Repository: https://gitlab.com/shashankshines/antigravity

## Deployment Steps

### Option 1: Automatic Deployment (Recommended)
If you have automatic deployment enabled in Streamlit Cloud:

1. **Verify Push Completed**
   - Confirm that `git push` was successful
   - Check GitLab repository to ensure latest commit is visible
   - Latest commit: "Disable quick templates section - simplified subject input"

2. **Wait for Auto-Deploy**
   - Streamlit Cloud automatically detects changes in connected repositories
   - Deployment typically takes 2-5 minutes
   - You'll receive an email notification when deployment completes

3. **Verify Deployment**
   - Visit your Streamlit app URL
   - Check that the Quick Templates dropdown is no longer visible
   - Verify the subject input is now a single text field
   - Test the app functionality

### Option 2: Manual Deployment
If automatic deployment is not enabled or you need to force a redeploy:

1. **Access Streamlit Cloud Dashboard**
   - Go to https://share.streamlit.io/
   - Sign in with your account

2. **Locate Your App**
   - Find "AntiGravity" or "AI Email Agent" in your apps list
   - Click on the app to open its settings

3. **Trigger Reboot**
   - Click the "⋮" (three dots) menu
   - Select "Reboot app"
   - This will pull the latest code from GitLab and restart the app

4. **Monitor Deployment**
   - Watch the deployment logs in the Streamlit Cloud interface
   - Look for any errors or warnings
   - Wait for "App is running" status

5. **Verify Deployment**
   - Click "Open app" to view your deployed application
   - Confirm the Quick Templates section is disabled
   - Test all functionality

## Post-Deployment Verification Checklist

- [ ] App loads without errors
- [ ] Quick Templates dropdown is removed
- [ ] Subject input field is visible and functional
- [ ] Email generation works correctly
- [ ] SMTP settings persist correctly
- [ ] Theme switcher (Light/Dark) works
- [ ] File attachments work
- [ ] Send email functionality works
- [ ] Undo send feature works

## Troubleshooting

### App Won't Start
- Check Streamlit Cloud logs for Python errors
- Verify all dependencies in `requirements.txt` are available
- Check if any environment variables are missing

### Changes Not Visible
- Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)
- Verify the correct branch is deployed (should be `master`)
- Check GitLab to confirm latest commit is present

### Deployment Fails
- Review error logs in Streamlit Cloud dashboard
- Check for any breaking changes in dependencies
- Verify `streamlit_quill` and other packages are properly installed

## Environment Variables to Check

If using Streamlit Cloud secrets, ensure these are configured:

```toml
# .streamlit/secrets.toml (on Streamlit Cloud)
GEMINI_API_KEY = "your-api-key-here"
```

## Rollback Plan

If the deployment causes issues:

1. **Revert Git Commit**
   ```bash
   git revert HEAD
   git push origin master
   ```

2. **Or Deploy Previous Commit**
   - In Streamlit Cloud, you can specify a different commit hash
   - Go to app settings → Advanced settings
   - Specify the previous working commit

## Notes

- Current repository: https://gitlab.com/shashankshines/antigravity
- Branch: master
- Latest change: Removed Quick Templates section for cleaner UX
- Files modified: `app.py`

## Support Resources

- Streamlit Cloud Docs: https://docs.streamlit.io/streamlit-community-cloud
- Streamlit Forum: https://discuss.streamlit.io/
- Your GitLab Repo: https://gitlab.com/shashankshines/antigravity
