import streamlit as st
from streamlit_quill import st_quill
import sys
if sys.version_info < (3, 10):
    try:
        import importlib_metadata
        import importlib.metadata
        if not hasattr(importlib.metadata, 'packages_distributions'):
            importlib.metadata.packages_distributions = importlib_metadata.packages_distributions
    except ImportError:
        pass
from email_agent import EmailAgent
import os


st.set_page_config(page_title="AI Email Agent", page_icon="favicon.png", layout="wide")

# --- PERSISTENCE LOGIC ---
if "keys_to_persist" not in st.session_state:
    st.session_state.keys_to_persist = ["api_key", "mode", "signature", "smtp_server", "smtp_port", "smtp_email", "to_email", "theme"]

for key in st.session_state.keys_to_persist:
    if key not in st.session_state and key in st.query_params:
        try:
            if key == "smtp_port":
                st.session_state[key] = int(st.query_params[key])
            else:
                st.session_state[key] = st.query_params[key]
        except:
            pass

def get_persisted_value(key, default=""):
    if key in st.session_state:
        return st.session_state[key]
    return default

# --- THEME SELECTION ---
with st.sidebar:
    st.image("logo.png", width=140)
    st.header("⚙️ Settings")
    
    theme_val = get_persisted_value("theme", "Light")
    theme_index = 0 if theme_val == "Light" else 1
    theme = st.radio("Theme", ["Light", "Dark"], index=theme_index, horizontal=True, key="theme")
    st.query_params["theme"] = theme

# --- DYNAMIC CSS ---
if theme == "Dark":
    css_vars = """
        --bg-color: #1c1c1e;
        --sidebar-bg: #2c2c2e;
        --text-color: #f5f5f7;
        --accent-color: #0a84ff;
        --border-color: #3a3a3c;
        --input-bg: #1c1c1e;
        --button-bg: #3a3a3c;
        --button-border: #48484a;
        --button-hover: #48484a;
        --shadow-sm: 0 1px 2px rgba(0,0,0,0.5);
        --shadow-md: 0 4px 6px rgba(0,0,0,0.3);
    """
else:
    css_vars = """
        --bg-color: #ffffff;
        --sidebar-bg: #f5f5f7;
        --text-color: #1d1d1f;
        --accent-color: #007aff;
        --border-color: #d2d2d7;
        --input-bg: #ffffff;
        --button-bg: #ffffff;
        --button-border: #d2d2d7;
        --button-hover: #f5f5f7;
        --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
        --shadow-md: 0 4px 6px rgba(0,0,0,0.05);
    """

