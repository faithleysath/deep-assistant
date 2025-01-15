import unittest
from datetime import datetime
from .memory import Memory, MemoryManager

class TestMemory(unittest.TestCase):
    def test_memory_creation(self):
        mem = Memory("test_key", {"value1", "value2"})
        self.assertEqual(mem.key, "test_key")
        self.assertEqual(mem.value, {"value1", "value2"})
        self.assertIsInstance(mem.created_at, str)
        self.assertIsInstance(mem.modified_at, str)

    def test_memory_to_dict(self):
        mem = Memory("test_key", {"value1", "value2"})
        mem_dict = mem.to_dict()
        self.assertEqual(mem_dict["key"], "test_key")
        self.assertEqual(set(mem_dict["value"]), {"value1", "value2"})
        self.assertIsInstance(mem_dict["created_at"], str)
        self.assertIsInstance(mem_dict["modified_at"], str)

class TestMemoryManager(unittest.TestCase):
    def setUp(self):
        self.manager = MemoryManager("test_agent")
        self.manager.memories = {}  # 清空记忆

    def test_save_and_get_memory(self):
        # 测试保存和获取记忆
        self.manager.save_memory("key1", ["value1"])
        self.assertEqual(len(self.manager.memories), 1)
        
        # 测试get_summary
        summary = self.manager.get_summary()
        self.assertIn("Agent: test_agent", summary)
        self.assertIn("Total Memories: 1", summary)
        self.assertIn("- key1", summary)
        self.assertIn("• value1", summary)

    def test_delete_memory(self):
        self.manager.save_memory("key1", ["value1"])
        self.manager.delete_memory("key1")
        self.assertEqual(len(self.manager.memories), 0)

    def test_multiple_memories_summary(self):
        # 测试多个记忆的摘要格式
        self.manager.save_memory("key1", ["value1"])
        self.manager.save_memory("key2", ["value2", "value3"])
        
        summary = self.manager.get_summary()
        self.assertIn("Total Memories: 2", summary)
        self.assertIn("- key1", summary)
        self.assertIn("- key2", summary)
        self.assertIn("• value1", summary)
        self.assertIn("• value2", summary)
        self.assertIn("• value3", summary)

    def tearDown(self):
        # 清理测试文件
        if self.manager.file_path.exists():
            self.manager.file_path.unlink()

if __name__ == "__main__":
    unittest.main()
