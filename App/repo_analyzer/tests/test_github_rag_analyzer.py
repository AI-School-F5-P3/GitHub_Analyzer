import unittest
from unittest.mock import patch, MagicMock
from RAG_analyzer import GitHubRAGAnalyzer

class TestGitHubRAGAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = GitHubRAGAnalyzer(api_key="test_key")

    @patch('RAG_analyzer.GitHubAnalyzer.clone_repo')
    @patch('RAG_analyzer.RepoRAGProcessor.process_repository')
    @patch('RAG_analyzer.RepoRAGProcessor.process_briefing')
    @patch('RAG_analyzer.GitHubAnalyzer.get_repo_stats')
    def test_analyze_requirements_completion(self, MockGetRepoStats, MockProcessBriefing, MockProcessRepository, MockCloneRepo):
        MockCloneRepo.return_value = "/path/to/repo"
        MockProcessRepository.return_value = True
        MockProcessBriefing.return_value = True
        MockGetRepoStats.return_value = {"stars": 10, "forks": 5}

        result = self.analyzer.analyze_requirements_completion("https://github.com/test/repo", "/path/to/briefing")

        self.assertEqual(result["status"], "success")
        self.assertIn("repository_stats", result)
        self.assertIn("tier_analysis", result)

if __name__ == '__main__':
    unittest.main()