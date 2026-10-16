from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from src.service import generate_documents


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Generatore appuntamenti Roma 2026")
        self.geometry("650x300")
        self.minsize(590, 280)

        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.status_var = tk.StringVar(
            value="Seleziona il file Excel e la cartella di destinazione."
        )

        container = ttk.Frame(self, padding=18)
        container.pack(fill="both", expand=True)
        ttk.Label(
            container,
            text="Generatore PDF appuntamenti",
            font=("Segoe UI", 17, "bold"),
        ).pack(anchor="w")
        ttk.Label(
            container,
            text="Verrà creato un PDF per ogni riga del file Excel.",
        ).pack(anchor="w", pady=(2, 14))

        self._path_row(
            container,
            "File Excel (.xlsx)",
            self.input_var,
            self.choose_input,
        )
        self._path_row(
            container,
            "Cartella di destinazione",
            self.output_var,
            self.choose_output,
        )

        self.generate_button = ttk.Button(
            container,
            text="Genera PDF",
            command=self.generate,
        )
        self.generate_button.pack(pady=(16, 8), ipadx=24, ipady=6)
        ttk.Label(
            container,
            textvariable=self.status_var,
            wraplength=590,
            justify="center",
        ).pack()

    def _path_row(
        self,
        parent: ttk.Frame,
        label: str,
        variable: tk.StringVar,
        command: object,
    ) -> None:
        ttk.Label(parent, text=label).pack(fill="x", pady=(5, 2))
        row = ttk.Frame(parent)
        row.pack(fill="x")
        ttk.Entry(row, textvariable=variable).pack(
            side="left", fill="x", expand=True
        )
        ttk.Button(row, text="Sfoglia…", command=command).pack(
            side="left", padx=(8, 0)
        )

    def choose_input(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Seleziona il file degli appuntamenti",
            filetypes=[("File Excel", "*.xlsx")],
        )
        if file_path:
            self.input_var.set(file_path)

    def choose_output(self) -> None:
        folder = filedialog.askdirectory(
            title="Seleziona la cartella di destinazione"
        )
        if folder:
            self.output_var.set(folder)

    def generate(self) -> None:
        source = self.input_var.get().strip()
        output = self.output_var.get().strip()
        if not source:
            messagebox.showerror("File mancante", "Seleziona un file Excel.")
            return
        if not output:
            messagebox.showerror(
                "Cartella mancante", "Seleziona una cartella di destinazione."
            )
            return

        self.generate_button.configure(state="disabled")
        self.status_var.set("Generazione in corso…")
        self.update_idletasks()
        try:
            result = generate_documents(source, output)
        except (OSError, ValueError) as exc:
            self.status_var.set("Generazione non completata.")
            messagebox.showerror("Impossibile generare i PDF", str(exc))
        else:
            self.status_var.set(
                f"Completato: {len(result.appointment_files)} PDF generati."
            )
            messagebox.showinfo(
                "Generazione completata",
                f"Creati {len(result.appointment_files)} PDF di appuntamento "
                f"e la guida in:\n{Path(output)}",
            )
        finally:
            self.generate_button.configure(state="normal")


def launch_gui() -> None:
    app = App()
    app.mainloop()
