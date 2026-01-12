import streamlit as st
import db

st.title("DB Connection Debugger")

if st.button("Test Connection"):
    try:
        client = db.get_connection()
        if not client:
            st.error("Client connection failed. Check secrets.")
        else:
            st.success("Client connected successfully!")
            
            try:
                sh = client.open("architecture-app-db")
                st.success(f"Found Spreadsheet: {sh.title}")
                
                worksheet = db.init_db()
                if worksheet:
                    st.success(f"Found/Created Worksheet: {worksheet.title}")
                    st.info("Attempting to save test data...")
                    if db.save_result("http://test.com/image.png", "test prompt", "debug-engine"):
                        st.success("Successfully saved test data!")
                    else:
                        st.error("Failed to save test data.")
                else:
                    st.error("Failed to get worksheet.")
            except Exception as e:
                st.error(f"Failed to open spreadsheet 'architecture-app-db': {e}")
                st.warning("Make sure you created a sheet named 'architecture-app-db' and shared it with the service account email.")
                
    except Exception as e:
        st.error(f"Unexpected error: {e}")

st.markdown("### Service Account Email")
if "gcp_service_account" in st.secrets:
    st.code(st.secrets["gcp_service_account"]["client_email"])
else:
    st.error("No service account secrets found.")
