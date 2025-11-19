"""
Модель пассажира и его перемещения по аэропорту
"""
import simpy
import random
from typing import List, Optional
from dataclasses import dataclass
from enum import Enum


class PassengerType(Enum):
    """Типы пассажиров"""
    ECONOMY = "Эконом"
    BUSINESS = "Бизнес"
    FIRST = "Первый класс"


@dataclass
class Passenger:
    """Пассажир"""
    passenger_id: int
    passenger_type: PassengerType
    arrival_time: float
    flight_time: float  # Время вылета
    zones_visited: List[str]
    total_time_in_airport: float = 0.0
    missed_flight: bool = False


class PassengerFlow:
    """Поток пассажиров"""
    
    def __init__(self, env: simpy.Environment, airport, 
                 arrival_rate: float,  # Пассажиров в минуту
                 simulation_duration: float,  # Длительность симуляции в минутах
                 passenger_types_distribution: dict = None):
        self.env = env
        self.airport = airport
        self.arrival_rate = arrival_rate
        self.simulation_duration = simulation_duration
        self.passenger_types_distribution = passenger_types_distribution or {
            PassengerType.ECONOMY: 0.7,
            PassengerType.BUSINESS: 0.25,
            PassengerType.FIRST: 0.05
        }
        self.passengers: List[Passenger] = []
        self.passenger_counter = 0
        
    def generate_passenger_type(self) -> PassengerType:
        """Генерация типа пассажира согласно распределению"""
        rand = random.random()
        cumulative = 0
        for ptype, prob in self.passenger_types_distribution.items():
            cumulative += prob
            if rand <= cumulative:
                return ptype
        return PassengerType.ECONOMY
    
    def passenger_process(self, passenger: Passenger, zone_sequence: List[str]):
        """Процесс прохождения пассажира через зоны"""
        start_time = self.env.now
        
        for zone_name in zone_sequence:
            zone = self.airport.get_zone(zone_name)
            if zone:
                yield self.env.process(zone.service(passenger.passenger_id))
                passenger.zones_visited.append(zone_name)
            else:
                # Если зона не найдена, пропускаем
                continue
        
        # Проверка, успел ли пассажир на рейс
        passenger.total_time_in_airport = self.env.now - start_time
        if self.env.now > passenger.flight_time:
            passenger.missed_flight = True
    
    def run(self):
        """Запуск генерации пассажиров"""
        while self.env.now < self.simulation_duration:
            # Интервал между прибытиями (экспоненциальное распределение)
            inter_arrival_time = random.expovariate(self.arrival_rate)
            yield self.env.timeout(inter_arrival_time)
            
            # Создание нового пассажира
            self.passenger_counter += 1
            passenger_type = self.generate_passenger_type()
            
            # Время вылета (через 60-180 минут после прибытия)
            flight_time = self.env.now + random.uniform(60, 180)
            
            passenger = Passenger(
                passenger_id=self.passenger_counter,
                passenger_type=passenger_type,
                arrival_time=self.env.now,
                flight_time=flight_time,
                zones_visited=[]
            )
            
            self.passengers.append(passenger)
            
            # Определение последовательности зон в зависимости от типа пассажира
            if passenger_type == PassengerType.FIRST:
                # Первый класс - быстрая регистрация, отдельный досмотр
                zone_sequence = ["Check-In VIP", "Security VIP", "Passport Control", "Gate", "Boarding"]
            elif passenger_type == PassengerType.BUSINESS:
                # Бизнес класс - отдельная регистрация
                zone_sequence = ["Check-In Business", "Security", "Passport Control", "Gate", "Boarding"]
            else:
                # Эконом класс - стандартный маршрут
                zone_sequence = ["Check-In", "Security", "Passport Control", "Gate", "Boarding"]
            
            # Запуск процесса пассажира
            self.env.process(self.passenger_process(passenger, zone_sequence))
    
    def get_statistics(self) -> dict:
        """Получить статистику по пассажирам"""
        if not self.passengers:
            return {
                'total_passengers': 0,
                'missed_flights': 0,
                'avg_time_in_airport': 0,
                'missed_flight_rate': 0
            }
        
        total = len(self.passengers)
        missed = sum(1 for p in self.passengers if p.missed_flight)
        avg_time = sum(p.total_time_in_airport for p in self.passengers) / total
        
        return {
            'total_passengers': total,
            'missed_flights': missed,
            'avg_time_in_airport': avg_time,
            'missed_flight_rate': missed / total if total > 0 else 0
        }



