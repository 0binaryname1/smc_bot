import tkinter as tk
print("Tkinter importado com sucesso, criando janela…")
root = tk.Tk()
root.title("Teste Tkinter")
root.geometry("300x100")
label = tk.Label(root, text="Se você vê isto, Tkinter funciona!")
label.pack(pady=20)
root.mainloop()

