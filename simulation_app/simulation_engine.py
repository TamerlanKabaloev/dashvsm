import math
import time
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class Element:
    """Базовый класс для элементов инфраструктуры"""
    id: str
    type: str
    x: float
    y: float
    width: float
    length: float
    capacity_per_second: float  # пропускная способность в чел/сек
    max_capacity: int  # максимальная вместимость
    
    def calculate_flow(self, density: float) -> float:
        """Рассчитать поток через элемент с учетом плотности"""
        # Учитываем, что при высокой плотности скорость снижается
        if density > 0.8:
            return self.capacity_per_second * 0.5
        elif density > 0.6:
            return self.capacity_per_second * 0.7
        elif density > 0.4:
            return self.capacity_per_second * 0.85
        return self.capacity_per_second

class SimulationEngine:
    """Движок имитационного моделирования"""
    
    def __init__(self):
        self.element_types = {
            'tunnel': {
                'name': 'Тоннель',
                'default_width': 10.0,
                'default_length': 50.0,
                'default_capacity': 1.5,  # чел/сек на метр ширины
            },
            'stairs': {
                'name': 'Лестница',
                'default_width': 3.0,
                'default_length': 20.0,
                'default_capacity': 1.2,
            },
            'escalator': {
                'name': 'Эскалатор',
                'default_width': 1.0,
                'default_length': 30.0,
                'default_capacity': 0.8,  # одна полоса
            },
            'turnstile': {
                'name': 'Турникет',
                'default_width': 0.6,
                'default_length': 0.6,
                'default_capacity': 0.3,  # один турникет
            },
            'corridor': {
                'name': 'Коридор',
                'default_width': 5.0,
                'default_length': 30.0,
                'default_capacity': 1.8,
            },
            'door': {
                'name': 'Дверь',
                'default_width': 2.0,
                'default_length': 0.2,
                'default_capacity': 0.5,
            }
        }
    
    def get_element_types(self) -> Dict[str, Any]:
        """Получить информацию о типах элементов"""
        return self.element_types
    
    def create_element(self, element_data: Dict[str, Any]) -> Element:
        """Создать элемент из данных"""
        element_type = element_data.get('type', 'tunnel')
        type_info = self.element_types.get(element_type, self.element_types['tunnel'])
        
        width = element_data.get('width', type_info['default_width'])
        length = element_data.get('length', type_info['default_length'])
        
        # Если пропускная способность задана вручную, используем её
        if 'capacity_per_second' in element_data and element_data['capacity_per_second']:
            capacity_per_second = float(element_data['capacity_per_second'])
        else:
            # Рассчитываем пропускную способность на основе ширины
            capacity_per_second = type_info['default_capacity'] * width
        
        # Максимальная плотность (чел/м²)
        max_density = element_data.get('max_density', 2.0)
        
        # Максимальная вместимость = площадь * плотность
        # Конвертируем пиксели в метры (примерно 1px = 0.1м для визуализации)
        area_m2 = (width * 0.1) * (length * 0.1)
        max_capacity = int(area_m2 * max_density)
        
        return Element(
            id=element_data.get('id', f"element_{time.time()}"),
            type=element_type,
            x=element_data.get('x', 0),
            y=element_data.get('y', 0),
            width=width,
            length=length,
            capacity_per_second=capacity_per_second,
            max_capacity=max_capacity
        )
    
    def run_simulation(self, elements_data: List[Dict], people_count: int, simulation_time: int) -> Dict[str, Any]:
        """
        Запустить имитационное моделирование
        
        Args:
            elements_data: Список элементов с их параметрами
            people_count: Количество людей
            simulation_time: Время симуляции в секундах
        
        Returns:
            Результаты моделирования
        """
        if not elements_data:
            return {
                'error': 'Нет элементов для моделирования',
                'total_time': 0,
                'people_processed': 0
            }
        
        # Создаем элементы
        elements = [self.create_element(elem) for elem in elements_data]
        
        # Находим узкое место (элемент с минимальной пропускной способностью)
        bottleneck = min(elements, key=lambda e: e.capacity_per_second)
        
        # Рассчитываем общее время прохождения
        # Упрощенная модель: люди проходят последовательно через все элементы
        # Время = количество людей / минимальная пропускная способность
        
        total_time = people_count / bottleneck.capacity_per_second if bottleneck.capacity_per_second > 0 else float('inf')
        
        # Учитываем ограничение по времени симуляции
        if total_time > simulation_time:
            people_processed = int(bottleneck.capacity_per_second * simulation_time)
            total_time = simulation_time
        else:
            people_processed = people_count
        
        # Рассчитываем статистику по каждому элементу
        element_stats = []
        for element in elements:
            density = min(people_processed / element.max_capacity, 1.0) if element.max_capacity > 0 else 0
            flow = element.calculate_flow(density)
            time_through_element = people_processed / flow if flow > 0 else 0
            
            element_stats.append({
                'id': element.id,
                'type': element.type,
                'name': self.element_types[element.type]['name'],
                'capacity_per_second': round(flow, 2),
                'time_through': round(time_through_element, 2),
                'density': round(density, 2),
                'is_bottleneck': element.id == bottleneck.id
            })
        
        return {
            'total_time': round(total_time, 2),
            'people_processed': people_processed,
            'people_count': people_count,
            'bottleneck': {
                'id': bottleneck.id,
                'type': bottleneck.type,
                'name': self.element_types[bottleneck.type]['name']
            },
            'elements': element_stats,
            'success': True
        }
    
    def prepare_animation_data(self, elements_data: List[Dict], people_count: int, simulation_time: int) -> Dict[str, Any]:
        """
        Подготовить данные для анимации - рассчитать траектории движения людей
        
        Returns:
            Данные для анимации: позиции элементов, скорости, траектории
        """
        if not elements_data:
            return {'error': 'Нет элементов для моделирования'}
        
        elements = [self.create_element(elem) for elem in elements_data]
        bottleneck = min(elements, key=lambda e: e.capacity_per_second)
        
        # Рассчитываем параметры для каждого элемента
        animation_data = []
        for element in elements:
            # Скорость движения через элемент (пикселей в секунду)
            # Базовая скорость зависит от пропускной способности
            base_speed = element.capacity_per_second * 10  # пикселей в секунду
            
            # Направление движения (слева направо по умолчанию)
            direction = {'x': 1, 'y': 0}
            
            animation_data.append({
                'id': element.id,
                'x': element.x,
                'y': element.y,
                'width': element.width,
                'length': element.length,
                'type': element.type,
                'speed': base_speed,
                'direction': direction,
                'capacity_per_second': element.capacity_per_second,
                'max_capacity': element.max_capacity
            })
        
        total_time = people_count / bottleneck.capacity_per_second if bottleneck.capacity_per_second > 0 else float('inf')
        if total_time > simulation_time:
            total_time = simulation_time
        
        return {
            'elements': animation_data,
            'people_count': people_count,
            'total_time': round(total_time, 2),
            'time_step': 0.1,  # шаг симуляции в секундах
            'success': True
        }

