import sys, os, threading
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd

from core.config import DETECTORS_BY_LEVEL

print("=== Iniciando app_tk.py ===")

class SMCBacktestApp(tk.Tk):
    def __init__(self):
        print("  → Construindo janela principal")
        super().__init__()
        self.title("SMC Bot Backtest")
        self.geometry("650x500")
        self.file_path = None

        # Cabeçalho de seleção de arquivo
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10, fill="x")
        tk.Button(btn_frame, text="Selecione CSV/Parquet", command=self.load_file).pack(side="left", padx=5)
        self.label_file = tk.Label(btn_frame, text="Nenhum arquivo selecionado")
        self.label_file.pack(side="left", padx=5)

        # Checkbuttons de níveis
        levels_frame = tk.LabelFrame(self, text="Níveis de Detectores")
        levels_frame.pack(pady=10, fill="x", padx=5)
        self.level_vars = {}
        for lvl in DETECTORS_BY_LEVEL:
            var = tk.BooleanVar(value=True)
            chk = tk.Checkbutton(levels_frame, text=lvl, variable=var)
            chk.pack(side="left", padx=5)
            self.level_vars[lvl] = var

        # Botão de execução
        self.run_btn = tk.Button(self, text="Rodar Backtest", command=self.on_run)
        self.run_btn.pack(pady=10)

        # Barra de progresso
        self.progress = ttk.Progressbar(self, orient="horizontal", length=600, mode="determinate")
        self.progress.pack(pady=5)

        # Caixa de resultados
        self.result_box = tk.Text(self, height=15)
        self.result_box.pack(fill="both", expand=True, padx=5, pady=5)

    def load_file(self):
        fp = filedialog.askopenfilename(filetypes=[("CSV","*.csv"),("Parquet","*.parquet")])
        if fp:
            self.file_path = fp
            self.label_file.config(text=os.path.basename(fp))

    def on_run(self):
        if not self.file_path:
            messagebox.showerror("Erro", "Selecione um arquivo antes de rodar.")
            return

        self.run_btn.config(state="disabled")
        self.result_box.delete("1.0", tk.END)

        try:
            if self.file_path.lower().endswith(".csv"):
                self.df = pd.read_csv(self.file_path, parse_dates=["datetime"], infer_datetime_format=True)
            else:
                self.df = pd.read_parquet(self.file_path)
        except Exception as e:
            messagebox.showerror("Erro ao ler arquivo", str(e))
            self.run_btn.config(state="normal")
            return

        # Monta lista de detectores
        self.detectors = []
        for lvl, var in self.level_vars.items():
            if var.get():
                self.detectors += DETECTORS_BY_LEVEL[lvl]

        self.progress["maximum"] = len(self.detectors)
        self.progress["value"] = 0

        threading.Thread(target=self._threaded_backtest, daemon=True).start()

    def _threaded_backtest(self):
        results = {}
        for i, det in enumerate(self.detectors, start=1):
            res = det(self.df)
            cnt = 1 if isinstance(res, bool) else len(res)
            results[det.__name__] = cnt
            # agenda update da barra
            self.after(0, lambda v=i: self.progress.config(value=v))

        self.after(0, self._finish_backtest, results)

    def _finish_backtest(self, results):
        for name, cnt in results.items():
            self.result_box.insert(tk.END, f"{name}: sinais = {cnt}\n")
        self.run_btn.config(state="normal")

if __name__ == "__main__":
    print("  → Chamando mainloop()")
    app = SMCBacktestApp()
    app.mainloop()

