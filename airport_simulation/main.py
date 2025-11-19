"""
Главный файл приложения для анализа пассажиропотоков в аэропорту
"""
import tkinter as tk
import sys
import os

# Добавление текущей директории в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import AirportSimulationApp

if __name__ == "__main__":
    root = tk.Tk()
    app = AirportSimulationApp(root)
    root.mainloop()

