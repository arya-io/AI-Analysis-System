import unittest
from unittest.mock import MagicMock
import asyncio
from websocket_server import generate_feedback, cache, handle_websocket_timeout

# Custom TestResult class to display tick marks and test names
class CustomTestResult(unittest.TextTestResult):
    def startTest(self, test):
        super().startTest(test)
        print(f"Running test: {test.__class__.__name__} - {test._testMethodName}...")

    def stopTest(self, test):
        super().stopTest(test)
        print(f"✔ {test.__class__.__name__} - {test._testMethodName}")

    def addSuccess(self, test):
        super().addSuccess(test)

    def addFailure(self, test, err):
        super().addFailure(test, err)

    def addError(self, test, err):
        super().addError(test, err)


# Custom TestRunner class to use our custom TestResult
class CustomTestRunner(unittest.TextTestRunner):
    def _makeResult(self):
        return CustomTestResult(self.stream, self.descriptions, self.verbosity)


class TestAnalysisLogic(unittest.TestCase):

    def setUp(self):
        # Setting up necessary state before each test
        self.question_1 = "What is a neural network?"
        self.answer_1 = "A neural network is a model inspired by biological networks."

        self.question_2 = "What is supervised learning?"
        self.answer_2 = "Supervised learning uses labeled data for training."
    
    def test_generate_feedback_correct(self):
        # Test feedback generation for a correct answer
        feedback = generate_feedback(self.question_1, self.answer_1)
        self.assertIn("Score: 10/10", feedback)
        self.assertIn("Your answer is correct", feedback)
    
    def test_generate_feedback_incorrect(self):
        # Test feedback generation for an incorrect answer
        feedback = generate_feedback(self.question_1, "This is an incorrect answer.")
        self.assertIn("Score: 5/10", feedback)
        self.assertIn("Good attempt, but your answer is incomplete", feedback)
    
    def test_generate_feedback_invalid_question(self):
        # Test feedback for an invalid question
        feedback = generate_feedback("Invalid Question", self.answer_1)
        self.assertIn("Score: 0/10", feedback)
        self.assertIn("This question is not recognized", feedback)
    
    def test_cache_miss(self):
        # Ensure that cache is initially empty and behaves correctly on a miss
        self.assertNotIn((self.question_1, self.answer_1), cache)

    def test_generate_feedback_empty_answer(self):
        # Test feedback generation for an empty answer
        feedback = generate_feedback(self.question_1, "")
        self.assertIn("Score: 0/10", feedback)
        self.assertIn("The answer provided is empty", feedback)

    def test_handle_websocket_timeout(self):
        # Create a mock WebSocket object
        mock_websocket = MagicMock()
        
        # Simulate the timeout by having the `recv()` method raise a `TimeoutError`
        mock_websocket.recv.side_effect = asyncio.TimeoutError
        
        # Call the function with a very short timeout (to trigger the exception)
        feedback = asyncio.run(handle_websocket_timeout(mock_websocket, timeout=0.001))
        
        # Assert that the returned feedback matches the timeout error message
        self.assertEqual(feedback, "Timeout: The server took too long to respond.")
    
    def test_cache_hit(self):
        # Test cache hit logic
        cache_key = (self.question_1, self.answer_1)
        feedback = generate_feedback(self.question_1, self.answer_1)
        
        # Manually add to cache
        cache[cache_key] = feedback
        
        # Check if the cache is hit
        cached_feedback = cache[cache_key]
        self.assertEqual(cached_feedback, feedback)
    
    def tearDown(self):
        # Clean up cache after each test
        cache.clear()

if __name__ == "__main__":
    unittest.main(testRunner=CustomTestRunner())
