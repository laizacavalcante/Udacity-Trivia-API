# TODO: refactor app to blueprints

import os
import json
import random
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
from flask import Flask, request, abort, jsonify

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


def pagination(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    page_elements = [element.format() for element in selection]
    current_page = page_elements[start:end]
    # print(f"page {page}, start {start}, end {end}")
    return current_page


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, origins="*")

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response


    # Working API + Front, Docs
    @app.route("/categories", methods=["GET"])
    def retrieve_categories():     
        print("\t route retrieve_categories")
        get_categories = Category.query.order_by(Category.id).all()
        
        if get_categories:
            return jsonify({
                "success": True,
                "categories": {item.id: item.type for item in get_categories},
            })
        else:
            abort(404)


    # Working API + Front, Docs
    @app.route("/questions", methods=["GET"])
    def retrieve_questions():
        print("\t route questions GET")
        try:
            get_questions = Question.query.order_by(Question.id).all()
            categories = Category.query.order_by(Category.id).all()
        except:
            print("Unable to perform the query -> retrieve_questions")
            abort(422)
        finally:
            db.session.close()

        if get_questions:
            # Why pagination is changing questions IDs order?
            page_questions = pagination(request, get_questions)
            if len(page_questions):
                page_categories = list(set([category['category'] for category in page_questions]))

                # All categories
                categories = dict([(category.id, category.type) for category in categories])

                # Questions categories paginated 
                page_categories_types = [categories.get(pg_cat) for pg_cat in page_categories if categories.get(pg_cat)]

                return jsonify({
                    "questions": page_questions,
                    "totalQuestions": len(get_questions),
                    "currentCategory": ", ".join(page_categories_types),
                    "categories": categories
                })

            else:
                abort(404)    
        else: 
            abort(404)


    # Working API + Front
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        print(f"\t route delete_question {question_id}")
        try:
            question_item = Question.query.filter(Question.id == question_id).one_or_none() #first()
        except:
            abort(422)    
        finally:
            db.session.close() 
        
        if question_item:
            question_item.delete()
            return jsonify({
                "success": True, 
                "deleted": question_id})
        else:
            abort(404)


    # Working API + Front
    @app.route("/questions", methods=["POST"])
    def create_question():
        print("\t questions POST")

        body = request.get_json()
        print(body)

        if body:
            question_input_cols = ["question", "answer", "category", "difficulty"]
            if all(item in body.keys() for item in question_input_cols):
                try:
                    new_question = Question(
                        question=body["question"],
                        answer=body["answer"],
                        category=body["category"],
                        difficulty=body["difficulty"]    
                    )
                    new_question.insert()
                    print(new_question)
                    return jsonify({"success": True, "message": "question inserted"})
                except:
                    abort(404)
                finally:
                    db.session.close()
            else:
                abort(400)
        else:
            abort(400)

    
    # Working API + Front
    @app.route("/questions/search", methods=["POST"])
    def search_question():
        print("\t route search_question")

        body = request.get_json()
        if body == None:
            abort(400)

        search_value = body.get("searchTerm", None)
        if search_value:
            try:
                questions = Question.query.filter(
                    Question.question.ilike(f"%{search_value}%")
                ).all()
            except:
                abort(422)
            finally:
                db.session.close()
            
            if questions:
                # output = [quest.format() for quest in question] 
                output = pagination(request, questions)
                print(output)
                return jsonify({"questions": output})
            else:
                print("No questions found")
                abort(404)
        
        else:
            abort(400)

    
    # Working API + Front
    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def retrieve_questions_by_category(category_id):
        print("\t route retrieve_questions_by_category")
        try:
            questions = Question.query.filter(Question.category == category_id).all()
            current_category = Category.query.filter(Category.id == category_id).first()
        except:
            abort(422)
        finally:
            db.session.close()

        if questions:
            output = pagination(request, questions)
            
            # TODO: Rever testes
            return jsonify({
                "questions": output,
                "total_questions": len(questions),
                "current_category": current_category.format()
                })
        else:
            abort(404)


    # Working API + Front, Docs
    @app.route("/quizzes", methods=["POST"])
    def quiz_questions():
        previous_info = request.get_json()
        
        print("\t route quizzes", previous_info)
        
        if previous_info == None:
            abort(400)

        previous_question = previous_info.get("previous_questions", None)
        quiz_category = previous_info.get("quiz_category", None)
        category_id = quiz_category["id"] 
        category_type = quiz_category["type"]
        print(category_id, category_type)

        try:
            categories = Category.query.order_by(Category.id).all()
            categories_ids = [category.id for category in categories]
        except:
            abort(404) #trocar esse padrão
        finally:
            db.session.close()
        
        if category_id and int(category_id) in categories_ids:
            if previous_question:
                new_question = Question.query.filter(
                    category_id == Question.category, 
                    ~Question.id.in_(previous_question)
                ).order_by(func.random()).first()
                
                if new_question:
                    print(new_question.format())
                    return jsonify(
                        {"question": new_question.format()})
                else:
                    abort(404)
            else:
                new_question = Question.query.filter(
                    category_id == Question.category,
                ).order_by(func.random()).first()

                if new_question:
                    print(new_question.format())

                    return jsonify(
                        {"question": new_question.format()})
                else:
                    abort(404)
        elif category_type == "click":
                new_question = Question.query.filter(
                    ~Question.id.in_(previous_question)
                ).order_by(func.random()).first()
                
                if new_question:
                    return jsonify(
                        {"question": new_question.format()})
                else:
                    abort(404)
        else:
            abort(404)


    @app.errorhandler(400)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 400, "message": "missing arguments"}),
            400,
        )
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "request unprocessable"}),
            422,
        )

    @app.errorhandler(500)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 500, "message": "Internal server error"}),
            500,
        )
    return app

