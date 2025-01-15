import json
import pytest
import os
from pathlib import Path
from datetime import datetime
from app.tools.builtin.memory import Memory, MemoryManager

@pytest.fixture
def temp_memory_dir(tmp_path):
    """Fixture to create temporary memory directory"""
    memory_dir = tmp_path / "memories"
    memory_dir.mkdir()
    return memory_dir

@pytest.fixture
def memory_manager(temp_memory_dir, monkeypatch):
    """Fixture to create MemoryManager instance with temporary directory"""
    monkeypatch.setattr("app.tools.builtin.memory.MemoryManager.memories_dir", temp_memory_dir)
    return MemoryManager("test_agent")

def test_memory_initialization():
    """Test Memory class initialization"""
    key = "test_key"
    value = {"data": "test"}
    memory = Memory(key, {value})
    
    assert memory.key == key
    assert value in memory.value
    assert isinstance(memory.created_at, str)
    assert isinstance(memory.modified_at, str)

def test_memory_to_dict():
    """Test Memory to_dict method"""
    key = "test_key"
    value = {"data": "test"}
    memory = Memory(key, {value})
    memory_dict = memory.to_dict()
    
    assert memory_dict["key"] == key
    assert memory_dict["value"] == [value]
    assert "created_at" in memory_dict
    assert "modified_at" in memory_dict

def test_memory_manager_singleton():
    """Test MemoryManager singleton pattern"""
    manager1 = MemoryManager("test_agent")
    manager2 = MemoryManager("test_agent")
    
    assert manager1 is manager2
    assert manager1.agent_name == "test_agent"

def test_save_and_load_memory(memory_manager):
    """Test saving and loading memories"""
    # Save memory
    key = "test_key"
    value = ["value1", "value2"]
    result = memory_manager.save_memory(key, value)
    
    assert result["status"] == "success"
    assert key in memory_manager.memories
    
    # Load memory
    new_manager = MemoryManager("test_agent")
    assert key in new_manager.memories
    assert set(new_manager.memories[key].value) == set(value)

def test_delete_memory(memory_manager):
    """Test deleting memories"""
    key = "test_key"
    value = ["value1", "value2"]
    memory_manager.save_memory(key, value)
    
    # Delete memory
    result = memory_manager.delete_memory(key)
    assert result["status"] == "success"
    assert key not in memory_manager.memories
    
    # Try to delete non-existent memory
    result = memory_manager.delete_memory("non_existent_key")
    assert result["status"] == "error"

def test_get_summary(memory_manager):
    """Test getting memory summary"""
    key1 = "key1"
    value1 = ["value1"]
    key2 = "key2"
    value2 = ["value2"]
    
    memory_manager.save_memory(key1, value1)
    memory_manager.save_memory(key2, value2)
    
    summary = memory_manager.get_summary()
    assert "Agent: test_agent" in summary
    assert "Total Memories: 2" in summary
    assert key1 in summary
    assert key2 in summary

def test_corrupted_json_file(memory_manager, temp_memory_dir):
    """Test handling of corrupted JSON file"""
    # Create corrupted JSON file
    file_path = temp_memory_dir / "test_agent.json"
    with open(file_path, "w") as f:
        f.write("invalid json")
    
    # Try to load corrupted file
    new_manager = MemoryManager("test_agent")
    assert len(new_manager.memories) == 0

def test_empty_json_file(memory_manager, temp_memory_dir):
    """Test handling of empty JSON file"""
    # Create empty JSON file
    file_path = temp_memory_dir / "test_agent.json"
    with open(file_path, "w") as f:
        f.write("")
    
    # Try to load empty file
    new_manager = MemoryManager("test_agent")
    assert len(new_manager.memories) == 0

def test_missing_json_file(memory_manager):
    """Test handling of missing JSON file"""
    # Ensure file doesn't exist
    file_path = memory_manager.file_path
    if file_path.exists():
        file_path.unlink()
    
    # Try to load non-existent file
    new_manager = MemoryManager("test_agent")
    assert len(new_manager.memories) == 0
