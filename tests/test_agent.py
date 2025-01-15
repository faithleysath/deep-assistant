import unittest
from unittest.mock import AsyncMock, patch, MagicMock
import json
from app.agent import Agent, send_messages
from app.tools.builtin.memory import MemoryManager

class TestAgent(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # Mock AsyncOpenAI client
        self.mock_client = AsyncMock()
        self.mock_chat = AsyncMock()
        self.mock_client.chat = self.mock_chat
        self.mock_completion = AsyncMock()
        self.mock_chat.completions = self.mock_completion
        
        # Patch the OpenAI client
        self.client_patcher = patch('app.agent.AsyncOpenAI', return_value=self.mock_client)
        self.client_patcher.start()
        
        # Mock MemoryManager
        self.mock_memory_manager = MagicMock(spec=MemoryManager)
        self.mock_memory_manager.get_summary.return_value = "Mocked memory summary"
        
        # Mock tool manager
        self.mock_tool_manager = MagicMock()
        self.mock_tool_manager.exports = {
            'mock_tool': MagicMock(return_value={'status': 'success'})
        }
        
    def tearDown(self):
        self.client_patcher.stop()
    
    async def test_send_messages(self):
        # Mock response
        mock_response = AsyncMock()
        mock_message = MagicMock()
        mock_message.content = "Mocked response"
        mock_message.tool_calls = None
        mock_response.choices = [MagicMock(message=mock_message)]
        self.mock_completion.create.return_value = mock_response
        
        # Test without tools
        messages = [{"role": "user", "content": "Test message"}]
        result = await send_messages(messages)
        
        # Verify
        self.mock_completion.create.assert_called_once_with(
            model="deepseek-chat",
            messages=messages,
            tools=None
        )
        self.assertEqual(result.content, "Mocked response")
        
        # Test with tools
        mock_tools = [{"name": "mock_tool"}]
        await send_messages(messages, tools=mock_tools)
        self.mock_completion.create.assert_called_with(
            model="deepseek-chat",
            messages=messages,
            tools=mock_tools
        )
        
    async def test_agent_think_once(self):
        # Test Agent.think_once method
        pass
        
    async def test_tool_calls(self):
        # Test tool call handling
        pass

if __name__ == '__main__':
    unittest.main()
