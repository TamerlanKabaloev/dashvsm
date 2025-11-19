"""
Панель визуализации результатов
"""
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np


class VisualizationPanel(ttk.Frame):
    """Панель визуализации"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
    
    def create_widgets(self):
        """Создание виджетов"""
        # Заголовок
        title = ttk.Label(self, text="Визуализация", font=("Arial", 14, "bold"))
        title.pack(pady=10)
        
        # Создание фигуры matplotlib
        self.fig = Figure(figsize=(12, 8), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Начальный график
        self.show_placeholder()
    
    def show_placeholder(self):
        """Показать заглушку"""
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.text(0.5, 0.5, 'Запустите симуляцию для отображения графиков',
                ha='center', va='center', fontsize=14, transform=ax.transAxes)
        ax.axis('off')
        self.canvas.draw()
    
    def update_visualization(self, results):
        """Обновление визуализации"""
        if not results or not results.get('zones'):
            self.show_placeholder()
            return
        
        self.fig.clear()
        zones = results['zones']
        
        if not zones:
            self.show_placeholder()
            return
        
        # Создание подграфиков
        gs = self.fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        
        # График 1: Среднее время ожидания по зонам
        ax1 = self.fig.add_subplot(gs[0, 0])
        zone_names = [z['zone_name'] for z in zones]
        wait_times = [z['avg_wait_time'] for z in zones]
        ax1.barh(zone_names, wait_times, color='skyblue')
        ax1.set_xlabel('Среднее время ожидания (мин)')
        ax1.set_title('Время ожидания по зонам')
        ax1.grid(axis='x', alpha=0.3)
        
        # График 2: Загрузка зон
        ax2 = self.fig.add_subplot(gs[0, 1])
        utilizations = [z['utilization'] * 100 for z in zones]
        colors = ['red' if u > 80 else 'orange' if u > 60 else 'green' for u in utilizations]
        ax2.barh(zone_names, utilizations, color=colors)
        ax2.set_xlabel('Загрузка (%)')
        ax2.set_title('Загрузка зон')
        ax2.set_xlim(0, 100)
        ax2.grid(axis='x', alpha=0.3)
        
        # График 3: Средняя длина очереди
        ax3 = self.fig.add_subplot(gs[1, 0])
        queue_lengths = [z['avg_queue_length'] for z in zones]
        ax3.barh(zone_names, queue_lengths, color='coral')
        ax3.set_xlabel('Средняя длина очереди')
        ax3.set_title('Длина очереди по зонам')
        ax3.grid(axis='x', alpha=0.3)
        
        # График 4: Количество обслуженных пассажиров
        ax4 = self.fig.add_subplot(gs[1, 1])
        served = [z['total_served'] for z in zones]
        ax4.barh(zone_names, served, color='lightgreen')
        ax4.set_xlabel('Количество обслуженных пассажиров')
        ax4.set_title('Пропускная способность')
        ax4.grid(axis='x', alpha=0.3)
        
        # Поворот подписей для лучшей читаемости
        for ax in [ax1, ax2, ax3, ax4]:
            ax.tick_params(axis='y', labelsize=8)
        
        self.canvas.draw()



