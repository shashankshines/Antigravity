import streamlit as st
from streamlit_quill import st_quill
from email_agent import EmailAgent
import os

st.set_page_config(page_title="AI Email Agent", page_icon="email_icon.png")

# Sidebar Settings
with st.sidebar:
    st.image("email_icon.png", width=100)
    st.header("⚙️ Settings")
    
    # --- PERSISTENCE LOGIC ---
    # Ensure critical keys are initialized in session state from query params
    # This prevents data loss on refresh or mode switching
    keys_to_persist = ["api_key", "mode", "signature", "smtp_server", "smtp_port", "smtp_email", "to_email"]
    
    for key in keys_to_persist:
        if key not in st.session_state and key in st.query_params:
            try:
                if key == "smtp_port":
                    st.session_state[key] = int(st.query_params[key])
                else:
                    st.session_state[key] = st.query_params[key]
            except:
                pass # Fallback to default if conversion fails

    # Helper to get value from Session State -> Query Param -> Default
    def get_persisted_value(key, default=""):
        # If in session state (user just edited or we restored it), use that
        if key in st.session_state:
            return st.session_state[key]
        return default

    # API Key
    api_key_val = get_persisted_value("api_key", os.getenv("GEMINI_API_KEY", ""))
    api_key = st.text_input("Gemini API Key", type="password", value=api_key_val, key="api_key")
    if not api_key:
        st.warning("Please enter your Gemini API Key.")
    
    st.divider()
    
    # Email Mode
    mode_val = get_persisted_value("mode", "Mock (Safe)")
    mode_index = 0
    if mode_val == "Real SMTP":
        mode_index = 1
    
    mode = st.radio("Sending Mode", ["Mock (Safe)", "Real SMTP"], index=mode_index, key="mode")
    mock_mode = (mode == "Mock (Safe)")
    
    # Signature
    st.divider()
    st.subheader("✍️ Signature")
    
    sig_val = get_persisted_value("signature", "Best regards,\n[Your Name]")
    signature = st.text_area("Email Signature", value=sig_val, height=100, key="signature")
    
    # Initialize SMTP variables to defaults to avoid NameError if mock_mode is True
    smtp_server = ""
    smtp_port = 587
    smtp_email = ""
    
    smtp_settings = {}
    if not mock_mode:
        st.subheader("SMTP Configuration")
        
        # SMTP Defaults
        srv_val = get_persisted_value("smtp_server", "smtp.gmail.com")
        port_val = int(get_persisted_value("smtp_port", 587))
        email_val = get_persisted_value("smtp_email", "")
        
        smtp_server = st.text_input("SMTP Server", value=srv_val, key="smtp_server")
        smtp_port = st.number_input("SMTP Port", value=port_val, key="smtp_port")
        smtp_email = st.text_input("Sender Email", value=email_val, key="smtp_email")
        smtp_password = st.text_input("App Password", type="password", key="smtp_password") # Never persist password
        
        # Sanitize inputs
        if smtp_server: smtp_server = smtp_server.strip().replace('\xa0', '')
        if smtp_email: smtp_email = smtp_email.strip().replace('\xa0', '')
        if smtp_password: smtp_password = smtp_password.strip().replace('\xa0', '')
        
        if smtp_server and smtp_port and smtp_email and smtp_password:
            smtp_settings = {
                "server": smtp_server,
                "port": int(smtp_port),
                "email": smtp_email,
                "password": smtp_password
            }
            
            if st.button("🔌 Test Connection"):
                with st.spinner("Testing SMTP Connection..."):
                    try:
                        import smtplib
                        server = smtplib.SMTP(smtp_settings['server'], smtp_settings['port'])
                        server.starttls()
                        server.login(smtp_settings['email'], smtp_settings['password'])
                        server.quit()
                        st.success("✅ Connected successfully!")
                    except Exception as e:
                        st.error(f"❌ Connection failed: {e}")
        else:
            st.warning("Please fill all SMTP details.")

    # Update Query Params (Sync state to URL)
    # This ensures that whenever any input changes (triggering rerun), the URL is updated
    st.query_params["api_key"] = api_key
    st.query_params["mode"] = mode
    st.query_params["signature"] = signature
    if not mock_mode:
        st.query_params["smtp_server"] = smtp_server
        st.query_params["smtp_port"] = str(smtp_port)
        st.query_params["smtp_email"] = smtp_email

# Initialize Agent
# Initialize Agent
if api_key:
    # Re-initialize if key changes or first run
    # We check against the widget values directly
    if 'agent' not in st.session_state or st.session_state.get('last_api_key') != api_key or st.session_state.get('last_mock_mode') != mock_mode:
        st.session_state.agent = EmailAgent(api_key=api_key, mock_mode=mock_mode)
        st.session_state.last_api_key = api_key
        st.session_state.last_mock_mode = mock_mode
