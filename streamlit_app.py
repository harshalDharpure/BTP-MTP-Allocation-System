"""
Streamlit Web Application for BTP/MTP Allocation
Provides a user-friendly interface for uploading input files and downloading results
"""

import streamlit as st
import pandas as pd
import io
import logging
from allocation_engine import AllocationEngine
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('streamlit_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="BTP/MTP Allocation System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main Streamlit application"""
    
    # Header
    st.title("🎓 BTP/MTP Allocation System")
    st.markdown("---")
    
    # Sidebar
    st.sidebar.title("📋 Navigation")
    page = st.sidebar.selectbox("Choose a page", ["Upload & Process", "About"])
    
    if page == "Upload & Process":
        upload_and_process_page()
    elif page == "About":
        about_page()

def upload_and_process_page():
    """Main processing page"""
    
    st.header("📤 Upload Input File")
    
    # File upload section
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload the student preference CSV file with columns: Roll, Name, Email, CGPA, and faculty preferences"
    )
    
    if uploaded_file is not None:
        try:
            # Read the uploaded file
            df = pd.read_csv(uploaded_file)
            
            # Display file info
            st.success(f"✅ File uploaded successfully!")
            st.info(f"📊 **File Info:** {len(df)} students, {len(df.columns)} columns")
            
            # Show preview
            with st.expander("📋 Preview of uploaded data"):
                st.dataframe(df.head(10))
            
            # Validate file structure
            required_columns = ['Roll', 'Name', 'Email', 'CGPA']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"❌ Missing required columns: {missing_columns}")
                return
            
            # Process button
            if st.button("🚀 Process Allocation", type="primary"):
                process_allocation(df, uploaded_file.name)
                
        except Exception as e:
            logger.error(f"Error processing uploaded file: {str(e)}")
            st.error(f"❌ Error reading file: {str(e)}")
    
    else:
        # Show sample data structure
        st.info("💡 **Expected file format:**")
        sample_data = {
            'Roll': ['1601CB01', '1601CB03'],
            'Name': ['Alok Baranwal', 'Amrit Raj'],
            'Email': ['random1@gmail.com', 'random2@gmail.com'],
            'CGPA': [5.81, 6.73],
            'ABM': [14, 3],
            'AE': [11, 5],
            'AM': [6, 12],
            # ... more faculty columns
        }
        st.dataframe(pd.DataFrame(sample_data))

def process_allocation(df, filename):
    """Process the allocation and show results"""
    
    try:
        # Initialize progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: Initialize engine
        status_text.text("🔄 Initializing allocation engine...")
        progress_bar.progress(10)
        
        engine = AllocationEngine()
        engine.students_data = df
        
        # Extract faculty names
        cgpa_col_index = df.columns.get_loc('CGPA')
        engine.faculties = list(df.columns[cgpa_col_index + 1:])
        
        # Step 2: Perform allocation
        status_text.text("🔄 Allocating students to faculties...")
        progress_bar.progress(30)
        
        allocation_results = engine.allocate_students()
        
        # Step 3: Generate preference statistics
        status_text.text("🔄 Generating preference statistics...")
        progress_bar.progress(60)
        
        preference_stats = engine.generate_preference_stats()
        
        # Step 4: Prepare results
        status_text.text("🔄 Preparing results...")
        progress_bar.progress(80)
        
        # Get summary
        summary = engine.get_allocation_summary()
        
        # Complete
        progress_bar.progress(100)
        status_text.text("✅ Processing completed!")
        
        # Display results
        display_results(allocation_results, preference_stats, summary)
        
        # Download buttons
        download_section(allocation_results, preference_stats, filename)
        
    except Exception as e:
        logger.error(f"Error in allocation process: {str(e)}")
        st.error(f"❌ Error during processing: {str(e)}")
        st.exception(e)

