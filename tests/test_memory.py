# test_memory.py
import unittest
from core.memory.episodic_memory import EpisodicMemory

class TestEpisodicMemory(unittest.TestCase):
    def setUp(self):
        self.memory = EpisodicMemory()
    
    def test_add_episode(self):
        episode = {"action": "test", "result": "success"}
        self.memory.add_episode(episode)
        self.assertEqual(len(self.memory.short_term), 1)

if __name__ == "__main__":
    unittest.main() 