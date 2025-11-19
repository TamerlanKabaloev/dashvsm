"""
Тестовый скрипт для проверки работоспособности симуляции
"""
import sys
import os

# Добавление текущей директории в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from simulation.engine import SimulationEngine

def test_simulation():
    """Быстрый тест симуляции"""
    print("Запуск тестовой симуляции...")
    
    engine = SimulationEngine()
    
    # Запуск короткой симуляции
    engine.run_simulation(
        arrival_rate=1.0,  # 1 пассажир в минуту
        simulation_duration=60.0  # 1 час
    )
    
    # Получение результатов
    results = engine.get_results()
    
    print("\n=== РЕЗУЛЬТАТЫ ТЕСТОВОЙ СИМУЛЯЦИИ ===\n")
    
    # Статистика по зонам
    print("Статистика по зонам:")
    for zone in results.get('zones', []):
        print(f"\n{zone['zone_name']}:")
        print(f"  Обслужено пассажиров: {zone['total_served']}")
        print(f"  Среднее время ожидания: {zone['avg_wait_time']:.2f} мин")
        print(f"  Среднее время обслуживания: {zone['avg_service_time']:.2f} мин")
        print(f"  Средняя длина очереди: {zone['avg_queue_length']:.2f}")
        print(f"  Загрузка: {zone['utilization']*100:.1f}%")
    
    # Статистика по пассажирам
    print("\n\nСтатистика по пассажирам:")
    passenger_stats = results.get('passengers', {})
    print(f"  Всего пассажиров: {passenger_stats.get('total_passengers', 0)}")
    print(f"  Пропущено рейсов: {passenger_stats.get('missed_flights', 0)}")
    print(f"  Процент пропущенных: {passenger_stats.get('missed_flight_rate', 0)*100:.2f}%")
    print(f"  Среднее время в аэропорту: {passenger_stats.get('avg_time_in_airport', 0):.2f} мин")
    
    print("\nТест завершен успешно!")

if __name__ == "__main__":
    test_simulation()



