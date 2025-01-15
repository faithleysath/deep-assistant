import unittest
from unittest.mock import patch, mock_open
from datetime import datetime
from app.tools.builtin.memory import Memory, MemoryManager
import os
import shutil

class TestMemory(unittest.TestCase):
    def test_memory_initialization(self):
        mem = Memory("test_key", {"value1", "value2"})
        self.assertEqual(mem.key, "test_key")
        self.assertEqual(mem.value, {"value1", "value2"})
        self.assertIsNotNone(mem.created_at)
        self.assertIsNotNone(mem.modified_at)

    def test_memory_to_dict(self):
        test_time = "2023-01-01T00:00:00"
        mem = Memory("test_key", {"value1"}, created_at=test_time, modified_at=test_time)
        expected = {
            "key": "test_key",
            "value": ["value1"],
            "created_at": test_time,
            "modified_at": test_time
        }
        self.assertEqual(mem.to_dict(), expected)

class TestMemoryManager(unittest.TestCase):
    def setUp(self):
        self.test_agent = "test_agent"
        self.memories_dir = "memories"
        self.test_file = f"{self.memories_dir}/{self.test_agent}.json"
        
        # Clean up before each test
        if os.path.exists(self.memories_dir):
            shutil.rmtree(self.memories_dir)

    def tearDown(self):
        # Clean up after each test
        if os.path.exists(self.memories_dir):
            shutil.rmtree(self.memories_dir)

    def test_singleton_pattern(self):
        manager1 = MemoryManager(self.test_agent)
        manager2 = MemoryManager(self.test_agent)
        self.assertIs(manager1, manager2)

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_save_memory_new(self, mock_json_dump, mock_file):
        manager = MemoryManager(self.test_agent)
        result = manager.save_memory("new_key", ["value1"])
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], 
                       f"Created new memory 'new_key' for agent '{self.test_agent}'")
        self.assertIn("new_key", manager.memories)
        mock_file.assert_called_once_with(self.test_file, "w", encoding="utf-8")
        mock_json_dump.assert_called_once()

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_save_memory_update(self, mock_json_dump, mock_file):
        manager = MemoryManager(self.test_agent)
        manager.save_memory("existing_key", ["value1"])
        result = manager.save_memory("existing_key", ["value2"])
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], 
                       f"Updated memory 'existing_key' for agent '{self.test_agent}'")
        self.assertEqual(len(manager.memories["existing_key"].value), 2)
        self.assertEqual(mock_json_dump.call_count, 2)

    @patch("builtins.open", new_callable=mock_open, read_data='{"test_key": {"key": "test_key", "value": ["value1"], "created_at": "2023-01-01T00:00:00", "modified_at": "2023-01-01T00:00:00"}}')
    @patch("json.load")
    def test_load_memories(self, mock_json_load, mock_file):
        mock_json_load.return_value = {
            "test_key": {
                "key": "test_key",
                "value": ["value1"],
                "created_at": "2023-01-01T00:00:00",
                "modified_at": "2023-01-01T00:00:00"
            }
        }
        
        manager = MemoryManager(self.test_agent)
        self.assertIn("test_key", manager.memories)
        self.assertEqual(manager.memories["test_key"].value, {"value1"})
        mock_file.assert_called_once_with(self.test_file, "r", encoding="utf-8")
        mock_json_load.assert_called_once()

    def test_delete_memory(self):
        manager = MemoryManager(self.test_agent)
        manager.save_memory("to_delete", ["value1"])
        
        result = manager.delete_memory("to_delete")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], 
                       f"Deleted memory 'to_delete' for agent '{self.test_agent}'")
        self.assertNotIn("to_delete", manager.memories)

    def test_delete_nonexistent_memory(self):
        manager = MemoryManager(self.test_agent)
        result = manager.delete_memory("nonexistent")
        
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], 
                       f"Memory 'nonexistent' not found for agent '{self.test_agent}'")

    def test_get_summary(self):
        manager = MemoryManager(self.test_agent)
        manager.save_memory("key1", ["value1"])
        manager.save_memory("key2", ["value2"])
        
        summary = manager.get_summary()
        self.assertIn("Agent: test_agent", summary)
        self.assertIn("Total Memories: 2", summary)
        self.assertIn("- key1", summary)
        self.assertIn("- key2", summary)

if __name__ == "__main__":
    unittest.main()