elif 'agent' not in st.session_state:
     st.session_state.agent = EmailAgent(mock_mode=True) # Fallback

col1, col2 = st.columns([1, 5])
with col1:
    st.image("email_icon.png", width=80)
with col2:
    st.title("Email AI Agent - Developed by Lakhotia Labs")

st.markdown("Generate and send professional emails with AI.")

# Input Section
with st.container():
    st.subheader("Email Details")
    to_val = get_persisted_value("to_email", "")
    to_email = st.text_input("Recipient Email", value=to_val, placeholder="e.g., boss@company.com", key="to_email")
    
    # Sync to_email to query params
    st.query_params["to_email"] = to_email
    
    # Subject Templates
    templates = {
        "Custom": "",
        "Job Application": "Application for [Position] - [Your Name]",
        "Follow Up": "Following up on [Topic]",
        "Meeting Request": "Request for Meeting: [Topic]",
        "Invoice": "Invoice #[Number] for [Service]",
        "Sick Leave": "Sick Leave Application - [Date]"
    }
    
    col_temp, col_subj = st.columns([1, 2])
    with col_temp:
        selected_template = st.selectbox("Quick Templates", list(templates.keys()))
    
    # Determine default subject value
    default_subject = ""
    if selected_template != "Custom":
        default_subject = templates[selected_template]
    
    with col_subj:
        # We use a key based on template to force update if template changes, 
        # but we also want to allow manual editing.
        # Streamlit trick: use session state to manage the value
        if "subject_val" not in st.session_state:
            st.session_state.subject_val = ""
        
        if selected_template != "Custom" and st.session_state.get("last_template") != selected_template:
            st.session_state.subject_val = templates[selected_template]
            st.session_state.last_template = selected_template
            
        subject = st.text_input("Subject", value=st.session_state.subject_val, key="subject_input")
        # Sync back to session state for manual edits
        st.session_state.subject_val = subject

    # Subject Optimization / Reverse Flow
    if st.button("✨ Optimize / Generate Subject from Content"):
        # Check if there is edited content in the quill editor first
        content_to_optimize = st.session_state.get("quill_editor") or st.session_state.get("generated_email")
        
        if content_to_optimize:
            # Generate from existing body (edited or original)
            with st.spinner("Analyzing content..."):
                # Quill returns HTML, we might want to strip tags for better context analysis, 
                # but Gemini handles HTML reasonably well.
                new_subject = st.session_state.agent.optimize_subject(content_to_optimize)
                st.session_state.subject_val = new_subject
                st.rerun()
        elif subject:
             # Optimize existing subject
             with st.spinner("Optimizing subject..."):
                new_subject = st.session_state.agent.optimize_subject(subject)
                st.session_state.subject_val = new_subject
                st.rerun()
        else:
            st.warning("Please enter some content in the Body or a rough Subject first.")

    # Attachments
    uploaded_files = st.file_uploader("Attachments (Max 10MB per file)", accept_multiple_files=True)
    valid_attachments = []
    if uploaded_files:
        for file in uploaded_files:
            if file.size > 10 * 1024 * 1024: # 10MB
                st.error(f"File {file.name} is too large (>10MB).")
            else:
                valid_attachments.append(file)

# Generation Section
if st.button("⚡ Generate Email Body"):
    if not subject:
        st.warning("Please enter a subject first.")
    elif not api_key:
        st.error("Please enter a Gemini API Key in the sidebar.")
    else:
        with st.spinner("Drafting your email..."):
            # Get list of file names
            attachment_names = [f.name for f in valid_attachments] if valid_attachments else []
            
            email_body = st.session_state.agent.generate_email(subject, attachment_names)
            
            # Append Signature
            if signature:
                email_body += f"\n\n{signature}"
            
            # Format for HTML Editor (Quill)
            import re
            # Bold placeholders (e.g., [Date] -> <b>[Date]</b>)
            email_body = re.sub(r'(\[.*?\])', r'<b>\1</b>', email_body)
            # Convert newlines to HTML breaks so structure is preserved in the editor
            email_body = email_body.replace("\n", "<br>")
                
            st.session_state.generated_email = email_body

