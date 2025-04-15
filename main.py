import tkinter as tk
from tkinter import ttk
import pyvisa
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque
import threading
import time
import random  # Só para simular leituras — remova quando conectar com o sensor de verdade

# ----------------- CONFIGURAÇÕES DO ALARME -----------------
ALARM_LOW = 35.0    # Temperatura baixa
ALARM_HIGH = 39.0   # Temperatura alta

# ----------------- COMUNICAÇÃO VIA PYVISA -----------------
rm = pyvisa.ResourceManager()
# Substituir pelo endereço do instrumento
# Ex: 'USB0::0x1AB1::0x0588::DS1ZA170000000::INSTR'
# device = rm.open_resource("SEU_ENDEREÇO_AQUI")

# Função para obter a leitura da temperatura via VISA
def ler_temperatura():
    # Comente a linha abaixo e descomente a de baixo ao usar um sensor real
    return round(random.uniform(5, 45), 2)  # Simulação

    # leitura = device.query("COMANDO_PARA_LER_TEMPERATURA")
    # return float(leitura)

class MonitorTemperatura:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor de Temperatura - PT100")

        # Dados
        self.temps = []
        self.times = []
        self.last_10 = deque(maxlen=10)
        self.max_temp = None
        self.min_temp = None
        self.start_time = time.time()

        # Criação do gráfico
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.line, = self.ax.plot([], [], color='blue')
        self.ax.set_title("Temperatura x Tempo")
        self.ax.set_xlabel("Tempo (s)")
        self.ax.set_ylabel("Temperatura (°C)")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack()

        # Infos de temperatura
        self.label_temp = ttk.Label(root, text="Temperatura atual: -- °C", font=("Arial", 12))
        self.label_temp.pack()

        self.label_max = ttk.Label(root, text="Máxima: -- °C", font=("Arial", 10))
        self.label_max.pack()

        self.label_min = ttk.Label(root, text="Mínima: -- °C", font=("Arial", 10))
        self.label_min.pack()

        self.label_ultimos = ttk.Label(root, text="Últimos 10 valores: --", font=("Arial", 10))
        self.label_ultimos.pack()

        self.label_alarme = ttk.Label(root, text="", font=("Arial", 12, "bold"))
        self.label_alarme.pack(pady=10)

        # Iniciar a atualização
        self.atualizar_dados()

    def atualizar_dados(self):
        temp = ler_temperatura()
        tempo = time.time() - self.start_time

        self.temps.append(temp)
        self.times.append(tempo)
        self.last_10.append(temp)

        # Atualiza máximos e mínimos
        if self.max_temp is None or temp > self.max_temp:
            self.max_temp = temp
        if self.min_temp is None or temp < self.min_temp:
            self.min_temp = temp

        # Atualiza gráfico
        self.line.set_data(self.times, self.temps)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

        # Atualiza labels
        self.label_temp.config(text=f"Temperatura atual: {temp:.2f} °C")
        self.label_max.config(text=f"Máxima: {self.max_temp:.2f} °C")
        self.label_min.config(text=f"Mínima: {self.min_temp:.2f} °C")
        self.label_ultimos.config(text=f"Últimos 10 valores: {list(self.last_10)}")

        # Verifica alarmes
        if temp < ALARM_LOW:
            self.label_alarme.config(text="⚠️ Alerta: Temperatura MUITO BAIXA!", foreground="blue")
        elif temp > ALARM_HIGH:
            self.label_alarme.config(text="⚠️ Alerta: Temperatura MUITO ALTA!", foreground="red")
        else:
            self.label_alarme.config(text="Temperatura dentro da faixa segura", foreground="green")

        # Chama novamente após 1 segundo
        self.root.after(1000, self.atualizar_dados)


# ----------------- INICIAR A INTERFACE -----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = MonitorTemperatura(root)
    root.mainloop()
