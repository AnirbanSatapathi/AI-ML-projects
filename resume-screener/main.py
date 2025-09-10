import streamlit as st
from streamlit_option_menu import option_menu
import time
from datetime import datetime

from utils.file_parser import FileParser
from utils.npl_processor import NLPProcessor
from utils.visualizations import VisualizationUtils

st.set_page_config(
    page_title="Resume Screener",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header { font-size: 3rem; color: #1f77b4; text-align: center; }
    .sub-header { font-size: 1.5rem; color: #2c3e50; border-bottom: 2px solid #1f77b4; padding-bottom: 0.5rem; }
    .success-box { background-color: #d4edda; color: #155724; padding: 15px; border-radius: 5px; border: 1px solid #c3e6cb; margin: 10px 0; }
    .metric-card { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 4px solid #1f77b4; margin: 10px 0; }
    .stProgress > div > div > div > div { background-color: #1f77b4; }
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
        st.markdown('<h1 class="main-header">Resume Screening Assistant</h1>', unsafe_allow_html=True)
        st.markdown("---")

        # Sidebar navigation
        with st.sidebar:
            st.image("https://img.icons8.com/dusk/64/000000/resume.png", width=80)
            st.markdown("### Navigation")
            selected = option_menu(menu_title=None,
                                   options=["Screening", "Results", "Help"],
                                   icons=["search", "bar-chart", "question-circle"],
                                   default_index=0)

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

        file_parser = FileParser()

        # --- Job Description ---
        with col1:
            st.markdown('<div class="sub-header">Job Description</div>', unsafe_allow_html=True)

            jd_source = st.radio("Select input method:", ["Upload JD", "Paste Text"], horizontal=True)

            if jd_source == "Upload JD":
                jd_file = st.file_uploader("Upload Job Description (PDF or DOCX)", type=["pdf", "docx"], key="jd_uploader")
                if jd_file:
                    with st.spinner("Extracting text from job description..."):
                        jd_bytes = jd_file.read()
                        # Use FileParser.parse_file instead of parse_resume
                        jd_data = file_parser.parse_file(jd_file.name) if hasattr(jd_file, 'name') else {}
                        if not jd_data:
                            # fallback: parse bytes directly
                            if jd_file.type == "application/pdf":
                                jd_text = file_parser.extract_text_from_pdf(jd_bytes)
                            else:
                                jd_text = file_parser.extract_text_from_docx(jd_bytes)
                            jd_text = file_parser.clean_text(jd_text)
                            jd_data = {"text": jd_text}
                        st.session_state.jd_text = jd_data.get("text", "")
            else:
                st.session_state.jd_text = st.text_area("Paste Job Description Text:", height=200, value=st.session_state.jd_text)

            if st.session_state.jd_text:
                with st.expander("Preview Job Description"):
                    st.write(st.session_state.jd_text[:500] + "..." if len(st.session_state.jd_text) > 500 else st.session_state.jd_text)

        # --- Resumes ---
        with col2:
            st.markdown('<div class="sub-header">Resumes</div>', unsafe_allow_html=True)

            resume_files = st.file_uploader("Upload Resumes (PDF or DOCX)", type=["pdf", "docx"], accept_multiple_files=True, key="resume_uploader")
            if resume_files:
                st.session_state.resumes = []
                progress_bar = st.progress(0)
                status_text = st.empty()

                for i, resume_file in enumerate(resume_files):
                    status_text.text(f"Processing {i + 1}/{len(resume_files)}: {resume_file.name}")
                    progress_bar.progress((i + 1) / len(resume_files))

                    try:
                        resume_bytes = resume_file.read()
                        # parse in memory
                        if resume_file.type == "application/pdf":
                            text = file_parser.extract_text_from_pdf(resume_bytes)
                        else:
                            text = file_parser.extract_text_from_docx(resume_bytes)
                        text = file_parser.clean_text(text)
                        contact = file_parser.extract_contact_info(text)
                        sections = file_parser.split_sections(text)
                        parsed_resume = {
                            "filename": resume_file.name,
                            "word_count": len(text.split()),
                            "contact_info": contact,
                            "sections": sections,
                            "text": text
                        }
                        st.session_state.resumes.append(parsed_resume)
                    except Exception as e:
                        st.error(f"Error processing {resume_file.name}: {str(e)}")

                status_text.text("Processing complete!")
                time.sleep(0.5)
                status_text.empty()
                progress_bar.empty()
                st.success(f"Successfully processed {len(st.session_state.resumes)} resumes")

        # --- Process Button ---
        if st.session_state.jd_text and st.session_state.resumes:
            if st.button("Screen Resumes", type="primary", use_container_width=True):
                with st.spinner("Analyzing resumes..."):
                    nlp_processor = self.initialize_nlp_processor()
                    st.session_state.results_df = nlp_processor.calculate_similarity(
                        st.session_state.jd_text,
                        st.session_state.resumes
                    )
                    st.session_state.processed = True
                    st.success("Analysis complete!")

    def render_results_page(self):
        """Render the results page"""
        if not st.session_state.processed or st.session_state.results_df is None:
            st.warning("Please process some resumes first on the Screening page.")
            return

        st.markdown('<div class="sub-header">Screening Results</div>', unsafe_allow_html=True)

        df = st.session_state.results_df
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total Resumes", len(df))
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Average Score", f"{df['Similarity Score'].mean():.2f}%")
            st.markdown('</div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Top Score", f"{df['Similarity Score'].max():.2f}%")
            st.markdown('</div>', unsafe_allow_html=True)
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total Skills Matched", df['Skills Count'].sum())
            st.markdown('</div>', unsafe_allow_html=True)

        st.dataframe(df, use_container_width=True, height=400)

        viz_utils = VisualizationUtils()
        tab1, tab2, tab3 = st.tabs(["Similarity Scores", "Skills Analysis", "Score Distribution"])

        with tab1:
            fig = viz_utils.create_similarity_chart(df)
            if fig: st.plotly_chart(fig, width="stretch")

        with tab2:
            fig = viz_utils.create_skills_chart(df)
            if fig: st.plotly_chart(fig, width="stretch")
            else: st.info("No skills detected in the resumes.")

        with tab3:
            fig = viz_utils.create_score_distribution(df)
            if fig: st.plotly_chart(fig, width="stretch")

        # Export
        st.markdown("---")
        st.markdown("### Export Results")
        col1, col2 = st.columns(2)
        with col1:
            csv = df.to_csv(index=False)
            st.download_button("Download CSV", csv, file_name=f"resume_screening_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv", width="stretch")
        with col2:
            def to_excel(df):
                import io
                output = io.BytesIO()
                df.to_excel(output, index=False, engine="openpyxl")
                return output.getvalue()
            excel_data = to_excel(df)
            st.download_button("Download Excel", excel_data, file_name=f"resume_screening_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", width="stretch")

    def render_help_page(self):
        """Render the help page"""
        st.markdown('<div class="sub-header">Help & Instructions</div>', unsafe_allow_html=True)
        with st.expander("How to use this tool"):
            st.markdown("""
            1. Upload or paste a Job Description
            2. Upload multiple resumes (PDF/DOCX)
            3. Click 'Screen Resumes' to analyze
            4. View results with similarity, matched skills, and export options
            """)
        with st.expander("Scoring Method"):
            st.markdown("""
            - Semantic Similarity via Sentence Transformers
            - Cosine Similarity between JD and resume embeddings
            - Dynamic skill extraction from JD keywords
            """)