def display_results(allocation_results, preference_stats, summary):
    """Display allocation results and statistics"""
    
    st.header("📊 Allocation Results")
    
    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Students", summary.get('total_students', 0))
    
    with col2:
        pref_1_count = summary.get('preference_satisfaction', {}).get('pref_1', 0)
        st.metric("1st Preference", pref_1_count)
    
    with col3:
        pref_2_count = summary.get('preference_satisfaction', {}).get('pref_2', 0)
        st.metric("2nd Preference", pref_2_count)
    
    with col4:
        other_count = summary.get('preference_satisfaction', {}).get('other', 0)
        st.metric("Other Preferences", other_count)
    
    # Faculty distribution
    st.subheader("🏛️ Faculty Distribution")
    faculty_dist = summary.get('faculty_distribution', {})
    
    if faculty_dist:
        faculty_df = pd.DataFrame(list(faculty_dist.items()), columns=['Faculty', 'Students'])
        st.bar_chart(faculty_df.set_index('Faculty'))
    
    # Allocation results table
    st.subheader("📋 Allocation Results")
    st.dataframe(allocation_results[['Roll', 'Name', 'CGPA', 'Allocated', 'Preference_Rank']])
    
    # Preference statistics
    st.subheader("📈 Faculty Preference Statistics")
    st.dataframe(preference_stats)

def download_section(allocation_results, preference_stats, original_filename):
    """Create download buttons for results"""
    
    st.header("💾 Download Results")
    
    # Prepare files for download
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Allocation results
    allocation_output = allocation_results[['Roll', 'Name', 'Email', 'CGPA', 'Allocated']].copy()
    allocation_csv = allocation_output.to_csv(index=False)
    
    # Preference statistics
    preference_csv = preference_stats.to_csv(index=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="📥 Download Allocation Results",
            data=allocation_csv,
            file_name=f"allocation_results_{timestamp}.csv",
            mime="text/csv",
            help="Download the student allocation results"
        )
    
    with col2:
        st.download_button(
            label="📥 Download Preference Statistics",
            data=preference_csv,
            file_name=f"preference_stats_{timestamp}.csv",
            mime="text/csv",
            help="Download the faculty preference statistics"
        )

def about_page():
    """About page with information about the system"""
    
    st.header("ℹ️ About BTP/MTP Allocation System")
    
    st.markdown("""
    ## 🎯 Purpose
    This system implements an automated allocation algorithm for BTP (Bachelor's Thesis Project) and MTP (Master's Thesis Project) assignments based on student preferences and CGPA.
    
    ## 🔧 Algorithm
    The allocation process follows these steps:
    
    1. **Sort by CGPA**: Students are sorted by CGPA in descending order
    2. **Mod N Allocation**: Each faculty gets exactly one student per cycle
    3. **Preference Matching**: Students are allocated based on their preference rankings
    4. **Fair Distribution**: Ensures balanced distribution across all faculties
    
    ## 📊 Output Files
    
    ### Allocation Results
    - Contains student information and their allocated faculty
    - Columns: Roll, Name, Email, CGPA, Allocated
    
    ### Preference Statistics
    - Shows how many students ranked each faculty at each preference level
    - Helps analyze faculty popularity and preference patterns
    
    ## 🚀 Features
    - ✅ Web-based interface using Streamlit
    - ✅ Real-time processing and results display
    - ✅ Comprehensive logging and error handling
    - ✅ Docker support for easy deployment
    - ✅ Downloadable results in CSV format
    
    ## 📝 Input Format
    The input CSV file should contain:
    - **Roll**: Student roll number
    - **Name**: Student name
    - **Email**: Student email
    - **CGPA**: Student's CGPA
    - **Faculty columns**: Preference rankings (1-18) for each faculty
    
    ## 🔍 Example Faculty Codes
    - ABM, AE, AM, AR, CA, JC, JM, MA, RH, RM, RM2, RS, SK, SKD, SKM, SM, SS, ST
    """)
    
    st.markdown("---")
    st.markdown("**Developed for Algorithm Course Assignment 2**")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Error in Streamlit app: {str(e)}")
        st.error("❌ An error occurred. Please check the logs for details.")
