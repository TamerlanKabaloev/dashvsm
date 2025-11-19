"""
Панель конфигурации параметров симуляции
"""
import tkinter as tk
from tkinter import ttk


class ConfigPanel(ttk.Frame):
    """Панель настройки параметров"""
    
    def __init__(self, parent, on_start_callback):
        super().__init__(parent)
        self.on_start_callback = on_start_callback
        self.create_widgets()
    
    def create_widgets(self):
        """Создание виджетов"""
        # Заголовок
        title = ttk.Label(self, text="Параметры симуляции", font=("Arial", 14, "bold"))
        title.pack(pady=10)
        
        # Параметры потока пассажиров
        flow_frame = ttk.LabelFrame(self, text="Поток пассажиров", padding=10)
        flow_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(flow_frame, text="Интенсивность прибытия (пасс/мин):").pack(anchor=tk.W)
        self.arrival_rate_var = tk.DoubleVar(value=2.0)
        arrival_rate_spin = ttk.Spinbox(flow_frame, from_=0.1, to=10.0, increment=0.1,
                                        textvariable=self.arrival_rate_var, width=15)
        arrival_rate_spin.pack(fill=tk.X, pady=2)
        
        ttk.Label(flow_frame, text="Длительность симуляции (мин):").pack(anchor=tk.W, pady=(10, 0))
        self.duration_var = tk.DoubleVar(value=480.0)
        duration_spin = ttk.Spinbox(flow_frame, from_=60, to=1440, increment=60,
                                    textvariable=self.duration_var, width=15)
        duration_spin.pack(fill=tk.X, pady=2)
        
        # Параметры зон
        zones_frame = ttk.LabelFrame(self, text="Конфигурация зон", padding=10)
        zones_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Создание скроллируемой области для зон
        canvas = tk.Canvas(zones_frame)
        scrollbar = ttk.Scrollbar(zones_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Зоны по умолчанию
        self.zone_vars = {}
        zones_config = [
            ("Check-In", "capacity", 8, 1, 20),
            ("Check-In", "service_time", 3.0, 0.5, 10.0),
            ("Security", "capacity", 4, 1, 10),
            ("Security", "service_time", 2.0, 0.5, 5.0),
            ("Passport Control", "capacity", 6, 1, 15),
            ("Passport Control", "service_time", 1.5, 0.5, 5.0),
            ("Gate", "capacity", 20, 1, 50),
            ("Gate", "service_time", 0.5, 0.1, 2.0),
            ("Boarding", "capacity", 2, 1, 10),
            ("Boarding", "service_time", 1.0, 0.2, 5.0),
        ]
        
        current_zone = None
        for zone_name, param, default, min_val, max_val in zones_config:
            if zone_name != current_zone:
                current_zone = zone_name
                ttk.Label(scrollable_frame, text=f"\n{zone_name}:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(5, 0))
            
            key = f"{zone_name}_{param}"
            label_text = "Вместимость" if param == "capacity" else "Время обслуживания (мин)"
            ttk.Label(scrollable_frame, text=label_text).pack(anchor=tk.W)
            
            var = tk.DoubleVar(value=default)
            self.zone_vars[key] = var
            spin = ttk.Spinbox(scrollable_frame, from_=min_val, to=max_val, increment=0.1 if param == "service_time" else 1,
                              textvariable=var, width=15)
            spin.pack(fill=tk.X, pady=2)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Кнопка запуска
        start_btn = ttk.Button(self, text="Запустить симуляцию", command=self.start_simulation)
        start_btn.pack(pady=20)
    
    def start_simulation(self):
        """Запуск симуляции"""
        config = {
            'arrival_rate': self.arrival_rate_var.get(),
            'simulation_duration': self.duration_var.get(),
            'zones': self.zone_vars
        }
        self.on_start_callback(config)



