from flask import Flask, jsonify, request, abort
import os
import logging
import random

logging.basicConfig(level = logging.DEBUG)

def format_question(question):
    """
    Take a SQL representation of a question, and return a dictionary.
    """
    return {
        "id": question[0],
        "category_id": question[1],
        "question": question[2],
        "answer": question[3],
        "difficulty": question[4]
    }

def paginate_questions(questions, page = 1):
    """
    Return a formatted list of 5 questions, based on the requested page.
    Only return the question text (not the answer).
    """
    QUESTIONS_PER_PAGE = 5
    # Define the indices of the first and last questions to return
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    # Format the selected questions
    formatted_questions = []
    for question in questions[start:end]:
        formatted_questions.append(question[2])
    return formatted_questions

def create_app(test_config = None, prod = True):
    app = Flask(__name__)

    # Add configuration keys
    app.config.from_mapping(
        PROD_DATABASE = os.path.join(app.instance_path, "flaskr.sqlite"),
        TEST_DATABASE = os.path.join(app.instance_path, "test-flaskr.sqlite"),
    )

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    @app.route("/")
    def hello():
        return "Hello, World!"

    @app.route("/questions")
    def get_questions():
        """
        Get questions.
        If request body includes a category, then
        only return questions in that category.
        If request body includes a search term, then returns
        questions with a partial string match.
        You can use both search and category parameters together.
        """
        # Parse request parameters
        category = request.args.get("category", None, type = str)
        page = request.args.get("page", 1, type = int)
        search = request.args.get("search", None, type = str)
        logging.debug(f"category={category}&page={page}&search={search}")

        # Establish connection
        conn = db.get_db(prod = prod)
        cur = conn.cursor()

        # Get the category ID if appropriate
        if category is not None:
            try:
                query = (
                    "SELECT id FROM category WHERE "
                    f"type = '{category}' COLLATE NOCASE "
                )
                category_id = cur.execute(query).fetchall()
            except:
                conn.close()
                abort(500)

            # If there was no category matching the parameter,
            # return a 404. (Could feasibly be 400, not sure.)
            if len(category_id) == 0:
                conn.close()
                abort(404)

        if search is not None and category is not None:
            # Filter on category and search text
            try:
                query = (
                    "SELECT * FROM question "
                    "WHERE question.category_id = "
                    f"{category_id[0][0]} "
                    f"AND question.question LIKE '%{search}%' COLLATE NOCASE"
                )
                res = cur.execute(query).fetchall()
            except:
                conn.close()
                abort(500)

        elif search is not None:
            # Filter on search text only
            try:
                query = (
                    "SELECT * FROM question "
                    f"WHERE question LIKE '%{search}%' COLLATE NOCASE"
                )
                res = cur.execute(query).fetchall()
            except:
                conn.close()
                abort(500)

        elif category is not None:
            # Filter on category only
            try:
                query = (
                    "SELECT * FROM question "
                    "WHERE question.category_id = "
                    f"{category_id[0][0]}"
                )
                res = cur.execute(query).fetchall()
            except:
                conn.close()
                abort(500)

        else:
            # No supplied parameters, just get all questions
            res = cur.execute("SELECT * FROM question").fetchall()

        # Subset the questions 
        questions = paginate_questions(res, page)

        # Get and format the categories
        categories = cur.execute("SELECT * FROM category").fetchall()

        formatted_categories= []
        for i in categories:
            formatted_categories.append(i[1])

        conn.close()      

        return jsonify({
            "success": True,
            "number_of_questions": len(res),
            "questions": questions,
            "current_category": category,
            "categories": formatted_categories,
        })

    @app.route("/questions/<int:id>")
    def get_question(id):
        # Get the specific question by ID
        conn = db.get_db(prod = prod)
        cur = conn.cursor()
        res = cur.execute(
            f"SELECT * FROM question WHERE id == {id}"
        ).fetchall()
        conn.close()

        # If there is no question at the requested ID,
        # abort with a 404 resource not found
        if len(res) == 0:
            abort(404)

        # Format the question
        formatted_question = format_question(res[0])

        # Return the response
        return jsonify({
            "success": True,
            "question": formatted_question,
        })

    @app.route("/questions/<int:id>", methods = ["DELETE"])
    def delete_question(id):
        # Confirm that the book exists
        conn = db.get_db(prod = prod)
        cur = conn.cursor()
        res = cur.execute(
            f"SELECT * FROM question WHERE id == {id}"
        ).fetchall()

        if len(res) == 0:
            conn.close()
            abort(404)

        # Delete it
        try:
            res = cur.execute(
                f"DELETE FROM question WHERE id == {id}"
            )
            conn.commit()
            conn.close()
            return jsonify({
                "success": True,
                "deleted": id,
            })
        except:
            # If this hasn't worked, it may be a server error
            logging.warning("Question could not be deleted.")
            conn.rollback()
            conn.close()
            abort(500)

    @app.route("/questions", methods = ["POST"])
    def create_question():
        
        # Get request body
        body = request.get_json()
        question = body.get("question", None)
        answer = body.get("answer", None)
        category_id = body.get("category_id", None)
        difficulty = body.get("difficulty", None)

        # Create the database connection and cursor
        conn = db.get_db(prod = prod)
        cur = conn.cursor()

        try:
            # Create the question
            res = cur.execute(
                f'INSERT INTO question (category_id, question, answer, difficulty) VALUES ({category_id}, "{question}", "{answer}", {difficulty});'
            )
            conn.commit()
        except:
            # If this hasn't worked, it's likely a bad request
            logging.warning("Question could not be inserted.")
            conn.rollback()
            conn.close()
            abort(400)
        try:
            # Get ID of newly created question
            new_question = cur.execute(
                f"SELECT id FROM question WHERE question == '{question}'"
            ).fetchone()
            conn.close()
            return jsonify({
                "success": True,
                "created_id": new_question[0]
            })
        except:
            # If this hasn't worked, it may be a server error
            logging.warning("Questions could not be retrieved.")
            conn.rollback()
            conn.close()
            abort(500)

    @app.route("/categories")
    def get_categories():
        """
        Get all categories
        """
        try:
            conn = db.get_db(prod = prod)
            cur = conn.cursor()
            categories = cur.execute("SELECT * FROM category").fetchall()
            conn.close()

            formatted_categories= []
            for category in categories:
                formatted_categories.append(
                    {
                        "id": category[0],
                        "type": category[1]
                    }
                )

            return jsonify({
                "success": True,
                "number_of_categories": len(categories),
                "categories": formatted_categories,
            })

        except:
            abort(500)

    @app.route("/categories/<int:id>/questions")
    def get_questions_in_category(id):
        """
        Get questions in a supplied category.
        """
        conn = db.get_db(prod = prod)
        cur = conn.cursor()
        # Verify that the category ID exists
        category = cur.execute(f"SELECT * FROM category WHERE id == {id}").fetchall()
        if len(category) == 0:
            conn.close()
            abort(404)
        # Get associated questions
        questions = cur.execute(f"SELECT * FROM question WHERE category_id == {id}").fetchall()
        if len(questions) == 0:
            conn.close()
            abort(422)

        formatted_questions = []
        for i in questions:
            formatted_questions.append(format_question(i))

        return jsonify({
            "success": True,
            "current_category": category[0][1],
            "questions": formatted_questions
        })

    @app.route("/quizzes", methods = ["POST"])
    def play_quiz():
        """
        Play the quiz by making POST requests.
        """
        # Get the quiz parameters
        body = request.get_json()
        # previous_questions is a list and must be provided 
        # (even if empty)
        previous_questions = body.get("previous_questions", None)
        # (optional) quiz_category is a str
        quiz_category = body.get("quiz_category", None)
        logging.debug(f"previous_questions={previous_questions}&quiz_category={quiz_category}")
        if previous_questions is None:
            abort(400)

        conn = db.get_db(prod = prod)
        cur = conn.cursor()

        if quiz_category is not None:
            try:
                # Get questions from the provided category
                query = (
                    "SELECT id FROM category "
                    f"WHERE type = '{quiz_category}' "
                    "COLLATE NOCASE"
                )
                category_id = cur.execute(query).fetchall()
                questions = get_questions_in_category(category_id[0][0]).get_json()
                questions = questions["questions"]
            except:
                # If this hasn't worked, then it's likely
                # that the category doesn't exist
                abort(404)

        else:
            # Otherwise, get all questions
            raw_questions = cur.execute("SELECT * FROM question").fetchall()
            questions = [format_question(i) for i in raw_questions]

        conn.close()

        try:
            # Remove previously used questions if applicable
            if len(previous_questions) > 0:
                unasked_questions = []
                for question in questions:
                    if question["id"] not in previous_questions:
                        unasked_questions.append(question)
            else:
                unasked_questions = questions
        except:
            abort(500)

        # Take a random question if there are any left to sample
        if len(unasked_questions) > 0:
            random_question = random.sample(unasked_questions, 1)[0]
        else:
            random_question = {}

        return jsonify({
            "success": True,
            "question": random_question,
        })

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad request"
        })    

    @app.errorhandler(404)
    def resource_not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource not found",
        })

    @app.errorhandler(422)
    def unprocessable_content(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable content",
        })

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal server error",
        })

    return app
