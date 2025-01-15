import unittest
from app.tools.builtin.memory import MemoryManager

class TestMemoryManager(unittest.TestCase):
    def setUp(self):
        self.agent_name = "test_agent"
        self.memory_manager = MemoryManager(self.agent_name)
        
    def test_save_and_retrieve_memory(self):
        # 测试保存和获取记忆
        key = "user.preferences.theme"
        value = ["dark", "light"]
        
        # 保存记忆
        result = self.memory_manager.save_memory(key, value)
        self.assertEqual(result["status"], "success")
        
        # 获取摘要并验证
        summary = self.memory_manager.get_summary()
        self.assertEqual(summary["agent_name"], self.agent_name)
        self.assertEqual(summary["total_memories"], 1)
        
        # 验证保存的内容
        memory = summary["all_memories"][0]
        self.assertEqual(memory["key"], key)
        self.assertEqual(set(memory["value"]), set(value))
        
    def test_update_memory(self):
        # 测试更新记忆
        key = "user.preferences.language"
        initial_value = ["English"]
        updated_value = ["English", "Chinese"]
        
        # 初始保存
        self.memory_manager.save_memory(key, initial_value)
        
        # 更新记忆
        result = self.memory_manager.save_memory(key, updated_value)
        self.assertEqual(result["status"], "success")
        self.assertIn("Updated", result["message"])
        
        # 验证更新后的内容
        summary = self.memory_manager.get_summary()
        memory = summary["all_memories"][0]
        self.assertEqual(set(memory["value"]), set(updated_value))
        
    def test_delete_memory(self):
        # 测试删除记忆
        key = "temp.memory"
        value = ["test data"]
        
        # 保存记忆
        self.memory_manager.save_memory(key, value)
        
        # 删除记忆
        result = self.memory_manager.delete_memory(key)
        self.assertEqual(result["status"], "success")
        
        # 验证删除
        summary = self.memory_manager.get_summary()
        self.assertEqual(summary["total_memories"], 0)
        
    def tearDown(self):
        # 清理测试数据
        self.memory_manager.delete_memory("user.preferences.theme")
        self.memory_manager.delete_memory("user.preferences.language")
        self.memory_manager.delete_memory("temp.memory")

if __name__ == "__main__":
    unittest.main()
