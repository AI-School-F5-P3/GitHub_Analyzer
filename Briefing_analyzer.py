import fitz
import logging
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from sklearn.metrics.pairwise import cosine_similarity

class ComplianceAnalyzer:
    def __init__(self):
        """Initialize ComplianceAnalyzer with logging configuration"""
        self.logger = logging.getLogger(__name__)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.threshold = 0.7  # Minimum similarity for compliance

    def extract_text_from_pdf(self, pdf_path):
        """
        Extracts text from a given PDF file.
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            str: Extracted text from PDF
        """
        text = ""
        try:
            doc = fitz.open(pdf_path)
            text = " ".join([page.get_text() for page in doc])
            self.logger.info(f"Successfully extracted text from {pdf_path}")
        except Exception as e:
            self.logger.error(f"Error extracting text from PDF: {e}")
        return text

    def check_compliance_with_briefing(self, repo_docs, briefing_text):
        """
        Compares repository content with briefing requirements using vector embeddings.
        
        Args:
            repo_docs (list): List of repository document texts
            briefing_text (str): Text from briefing document
            
        Returns:
            list: List of dictionaries containing compliance results
        """
        try:
            # Convert briefing text to embeddings
            briefing_embedding = self.embeddings.embed_query(briefing_text)

            # Convert repository text to embeddings
            repo_embeddings = [self.embeddings.embed_query(doc) for doc in repo_docs]

            # Compute similarity scores
            similarities = cosine_similarity([briefing_embedding], repo_embeddings)[0]

            compliance_results = []

            for idx, sim in enumerate(similarities):
                compliance_results.append({
                    "section": repo_docs[idx][:100],  
                    "similarity": round(sim * 100, 2),
                    "compliant": sim >= self.threshold
                })

            self.logger.info(f"Completed compliance check for {len(repo_docs)} documents")
            return compliance_results

        except Exception as e:
            self.logger.error(f"Error in compliance check: {e}")
            return []