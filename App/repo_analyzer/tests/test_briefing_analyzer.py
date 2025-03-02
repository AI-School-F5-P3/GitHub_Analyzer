import unittest
from Briefing_analyzer import ComplianceAnalyzer

class TestComplianceAnalyzer(unittest.TestCase):
    def setUp(self):
        self.compliance_analyzer = ComplianceAnalyzer()

    def test_analyze_compliance(self):
        result = self.compliance_analyzer.analyze_compliance("path/to/briefing")
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()