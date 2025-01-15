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
        # Mock agent initialization
        agent = Agent("test_agent")
        agent.memory_manager = self.mock_memory_manager
        agent.uniform_prompt = "Mocked uniform prompt"
        agent.special_prompts = "Mocked special prompts"
        
        # Mock response without tool calls
        mock_response = AsyncMock()
        mock_message = MagicMock()
        mock_message.content = "Final response"
        mock_message.tool_calls = None
        mock_response.choices = [MagicMock(message=mock_message)]
        self.mock_completion.create.return_value = mock_response
        
        # Test think_once
        messages_history = [{"role": "user", "content": "Test message"}]
        result = await agent.think_once(messages_history)
        
        # Verify message construction
        expected_messages = [
            {"role": "system", "content": "Mocked uniform prompt\nMocked special prompts"},
            {"role": "system", "content": "Mocked memory summary"},
            *messages_history
        ]
        self.mock_completion.create.assert_called_once_with(
            model="deepseek-chat",
            messages=expected_messages,
            tools=None
        )
        self.assertEqual(result, "Final response")
        
    async def test_tool_calls(self):
        # Mock agent initialization
        agent = Agent("test_agent")
        agent.memory_manager = self.mock_memory_manager
        agent.uniform_prompt = "Mocked uniform prompt"
        agent.special_prompts = "Mocked special prompts"
        
        # Mock tool call response
        mock_tool_call = MagicMock()
        mock_tool_call.function.name = "mock_tool"
        mock_tool_call.function.arguments = json.dumps({"param": "value"})
        mock_tool_call.id = "tool_call_id"
        
        # First response with tool call
        mock_response1 = AsyncMock()
        mock_message1 = MagicMock()
        mock_message1.content = None
        mock_message1.tool_calls = [mock_tool_call]
        mock_response1.choices = [MagicMock(message=mock_message1)]
        
        # Final response
        mock_response2 = AsyncMock()
        mock_message2 = MagicMock()
        mock_message2.content = "Final response"
        mock_message2.tool_calls = None
        mock_response2.choices = [MagicMock(message=mock_message2)]
        
        # Set up mock sequence
        self.mock_completion.create.side_effect = [mock_response1, mock_response2]
        
        # Test think_once with tool calls
        messages_history = [{"role": "user", "content": "Test message"}]
        result = await agent.think_once(messages_history)
        
        # Verify tool call handling
        expected_tool_result = {"status": "success"}
        expected_messages = [
            {"role": "system", "content": "Mocked uniform prompt\nMocked special prompts"},
            {"role": "system", "content": "Mocked memory summary"},
            *messages_history,
            mock_message1,
            {
                "role": "tool",
                "content": json.dumps(expected_tool_result),
                "tool_call_id": "tool_call_id"
            }
        ]
        
        # Verify final response
        self.assertEqual(result, "Final response")
        self.mock_completion.create.assert_called_with(
            model="deepseek-chat",
            messages=expected_messages,
            tools=None
        )
        
        # Test error handling
        self.mock_tool_manager.exports["mock_tool"].side_effect = Exception("Test error")
        self.mock_completion.create.side_effect = [mock_response1, mock_response2]
        result = await agent.think_once(messages_history)
        self.assertEqual(result, "Final response")

if __name__ == '__main__':
    unittest.main()
