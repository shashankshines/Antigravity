import unittest
from unittest.mock import MagicMock, patch
from email_agent import EmailAgent

class TestEmailAgent(unittest.TestCase):
    def test_mock_initialization(self):
        agent = EmailAgent(api_key="dummy", mock_mode=True)
        self.assertTrue(agent.mock_mode)

    @patch('email_agent.genai.GenerativeModel')
    def test_generate_email(self, mock_model_class):
        # Setup mock
        mock_model_instance = MagicMock()
        mock_model_class.return_value = mock_model_instance
        mock_response = MagicMock()
        mock_response.text = "Subject: Test\n\nBody: This is a test email."
        mock_model_instance.generate_content.return_value = mock_response

        agent = EmailAgent(api_key="dummy", mock_mode=True)
        email_content = agent.generate_email("Test Subject")
        
        self.assertIn("This is a test email", email_content)

    def test_send_email_mock(self):
        agent = EmailAgent(api_key="dummy", mock_mode=True)
        # Capture stdout to verify print
        with patch('builtins.print') as mock_print:
            result = agent.send_email("test@example.com", "Subject", "Body")
            self.assertTrue(result)
            # Check if print was called (mock sending)
            self.assertTrue(mock_print.called)

if __name__ == '__main__':
    unittest.main()
