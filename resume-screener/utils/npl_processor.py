import logging
import re
from typing import List, Dict
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

logger = logging.getLogger(__name__)


class NLPProcessor:
    """NLP processor for resume screening (dynamic skills extraction from JD)."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self._initialize_model()

    def _initialize_model(self):
        """Load the sentence transformer model."""
        try:
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Loaded model: {self.model_name}")
        except Exception as e:
            logger.error(f"Error loading SentenceTransformer: {e}")
            raise

    def extract_skills(self, text: str, jd_keywords: List[str] = None) -> List[str]:
        found_skills = set()
        text_lower = text.lower()

        if jd_keywords:
            for keyword in jd_keywords:
                kw = keyword.lower().strip()
                if re.search(r"\b" + re.escape(kw) + r"\b", text_lower):
                    found_skills.add(keyword)

        return sorted(list(found_skills))

    def calculate_similarity(self, job_description: str, resumes: List[Dict]) -> pd.DataFrame:
        if len(resumes) == 0:
            logger.warning("No resumes provided.")
            return pd.DataFrame()

        try:
            # Prepare texts for embeddings
            texts = [job_description] + [resume.get("text", "") for resume in resumes]

            # Generate embeddings
            embeddings = self.model.encode(texts, convert_to_tensor=False)

            jd_embedding = embeddings[0].reshape(1, -1)
            resume_embeddings = np.array(embeddings[1:])

            # Compute similarity
            similarity_scores = cosine_similarity(jd_embedding, resume_embeddings)[0]

            # Extract JD keywords dynamically
            try:
                vectorizer = TfidfVectorizer(max_features=20, stop_words="english")
                vectorizer.fit([job_description])
                jd_keywords = vectorizer.get_feature_names_out()
            except Exception:
                jd_keywords = []

            results = []
            for i, resume in enumerate(resumes):
                skills = self.extract_skills(resume.get("text", ""), list(jd_keywords))
                results.append({
                    "Filename": resume.get("filename", "Unknown"),
                    "Similarity Score": round(float(similarity_scores[i]) * 100, 2),
                    "Word Count": resume.get("word_count", 0),
                    "Email": (resume.get("contact_info", {}).get("emails", ["Not found"])[0]),
                    "Phone": (resume.get("contact_info", {}).get("phones", ["Not found"])[0]),
                    "Matched Skills": ", ".join(skills) if skills else "None",
                    "Skills Count": len(skills),
                })

            df = pd.DataFrame(results)
            df = df.sort_values("Similarity Score", ascending=False)
            df.reset_index(drop=True, inplace=True)
            df.index = df.index + 1
            return df

        except Exception as e:
            logger.error(f"Error in calculate_similarity: {e}")
            return pd.DataFrame()

