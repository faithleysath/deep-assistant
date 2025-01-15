import unittest
import json
import os
from pathlib import Path
from app.tools.builtin.memory import MemoryManager

class TestMemoryManager(unittest.TestCase):
    def setUp(self):
        # 使用测试专用的agent名称
        self.agent_name = "test_agent"
        self.memories_dir = "test_memories"
        self.manager = MemoryManager(self.agent_name, self.memories_dir)
        self.test_file = Path(self.memories_dir) / f"{self.agent_name}.json"
        
    def tearDown(self):
        # 清理测试文件
        if self.test_file.exists():
            os.remove(self.test_file)
        if Path(self.memories_dir).exists():
            os.rmdir(self.memories_dir)

    def test_singleton_pattern(self):
        manager1 = MemoryManager(self.agent_name)
        manager2 = MemoryManager(self.agent_name)
        self.assertIs(manager1, manager2)

    def test_save_and_retrieve_memory(self):
        # 测试保存和获取内存
        key = "test.key"
        value = ["value1", "value2"]
        
        # 保存新内存
        result = self.manager.save_memory(key, value)
        self.assertEqual(result["status"], "success")
        
        # 验证文件存在
        self.assertTrue(self.test_file.exists())
        
        # 读取文件验证内容
        with open(self.test_file, "r") as f:
            data = json.load(f)
            self.assertIn(key, data)
            self.assertEqual(set(data[key]["value"]), set(value))

    def test_update_memory(self):
        # 测试更新内存
        key = "test.key"
        initial_value = ["value1"]
        updated_value = ["value2"]
        
        # 初始保存
        self.manager.save_memory(key, initial_value)
        
        # 更新内存
        result = self.manager.save_memory(key, updated_value, override=False)
        self.assertEqual(result["status"], "success")
        
        # 验证更新后的值
        with open(self.test_file, "r") as f:
            data = json.load(f)
            self.assertEqual(set(data[key]["value"]), set(initial_value + updated_value))

    def test_delete_memory(self):
        # 测试删除内存
        key = "test.key"
        value = ["value1"]
        
        # 先保存
        self.manager.save_memory(key, value)
        
        # 删除
        result = self.manager.delete_memory(key)
        self.assertEqual(result["status"], "success")
        
        # 验证文件内容
        with open(self.test_file, "r") as f:
            data = json.load(f)
            self.assertNotIn(key, data)

    def test_corrupted_json_file(self):
        # 测试文件损坏情况
        # 创建损坏的json文件
        with open(self.test_file, "w") as f:
            f.write("{invalid json")
        
        # 尝试加载
        new_manager = MemoryManager(self.agent_name, self.memories_dir)
        self.assertEqual(len(new_manager.memories), 0)

    def test_get_summary(self):
        # 测试获取摘要
        key1 = "key1"
        value1 = ["value1"]
        key2 = "key2"
        value2 = ["value2"]
        
        self.manager.save_memory(key1, value1)
        self.manager.save_memory(key2, value2)
        
        summary = self.manager.get_summary()
        self.assertIn(self.agent_name, summary)
        self.assertIn(key1, summary)
        self.assertIn(key2, summary)
        self.assertIn(str(len(value1)), summary)
        self.assertIn(str(len(value2)), summary)

if __name__ == "__main__":
    unittest.main()
