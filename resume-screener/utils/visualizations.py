import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import streamlit as st


class VisualizationUtils:
    """Utilities for creating visualizations"""

    @staticmethod
    def create_similarity_chart(df: pd.DataFrame):
        """Create a bar chart of similarity scores"""
        fig = px.bar(
            df,
            x='Filename',
            y='Similarity Score',
            title='Resume Similarity Scores',
            labels={'Similarity Score': 'Score (%)', 'Filename': 'Resume'},
            color='Similarity Score',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(xaxis_tickangle=-45)
        return fig

    @staticmethod
    def create_skills_chart(df: pd.DataFrame):
        """Create a chart showing skills distribution"""
        # Count skills
        all_skills = []
        for skills_str in df['Matched Skills']:
            if skills_str != 'None':
                skills = [s.strip() for s in skills_str.split(',')]
                all_skills.extend(skills)

        if not all_skills:
            return None

        skills_series = pd.Series(all_skills)
        skills_count = skills_series.value_counts().reset_index()
        skills_count.columns = ['Skill', 'Count']

        fig = px.bar(
            skills_count.head(10),
            x='Skill',
            y='Count',
            title='Top Skills Across Resumes',
            color='Count',
            color_continuous_scale='Blues'
        )
        return fig

    @staticmethod
    def create_score_distribution(df: pd.DataFrame):
        """Create a distribution chart of scores"""
        fig = px.histogram(
            df,
            x='Similarity Score',
            title='Distribution of Similarity Scores',
            nbins=10,
            color_discrete_sequence=['#1f77b4']
        )
        fig.update_layout(showlegend=False)
        return fig