"""
Модуль для управления матрицей динамического ценообразования
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class PricingConfig:
    """Конфигурация системы ценообразования"""
    target_price: float  # Целевая цена
    base_platskart_share: float = 0.6  # Доля плацкартной части (60%)
    min_coefficient: float = 0.3  # Минимальный коэффициент
    max_coefficient: float = 2.5  # Максимальный коэффициент
    num_classes: int = 4  # Количество классов
    max_days_before_departure: int = 105  # Максимальное количество дней до отправления
    max_load_percentage: int = 100  # Максимальная загрузка в процентах


class PricingMatrix:
    """Класс для управления матрицей коэффициентов ценообразования"""
    
    def __init__(self, config: PricingConfig):
        self.config = config
        # Инициализация матрицы коэффициентов (дни до отправления x загрузка)
        # Начало продаж слева внизу - значит дни увеличиваются вверх, загрузка вправо
        self.matrix = self._initialize_matrix()
        
        # Коэффициенты сезонности (можно расширить)
        self.seasonality_coefficients = np.ones(12)  # По умолчанию все 1.0
        
        # Коэффициенты классов (4 класса)
        self.class_coefficients = np.array([1.0, 1.2, 1.5, 2.0])  # Примерные значения
        
        # История продаж для оптимизации
        self.sales_history: List[Dict] = []
    
    def _initialize_matrix(self) -> np.ndarray:
        """Инициализация матрицы коэффициентов"""
        # Создаем матрицу: строки - дни до отправления (от 0 до max_days), 
        # столбцы - загрузка в процентах (от 0 до 100)
        matrix = np.ones((self.config.max_days_before_departure + 1, 
                         self.config.max_load_percentage + 1))
        
        # Начальные значения: начинаем с минимального коэффициента внизу слева
        # и постепенно увеличиваем вверх и вправо
        for days in range(matrix.shape[0]):
            for load in range(matrix.shape[1]):
                # Базовый коэффициент зависит от дней и загрузки
                # Чем меньше дней до отправления и больше загрузка - выше коэффициент
                days_factor = 1.0 - (days / self.config.max_days_before_departure) * 0.5
                load_factor = 1.0 + (load / self.config.max_load_percentage) * 0.5
                
                base_coef = self.config.min_coefficient + \
                           (self.config.max_coefficient - self.config.min_coefficient) * \
                           (days_factor * 0.5 + load_factor * 0.5)
                
                matrix[days, load] = np.clip(base_coef, 
                                            self.config.min_coefficient, 
                                            self.config.max_coefficient)
        
        return matrix
    
    def get_coefficient(self, days_before_departure: int, load_percentage: float) -> float:
        """Получить коэффициент для заданных дней до отправления и загрузки"""
        days_idx = min(days_before_departure, self.config.max_days_before_departure)
        load_idx = min(int(load_percentage), self.config.max_load_percentage)
        
        return self.matrix[days_idx, load_idx]
    
    def calculate_price(self, 
                       days_before_departure: int,
                       load_percentage: float,
                       class_index: int,
                       month: int = 1) -> float:
        """
        Рассчитать цену для заданных параметров
        
        Args:
            days_before_departure: Дни до отправления
            load_percentage: Загрузка в процентах
            class_index: Индекс класса (0-3)
            month: Месяц для учета сезонности (1-12)
        
        Returns:
            Рассчитанная цена
        """
        # Базовый коэффициент из матрицы
        base_coef = self.get_coefficient(days_before_departure, load_percentage)
        
        # Коэффициент сезонности
        seasonality_coef = self.seasonality_coefficients[month - 1]
        
        # Коэффициент класса
        class_coef = self.class_coefficients[class_index]
        
        # Плацкартная часть цены (60% от целевой)
        platskart_base = self.config.target_price * self.config.base_platskart_share
        
        # Итоговая цена
        price = platskart_base * base_coef * seasonality_coef * class_coef
        
        return price
    
    def calculate_weighted_average_price(self, sales_by_class: Dict[int, int]) -> float:
        """
        Рассчитать средневзвешенную цену по проданным классам
        
        Args:
            sales_by_class: Словарь {class_index: количество_проданных}
        
        Returns:
            Средневзвешенная цена
        """
        total_price = 0.0
        total_quantity = 0
        
        for class_idx, quantity in sales_by_class.items():
            if quantity > 0:
                # Используем средние значения для расчета
                avg_days = self.config.max_days_before_departure // 2
                avg_load = 50.0
                avg_month = 6  # Июнь
                
                price = self.calculate_price(avg_days, avg_load, class_idx, avg_month)
                total_price += price * quantity
                total_quantity += quantity
        
        return total_price / total_quantity if total_quantity > 0 else 0.0
    
    def optimize_matrix(self, 
                       current_sales: Dict[int, int],
                       current_days: int,
                       current_load: float,
                       learning_rate: float = 0.01):
        """
        Оптимизировать матрицу коэффициентов для приближения к целевой цене
        
        Args:
            current_sales: Текущие продажи по классам {class_index: quantity}
            current_days: Текущие дни до отправления
            current_load: Текущая загрузка в процентах
            learning_rate: Скорость обучения для корректировки
        """
        if not current_sales or sum(current_sales.values()) == 0:
            return
        
        # Рассчитываем текущую средневзвешенную цену
        weighted_price = self.calculate_weighted_average_price(current_sales)
        
        # Вычисляем отклонение от целевой цены
        deviation = (self.config.target_price - weighted_price) / self.config.target_price
        
        # Корректируем коэффициент в текущей ячейке матрицы
        days_idx = min(current_days, self.config.max_days_before_departure)
        load_idx = min(int(current_load), self.config.max_load_percentage)
        
        current_coef = self.matrix[days_idx, load_idx]
        
        # Если цена ниже целевой - увеличиваем коэффициент, и наоборот
        adjustment = deviation * learning_rate
        new_coef = current_coef * (1 + adjustment)
        
        # Ограничиваем диапазоном
        new_coef = np.clip(new_coef, 
                          self.config.min_coefficient, 
                          self.config.max_coefficient)
        
        self.matrix[days_idx, load_idx] = new_coef
        
        # Сохраняем в историю
        self.sales_history.append({
            'days': current_days,
            'load': current_load,
            'sales': current_sales.copy(),
            'weighted_price': weighted_price,
            'target_price': self.config.target_price,
            'coefficient': new_coef
        })
    
    def get_matrix_dataframe(self) -> pd.DataFrame:
        """Получить матрицу в виде DataFrame для визуализации"""
        # Создаем DataFrame с днями до отправления как индекс
        # и загрузкой в процентах как столбцы
        days = range(self.config.max_days_before_departure + 1)
        loads = range(0, self.config.max_load_percentage + 1, 5)  # Каждые 5%
        
        # Создаем подматрицу для отображения
        submatrix = self.matrix[:, ::5]  # Берем каждую 5-ю колонку
        
        df = pd.DataFrame(
            submatrix,
            index=days,
            columns=loads
        )
        
        return df
    
    def set_seasonality_coefficient(self, month: int, coefficient: float):
        """Установить коэффициент сезонности для месяца"""
        if 1 <= month <= 12:
            self.seasonality_coefficients[month - 1] = coefficient
    
    def set_class_coefficient(self, class_index: int, coefficient: float):
        """Установить коэффициент для класса"""
        if 0 <= class_index < self.config.num_classes:
            self.class_coefficients[class_index] = coefficient
    
    def manual_adjust_matrix(self, days: int, load: int, new_coefficient: float):
        """Ручная корректировка коэффициента в матрице"""
        days_idx = min(days, self.config.max_days_before_departure)
        load_idx = min(load, self.config.max_load_percentage)
        
        self.matrix[days_idx, load_idx] = np.clip(
            new_coefficient,
            self.config.min_coefficient,
            self.config.max_coefficient
        )