st.markdown(f"""
<style>
    /* Global Variables */
    :root {{
        {css_vars}
    }}

    /* Import Roboto Font */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

    /* Main Background */
    .stApp {{
        background-color: var(--bg-color);
        color: var(--text-color);
        font-family: 'Roboto', sans-serif;
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: var(--sidebar-bg);
        border-right: 1px solid var(--border-color);
    }}
    
    [data-testid="stSidebar"] label {{
        color: var(--text-color) !important;
    }}
    
    [data-testid="stSidebar"] p {{
        color: var(--text-color) !important;
    }}
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {{
        color: var(--text-color) !important;
    }}
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Roboto', sans-serif !important;
        font-weight: 600 !important;
        color: var(--text-color) !important;
        letter-spacing: -0.01em;
    }}
    
    /* Elegant Title Size */
    h1 {{
        font-size: 2.0rem !important;
    }}
    
    p, label {{
        font-family: 'Roboto', sans-serif;
        color: var(--text-color);
    }}
    
    /* Rounded Images */
    img {{
        border-radius: 12px;
    }}

    /* Inputs (Text Input, Text Area, Selectbox) */
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea, 
    .stSelectbox > div > div > div {{
        background-color: var(--input-bg) !important;
        color: var(--text-color) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 6px !important;
        box-shadow: var(--shadow-sm);
        transition: all 0.2s ease;
    }}

    .stTextInput > div > div > input:focus, 
    .stTextArea > div > div > textarea:focus {{
        border-color: var(--accent-color) !important;
        box-shadow: 0 0 0 3px rgba(0,122,255,0.2) !important;
    }}

    /* Selectbox Dropdown Menu */
    [data-baseweb="popover"] {{
        background-color: var(--input-bg) !important;
    }}
    
    [data-baseweb="menu"] {{
        background-color: var(--input-bg) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 6px !important;
        box-shadow: var(--shadow-md) !important;
    }}
    
    [data-baseweb="menu"] ul {{
        background-color: var(--input-bg) !important;
    }}
    
    /* Selectbox Options */
    [role="option"] {{
        background-color: var(--input-bg) !important;
        color: var(--text-color) !important;
    }}
    
    [role="option"]:hover {{
        background-color: var(--sidebar-bg) !important;
        color: var(--text-color) !important;
    }}
    
    [role="option"][aria-selected="true"] {{
        background-color: var(--accent-color) !important;
        color: #ffffff !important;
    }}
    
    /* Selectbox Selected Value Display */
    .stSelectbox [data-baseweb="select"] > div {{
        background-color: var(--input-bg) !important;
        color: var(--text-color) !important;
        border-color: var(--border-color) !important;
    }}
    
    .stSelectbox [data-baseweb="select"] span {{
        color: var(--text-color) !important;
    }}
    
    .stSelectbox [data-baseweb="select"] svg {{
        fill: var(--text-color) !important;
    }}

    /* Placeholder Text Visibility */
    ::placeholder {{
        color: var(--text-color) !important;
        opacity: 0.5 !important;
    }}
    
    /* Chrome, Firefox, Opera, Safari 10.1+ */
    input::placeholder, textarea::placeholder {{
        color: var(--text-color) !important;
        opacity: 0.5 !important;
    }}
    
    /* Internet Explorer 10-11 */
    :-ms-input-placeholder {{
        color: var(--text-color) !important;
        opacity: 0.5 !important;
    }}
    
    /* Number Input */
    .stNumberInput > div > div > input {{
        background-color: var(--input-bg) !important;
        color: var(--text-color) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 6px !important;
    }}
    
    /* Radio Buttons */
    .stRadio > div {{
        color: var(--text-color) !important;
    }}
    
    .stRadio label {{
        color: var(--text-color) !important;
    }}
    
    /* Warnings and Info boxes */
    .stAlert {{
        color: var(--text-color) !important;
    }}
    
    /* Success/Error/Warning/Info messages */
    [data-testid="stNotification"] {{
        background-color: var(--sidebar-bg) !important;
        border: 1px solid var(--border-color) !important;
    }}
    
    /* Expander */
    [data-testid="stExpander"] {{
        background-color: var(--input-bg) !important;
        border: 1px solid var(--border-color) !important;
    }}
    
    [data-testid="stExpander"] summary {{
        color: var(--text-color) !important;
    }}

    /* Buttons - macOS Push Button Style */
    .stButton > button {{
        background: var(--button-bg) !important;
        border: 1px solid var(--button-border) !important;
        color: var(--text-color) !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        padding: 0.4rem 1rem !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.3) !important;
        transition: all 0.1s ease;
    }}

    .stButton > button:hover {{
        background: var(--button-hover) !important;
        border-color: var(--accent-color) !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.4) !important;
    }}
    
    .stButton > button:active {{
        background-color: var(--border-color) !important;
        transform: scale(0.98);
        box-shadow: 0 1px 2px rgba(0,0,0,0.2) !important;
    }}

    /* Disabled Button Styling */
    .stButton > button:disabled {{
        background-color: var(--sidebar-bg) !important;
        color: #a1a1a6 !important;
        border-color: var(--border-color) !important;
        cursor: not-allowed !important;
        box-shadow: none !important;
        transform: none !important;
    }}

    /* Status Containers */
    .stStatus {{
        background-color: var(--sidebar-bg) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 10px;
    }}

    /* Progress Bar */
    .stProgress > div > div > div > div {{
        background-color: var(--accent-color) !important;
    }}
    
    /* Quill Editor Customization */
    .ql-toolbar {{
        background-color: var(--sidebar-bg);
        border-color: var(--border-color) !important;
        border-radius: 8px 8px 0 0;
    }}
    .ql-container {{
        background-color: var(--input-bg);
        border-color: var(--border-color) !important;
        border-radius: 0 0 8px 8px;
        color: var(--text-color);
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        min-height: 200px !important;
    }}
    
    /* Dividers */
    hr {{
        border-color: var(--border-color) !important;
    }}

    /* File Uploader Styling */
    [data-testid="stFileUploader"] {{
        background-color: var(--input-bg) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        padding: 0.5rem !important;
    }}
    
    [data-testid="stFileUploader"] label {{
        color: var(--text-color) !important;
        font-weight: 500 !important;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}
    
    [data-testid="stFileUploader"] section {{
        background-color: var(--input-bg) !important;
        border: 2px dashed var(--border-color) !important;
        border-radius: 6px !important;
        padding: 0.5rem !important;
        min-height: 0px !important;
    }}
    
    [data-testid="stFileUploader"] section:hover {{
        border-color: var(--accent-color) !important;
        background-color: var(--sidebar-bg) !important;
    }}
    
    [data-testid="stFileUploader"] small {{
        color: var(--text-color) !important;
        opacity: 0.7 !important;
    }}
    
    /* File Uploader Drag Area Text/Icon Alignment */
    [data-testid="stFileUploader"] section > div {{
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 0.5rem !important;
    }}
    
    [data-testid="stFileUploader"] section svg {{
        vertical-align: middle !important;
        margin-top: -2px !important;
    }}
    
    [data-testid="stFileUploader"] section span {{
        color: var(--text-color) !important;
    }}
    
    /* File Upload Button */
    [data-testid="stFileUploader"] button {{
        background-color: var(--input-bg) !important;
        border: 1px solid var(--border-color) !important;
        color: var(--text-color) !important;
        border-radius: 6px !important;
    }}
    
    [data-testid="stFileUploader"] button:hover {{
        background-color: var(--sidebar-bg) !important;
        border-color: var(--accent-color) !important;
    }}
    
    /* Uploaded File Display */
    [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] {{
        background-color: var(--sidebar-bg) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 6px !important;
        color: var(--text-color) !important;
    }}
    
    [data-testid="stFileUploader"] [data-testid="stFileUploaderFileName"] {{
        color: var(--text-color) !important;
    }}
    
    [data-testid="stFileUploader"] [data-testid="stFileUploaderFileSize"] {{
        color: var(--text-color) !important;
        opacity: 0.7 !important;
    }}
    
    /* File Delete Button */
    [data-testid="stFileUploader"] [data-testid="stFileUploaderDeleteBtn"] {{
        color: var(--text-color) !important;
    }}
    
    [data-testid="stFileUploader"] [data-testid="stFileUploaderDeleteBtn"]:hover {{
        color: #ff3b30 !important;
    }}

</style>
""", unsafe_allow_html=True)

