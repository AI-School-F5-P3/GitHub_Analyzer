import unittest
from RAG_process import RepoRAGProcessor

class TestRepoRAGProcessor(unittest.TestCase):
    def setUp(self):
        self.rag_processor = RepoRAGProcessor(embedding_model_name="sentence-transformers/all-MiniLM-L6-v2")

    def test_process_repository(self):
        result = self.rag_processor.process_repository("path/to/repo")
        self.assertTrue(result)

    def test_process_briefing(self):
        result = self.rag_processor.process_briefing("path/to/briefing")
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()