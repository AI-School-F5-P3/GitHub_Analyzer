# tests/test_briefing_analyzer.py
import pytest
from briefing_analyzer import ComplianceAnalyzer

@pytest.fixture
def compliance_analyzer():
    return ComplianceAnalyzer()

def test_extract_text_from_pdf(compliance_analyzer):
    briefing_path = "../../briefings/Briefing_proyecto_Data_Scientist.pdf"  # Briefing de prueba
    text = compliance_analyzer.extract_text_from_pdf(briefing_path)
    assert isinstance(text, str)
    assert len(text) > 0

def test_check_compliance_with_briefing(compliance_analyzer):
    repo_docs = ["Este es un documento de prueba."]
    briefing_text = "Este es el texto del briefing."
    compliance_results = compliance_analyzer.check_compliance_with_briefing(repo_docs, briefing_text)
    assert isinstance(compliance_results, list)
    assert len(compliance_results) > 0