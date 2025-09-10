import sys
import logging
import pandas as pd
from utils.file_parser import FileParser
from utils.npl_processor import NLPProcessor
from utils.visualizations import VisualizationUtils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_job_description(file_path: str) -> str:
    """Load Job Description text from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Failed to read JD file: {e}")
        return ""


def main():
    if len(sys.argv) < 3:
        print("Usage: python code_test.py <JD_file> <resume1> [<resume2> ...]")
        return

    jd_path = sys.argv[1]
    resume_paths = sys.argv[2:]

    print("===== Resume Screening Started =====")

    # Parse resumes
    resumes = []
    for rpath in resume_paths:
        print(f"Parsing: {rpath}")
        parsed = FileParser.parse_resume(rpath)
        if parsed:
            resumes.append(parsed)
        else:
            logger.warning(f"Failed to parse resume: {rpath}")

    if not resumes:
        logger.error("No resumes parsed successfully. Exiting.")
        return

    # Load JD
    jd_text = load_job_description(jd_path)
    if not jd_text:
        logger.error("Job Description is empty. Exiting.")
        return

    nlp = NLPProcessor()
    df_results = nlp.calculate_similarity(job_description=jd_text, resumes=resumes)

    if df_results.empty:
        logger.error("No similarity results generated. Exiting.")
        return

    print("\n===== Ranked Results =====")
    print(df_results)

    # Save results
    df_results.to_excel("results.xlsx", index=False)
    print("\nResults saved to results.xlsx")

    # Visualizations
    sim_fig = VisualizationUtils.create_similarity_chart(df_results)
    skills_fig = VisualizationUtils.create_skills_chart(df_results, top_n=10)
    dist_fig = VisualizationUtils.create_score_distribution(df_results)

    if sim_fig:
        sim_fig.show()
    if skills_fig:
        skills_fig.show()
    if dist_fig:
        dist_fig.show()


if __name__ == "__main__":
    main()
