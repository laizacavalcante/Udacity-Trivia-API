import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            'postgres', 'admin', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass


    # Route /categories
    # Como fazer um teste para verificar o resultado 404?
    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200) #Verificando o status code
        self.assertEqual(data["success"], True) #Verificando exisência do output
        self.assertTrue(data["categories"]) #Verificando exisência do output


    # Route /questions
    def test_get_questions_by_page(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["questions"]) 
        self.assertTrue(data["totalQuestions"])

        # Key exists, but doesn't have a value
        self.assertIn("questions", data) 
        self.assertIn("currentCategory", data) 
        self.assertIn("categories", data) 
   

    def test_get_questions_invalid_page_404(self):
        res = self.client().get("/questions?page=300")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")


    # Route /questions/<int:question_id>
    def test_delete_question_by_id(self):
        res = self.client().delete("/questions/13")
        print(res, res.data)
        data = json.loads(res.data)

        question_deleted = Question.query.filter(Question.id == 13).one_or_none()

        self.assertEqual(res.status_code, 200) 
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], 13)
        self.assertEqual(question_deleted, None)


    def test_delete_question_by_id_not_exist_404(self):
        res = self.client().delete("/questions/3000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")


    # Route /questions POST
    # Try to add questions for missing categories and difficulty levels
    def test_post_questions(self):
        res = self.client().post("/questions", json={
            "question":"test question to be added", 
            "answer": "test answer", 
            "category": "2", 
            "difficulty": "2"
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["message"], "question inserted")


    def test_post_questions_missing_JSON_keys_400(self):
        res = self.client().post("/questions", json={
            "question":"test question to be added", 
            "answer": "test answer", 
            "category": "3", 
        })

        # Adicionar verificação pra ver se a questão foi adicionada
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400) 
        self.assertEqual(data["success"], False)
        self.assertEqual(data["error"], 400)
        self.assertEqual(data["message"], "missing arguments")


    def test_post_questions_missing_JSON_400(self):
        res = self.client().post("/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400) 
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "missing arguments")

    # Route questions search
    # Como lidar com uma lista de resultados?
    def test_post_search_questions(self):
        res = self.client().post("/questions/search", json={
            "searchTerm":"butter", 
        })
        print("test_post_search_questions -> ", res.data)
        data = json.loads(res.data) # aqui retornamos uma lista de resultados
        
        self.assertTrue(data["questions"]) 
        for d in data["questions"]:
            self.assertEqual(res.status_code, 200)
            self.assertIn("id", d)
            self.assertIn("question", d)
            self.assertIn("answer", d)
            self.assertIn("category", d)
            self.assertIn("difficulty", d)


    def test_post_search_questions_404(self):
        res = self.client().post("/questions/search", json={
            "searchTerm":"####", 
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404) 
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")


    def test_post_search_questions_missing_JSON_keys_400(self):
        res = self.client().post("/questions/search", json={"wrong_key": "useless"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["error"], 400)
        self.assertEqual(data["message"], "missing arguments")


    def test_post_search_questions_missing_JSON_400(self):
        res = self.client().post("/questions/search")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["error"], 400)
        self.assertEqual(data["message"], "missing arguments")


    # Route /categories/id/questions
    def test_get_questions_by_category(self):
        res = self.client().get("/categories/3/questions")
        data = json.loads(res.data) # retornamos uma lista 

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["questions"]) 
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["current_category"])
        for d in data["questions"]:
            self.assertIn("id", d)
            self.assertIn("question", d)
            self.assertIn("answer", d)
            self.assertIn("category", d)
            self.assertIn("difficulty", d)


    def test_get_questions_by_missing_category(self):
        res = self.client().get("/categories/600/questions")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404) 
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")


    #Route quizzes
    def test_get_quizzes_previous_category_and_question(self):
        res = self.client().post("/quizzes", 
            json={
                "previous_questions": [1], 
                "quiz_category": {
                    "id": 1,
                    "type": "Science"
                }
            })
        data = json.loads(res.data) # retornamos uma lista 
        print("test_get_quizzes_previous_category_and_question", data)

        self.assertEqual(res.status_code, 200)
        self.assertIn("question", data)
        self.assertIn("id", data["question"])
        self.assertIn("answer", data["question"])
        self.assertIn("category", data["question"])
        self.assertIn("difficulty", data["question"])


    def test_get_quizzes_missing_JSON_400(self):
        res = self.client().post("/quizzes")
        data = json.loads(res.data) # retornamos uma lista 

        self.assertEqual(res.status_code, 400) 
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "missing arguments")



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()