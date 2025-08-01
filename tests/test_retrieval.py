# test_retrieval.py
import unittest
from core.retrieval.semantic_matcher import SemanticMatcher

class TestSemanticMatcher(unittest.TestCase):
    def setUp(self):
        self.matcher = SemanticMatcher()
    
    def test_match_semantic(self):
        query = "test query"
        candidates = ["test candidate 1", "test candidate 2"]
        results = self.matcher.match_semantic(query, candidates)
        # 测试逻辑

if __name__ == "__main__":
    unittest.main() 