# 📖 TRIVIA API Docs

## GET methods
`GET '/categories'`
- **Summary**: Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- **Request Arguments**: None
- **Returns**: An object with the request status and categories, that contains an object of id: category_string key: value pairs.

    ```JSON
    {   
        "success": True,
        "categories": {
            "1": "Science",
            "2": "Art",
            "3": "Geography",
            "4": "History",
            "5": "Entertainment",
            "6": "Sports"
        }
    }
    ```

`GET '/questions?page=${int}'`
- **Summary**: Fetches a dictionary of questions (paginated).
- **Request Arguments**: page (optional)
- **Returns**: A JSON with a list of questions (id, question, answer, category, difficulty), the total number of questions, categories listed on questions, and all categories.

    ```JSON
    {   
        "questions": [
            {
                "answer": "Apollo 13", 
                "category": 5, 
                "difficulty": 4, 
                "id": 2, 
                "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
            }
        ],
        "totalQuestions": 100,
        "currentCategory": "Science, Art",
        "categories": {
            "1": "Science",
            "2": "Art",
            "3": "Geography",
            "4": "History",
            "5": "Entertainment",
            "6": "Sports"
        }
    }
    ```


`POST '/categories/<int:category_id>/questions'`
- **Summary**: Get questions based on category.
- **Request Arguments**: category desired
- **Returns**: A JSON with question retrieved
    ``` JSON
    {   
        "questions": [
            {
                "answer": "Apollo 13", 
                "category": 5, 
                "difficulty": 4, 
                "id": 2, 
                "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
            }
        ],
    }
    ```

## POST methods
`POST '/questions'`
- **Summary**: Add new questions detailing its category, difficulty, question and answer through a JSON.
- **Request Arguments**: page (optional)
- **Returns**: A JSON with request status and insert message.
  
    ```JSON
    {   
        "success": True,
        "message": "question inserted" 
    }
    ```


`POST '/question/search'`
- **Summary**: endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question.
- **Request Arguments**: 
- **Returns**: A list of matched questions.
  
    ```JSON
    {
        [
            {
                "answer": "George Washington Carver", 
                "category": 4, 
                "difficulty": 2, 
                "id": 12, 
                "question": "Who invented Peanut Butter?"
            }
        ]
    }

    ```


`POST '/quizzes'`
- **Summary**: endpoint to retrieve a random question from same category (if provided) and a different then the question passed. 
- **Request Arguments**: a JSON with the previous question and its category (optional)
    ```JSON
    {
        [
            {
                "previous_questions": [1, 4, 20, 15],
                "quiz_category": '{
                    "id": 1,
                    "type": "Science"
                }
            }
        ]
    }

    ```
- **Returns**: a JSON with a random question, answer, its category, id and difficulty.
  
    ```JSON
    {
        [
            {
                "question": {
                    "answer": "Apollo 13", 
                    "category": 4, 
                    "difficulty": 4, 
                    "id": 2, 
                    "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
                }
            }
        ]
    }

    ```



## DELETE methods
`DELETE '/questions/{question_id}>'`
- **Summary**: Deletes a question with and id.
- **Request Arguments**: id question (`int`)
- **Returns**: A JSON with request status and question id deleted
  
    ```JSON
    {   
        "success": True,
        "deleted": 2 
    }
    ```