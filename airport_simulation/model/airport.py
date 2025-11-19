"""
Модель аэропорта с различными зонами обслуживания
"""
import simpy
import random
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum


class ZoneType(Enum):
    """Типы зон в аэропорту"""
    CHECK_IN = "Регистрация"
    SECURITY = "Досмотр"
    PASSPORT = "Паспортный контроль"
    GATE = "Гейт"
    BOARDING = "Посадка"


@dataclass
class ZoneConfig:
    """Конфигурация зоны"""
    name: str
    zone_type: ZoneType
    capacity: int  # Количество параллельных сервисов
    service_time_mean: float  # Среднее время обслуживания (минуты)
    service_time_std: float  # Стандартное отклонение времени обслуживания


class AirportZone:
    """Зона обслуживания в аэропорту"""
    
    def __init__(self, env: simpy.Environment, config: ZoneConfig):
        self.env = env
        self.config = config
        self.resource = simpy.Resource(env, capacity=config.capacity)
        self.queue_length_history = []
        self.service_times = []
        self.total_served = 0
        self.total_wait_time = 0.0
        
    def service(self, passenger_id: int) -> simpy.Process:
        """Процесс обслуживания пассажира"""
        arrival_time = self.env.now
        
        # Запись длины очереди
        queue_length = len(self.resource.queue)
        self.queue_length_history.append((self.env.now, queue_length))
        
        with self.resource.request() as request:
            yield request
            
            # Время ожидания в очереди
            wait_time = self.env.now - arrival_time
            self.total_wait_time += wait_time
            
            # Время обслуживания (нормальное распределение)
            service_time = max(0.1, random.gauss(
                self.config.service_time_mean,
                self.config.service_time_std
            ))
            
            yield self.env.timeout(service_time)
            
            self.service_times.append(service_time)
            self.total_served += 1
            
            return service_time + wait_time
    
    def get_statistics(self) -> Dict:
        """Получить статистику по зоне"""
        avg_wait_time = (self.total_wait_time / self.total_served 
                        if self.total_served > 0 else 0)
        avg_service_time = (sum(self.service_times) / len(self.service_times)
                           if self.service_times else 0)
        avg_queue_length = (sum(length for _, length in self.queue_length_history) 
                           / len(self.queue_length_history)
                           if self.queue_length_history else 0)
        
        return {
            'zone_name': self.config.name,
            'zone_type': self.config.zone_type.value,
            'total_served': self.total_served,
            'avg_wait_time': avg_wait_time,
            'avg_service_time': avg_service_time,
            'avg_queue_length': avg_queue_length,
            'utilization': (self.total_served * avg_service_time / (self.env.now * self.config.capacity)
                           if self.env.now > 0 else 0)
        }


class Airport:
    """Модель аэропорта"""
    
    def __init__(self, env: simpy.Environment, zones_config: List[ZoneConfig]):
        self.env = env
        self.zones: Dict[str, AirportZone] = {}
        
        # Создание зон
        for config in zones_config:
            zone = AirportZone(env, config)
            self.zones[config.name] = zone
    
    def get_zone(self, zone_name: str) -> AirportZone:
        """Получить зону по имени"""
        return self.zones.get(zone_name)
    
    def get_all_statistics(self) -> List[Dict]:
        """Получить статистику по всем зонам"""
        return [zone.get_statistics() for zone in self.zones.values()]



