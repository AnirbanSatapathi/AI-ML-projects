import plotly.express as px
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class VisualizationUtils:
    """Utilities for creating visualizations of resume screening results"""

    @staticmethod
    def create_similarity_chart(df: pd.DataFrame):
        """Create a bar chart of similarity scores"""
        if df.empty:
            logger.warning("DataFrame is empty. Cannot create similarity chart.")
            return None
        try:
            fig = px.bar(
                df,
                x='Filename',
                y='Similarity Score',
                title='Resume Similarity Scores',
                labels={'Similarity Score': 'Score (%)', 'Filename': 'Resume'},
                color='Similarity Score',
                color_continuous_scale='Viridis',
                hover_data={'Filename': True, 'Similarity Score': True, 'Word Count': True}
            )
            fig.update_layout(xaxis_tickangle=-45)
            return fig
        except Exception as e:
            logger.error(f"Error creating similarity chart: {e}")
            return None

    @staticmethod
    def create_skills_chart(df: pd.DataFrame, top_n: int = 10):
        """Create a bar chart showing top skills distribution"""
        if df.empty:
            logger.warning("DataFrame is empty. Cannot create skills chart.")
            return None
        try:
            # Aggregate skills
            all_skills = []
            for skills_str in df['Matched Skills']:
                if skills_str != 'None':
                    skills = [s.strip() for s in skills_str.split(',')]
                    all_skills.extend(skills)

            if not all_skills:
                logger.info("No skills found in resumes.")
                return None

            skills_series = pd.Series(all_skills)
            skills_count = skills_series.value_counts().reset_index()
            skills_count.columns = ['Skill', 'Count']
            skills_count = skills_count.sort_values(by='Count', ascending=False)

            fig = px.bar(
                skills_count.head(top_n),
                x='Skill',
                y='Count',
                title=f'Top {top_n} Skills Across Resumes',
                color='Count',
                color_continuous_scale='Blues',
                hover_data={'Skill': True, 'Count': True}
            )
            return fig
        except Exception as e:
            logger.error(f"Error creating skills chart: {e}")
            return None

    @staticmethod
    def create_score_distribution(df: pd.DataFrame):
        """Create a histogram of similarity scores"""
        if df.empty:
            logger.warning("DataFrame is empty. Cannot create score distribution chart.")
            return None
        try:
            fig = px.histogram(
                df,
                x='Similarity Score',
                title='Distribution of Similarity Scores',
                nbins=10,
                color_discrete_sequence=['#1f77b4'],
                hover_data={'Similarity Score': True}
            )
            fig.update_layout(showlegend=False)
            return fig
        except Exception as e:
            logger.error(f"Error creating score distribution chart: {e}")
            return None
