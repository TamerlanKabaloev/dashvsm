"""
Главное окно приложения
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import sys
import os

# Добавление корневой директории в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation.engine import SimulationEngine
from gui.results_panel import ResultsPanel
from gui.config_panel import ConfigPanel
from gui.visualization_panel import VisualizationPanel


class AirportSimulationApp:
    """Главное приложение"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Анализ пассажиропотоков в аэропорту")
        self.root.geometry("1400x900")
        
        self.simulation_engine = SimulationEngine()
        
        # Создание интерфейса
        self.create_widgets()
        
    def create_widgets(self):
        """Создание виджетов интерфейса"""
        # Главный контейнер
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Левая панель - конфигурация
        left_frame = ttk.Frame(main_container)
        main_container.add(left_frame, weight=1)
        
        # Правая панель - результаты и визуализация
        right_frame = ttk.Frame(main_container)
        main_container.add(right_frame, weight=2)
        
        # Панель конфигурации
        self.config_panel = ConfigPanel(left_frame, self.on_simulation_start)
        self.config_panel.pack(fill=tk.BOTH, expand=True)
        
        # Панель результатов
        self.results_panel = ResultsPanel(right_frame)
        self.results_panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Панель визуализации
        self.viz_panel = VisualizationPanel(right_frame)
        self.viz_panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def on_simulation_start(self, config):
        """Обработчик запуска симуляции"""
        def run_simulation():
            try:
                # Запуск симуляции в отдельном потоке
                self.simulation_engine.run_simulation(
                    arrival_rate=config['arrival_rate'],
                    simulation_duration=config['simulation_duration']
                )
                
                # Получение результатов
                results = self.simulation_engine.get_results()
                
                # Обновление UI в главном потоке
                self.root.after(0, lambda: self.on_simulation_complete(results))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Ошибка", f"Ошибка симуляции: {str(e)}"))
        
        # Запуск в отдельном потоке
        thread = threading.Thread(target=run_simulation, daemon=True)
        thread.start()
        
        # Показ индикатора загрузки
        self.results_panel.show_loading()
    
    def on_simulation_complete(self, results):
        """Обработчик завершения симуляции"""
        # Обновление панели результатов
        self.results_panel.update_results(results)
        
        # Обновление визуализации
        self.viz_panel.update_visualization(results)

