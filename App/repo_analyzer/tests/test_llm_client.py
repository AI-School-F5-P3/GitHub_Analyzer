import unittest
from unittest.mock import patch, MagicMock
from RAG_analyzer import LLMClient

class TestLLMClient(unittest.TestCase):
    def setUp(self):
        self.llm_client = LLMClient(groq_api_key="test_key")

    @patch('RAG_analyzer.ChatGroq')
    def test_initialize_llm(self, MockChatGroq):
        mock_instance = MockChatGroq.return_value
        self.llm_client._initialize_llm()
        MockChatGroq.assert_called_once_with(api_key="test_key", model_name="mixtral-8x7b-32768", max_retries=0)
        self.assertFalse(self.llm_client.using_ollama)

    @patch('RAG_analyzer.Ollama')
    def test_switch_to_ollama(self, MockOllama):
        mock_instance = MockOllama.return_value
        result = self.llm_client._switch_to_ollama()
        MockOllama.assert_called_once()
        self.assertTrue(result)
        self.assertTrue(self.llm_client.using_ollama)

    @patch('RAG_analyzer.LLMClient._switch_to_ollama')
    @patch('RAG_analyzer.ChatGroq.invoke')
    def test_invoke(self, MockInvoke, MockSwitchToOllama):
        MockInvoke.return_value = MagicMock(content="response content")
        messages = ["message1", "message2"]
        response = self.llm_client.invoke(messages)
        MockInvoke.assert_called_once_with(messages)
        self.assertEqual(response, "response content")

if __name__ == '__main__':
    unittest.main()