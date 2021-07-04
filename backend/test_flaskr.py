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
        self.database_path = "postgresql://{}:{}@{}/{}".format('postgres', '12postgres34','localhost:5432', self.database_name)

        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question = {
            'question': 'Who is this',
            'answer': 'I do not know',
            'difficulty': 1,
            'category': 3,       
        }
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=49')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'resource not found')



    def test_delete_question(self):
        res = self.client().delete('/questions/2')
        data = json.loads(res.data)
        question = Question.query.filter(Question.id==2).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertIsNone(question)

    def test_422_if_question_does_not_exist(self):
        res = self.client().delete('/questions/5999')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'unprocessable')



    def test_add_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']))

    def test_405_if_adding_question_not_allowed(self):
        res = self.client().post('/questions/45', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'method not allowed')



    def test_get_question_search_with_results(self):
        res = self.client().post('/questions/search', json={'searchTerm':'egypt'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        # self.assertEqual(data['current_category'], 4)
        self.assertTrue(data['total_questions'])
        self.assertEqual(len(data['questions']), 1)

    def test_get_question_search_without_results(self):
        res = self.client().post('/questions/search', json={'searchTerm':'kijfioet'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        # print(data['questions'])
        self.assertFalse(data['questions'])
        self.assertFalse(data['total_questions'])

    def test_422_get_search_nothing(self):
        res = self.client().post('/questions/search', json={'searchTerm':''})
        data = json.loads(res.data)
        # print(data)
        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'unprocessable')



    def test_play_quiz(self):
        res = self.client().post('/quizzes', json={'previous_questions':[2,6],'quiz_category':{'type':'Entertainment','id':5}})
        data = json.loads(res.data)
        # print(data)
        # print(data['question'])

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['question'],
        # {'answer': 'Edward Scissorhands', 'category': 5, 'difficulty': 3, 'id': 6, 'question': 'What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?'})
        {'answer': 'Tom Cruise', 'category': 5, 'difficulty': 4, 'id': 4, 'question': 'What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?'})    
    
    def test_422_play_quiz(self):
        res = self.client().post('/quizzes', 
                    json={'previous_questions':[],'quiz_category':{'type':'here','id':6}})
        data = json.loads(res.data)
        # print(data)
        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'unprocessable')



    def test_get_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['total_questions'], 3)

    def test_404_get_questions_by_category(self):
        res = self.client().get('categories/8/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'resource not found')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()