from __future__ import annotations

import os
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

from src.excel_parser import read_appointments
from src.pdf_generator import write_appointment_pdf, write_user_guide_pdf


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Generatore PDF appuntamenti Roma 2026")
        self.geometry("560x240")
        self.minsize(520, 220)

        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar()

        tk.Label(self, text="File Excel (.xlsx):", anchor="w").pack(fill="x", padx=12, pady=(12, 0))
        frame_input = tk.Frame(self)
        frame_input.pack(fill="x", padx=12, pady=4)
        tk.Entry(frame_input, textvariable=self.input_var, width=70).pack(side="left", fill="x", expand=True)
        tk.Button(frame_input, text="Sfoglia", command=self.choose_input).pack(side="left", padx=(8, 0))

        tk.Label(self, text="Cartella destinazione PDF:", anchor="w").pack(fill="x", padx=12, pady=(8, 0))
        frame_output = tk.Frame(self)
        frame_output.pack(fill="x", padx=12, pady=4)
        tk.Entry(frame_output, textvariable=self.output_var, width=70).pack(side="left", fill="x", expand=True)
        tk.Button(frame_output, text="Sfoglia", command=self.choose_output).pack(side="left", padx=(8, 0))

        tk.Button(self, text="Genera PDF", command=self.generate, width=20, height=2, bg="#dfefff").pack(pady=(16, 8))

    def choose_input(self) -> None:
        file_path = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx")])
        if file_path:
            self.input_var.set(file_path)

    def choose_output(self) -> None:
        folder = filedialog.askdirectory()
        if folder:
            self.output_var.set(folder)

    def generate(self) -> None:
        source = self.input_var.get().strip()
        output = self.output_var.get().strip()
        if not source:
            messagebox.showerror("Errore", "Selezionare un file Excel.")
            return
        if not output:
            messagebox.showerror("Errore", "Selezionare una cartella di destinazione.")
            return

        try:
            appointments = read_appointments(source)
            out_dir = Path(output)
            out_dir.mkdir(parents=True, exist_ok=True)
            for appointment in appointments:
                file_name = f"{appointment.group or appointment.code or appointment.source_row_number}.pdf"
                safe_name = "".join(ch if ch.isalnum() or ch in (" ", "_", "-", ".") else "_" for ch in file_name).strip()
                write_appointment_pdf(appointment, out_dir / safe_name, os.path.join(os.getcwd(), "assets", "icon.png"))
            guide_target = out_dir / "Guida-uso.pdf"
            write_user_guide_pdf(guide_target, os.path.join(os.getcwd(), "assets", "icon.png"))
            messagebox.showinfo("Completato", f"Generati {len(appointments)} PDF in:\n{out_dir}")
        except Exception as exc:  # pragma: no cover - gui error path
            messagebox.showerror("Errore", str(exc))


def launch_gui() -> None:
    app = App()
    app.mainloop()
