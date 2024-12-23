# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pymorphy2
from flask_cors import CORS
from flasgger import Swagger

nltk.download('stopwords')


app = Flask(__name__)
swagger = Swagger(app, template_file='analysis_api.yaml')
CORS(app)  # Разрешить запросы с любого домена


# Инициализация анализатора
morph = pymorphy2.MorphAnalyzer()

# Определяем стоп-слова и синонимы
stop_words = set(stopwords.words('russian'))
positive_words = {'хороший', 'отличный', 'прекрасный', 'потрясающий', 'замечательный', 'позитивный', 'удивительный'}
negative_words = {'плохой', 'ужасный', 'отвратительный', 'негативный', 'гадкий', 'ужас'}

# Глобальная переменная для хранения отзывов и результатов анализа
reviews_list = []
last_analysis_result = {}


@app.route('/reviews', methods=['POST'])
def add_reviews():
    global reviews_list
    data = request.get_json(force=True)
    new_reviews = data.get('reviews', [])

    if not new_reviews:
        return jsonify({'error': 'No reviews provided'}), 400

    reviews_list.extend(new_reviews)
    return jsonify({'message': 'Reviews added successfully', 'total_reviews': len(reviews_list)}), 201


@app.route('/analyze', methods=['GET'])
def analyze_reviews():
    global last_analysis_result

    if not reviews_list:
        return jsonify({'error': 'No reviews available for analysis'}), 404

    positive_count = 0
    negative_count = 0
    all_words = []

    for review in reviews_list:
        words = word_tokenize(review, language='russian')
        filtered_words = [word.lower() for word in words if word.isalpha() and word.lower() not in stop_words]

        # Приведение слов к нормальной форме
        normalized_words = [morph.parse(word)[0].normal_form for word in filtered_words]
        all_words.extend(normalized_words)

        # Определяем тональность отзыва
        if any(word in positive_words for word in normalized_words):
            positive_count += 1
        elif any(word in negative_words for word in normalized_words):
            negative_count += 1

    total_reviews = len(reviews_list)
    positive_percentage = (positive_count / total_reviews) * 100 if total_reviews else 0
    negative_percentage = (negative_count / total_reviews) * 100 if total_reviews else 0

    # Частотный анализ слов
    word_freq = Counter(all_words)
    most_common_words = word_freq.most_common(10)

    last_analysis_result = {
        'positive_percentage': positive_percentage,
        'negative_percentage': negative_percentage,
        'most_common_words': most_common_words
    }

    return jsonify(last_analysis_result)


@app.route('/results', methods=['GET'])
def get_results():
    if not last_analysis_result:
        return jsonify({'error': 'No analysis results available'}), 404
    return jsonify(last_analysis_result)

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=8080, debug=True)
