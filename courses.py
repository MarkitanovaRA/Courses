import json
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from flask import Flask, send_from_directory, jsonify, request
import os
import qrcode


app = Flask(__name__)
CORS(app)  # Разрешить запросы с любого домена


# Path to the database folder
DB_FOLDER = 'database'

# Ensure the database folder exists
os.makedirs(DB_FOLDER, exist_ok=True)

# Helper function to load data from a JSON file
def load_data(filename):
    # Построение пути к файлу в папке 'database'
    filepath = os.path.join(DB_FOLDER, filename)

    # Проверка существования файла и его содержимого
    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # Возвращаем пустой список, если файл отсутствует или пуст
        return []
# Helper function to save data to a JSON file
def save_data(filename, data):
    with open(os.path.join(DB_FOLDER, filename), 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

# Models (as in-memory data, no SQLAlchemy)
class User:
    def __init__(self, id, username, email, password, role):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.role = role

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'password': self.password,
            'role': self.role
        }

class Course:
    def __init__(self, id, title, description):
        self.id = id
        self.title = title
        self.description = description

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description
        }

class Module:
    def __init__(self, id, course_id, title, order_index):
        self.id = id
        self.course_id = course_id
        self.title = title
        self.order_index = order_index

    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'title': self.title,
            'order_index': self.order_index
        }

class Lesson:
    def __init__(self, id, module_id, title, content, media_type, media_url, order_index):
        self.id = id
        self.module_id = module_id
        self.title = title
        self.content = content
        self.media_type = media_type
        self.media_url = media_url
        self.order_index = order_index

    def to_dict(self):
        return {
            'id': self.id,
            'module_id': self.module_id,
            'title': self.title,
            'content': self.content,
            'media_type': self.media_type,
            'media_url': self.media_url,
            'order_index': self.order_index
        }
class Review:
    def __init__(self, id, course_id, rating, comment):
        self.id = id
        self.course_id = course_id
        self.rating = rating
        self.comment = comment

    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'rating': self.rating,
            'comment': self.comment,
        }

# Endpoints
@app.route('/register', methods=['POST'])
def register_user():
    data = request.json
    users = load_data('users.json')
    user_id = len(users) + 1
    hashed_password = generate_password_hash(data['password'])
    new_user = User(user_id, data['username'], data['email'], hashed_password, data['role'])
    users.append(new_user.to_dict())
    save_data('users.json', users)
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login_user():
    data = request.json
    users = load_data('users.json')
    user = next((u for u in users if u['email'] == data['email']), None)
    if user and check_password_hash(user['password'], data['password']):
        return jsonify({'message': 'Login successful', 'user_id': user['id'], 'role': user['role']}), 200
    return jsonify({'message': 'Invalid credentials'}), 401


# Эндпоинт для создания модуля
@app.route('/create_module', methods=['POST'])
def create_module():
    data = request.json
    modules = load_data('modules.json')
    module_id = len(modules) + 1
    new_module = Module(module_id, data['course_id'], data['title'], data['order_index'])
    modules.append(new_module.to_dict())
    save_data('modules.json', modules)
    return jsonify({'message': 'Module created successfully', 'module_id': new_module.id})

# Эндпоинт для создания урока
@app.route('/create_lesson', methods=['POST'])
def create_lesson():
    data = request.json
    lessons = load_data('lessons.json')
    lesson_id = len(lessons) + 1
    new_lesson = Lesson(lesson_id, data['module_id'], data['title'], data['content'], data['media_type'], data['media_url'], data['order_index'])
    lessons.append(new_lesson.to_dict())
    save_data('lessons.json', lessons)
    return jsonify({'message': 'Lesson created successfully', 'lesson_id': new_lesson.id})

# Эндпоинт для создания теста
@app.route('/create_test', methods=['POST'])
def create_test():
    data = request.json
    tests = load_data('tests.json')
    test_id = len(tests) + 1
    new_test = {
        'id': test_id,
        'module_id': data['module_id'],
        'title': data['title'],
        'questions': data['questions'],  # Список вопросов
    }
    tests.append(new_test)
    save_data('tests.json', tests)
    return jsonify({'message': 'Test created successfully', 'test_id': new_test['id']})

@app.route('/create_course', methods=['POST'])
def create_course():
    data = request.json
    courses = load_data('courses.json')

    course_id = len(courses) + 1
    new_course = {
        'id': course_id,
        'title': data['title'],
        'description': data['description'],
        'modules': data['modules'],
    }

    courses.append(new_course)
    save_data('courses.json', courses)

    return jsonify({'message': 'Course created successfully', 'course_id': course_id})

# Эндпоинт для получения списка курсов
@app.route('/courses', methods=['GET'])
def get_courses():
    courses = load_data('courses.json')
    # Добавляем путь к QR-коду для каждого курса
    for course in courses:
        course['qr_code_url'] = f"http://localhost:5000/download_qr/{course['title']}.png"
    return jsonify(courses)


# Эндпоинт для получения подробной информации о курсе
@app.route('/course/<int:course_id>', methods=['GET'])
def get_course_details(course_id):
    courses = load_data('courses.json')
    course = next((c for c in courses if c['id'] == course_id), None)
    if not course:
        return jsonify({'message': 'Course not found'}), 404
    return jsonify(course)


@app.route('/submit_review', methods=['POST'])
def submit_review():
    data = request.get_json()

    # Проверьте данные
    rating = data.get('rating')
    comment = data.get('comment')
    course_id = data.get('course_id')

    if not all([rating, comment, course_id]):
        return jsonify({"message": "Invalid input data"}), 400

    # Логика сохранения данных в базе (пример)
    print(f"Received review: {rating} stars, comment: '{comment}', for course {course_id}")

    # Возвращаем успешный ответ
    return jsonify({"message": "Review submitted successfully!"}), 200

# Путь к директории с файлами
DATABASE_FOLDER = os.path.join(os.getcwd(), 'database')

# Роут для отдачи статического файла
# Роут для отдачи файла reviews.json
@app.route('/database/reviews.json')
def get_reviews():
    reviews = load_data('reviews.json')
    return jsonify(reviews)  # Возвращаем данные как JSON

# Эндпоинт для генерации QR-кода
@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    data = request.json
    title = data.get('title')
    description = data.get('description')

    if not title or not description:
        return jsonify({"message": "Title and description are required"}), 400

    qr_data = f"Course: {title}\nDescription: {description}"
    qr_image = qrcode.make(qr_data)

    # Путь для сохранения изображения QR-кода
    qr_folder = os.path.join(DB_FOLDER, "qr_codes")
    os.makedirs(qr_folder, exist_ok=True)
    qr_file_path = os.path.join(qr_folder, f"{title}.png")
    qr_image.save(qr_file_path)

    # Сохранение данных в файл qr.json
    qr_json_path = os.path.join(DB_FOLDER, "qr.json")
    qr_entries = load_data("qr.json")
    qr_entry = {
        "title": title,
        "description": description,
        "qr_code_path": qr_file_path
    }
    qr_entries.append(qr_entry)
    save_data("qr.json", qr_entries)

    return jsonify({
        "message": "QR code generated successfully",
        "qr_code_path": qr_file_path
    })

# Эндпоинт для загрузки QR-кода
@app.route('/download_qr/<filename>', methods=['GET'])
def download_qr(filename):
    qr_folder = os.path.join(DB_FOLDER, "qr_codes")

    # Проверяем, существует ли файл
    if not os.path.exists(os.path.join(qr_folder, filename)):
        return jsonify({"message": "QR code not found"}), 404

    return send_from_directory(qr_folder, filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
