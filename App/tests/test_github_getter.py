# tests/test_github_getter.py
import pytest
from github_getter import GitHubAnalyzer

@pytest.fixture
def github_analyzer():
    return GitHubAnalyzer()

def test_clone_repo(github_analyzer):
    repo_url = "https://github.com/AI-School-F5-P3/DS_Grupo3/tree/main"  # Repositorio de prueba
    repo_path = github_analyzer.clone_repo(repo_url)
    assert repo_path is not None
    assert isinstance(repo_path, str)

def test_get_repo_stats(github_analyzer):
    repo_url = "https://github.com/AI-School-F5-P3/DS_Grupo3/tree/main"
    stats = github_analyzer.get_repo_stats(repo_url)
    assert isinstance(stats, dict)
    assert 'commit_count' in stats
    assert 'contributors' in stats
    assert 'languages' in stats

def test_generate_visualizations(github_analyzer):
    repo_url = "https://github.com/AI-School-F5-P3/DS_Grupo3/tree/main"
    stats = github_analyzer.get_repo_stats(repo_url)
    github_analyzer.generate_visualizations(stats)
    # Verifica que se hayan creado los archivos de visualización
    import os
    assert os.path.exists('figures/commits_by_branch.png')
    assert os.path.exists('figures/commits_by_author.png')