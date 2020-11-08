import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import math 

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app,resources={r"/api/*":{"origins" : "*"}})
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers','Content-Type, Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
    return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def display_categories():

    categories=Category.query.all()
    formatted_categories=[category.type for category in categories]
    return jsonify({
      'success':True,
      'categories':formatted_categories
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
  def display_Question():
    page = request.args.get('page',1,type=int)
    start=(page-1)*10
    end = start + 10
    Questions=Question.query.all()
    if page <= int(math.ceil(len(Questions)/10)): 
      formatted_Questions=[Question.format() for Question in Questions]
      categories=Category.query.all()
      formatted_categories=[category.type for category in categories]
      return jsonify({
        'questions':formatted_Questions[start:end],
        'total_questions':len(formatted_Questions),
        'categories':formatted_categories,
        'success':True
      })
    else:
      abort(404)

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>',methods =['DELETE'])
  def Delete_Question(question_id):
    question = Question.query.filter(Question.id == question_id).one_or_none()

    if question == None:
      abort(400)
    else:
      question.delete()
      return jsonify({
      'question_id':question.id,
      'success':True
    })

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions/add',methods =['POST'])
  def add_question():

    json_body=request.get_json()
   
    new_question = json_body.get('question',None)
    new_answer = json_body.get('answer',None)
    new_category = json_body.get('category',None)
    new_difficulty = json_body.get('difficulty',None)
    
    try:

      question = Question(question = new_question,answer = new_answer, category = new_category,difficulty = new_difficulty)
      
      question.insert()
      return jsonify({
      'question_id':question.id,
      'success':True
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

  @app.route('/questions',methods =['POST'])
  def search_question():
    question_list = list(Question.query.filter(Question.question.ilike('%' + request.get_json().get("searchTerm") + '%'))) 

    formatted_Questions=[Question.format() for Question in question_list]
    return jsonify({
        'questions':formatted_Questions,
        'success':True
        })
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

  @app.route('/categories/<int:category_id>/questions')
  def display_questions_based_categories(category_id):
    
    if category_id <= len(Category.query.all()) and  category_id >= 0:
      question_list = list(Question.query.filter_by(category=category_id))
      formatted_Questions=[Question.format() for Question in question_list]
      return jsonify({
        'questions':formatted_Questions,
        'success':True
        })
     
    else:
      abort(404)

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

  @app.route('/quizzes',methods =['POST'])
  def play_quiz():
    json_body=request.get_json()
    
    previous_questions=json_body.get("previous_questions")
    category_id = json_body.get("quiz_category")['id']
    
    if int(category_id) <= len(Category.query.all()) and  int(category_id) >= 1:
      questions = list(Question.query.filter_by(category=int(category_id)))
    else:
      questions=Question.query.all()

    formatted_Questions=[Question.format() for Question in questions]
    random_questions_object=random.choice(formatted_Questions)

    while   random_questions_object['id'] in previous_questions and len(previous_questions)< len(formatted_Questions):
      random_questions_object=random.choice(formatted_Questions)
   
    return jsonify({
        'question':random_questions_object,
        'success':True
        })


  

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def bad_requuest(error):
      return jsonify({
          "success": False, 
          "error": 400,
          "message": "Bad requuest"
          }), 400
  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
          "success": False, 
          "error": 404,
          "message": "Not found"
          }), 404
  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "unprocessable"
      }), 422
  @app.errorhandler(500)
  def internal_server_error(error):
    return jsonify({
      "success": False, 
      "error": 500,
      "message": "Internal server error"
      }), 500    


  return app

    