# --- APPLE MAIL / macOS UI STYLING ---


# Sidebar Settings
with st.sidebar:
    # API Key
    api_key_val = get_persisted_value("api_key", os.getenv("GEMINI_API_KEY", ""))
    api_key = st.text_input("Gemini API Key", type="password", value=api_key_val, key="api_key")
    if not api_key:
        st.warning("Please enter your Gemini API Key.")
    
    
    # Always use Real SMTP mode
    mock_mode = False
    
    # Signature
    st.divider()
    st.subheader("✍️ Signature")
    
    sig_val = get_persisted_value("signature", "Best regards,\n[Your Name]")
    signature = st.text_area("Email Signature", value=sig_val, height=100, key="signature")
    
    
    st.divider()
    st.subheader("📧 SMTP Configuration")
    
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
        
        if st.button("🔗 Connect mail", help="Tests the SMTP connection for sending emails. Does not import contacts."):
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
    st.query_params["api_key"] = api_key
    st.query_params["signature"] = signature
    st.query_params["smtp_server"] = smtp_server
    st.query_params["smtp_port"] = str(smtp_port)
    st.query_params["smtp_email"] = smtp_email



# Initialize Agent
if api_key:
    # Re-initialize if key changes or first run
    if 'agent' not in st.session_state or st.session_state.get('last_api_key') != api_key:
        st.session_state.agent = EmailAgent(api_key=api_key, mock_mode=False)
        st.session_state.last_api_key = api_key
