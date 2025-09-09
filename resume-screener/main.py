import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import time
import base64
from datetime import datetime

# Import our utilities
from utils.file_parser import FileParser
from utils.npl_processor import NLPProcessor
from utils.visualizations import VisualizationUtils

# Page configuration
st.set_page_config(
    page_title="Advanced Resume Screener",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2c3e50;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
    }
    .success-box {
        background-color: #d4edda;
        color: #155724;
        padding: 15px;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
        margin: 10px 0;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 10px 0;
    }
    .stProgress > div > div > div > div {
        background-color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)


class ResumeScreenerApp:
    """Main application class for the Resume Screener"""

    def __init__(self):
        self.nlp_processor = None
        self.initialize_session_state()

    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'processed' not in st.session_state:
            st.session_state.processed = False
        if 'results_df' not in st.session_state:
            st.session_state.results_df = None
        if 'jd_text' not in st.session_state:
            st.session_state.jd_text = ""
        if 'resumes' not in st.session_state:
            st.session_state.resumes = []

    def initialize_nlp_processor(self):
        """Initialize the NLP processor with caching"""
        if self.nlp_processor is None:
            with st.spinner("Loading AI model..."):
                self.nlp_processor = NLPProcessor()
        return self.nlp_processor

    def run(self):
        """Run the main application"""
        # Header
        st.markdown('<h1 class="main-header">Advanced Resume Screening Assistant</h1>',
                    unsafe_allow_html=True)
        st.markdown("---")

        # Sidebar navigation
        with st.sidebar:
            st.image("https://img.icons8.com/dusk/64/000000/resume.png", width=80)
            st.markdown("### Navigation")
            selected = option_menu(
                menu_title=None,
                options=["Screening", "Results", "Help"],
                icons=["search", "bar-chart", "question-circle"],
                default_index=0,
            )

        # Page routing
        if selected == "Screening":
            self.render_screening_page()
        elif selected == "Results":
            self.render_results_page()
        elif selected == "Help":
            self.render_help_page()

    def render_screening_page(self):
        """Render the main screening page"""
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown('<div class="sub-header">Job Description</div>',
                        unsafe_allow_html=True)

            jd_source = st.radio(
                "Select input method:",
                ["Upload JD", "Paste Text"],
                horizontal=True
            )

            if jd_source == "Upload JD":
                jd_file = st.file_uploader(
                    "Upload Job Description (PDF or DOCX)",
                    type=["pdf", "docx"],
                    key="jd_uploader"
                )

                if jd_file:
                    with st.spinner("Extracting text from job description..."):
                        file_parser = FileParser()
                        jd_bytes = jd_file.read()
                        st.session_state.jd_text = file_parser.parse_resume(jd_bytes, jd_file.name)['text']

            else:  # Paste Text
                st.session_state.jd_text = st.text_area(
                    "Paste Job Description Text:",
                    height=200,
                    value=st.session_state.jd_text
                )

            if st.session_state.jd_text:
                with st.expander("Preview Job Description"):
                    st.write(st.session_state.jd_text[:500] + "..."
                             if len(st.session_state.jd_text) > 500 else st.session_state.jd_text)

        with col2:
            st.markdown('<div class="sub-header">Resumes</div>',
                        unsafe_allow_html=True)

            resume_files = st.file_uploader(
                "Upload Resumes (PDF or DOCX)",
                type=["pdf", "docx"],
                accept_multiple_files=True,
                key="resume_uploader"
            )

            if resume_files:
                st.session_state.resumes = []
                file_parser = FileParser()

                progress_bar = st.progress(0)
                status_text = st.empty()

                for i, resume_file in enumerate(resume_files):
                    status_text.text(f"Processing {i + 1}/{len(resume_files)}: {resume_file.name}")
                    progress_bar.progress((i + 1) / len(resume_files))

                    try:
                        resume_bytes = resume_file.read()
                        parsed_resume = file_parser.parse_resume(resume_bytes, resume_file.name)
                        st.session_state.resumes.append(parsed_resume)
                    except Exception as e:
                        st.error(f"Error processing {resume_file.name}: {str(e)}")

                status_text.text("Processing complete!")
                time.sleep(0.5)
                status_text.empty()
                progress_bar.empty()

                st.success(f"Successfully processed {len(st.session_state.resumes)} resumes")

        # Process button
        if st.session_state.jd_text and st.session_state.resumes:
            if st.button("🚀 Screen Resumes", type="primary", use_container_width=True):
                with st.spinner("Analyzing resumes..."):
                    nlp_processor = self.initialize_nlp_processor()
                    st.session_state.results_df = nlp_processor.calculate_similarity(
                        st.session_state.jd_text,
                        st.session_state.resumes
                    )
                    st.session_state.processed = True

                    # Switch to results page
                    st.success("Analysis complete!")
                    st.experimental_rerun()

    def render_results_page(self):
        """Render the results page"""
        if not st.session_state.processed or st.session_state.results_df is None:
            st.warning("Please process some resumes first on the Screening page.")
            return

        st.markdown('<div class="sub-header">Screening Results</div>',
                    unsafe_allow_html=True)

        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total Resumes", len(st.session_state.results_df))
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            avg_score = st.session_state.results_df['Similarity Score'].mean()
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Average Score", f"{avg_score:.2f}%")
            st.markdown('</div>', unsafe_allow_html=True)
        with col3:
            top_score = st.session_state.results_df['Similarity Score'].max()
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Top Score", f"{top_score:.2f}%")
            st.markdown('</div>', unsafe_allow_html=True)
        with col4:
            skills_count = st.session_state.results_df['Skills Count'].sum()
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total Skills Matched", skills_count)
            st.markdown('</div>', unsafe_allow_html=True)

        # Results table
        st.dataframe(
            st.session_state.results_df,
            use_container_width=True,
            height=400
        )

        # Visualizations
        viz_utils = VisualizationUtils()

        tab1, tab2, tab3 = st.tabs(["Similarity Scores", "Skills Analysis", "Score Distribution"])

        with tab1:
            fig = viz_utils.create_similarity_chart(st.session_state.results_df)
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            fig = viz_utils.create_skills_chart(st.session_state.results_df)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No skills detected in the resumes.")

        with tab3:
            fig = viz_utils.create_score_distribution(st.session_state.results_df)
            st.plotly_chart(fig, use_container_width=True)

        # Export options
        st.markdown("---")
        st.markdown("### Export Results")

        col1, col2 = st.columns(2)

        with col1:
            # CSV export
            csv = st.session_state.results_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"resume_screening_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )

        with col2:
            # Excel export
            @st.cache_data
            def convert_df_to_excel(df):
                return df.to_excel(index=False, engine='openpyxl')

            excel_data = convert_df_to_excel(st.session_state.results_df)
            st.download_button(
                label="Download Excel",
                data=excel_data,
                file_name=f"resume_screening_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

    def render_help_page(self):
        """Render the help page"""
        st.markdown('<div class="sub-header">Help & Instructions</div>',
                    unsafe_allow_html=True)

        with st.expander("How to use this tool"):
            st.markdown("""
            1. **Job Description**: Either upload a PDF/DOCX file or paste the text of the job description
            2. **Resumes**: Upload multiple resumes in PDF or DOCX format
            3. **Processing**: Click the 'Screen Resumes' button to analyze the resumes
            4. **Results**: View the results on the Results page, including:
               - Similarity scores for each resume
               - Extracted contact information
               - Matched skills
               - Visualizations of the data
            5. **Export**: Download the results as CSV or Excel for further analysis
            """)

        with st.expander("How the scoring works"):
            st.markdown("""
            The tool uses advanced natural language processing (NLP) techniques:

            - **Semantic Similarity**: We use sentence transformers to convert text into numerical vectors
            - **Cosine Similarity**: We measure the angle between vectors to determine similarity
            - **TF-IDF Analysis**: We extract important keywords from the job description
            - **Skill Matching**: We identify which skills from the JD appear in each resume

            This approach is more advanced than simple keyword matching as it understands
            the context and meaning of the text.
            """)

        with st.expander("Tips for best results"):
            st.markdown("""
            - Provide a detailed job description with required skills and qualifications
            - Ensure resumes are in text-based PDF format (not scanned images)
            - For large batches of resumes, process them in groups of 20-30 for better performance
            - Review the top matches manually to refine your selection criteria
            """)
