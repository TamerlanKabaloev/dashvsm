from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
from simulation_engine import SimulationEngine

app = Flask(__name__)
CORS(app)

simulation_engine = SimulationEngine()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/simulate', methods=['POST'])
def simulate():
    """Запуск имитационного моделирования"""
    data = request.json
    elements = data.get('elements', [])
    people_count = data.get('people_count', 1000)
    simulation_time = data.get('simulation_time', 3600)  # секунды
    
    result = simulation_engine.run_simulation(elements, people_count, simulation_time)
    return jsonify(result)

@app.route('/api/elements/types', methods=['GET'])
def get_element_types():
    """Получить список типов элементов"""
    return jsonify(simulation_engine.get_element_types())

@app.route('/api/animation/prepare', methods=['POST'])
def prepare_animation():
    """Подготовить данные для анимации"""
    data = request.json
    elements = data.get('elements', [])
    people_count = data.get('people_count', 1000)
    simulation_time = data.get('simulation_time', 3600)
    
    result = simulation_engine.prepare_animation_data(elements, people_count, simulation_time)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

