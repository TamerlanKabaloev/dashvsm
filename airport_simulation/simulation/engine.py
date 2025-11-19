"""
Движок имитационного моделирования
"""
import simpy
from typing import List, Dict, Callable, Optional
from model.airport import Airport, ZoneConfig, ZoneType
from model.passenger import PassengerFlow


class SimulationEngine:
    """Движок симуляции"""
    
    def __init__(self):
        self.env: Optional[simpy.Environment] = None
        self.airport: Optional[Airport] = None
        self.passenger_flow: Optional[PassengerFlow] = None
        self.is_running = False
        self.progress_callback: Optional[Callable] = None
        
    def create_default_zones(self) -> List[ZoneConfig]:
        """Создание зон по умолчанию"""
        return [
            # Эконом класс
            ZoneConfig("Check-In", ZoneType.CHECK_IN, capacity=8, service_time_mean=3.0, service_time_std=1.0),
            ZoneConfig("Security", ZoneType.SECURITY, capacity=4, service_time_mean=2.0, service_time_std=0.5),
            ZoneConfig("Passport Control", ZoneType.PASSPORT, capacity=6, service_time_mean=1.5, service_time_std=0.3),
            ZoneConfig("Gate", ZoneType.GATE, capacity=20, service_time_mean=0.5, service_time_std=0.1),
            ZoneConfig("Boarding", ZoneType.BOARDING, capacity=2, service_time_mean=1.0, service_time_std=0.2),
            
            # Бизнес класс
            ZoneConfig("Check-In Business", ZoneType.CHECK_IN, capacity=2, service_time_mean=2.0, service_time_std=0.5),
            
            # VIP
            ZoneConfig("Check-In VIP", ZoneType.CHECK_IN, capacity=1, service_time_mean=1.5, service_time_std=0.3),
            ZoneConfig("Security VIP", ZoneType.SECURITY, capacity=1, service_time_mean=1.0, service_time_std=0.2),
        ]
    
    def run_simulation(self, 
                      arrival_rate: float = 2.0,  # Пассажиров в минуту
                      simulation_duration: float = 480,  # 8 часов
                      zones_config: Optional[List[ZoneConfig]] = None,
                      progress_callback: Optional[Callable] = None):
        """Запуск симуляции"""
        self.is_running = True
        self.progress_callback = progress_callback
        
        # Создание окружения
        self.env = simpy.Environment()
        
        # Создание зон
        if zones_config is None:
            zones_config = self.create_default_zones()
        
        self.airport = Airport(self.env, zones_config)
        
        # Создание потока пассажиров
        self.passenger_flow = PassengerFlow(
            self.env,
            self.airport,
            arrival_rate,
            simulation_duration
        )
        
        # Запуск генерации пассажиров
        self.env.process(self.passenger_flow.run())
        
        # Запуск симуляции
        try:
            self.env.run(until=simulation_duration)
        except Exception as e:
            print(f"Ошибка симуляции: {e}")
        finally:
            self.is_running = False
    
    def get_results(self) -> Dict:
        """Получить результаты симуляции"""
        if not self.airport or not self.passenger_flow:
            return {}
        
        zone_stats = self.airport.get_all_statistics()
        passenger_stats = self.passenger_flow.get_statistics()
        
        return {
            'zones': zone_stats,
            'passengers': passenger_stats,
            'simulation_time': self.env.now if self.env else 0
        }
    
    def stop(self):
        """Остановка симуляции"""
        self.is_running = False
        if self.env:
            # Прерывание симуляции
            pass



