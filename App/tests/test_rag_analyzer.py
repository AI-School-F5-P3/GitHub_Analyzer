# tests/test_rag_analyzer.py
import pytest
from unittest.mock import patch, MagicMock
from RAG_analyzer import GitHubRAGAnalyzer

@pytest.fixture
def rag_analyzer():
    return GitHubRAGAnalyzer()

def test_analyze_requirements_completion(rag_analyzer):
    # Simulamos el comportamiento de las dependencias
    with patch.object(rag_analyzer.github_analyzer, 'clone_repo') as mock_clone_repo, \
         patch.object(rag_analyzer.github_analyzer, 'get_repo_stats') as mock_get_repo_stats, \
         patch.object(rag_analyzer.rag_processor, 'process_repository') as mock_process_repo, \
         patch.object(rag_analyzer.rag_processor, 'process_briefing') as mock_process_briefing, \
         patch.object(rag_analyzer.llm_client, 'invoke') as mock_llm_invoke:

        # Configuramos los valores simulados
        mock_clone_repo.return_value = "/fake/path/to/cloned_repo"
        mock_get_repo_stats.return_value = {
            "files": 10,
            "lines_of_code": 500,
            "languages": ["Python"],
        }
        mock_process_repo.return_value = True
        mock_process_briefing.return_value = True
        mock_llm_invoke.return_value = "Análisis simulado del repositorio."

        # Llamamos a la función bajo prueba
        repo_url = "https://github.com/AI-School-F5-P3/DS_Grupo3/tree/main"
        briefing_path = "../../briefings/Briefing_proyecto_Data_Scientist.pdf"
        analysis_results = rag_analyzer.analyze_requirements_completion(repo_url, briefing_path)

        # Verificamos que el resultado sea un diccionario
        assert isinstance(analysis_results, dict)

        # Verificamos que las claves esperadas estén presentes
        assert 'repository_stats' in analysis_results
        assert 'tier_analysis' in analysis_results

        # Verificamos que los métodos simulados fueron llamados
        mock_clone_repo.assert_called_once_with(repo_url)
        mock_get_repo_stats.assert_called_once_with(repo_url)
        mock_process_repo.assert_called_once_with("/fake/path/to/cloned_repo")
        mock_process_briefing.assert_called_once_with(briefing_path)
        mock_llm_invoke.assert_called_once()

def test_llm_client_invoke(rag_analyzer):
    # Simulamos el comportamiento del LLMClient
    with patch.object(rag_analyzer.llm_client, 'invoke') as mock_llm_invoke:
        # Configuramos el valor simulado
        mock_llm_invoke.return_value = "Respuesta simulada del LLM."

        # Llamamos a la función bajo prueba
        messages = [{"role": "user", "content": "Hola, ¿cómo estás?"}]
        response = rag_analyzer.llm_client.invoke(messages)

        # Verificamos que la respuesta sea un string no vacío
        assert isinstance(response, str)
        assert len(response) > 0

        # Verificamos que el método simulado fue llamado
        mock_llm_invoke.assert_called_once_with(messages)