# Display & Send Section
if 'generated_email' in st.session_state:
    st.subheader("Review & Send")
    
    # Show validation errors if they exist from a previous run
    if 'validation_error' in st.session_state and st.session_state.validation_error:
        st.warning(st.session_state.validation_error)
        st.error("Please fill in the missing details in the editor below before sending.")
        # Clear error after showing it once
        del st.session_state.validation_error
    
    # Allow user to edit the generated email using WYSIWYG editor
    final_body = st_quill(
        value=st.session_state.generated_email,
        html=True,
        key="quill_editor",
        placeholder="Write your email here..."
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        send_clicked = st.button("📨 Send Email", key="send_email_btn")
    
    if send_clicked:
        print("DEBUG: Send button clicked")
        if not to_email:
            st.toast("❌ Recipient email is missing!", icon="❌")
            st.error("Please specify a recipient email.")
        else:
            # 1. Validate Subject for Placeholders
            import re
            subject_placeholders = re.findall(r'\[(.*?)\]', subject)
            if subject_placeholders:
                st.toast("⚠️ Subject line contains placeholders!", icon="⚠️")
                st.warning(f"⚠️ Subject line contains placeholders: {', '.join(['['+p+']' for p in subject_placeholders])}")
                st.error("Please optimize the subject line or fill in the details before sending.")
                st.stop() # Stop execution here

            # 2. Validate Body for Placeholders
            missing_placeholders = st.session_state.agent.validate_email(final_body)
            
            if missing_placeholders:
                st.toast("⚠️ Missing information in email body!", icon="⚠️")
                
                # Store error in session state so it survives the rerun
                st.session_state.validation_error = f"⚠️ Missing Information Detected in Body: {', '.join(missing_placeholders)}"
                
                # Highlight placeholders in the editor
                highlighted_body = final_body
                for placeholder in missing_placeholders:
                    # Simple replacement to highlight
                    highlighted_body = highlighted_body.replace(
                        placeholder, 
                        f'<span style="background-color: #ffcccc; color: red; font-weight: bold;">{placeholder}</span>'
                    )
                
                st.session_state.generated_email = highlighted_body
                st.rerun()

            else:
                # 3. Aggressive HTML Cleanup
                cleaned_body = final_body.replace("<p><br></p>", "<br>")
                cleaned_body = cleaned_body.replace("<p></p>", "")
                cleaned_body = re.sub(r'<p.*?>', '', cleaned_body)
                cleaned_body = cleaned_body.replace('</p>', '<br>')
                cleaned_body = re.sub(r'(<br>\s*){2,}', '<br><br>', cleaned_body)
                cleaned_body = cleaned_body.strip()
                if cleaned_body.startswith("<br>"): cleaned_body = cleaned_body[4:]
                if cleaned_body.endswith("<br>"): cleaned_body = cleaned_body[:-4]

                styled_body = f"""
                <div style="font-family: 'Calibri', 'Arial', sans-serif; font-size: 11pt; color: #000000;">
                    {cleaned_body}
                </div>
                """
                
                # INITIATE COUNTDOWN
                import time
                st.session_state.final_body_to_send = styled_body
                st.session_state.sending_phase = 'countdown'
                st.session_state.countdown_start = time.time()
                st.rerun()

    # --- HANDLE COUNTDOWN & SENDING ---
    if st.session_state.get('sending_phase') == 'countdown':
        import time
        elapsed = time.time() - st.session_state.countdown_start
        remaining = 10 - int(elapsed)
        
        if remaining <= 0:
            # TIME UP - SEND EMAIL
            st.session_state.sending_phase = 'sending' # Transition to sending
            st.rerun()
        else:
            # SHOW COUNTDOWN
            st.info(f"⏳ Sending email in {remaining} seconds...")
            progress = min(elapsed / 10.0, 1.0)
            st.progress(progress)
            
            col_undo, col_dummy = st.columns([1, 4])
            with col_undo:
                if st.button("↩️ Undo Send", key="undo_btn"):
                    st.session_state.sending_phase = 'cancelled'
                    st.toast("🛑 Sending cancelled!", icon="🛑")
                    st.rerun()
            
            time.sleep(1)
            st.rerun()

    elif st.session_state.get('sending_phase') == 'sending':
        # ACTUAL SEND LOGIC
        styled_body = st.session_state.get('final_body_to_send', "")
        
        status_placeholder = st.empty()
        success = False
        
        try:
            with status_placeholder.status("Making sure to attach files...", expanded=True) as status:
                if valid_attachments:
                    for file in valid_attachments:
                        st.write(f"🔄 Attaching {file.name}...")
                
                st.write("Sending email...")
                success = st.session_state.agent.send_email(to_email, subject, styled_body, smtp_settings, valid_attachments)
                
                if success:
                    status.update(label="Email Sent!", state="complete", expanded=False)
                else:
                    status.update(label="Failed to send", state="error", expanded=True)
        except Exception as e:
            st.error(f"An error occurred: {e}")
            success = False
        
        if success:
            status_placeholder.empty()
            st.toast("✅ Email sent successfully!", icon="✅")
            st.success(f"Email sent to {to_email}!")
            if st.session_state.agent.mock_mode:
                st.info("Mock Mode: Email printed to console/logs.")
        else:
            st.toast("❌ Failed to send email.", icon="❌")
            st.error("Failed to send email. Check your SMTP settings.")
        
        # Reset phase
        st.session_state.sending_phase = None
        
    elif st.session_state.get('sending_phase') == 'cancelled':
        st.warning("Sending was cancelled.")
        st.session_state.sending_phase = None
