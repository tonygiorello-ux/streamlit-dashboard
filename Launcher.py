import tkinter as tk
import subprocess
import os
import sys
import platform

# --- DÉFINIR LES CHEMINS DE TES SCRIPTS ---
SCRIPTS = {
    "Dashboard": r"C:\Users\tgiorello\Documents\Dashboard\Dashboard.py",
    "CEO": r"C:\Users\tgiorello\Documents\Dashboard\CEO.py",
    "Saisie de Fiche": r"C:\Users\tgiorello\Documents\Dashboard\trading_app\Saisie de Fiche.py"
}

# --- LANCEMENT SILENCIEUX ---
def run_script(script_path):
    if not os.path.exists(script_path):
        return  # ne rien faire si le script n’existe pas

    try:
        # Vérifie si le script utilise Streamlit
        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()
        is_streamlit = "streamlit" in content

        # Commande à exécuter
        if is_streamlit:
            cmd = ["streamlit", "run", script_path]
        else:
            cmd = [sys.executable, script_path]

        # Supprime la fenêtre console sous Windows
        creation_flags = 0
        if platform.system() == "Windows":
            creation_flags = subprocess.CREATE_NO_WINDOW

        subprocess.Popen(
            cmd,
            shell=False,
            creationflags=creation_flags,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    except Exception as e:
        print(f"Erreur lors du lancement de {script_path}: {e}")

# --- INTERFACE PRINCIPALE ---
root = tk.Tk()
root.title("🎛️ Launcher")
root.config(bg="#1e1e1e")

frame = tk.Frame(root, bg="#1e1e1e", padx=20, pady=20)
frame.pack(expand=True)

tk.Label(frame, text="Sélection :", 
         bg="#1e1e1e", fg="white", font=("Segoe UI", 14, "bold")).pack(pady=(0, 15))

for name, path in SCRIPTS.items():
    tk.Button(
        frame, text=f" {name}", width=30,
        bg="#3a7ff6", fg="white", relief="raised", bd=3,
        command=lambda p=path: run_script(p)
    ).pack(pady=8)

tk.Button(
    frame, text="Quitter", width=30, relief="raised", bd=3,
    bg="#d9534f", fg="white",
    command=root.destroy
).pack(pady=(20, 0))

# Centrage automatique
root.update_idletasks()
width = root.winfo_reqwidth() + 20
height = root.winfo_reqheight() + 20
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width // 2) - (width // 2)
y = (screen_height // 2) - (height // 2)
root.geometry(f"{width}x{height}+{x}+{y}")
root.resizable(False, False)

root.mainloop()
