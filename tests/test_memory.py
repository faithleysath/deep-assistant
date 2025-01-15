import unittest
from datetime import datetime
from app.tools.builtin.memory import Memory, MemoryManager

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

    def test_memory_with_different_value_types(self):
        # 测试不同类型value
        mem1 = Memory("key1", "string_value")
        mem2 = Memory("key2", 123)
        mem3 = Memory("key3", [1, 2, 3])
        
        self.assertEqual(mem1.value, "string_value")
        self.assertEqual(mem2.value, 123)
        self.assertEqual(mem3.value, [1, 2, 3])

    def test_memory_manager_exceptions(self):
        # 测试异常情况
        with self.assertRaises(ValueError):
            self.manager.save_memory(None, "value")
            
        with self.assertRaises(ValueError):
            self.manager.save_memory("key", None)
            
        with self.assertRaises(KeyError):
            self.manager.get_memory("non_existent_key")

    def test_memory_persistence(self):
        # 测试持久化功能
        self.manager.save_memory("persistent_key", "persistent_value")
        self.manager.save_to_file()
        
        new_manager = MemoryManager("test_agent")
        new_manager.load_from_file()
        self.assertEqual(new_manager.get_memory("persistent_key").value, "persistent_value")

    def test_update_memory(self):
        # 测试更新记忆
        self.manager.save_memory("update_key", "old_value")
        self.manager.save_memory("update_key", "new_value")
        self.assertEqual(self.manager.get_memory("update_key").value, "new_value")

    def test_batch_operations(self):
        # 测试批量操作
        memories = {
            "batch_key1": "value1",
            "batch_key2": "value2",
            "batch_key3": "value3"
        }
        self.manager.save_memories(memories)
        self.assertEqual(len(self.manager.memories), 3)
        
        self.manager.delete_memories(["batch_key1", "batch_key2"])
        self.assertEqual(len(self.manager.memories), 1)

if __name__ == "__main__":
    unittest.main()
