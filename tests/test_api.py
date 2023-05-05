import unittest
from flaskr import create_app, db
import json

class QuestionsTestCase(unittest.TestCase):
    def setUp(self):
        """
        Set up the test client, using the test database.
        """
        self.app = create_app(prod = False)
        with self.app.app_context():
            db.init_db()
        self.client = self.app.test_client

    def tearDown(self):
        pass

    def test_get_questions(self):
        """
        Test GET /questions with no parameters
        """
        res = self.client().get("/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["number_of_questions"], 19)
        self.assertEqual(len(data["questions"]), 5)
        self.assertIsNone(data["current_category"])
        self.assertEqual(len(data["categories"]), 6)

    def test_get_questions_in_category(self):
        """
        Test GET /questions with category parameter, e.g.,
        GET /questions?category=art
        """
        res = self.client().get("/questions?category=art")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        # Test data has 4 questions in art category
        self.assertEqual(data["number_of_questions"], 4)
        self.assertEqual(len(data["questions"]), 4)
        self.assertEqual(data["current_category"], "art")
        self.assertEqual(len(data["categories"]), 6)

    def test_get_questions_with_nonexistent_category(self):
        """
        Test GET /questions with a category parameter that doesn't exist,
        e.g.,
        GET /questions?category=abc
        """
        res = self.client().get("/questions?category=abc")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], 404)
        self.assertEqual(data["message"], "Resource not found")

    def test_get_question_by_id(self):
        """
        Test GET /questions/<id>. We expect a HTTP 200 response, with JSON data
        including {
            "success": True,
            "question": {
                "id": <id>,
                "question": <question text>, 
                "answer": <answer text>,
                "category_id": <category ID>,
                "difficulty": <difficulty>    
            }
        }.
        """
        res = self.client().get("/questions/1")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["question"]["id"], 1)
        self.assertEqual(data["question"]["question"], "What is the heaviest organ in the human body?")
        self.assertEqual(data["question"]["answer"], "The liver")
        self.assertEqual(data["question"]["category_id"], 1)
        self.assertEqual(data["question"]["difficulty"], 4)

    def test_search_question_text(self):
        """
        Test GET /questions with a search parameter for question 
        text. E.g.,
        GET /questions?search=title
        """
        res = self.client().get("/questions?search=title")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        # Test data has two questions containing partial
        # string match for "title"
        self.assertEqual(data["number_of_questions"], 2)
        self.assertEqual(len(data["questions"]), 2)

    def test_search_and_category_combination(self):
        """
        You should be able to search text and filter on category.
        E.g.,
        GET /questions?search=title&category=history
        """
        res = self.client().get("/questions?search=title&category=history")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        # Test data has one questions containing partial
        # string match for "title" in the history category
        self.assertEqual(data["number_of_questions"], 1)
        self.assertEqual(len(data["questions"]), 1)

    def test_delete_question(self):
        """
        Test DELETE /questions/<id>. We expect a HTTP 200 response, with JSON
        data including {"success": True, "deleted": <id>}.
        """
        res = self.client().delete("/questions/1")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["deleted"], 1)
        res = self.client().get("/questions/1")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["error"], 404)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "Resource not found")

    def test_delete_question_404(self):
        """
        Test DELETE /questions/<id>, where <id> is not a valid question ID.
        We expect a HTTP 404 response, with JSON
        data including {
            "success": False,
            "error": 404,
            "message": "Resource not found"
        }.
        """
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["error"], 404)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "Resource not found")

    def test_create_question(self):
        """
        Test POST /questions. Requires question and answer text, category ID,
        and difficulty score. We expect a HTTP 200 response, with JSON data
        including {
            "success": True,
            "created_id": <id>,
            "number_of_questions": <number>
        }
        """
        res = self.client().post("/questions", json = {
            "question": "How many years are celebrated with a ruby anniversary?",
            "answer": "40",
            "category_id": 4,
            "difficulty": 3
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["created_id"], 20)

    def test_get_categories(self):
        """
        Test GET /categories
        """
        res = self.client().get("/categories")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["number_of_categories"], 6)

    def test_get_questions_in_category(self):
        """
        Test GET /categories/<id>/questions
        """
        res = self.client().get("/categories/1/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["current_category"], "Science")

    def test_quizzes_no_prev_question_all_categories(self):
        """
        Test POST /quizzes with no previous questions
        and no specified category
        """
        res = self.client().post("/quizzes", json = {
            "previous_questions": []
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(len(data["question"]), 5)

    def test_quizzes_one_prev_question_all_categories(self):
        """
        Test POST /quizzes with one previous question and 
        no specific category
        """
        res = self.client().post("/quizzes", json = {
            "previous_questions": [1]
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(len(data["question"]), 5)

    def test_quizzes_multiple_prev_questions_all_categories(self):
        """
        Test POST /quizzes with multiple previous questions
        and no specific category
        """
        previous_question_ids = [
                1, 2, 3, 4, 5, 6, 7, 8,
                9, 10, 11, 12, 13, 14, 15, 16
            ]
        res = self.client().post("/quizzes", json = {
            "previous_questions": previous_question_ids
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(len(data["question"]), 5)
        self.assertFalse(int(data["question"]["id"]) in previous_question_ids)

    def test_quizzes_no_prev_question_specific_category(self):
        """
        Test POST /quizzes with no previous question in
        a specific category
        """
        res = self.client().post("/quizzes", json = {
            "previous_questions": [], "quiz_category": "art"
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(len(data["question"]), 5)

    def test_quizzes_one_prev_question_specific_category(self):
        """
        Test POST /quizzes with one previous question in
        a specific category
        """
        res = self.client().post("/quizzes", json = {
            "previous_questions": [4], "quiz_category": "art"
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(len(data["question"]), 5)

    def test_quizzes_multiple_prev_questions_specific_category(self):
        """
        Test POST /quizzes with multiple previous questions in
        a specific category
        """
        res = self.client().post("/quizzes", json = {
            "previous_questions": [4, 5, 6], "quiz_category": "art"
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(len(data["question"]), 5)

    def test_quizzes_no_unasked_questions(self):
        """
        Test POST /quizzes with no unasked questions in the
        category remaining
        """
        res = self.client().post("/quizzes", json = {
            "previous_questions": [4, 5, 6, 7], "quiz_category": "art"
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(len(data["question"]), 0)

    def test_quizzes_returns_404_with_nonexistent_category(self):
        """
        Test POST /quizzes returns 404 if the quiz_category
        value doesn't correspond to an existing category type.
        """
        res = self.client().post("/quizzes", json = {
            "previous_questions": [], "quiz_category": "abc"
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], 404)
        self.assertEqual(data["message"], "Resource not found")

    def test_quizzes_returns_400_with_no_previous_questions_supplied(self):
        """
        Test POST /quizzes returns 400 if the previous_questions
        key is not supplied.
        """
        res = self.client().post("/quizzes", json = {
            "quiz_category": "art"
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], 400)
        self.assertEqual(data["message"], "Bad request")

if __name__ == "__main__":
    unittest.main()
