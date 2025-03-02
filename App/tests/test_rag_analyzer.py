# tests/test_rag_analyzer.py
import pytest
from RAG_analyzer import GitHubRAGAnalyzer

@pytest.fixture
def rag_analyzer():
    return GitHubRAGAnalyzer()

def test_analyze_requirements_completion(rag_analyzer):
    repo_url = "https://github.com/AI-School-F5-P3/DS_Grupo3/tree/main"  # Repositorio de prueba
    briefing_path = "../../briefings/Briefing_proyecto_Data_Scientist.pdf"  # Briefing de prueba
    analysis_results = rag_analyzer.analyze_requirements_completion(repo_url, briefing_path)
    assert isinstance(analysis_results, dict)
    assert 'repository_stats' in analysis_results
    assert 'tier_analysis' in analysis_results

def test_llm_client_invoke(rag_analyzer):
    messages = [{"role": "user", "content": "Hola, ¿cómo estás?"}]
    response = rag_analyzer.llm_client.invoke(messages)
    assert isinstance(response, str)
    assert len(response) > 0