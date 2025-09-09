from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import pandas as pd
import logging
import re
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)


class NLPProcessor:
    """Advanced NLP processing for resume screening"""

    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = None
        self.model_name = model_name
        self._initialize_model()

    def _initialize_model(self):
        """Initialize the sentence transformer model"""
        try:
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Loaded model: {self.model_name}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise

    def extract_skills(self, text: str, skills_list: List[str]) -> List[str]:
        """Extract skills from text based on a predefined skills list"""
        found_skills = []
        text_lower = text.lower()

        for skill in skills_list:
            # Use regex to find whole word matches only
            if re.search(r'\b' + re.escape(skill.lower()) + r'\b', text_lower):
                found_skills.append(skill)

        return found_skills

    def calculate_similarity(self, job_description: str, resumes: List[Dict]) -> pd.DataFrame:
        """Calculate similarity between job description and resumes"""
        # Prepare texts for embedding
        texts = [job_description] + [resume['text'] for resume in resumes]

        # Generate embeddings
        embeddings = self.model.encode(texts, convert_to_tensor=False)

        # Calculate similarity
        jd_embedding = embeddings[0].reshape(1, -1)
        resume_embeddings = embeddings[1:]

        similarity_scores = cosine_similarity(jd_embedding, resume_embeddings)[0]

        # Extract keywords using TF-IDF
        vectorizer = TfidfVectorizer(max_features=20, stop_words='english')
        try:
            tfidf_matrix = vectorizer.fit_transform([job_description])
            keywords = vectorizer.get_feature_names_out()
        except:
            keywords = []

        # Prepare results
        results = []
        for i, resume in enumerate(resumes):
            # Extract skills if skills list is provided
            skills = self.extract_skills(resume['text'], list(keywords))

            results.append({
                'Filename': resume['filename'],
                'Similarity Score': round(similarity_scores[i] * 100, 2),
                'Word Count': resume['word_count'],
                'Email': resume['contact_info']['emails'][0] if resume['contact_info']['emails'] else 'Not found',
                'Phone': resume['contact_info']['phones'][0] if resume['contact_info']['phones'] else 'Not found',
                'Matched Skills': ', '.join(skills) if skills else 'None',
                'Skills Count': len(skills)
            })

        # Create DataFrame and sort by similarity score
        df = pd.DataFrame(results)
        df = df.sort_values('Similarity Score', ascending=False)
        df.reset_index(drop=True, inplace=True)
        df.index = df.index + 1  # Start ranking from 1

        return df