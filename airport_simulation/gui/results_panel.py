"""
Панель отображения результатов симуляции
"""
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText


class ResultsPanel(ttk.Frame):
    """Панель результатов"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
    
    def create_widgets(self):
        """Создание виджетов"""
        # Заголовок
        title = ttk.Label(self, text="Результаты симуляции", font=("Arial", 14, "bold"))
        title.pack(pady=10)
        
        # Notebook для вкладок
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Вкладка статистики по зонам
        zones_frame = ttk.Frame(notebook)
        notebook.add(zones_frame, text="Статистика по зонам")
        
        self.zones_tree = ttk.Treeview(zones_frame, columns=("served", "avg_wait", "avg_service", "avg_queue", "utilization"),
                                      show="headings", height=15)
        self.zones_tree.heading("#0", text="Зона")
        self.zones_tree.heading("served", text="Обслужено")
        self.zones_tree.heading("avg_wait", text="Ср. время ожидания (мин)")
        self.zones_tree.heading("avg_service", text="Ср. время обслуживания (мин)")
        self.zones_tree.heading("avg_queue", text="Ср. длина очереди")
        self.zones_tree.heading("utilization", text="Загрузка (%)")
        
        self.zones_tree.column("#0", width=200)
        self.zones_tree.column("served", width=100)
        self.zones_tree.column("avg_wait", width=150)
        self.zones_tree.column("avg_service", width=150)
        self.zones_tree.column("avg_queue", width=120)
        self.zones_tree.column("utilization", width=100)
        
        zones_scroll = ttk.Scrollbar(zones_frame, orient=tk.VERTICAL, command=self.zones_tree.yview)
        self.zones_tree.configure(yscrollcommand=zones_scroll.set)
        
        self.zones_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        zones_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Вкладка статистики по пассажирам
        passengers_frame = ttk.Frame(notebook)
        notebook.add(passengers_frame, text="Статистика по пассажирам")
        
        self.passengers_text = ScrolledText(passengers_frame, height=20, wrap=tk.WORD)
        self.passengers_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Вкладка общего анализа
        analysis_frame = ttk.Frame(notebook)
        notebook.add(analysis_frame, text="Общий анализ")
        
        self.analysis_text = ScrolledText(analysis_frame, height=20, wrap=tk.WORD)
        self.analysis_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def show_loading(self):
        """Показать индикатор загрузки"""
        # Очистка данных
        for item in self.zones_tree.get_children():
            self.zones_tree.delete(item)
        self.passengers_text.delete(1.0, tk.END)
        self.analysis_text.delete(1.0, tk.END)
        
        self.passengers_text.insert(tk.END, "Выполняется симуляция... Пожалуйста, подождите.\n")
        self.analysis_text.insert(tk.END, "Выполняется симуляция... Пожалуйста, подождите.\n")
    
    def update_results(self, results):
        """Обновление результатов"""
        if not results:
            return
        
        # Обновление статистики по зонам
        for item in self.zones_tree.get_children():
            self.zones_tree.delete(item)
        
        for zone_stat in results.get('zones', []):
            self.zones_tree.insert("", tk.END, text=zone_stat['zone_name'],
                                  values=(
                                      int(zone_stat['total_served']),
                                      f"{zone_stat['avg_wait_time']:.2f}",
                                      f"{zone_stat['avg_service_time']:.2f}",
                                      f"{zone_stat['avg_queue_length']:.2f}",
                                      f"{zone_stat['utilization']*100:.1f}"
                                  ))
        
        # Обновление статистики по пассажирам
        self.passengers_text.delete(1.0, tk.END)
        passenger_stats = results.get('passengers', {})
        
        self.passengers_text.insert(tk.END, "=== СТАТИСТИКА ПО ПАССАЖИРАМ ===\n\n")
        self.passengers_text.insert(tk.END, f"Всего пассажиров: {passenger_stats.get('total_passengers', 0)}\n")
        self.passengers_text.insert(tk.END, f"Пропущено рейсов: {passenger_stats.get('missed_flights', 0)}\n")
        self.passengers_text.insert(tk.END, f"Процент пропущенных рейсов: {passenger_stats.get('missed_flight_rate', 0)*100:.2f}%\n")
        self.passengers_text.insert(tk.END, f"Среднее время в аэропорту: {passenger_stats.get('avg_time_in_airport', 0):.2f} минут\n")
        
        # Обновление общего анализа
        self.analysis_text.delete(1.0, tk.END)
        self.analysis_text.insert(tk.END, "=== ОБЩИЙ АНАЛИЗ ===\n\n")
        
        # Анализ узких мест
        zones = results.get('zones', [])
        if zones:
            max_wait = max(zones, key=lambda z: z['avg_wait_time'])
            max_queue = max(zones, key=lambda z: z['avg_queue_length'])
            max_util = max(zones, key=lambda z: z['utilization'])
            
            self.analysis_text.insert(tk.END, "УЗКИЕ МЕСТА:\n")
            self.analysis_text.insert(tk.END, f"- Максимальное время ожидания: {max_wait['zone_name']} "
                                             f"({max_wait['avg_wait_time']:.2f} мин)\n")
            self.analysis_text.insert(tk.END, f"- Максимальная очередь: {max_queue['zone_name']} "
                                             f"({max_queue['avg_queue_length']:.2f} пассажиров)\n")
            self.analysis_text.insert(tk.END, f"- Максимальная загрузка: {max_util['zone_name']} "
                                             f"({max_util['utilization']*100:.1f}%)\n\n")
            
            # Рекомендации
            self.analysis_text.insert(tk.END, "РЕКОМЕНДАЦИИ:\n")
            for zone in zones:
                if zone['utilization'] > 0.8:
                    self.analysis_text.insert(tk.END, f"- Увеличить пропускную способность зоны '{zone['zone_name']}' "
                                                     f"(текущая загрузка: {zone['utilization']*100:.1f}%)\n")
                if zone['avg_wait_time'] > 10:
                    self.analysis_text.insert(tk.END, f"- Оптимизировать зону '{zone['zone_name']}' "
                                                     f"(среднее время ожидания: {zone['avg_wait_time']:.2f} мин)\n")



