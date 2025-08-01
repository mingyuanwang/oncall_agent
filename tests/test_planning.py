# test_planning.py
import unittest
from core.planning.planner import Planner

class TestPlanner(unittest.TestCase):
    def setUp(self):
        self.planner = Planner()
    
    def test_plan_task(self):
        task = "test task"
        context = {"context": "test"}
        plan = self.planner.plan_task(task, context)
        # 测试逻辑

if __name__ == "__main__":
    unittest.main() 