elif 'agent' not in st.session_state:
     st.session_state.agent = EmailAgent(mock_mode=False) # Fallback

col1, col2 = st.columns([1, 8], vertical_alignment="center")
with col1:
    st.image("logo.png", width=100)
with col2:
    st.title("Auto-Gen email")

st.markdown("Generate and send professional looking emails via Subject line.")

# Input Section
with st.container():
    st.subheader("Email Details")
    # Recipient Email
    to_val = get_persisted_value("to_email", "")
    to_email = st.text_input("Recipient Email", value=to_val, placeholder="e.g., boss@company.com", key="to_email")
    
    # Sync to_email to query params
    if to_email:
        st.query_params["to_email"] = to_email
    
    # Subject Templates - DISABLED
    # templates = {
    #     "Custom": "",
    #     "Job Application": "Application for [Position] - [Your Name]",
    #     "Follow Up": "Following up on [Topic]",
    #     "Meeting Request": "Request for Meeting: [Topic]",
    #     "Invoice": "Invoice #[Number] for [Service]",
    #     "Sick Leave": "Sick Leave Application - [Date]"
    # }
    
    # col_temp, col_subj = st.columns([1, 2])
    # with col_temp:
    #     selected_template = st.selectbox("Quick Templates", list(templates.keys()))
    
    # Determine default subject value
    # default_subject = ""
    # if selected_template != "Custom":
    #     default_subject = templates[selected_template]
    
    # Simple subject input without templates
    if "subject_val" not in st.session_state:
        st.session_state.subject_val = ""
    
    subject = st.text_input("Subject", value=st.session_state.subject_val, key="subject_input", placeholder="Enter email subject")
    # Sync back to session state for manual edits
    st.session_state.subject_val = subject

    # Subject Optimization / Reverse Flow
    # Disable button until body text is generated
    body_generated = st.session_state.get("generated_email", "").strip() != ""
    
    opt_btn_text = "✨ Optimize / Generate Subject" if body_generated else "⚪ Optimize Subject (Generate Body First)"
    
    if st.button(opt_btn_text, disabled=not body_generated):
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



# Generation Section
if st.button("🚀 Generate Email"):
    if not subject:
        st.warning("Please enter a subject first.")
    elif not api_key:
        st.error("Please enter a Gemini API Key in the sidebar.")
    else:
        with st.spinner("Drafting your email..."):
            # Get list of file names
            attachment_names = [] # Attachments are now added after generation
            
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
    
    # Attachments (Moved here)
    uploaded_files = st.file_uploader("📎 Attachments (Max 10MB)", accept_multiple_files=True, key="file_uploader")
    valid_attachments = []
    if uploaded_files:
        for file in uploaded_files:
            if file.size > 10 * 1024 * 1024: # 10MB
                st.error(f"File {file.name} is too large (>10MB).")
            else:
                valid_attachments.append(file)

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
        else:
            st.toast("❌ Failed to send email.", icon="❌")
            st.error("Failed to send email. Check your SMTP settings.")
        
        # Reset phase
        st.session_state.sending_phase = None
        
    elif st.session_state.get('sending_phase') == 'cancelled':
        st.warning("Sending was cancelled.")
        st.session_state.sending_phase = None
