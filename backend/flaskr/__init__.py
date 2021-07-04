import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import sys
# sys.path.append('C:/Users/User/FSND-master/projects/02_trivia_api/starter/')

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  # page = int(request.args.get('page', 1))
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]

  # if len(selection)%page == 0:
  #   current_questions = questions[start:]

  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  # CORS(app)
  CORS(app, resources={r"*": {"origins": "*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,DELETE,POST')
    return response

  # @app.route('/')
  # def index():   
  #   return ( 'hello world!')

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def retrieve_categories():
    categories = Category.query.all()
    formatted_categories = {category.id: category.type for category in categories}
    # formatted_categories = [category.format() for category in categories]
    
    if categories is None:
      abort(404)    
    
    return jsonify({
      'success' : True,
      'categories': formatted_categories
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def retrieve_questions():
    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, selection)
    
    categories = Category.query.all()    
    formatted_categories = {category.id: category.type for category in categories}
    # formatted_categories = {category.format() for category in categories}
    # print(selection)
    # if selection is None:
    if len(current_questions)==0:
      abort(404)
    
    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(Question.query.all()),
      'current_category':None,
      'categories': formatted_categories
    })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()
      
      if question is None:
        abort(404)
      question.delete()
      
      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)
      
      return jsonify({
        'success':True,
        'questions':current_questions,
        'total_questions':len(Question.query.all())
      })

    except:
      abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def add_question():
    # added this declaration because when submitting without alertng values it takes the old but not throws an error
    # body={'question':'','answer':'','category':0,'difficulty':0}
    
    body = request.get_json()
    # if request.method==['POST']:
    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_category = body.get('category', None)
    new_difficulty = body.get('difficulty', None)
    print(body)

    try:
      if new_question=='' or new_answer=='':
      # if not ('question' in body and 'answer' in body and 'difficulty' in body and 'category' in body):
        abort(422)
      else:
        question = Question(question=new_question, answer=new_answer, 
                            category=new_category, difficulty=new_difficulty )

        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        question.insert()
        return jsonify({
          'success':True,
          'questions': current_questions,
          'total_books': len(Question.query.all())
      })

    except:
      abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def get_question_based_on_search():
    body = request.get_json()
    search_term = body.get('searchTerm', None)
    try:
      if search_term:
        selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search_term))).all()
        current_questions = paginate_questions(request, selection)
        
        return jsonify({
          'success': True,
          'questions': current_questions,
          'total_questions': len(selection),
          'current_category': None
        })
      else:
        abort(422)
    except:
      abort(422)
    # exceptException as e:
    #   print(str(e))

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  def retrieve_questions_by_category(category_id):
    # selection = Question.query.filter(Question.category==str(category_id)).order_by(Question.id).all()
    category = Category.query.get(category_id)
    selection = Question.query.filter_by(category=str(category_id)
                                          ).order_by(Question.id).all()
    current_questions = paginate_questions(request, selection)
    # print(selection)
    # if len(selection)==0:
    # if selection is None
    if not selection:
      abort(404)

    # print(category.type)
    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(selection),
      'current_category': category.type
      # 'current_category':category_id
    })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
    body = request.get_json()
    previous_questions = body.get('previous_questions', None)
    quiz_category = body.get('quiz_category', None)
    try:

      # if not quiz_category['id']:
      #   distinct_questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
      
      # else:
      #   distinct_questions = Question.query.filter(Question.category==quiz_category['id'],
      #                                     Question.id.notin_(previous_questions)).all()
        
      if not quiz_category['id']:
        questions = Question.query.all()
      
      else:
        questions = Question.query.filter(Question.category==quiz_category['id']).all()
      
      #if len(questions)==0:
      if not questions:
        abort(422)  

      distinct_questions = []
      # formatted_distinct_questions=[]
      for question in questions:
        if question.id not in previous_questions:
          distinct_questions.append(question)
          # formatted_distinct_questions.append(question) 
  
      # print(distinct_questions) 

      if len(distinct_questions) == 0: 
        return jsonify({
          'success': True,
          'question': None
        })

      # else:
      formatted_questions = [question.format() for question in distinct_questions]     
      print(formatted_questions)
      random_question = random.choice(formatted_questions)
      # random_question = random.choice(formatted_distinct_questions)

      return jsonify({
        'success': True,
        'question': random_question,
      })
    except:
      abort(422)


  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success':False,
      'error':404,
      'message':'resource not found'
    }),404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success':False,
      'error':422,
      'message':'unprocessable'
    }),422
    
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "bad request"
      }),400
  
  @app.errorhandler(405)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 405,
      "message": "method not allowed"
      }), 405

  return app



    