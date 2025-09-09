try:
    import fitz
    import docx
    from sentence_transformers import SentenceTransformer
    import numpy as np
    import pandas as pd
    import streamlit as st
    print("All imports successful!")
except ImportError as e:
    print(f"Import error: {e}")