# tests/test_rag_process.py
import pytest
from RAG_process import RepoRAGProcessor

@pytest.fixture
def rag_processor():
    return RepoRAGProcessor()

def test_process_repository(rag_processor):
    repo_path = "../cloned_repo/"  # Repositorio clonado de prueba
    success = rag_processor.process_repository(repo_path)
    assert success is True

def test_process_briefing(rag_processor):
    briefing_path = "../../briefings/Briefing_proyecto_Data_Scientist.pdf"  # Asegúrate de tener un briefing de prueba
    success = rag_processor.process_briefing(briefing_path)
    assert success is True