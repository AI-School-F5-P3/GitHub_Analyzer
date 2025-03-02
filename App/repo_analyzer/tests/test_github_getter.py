import unittest
from unittest.mock import patch, MagicMock
from github_getter import GitHubAnalyzer

class TestGitHubAnalyzer(unittest.TestCase):
    def setUp(self):
        self.github_analyzer = GitHubAnalyzer()

    @patch('github_getter.GitHub')
    def test_clone_repo(self, MockGitHub):
        mock_instance = MockGitHub.return_value
        mock_instance.get_repo.return_value = MagicMock(clone_url="https://github.com/test/repo")
        repo_path = self.github_analyzer.clone_repo("https://github.com/test/repo")
        self.assertEqual(repo_path, "/path/to/repo")

    @patch('github_getter.GitHub')
    def test_get_repo_stats(self, MockGitHub):
        mock_instance = MockGitHub.return_value
        mock_instance.get_repo.return_value = MagicMock(stargazers_count=10, forks_count=5)
        stats = self.github_analyzer.get_repo_stats("https://github.com/test/repo")
        self.assertEqual(stats, {"stars": 10, "forks": 5})

if __name__ == '__main__':
    unittest.main()