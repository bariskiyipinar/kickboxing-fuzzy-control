#!/usr/bin/env python
# coding: utf-8

import tkinter as tk
from tkinter import messagebox
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import requests
from io import BytesIO

# ---------- BULANIK DEĞİŞKENLER VE KURALLAR ----------

kalp_atisi = ctrl.Antecedent(np.arange(40, 181, 1), 'Kalp Atış Hızı (BPM)')
kas_yorgunlugu = ctrl.Antecedent(np.arange(0, 11, 1), 'Kas Yorgunluğu (0-10)')
onceki_set = ctrl.Antecedent(np.arange(0, 11, 1), 'Önceki Set Zorluğu (0-10)')
uyku = ctrl.Antecedent(np.arange(0, 11, 1), 'Uyku Kalitesi (0-10)')
su = ctrl.Antecedent(np.arange(0, 4.1, 0.1), 'Su Tüketimi (L)')

antrenman_zorlugu = ctrl.Consequent(np.arange(0, 11, 1), 'Antrenman Zorluğu')
dinlenme_suresi = ctrl.Consequent(np.arange(0, 61, 1), 'Dinlenme Süresi (dak)')

# Üyelik fonksiyonları
kalp_atisi['düşük'] = fuzz.trimf(kalp_atisi.universe, [40, 40, 90])
kalp_atisi['orta'] = fuzz.trimf(kalp_atisi.universe, [80, 110, 140])
kalp_atisi['yüksek'] = fuzz.trimf(kalp_atisi.universe, [130, 180, 180])

kas_yorgunlugu['az'] = fuzz.trimf(kas_yorgunlugu.universe, [0, 0, 5])
kas_yorgunlugu['orta'] = fuzz.trimf(kas_yorgunlugu.universe, [3, 5, 7])
kas_yorgunlugu['çok'] = fuzz.trimf(kas_yorgunlugu.universe, [6, 10, 10])

onceki_set['kolay'] = fuzz.trimf(onceki_set.universe, [0, 0, 5])
onceki_set['orta'] = fuzz.trimf(onceki_set.universe, [3, 5, 7])
onceki_set['zor'] = fuzz.trimf(onceki_set.universe, [6, 10, 10])

uyku['kötü'] = fuzz.trimf(uyku.universe, [0, 0, 5])
uyku['orta'] = fuzz.trimf(uyku.universe, [3, 5, 7])
uyku['iyi'] = fuzz.trimf(uyku.universe, [6, 10, 10])

su['az'] = fuzz.trimf(su.universe, [0, 0, 2])
su['yeterli'] = fuzz.trimf(su.universe, [1, 2, 3])
su['çok'] = fuzz.trimf(su.universe, [2.5, 4, 4])

antrenman_zorlugu['düşük'] = fuzz.trimf(antrenman_zorlugu.universe, [0, 0, 5])
antrenman_zorlugu['orta'] = fuzz.trimf(antrenman_zorlugu.universe, [3, 5, 7])
antrenman_zorlugu['yüksek'] = fuzz.trimf(antrenman_zorlugu.universe, [6, 10, 10])

dinlenme_suresi['kısa'] = fuzz.trimf(dinlenme_suresi.universe, [0, 0, 20])
dinlenme_suresi['orta'] = fuzz.trimf(dinlenme_suresi.universe, [15, 30, 45])
dinlenme_suresi['uzun'] = fuzz.trimf(dinlenme_suresi.universe, [40, 60, 60])

# Kurallar
rule1 = ctrl.Rule(kalp_atisi['yüksek'] | kas_yorgunlugu['çok'] | onceki_set['zor'],
                  (antrenman_zorlugu['yüksek'], dinlenme_suresi['uzun']))
rule2 = ctrl.Rule(uyku['kötü'] | su['az'],
                  (antrenman_zorlugu['düşük'], dinlenme_suresi['uzun']))
rule3 = ctrl.Rule(kalp_atisi['orta'] & kas_yorgunlugu['orta'] & uyku['iyi'],
                  (antrenman_zorlugu['orta'], dinlenme_suresi['orta']))
rule4 = ctrl.Rule(kalp_atisi['düşük'] & kas_yorgunlugu['az'],
                  (antrenman_zorlugu['düşük'], dinlenme_suresi['kısa']))

training_system = ctrl.ControlSystem([rule1, rule2, rule3, rule4])
training = ctrl.ControlSystemSimulation(training_system)

# ---------- ARAYÜZ SINIFI ----------

class KickboxingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🥊 Kickboks Antrenman Kontrolcüsü 🥊")
        self.geometry("700x1100")
        self.configure(bg="#222831")

        url = "https://images.pexels.com/photos/10689269/pexels-photo-10689269.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"
        try:
            response = requests.get(url)
            img_data = response.content
            self.bg_image = Image.open(BytesIO(img_data)).resize((700, 1100))
            self.bg_photo = ImageTk.PhotoImage(self.bg_image)
            self.bg_label = tk.Label(self, image=self.bg_photo)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            messagebox.showwarning("Uyarı", f"Arka plan resmi indirilemedi.\n{e}")

        title = tk.Label(self, text="🥋 Kickboks Antrenman Kontrolcüsü", font=("Helvetica", 20, "bold"), fg="#00adb5", bg="#222831")
        title.pack(pady=10)

        self.entries = {}
        self.inputs = [
            ("Kalp Atış Hızı (BPM)", 40, 180, kalp_atisi),
            ("Kas Yorgunluğu (0-10)", 0, 10, kas_yorgunlugu),
            ("Önceki Set Zorluğu (0-10)", 0, 10, onceki_set),
            ("Uyku Kalitesi (0-10)", 0, 10, uyku),
            ("Su Tüketimi (L)", 0, 4, su)
        ]

        for label_text, min_val, max_val, _ in self.inputs:
            frame = tk.Frame(self, bg="#393e46")
            frame.pack(pady=5, padx=15, fill='x')
            lbl = tk.Label(frame, text=label_text + " 🏋️‍♂️", font=("Helvetica", 12), fg="#eeeeee", bg="#393e46")
            lbl.pack(side="left", padx=10)
            entry = tk.Entry(frame, font=("Helvetica", 12))
            entry.pack(side="left", fill='x', expand=True, padx=10)
            self.entries[label_text] = (entry, min_val, max_val)

        calc_btn = tk.Button(self, text="🚀 Hesapla", font=("Helvetica", 14, "bold"), bg="#00adb5", fg="#222831", command=self.calculate)
        calc_btn.pack(pady=15)

        self.result_antrenman = tk.Label(self, text="", font=("Helvetica", 16, "bold"), fg="#ffd369", bg="#222831")
        self.result_antrenman.pack(pady=5)
        self.result_dinlenme = tk.Label(self, text="", font=("Helvetica", 16, "bold"), fg="#ffd369", bg="#222831")
        self.result_dinlenme.pack(pady=5)

        # Grafikların gösterileceği frame
        self.graph_frame = tk.Frame(self, bg="#222831")
        self.graph_frame.pack(pady=10, fill='both', expand=True)

        # Grafik canvas referanslarını tutar
        self.canvas_antrenman = None
        self.canvas_dinlenme = None
        self.canvas_inputs = {}  # Girdi grafik canvasları
        self.current_values = {}

    def calculate(self):
        try:
            # Girdi değerlerini al ve doğrula
            for label_text, min_val, max_val in [(k, v[1], v[2]) for k,v in self.entries.items()]:
                entry_widget = self.entries[label_text][0]
                val_str = entry_widget.get()
                val = float(val_str)
                if val < min_val or val > max_val:
                    raise ValueError(f"{label_text} için değer {min_val} ile {max_val} arasında olmalıdır.")
                self.current_values[label_text] = val
        except ValueError as e:
            messagebox.showerror("Hata", str(e))
            return

        # Girdi değerlerini bulanık kontrol sistemine ata
        training.input['Kalp Atış Hızı (BPM)'] = self.current_values['Kalp Atış Hızı (BPM)']
        training.input['Kas Yorgunluğu (0-10)'] = self.current_values['Kas Yorgunluğu (0-10)']
        training.input['Önceki Set Zorluğu (0-10)'] = self.current_values['Önceki Set Zorluğu (0-10)']
        training.input['Uyku Kalitesi (0-10)'] = self.current_values['Uyku Kalitesi (0-10)']
        training.input['Su Tüketimi (L)'] = self.current_values['Su Tüketimi (L)']

        training.compute()

        # Sonuçları al
        antrenman_degeri = training.output['Antrenman Zorluğu']
        dinlenme_degeri = training.output['Dinlenme Süresi (dak)']

        self.result_antrenman.config(text=f"Antrenman Zorluğu: {antrenman_degeri:.2f}")
        self.result_dinlenme.config(text=f"Dinlenme Süresi: {dinlenme_degeri:.2f} dakika")

        self.plot_graphs(antrenman_degeri, dinlenme_degeri)

    def plot_graphs(self, antrenman_degeri, dinlenme_degeri):
        # Önceki grafik varsa temizle
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        fig, axs = plt.subplots(3, 2, figsize=(10, 12))
        fig.subplots_adjust(hspace=0.5)

        # Giriş üyelik fonksiyonlarını çiz
        for i, (label_text, min_val, max_val, fuzzy_var) in enumerate(self.inputs):
            ax = axs[i//2, i%2]
            universe = fuzzy_var.universe
            for term_name, mf in fuzzy_var.terms.items():
                ax.plot(universe, mf.mf, label=term_name)
            # Dikey çizgi ile girilen değeri göster
            val = self.current_values.get(label_text, None)
            if val is not None:
                ax.axvline(val, color='red', linestyle='--', label=f"Girdi: {val}")
            ax.set_title(label_text)
            ax.legend()
            ax.grid(True)

        # Çıkış üyelik fonksiyonlarını çiz
        axs[2, 0].plot(antrenman_zorlugu.universe, antrenman_zorlugu['düşük'].mf, label='Düşük')
        axs[2, 0].plot(antrenman_zorlugu.universe, antrenman_zorlugu['orta'].mf, label='Orta')
        axs[2, 0].plot(antrenman_zorlugu.universe, antrenman_zorlugu['yüksek'].mf, label='Yüksek')
        axs[2, 0].axvline(antrenman_degeri, color='red', linestyle='--', label=f"Sonuç: {antrenman_degeri:.2f}")
        axs[2, 0].set_title("Antrenman Zorluğu")
        axs[2, 0].legend()
        axs[2, 0].grid(True)

        axs[2, 1].plot(dinlenme_suresi.universe, dinlenme_suresi['kısa'].mf, label='Kısa')
        axs[2, 1].plot(dinlenme_suresi.universe, dinlenme_suresi['orta'].mf, label='Orta')
        axs[2, 1].plot(dinlenme_suresi.universe, dinlenme_suresi['uzun'].mf, label='Uzun')
        axs[2, 1].axvline(dinlenme_degeri, color='red', linestyle='--', label=f"Sonuç: {dinlenme_degeri:.2f}")
        axs[2, 1].set_title("Dinlenme Süresi (dak)")
        axs[2, 1].legend()
        axs[2, 1].grid(True)

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

if __name__ == "__main__":
    app = KickboxingApp()
    app.mainloop()
