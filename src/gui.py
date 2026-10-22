from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

from src.service import generate_documents


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Generatore appuntamenti Roma 2026")
        self.geometry("760x610")
        self.minsize(680, 520)

        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.mode_var = tk.StringVar(value="delegato")
        self.volunteer_var = tk.StringVar()
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
            text="Scegli il tipo di output da generare e l'Excel da elaborare.",
        ).pack(anchor="w", pady=(2, 12))

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

        mode_frame = ttk.LabelFrame(container, text="Tipo di generazione")
        mode_frame.pack(fill="x", pady=(12, 10))
        for label, value in (
            ("Appuntamenti per capogruppo Delegato", "delegato"),
            ("Appuntamenti per capogruppo Volontario", "volontario"),
        ):
            ttk.Radiobutton(
                mode_frame,
                text=label,
                variable=self.mode_var,
                value=value,
            ).pack(anchor="w", padx=12, pady=3)

        ttk.Label(
            mode_frame,
            text="Volontario singolo (NOME_COMPLETO NUMERO_TELEFONO, opzionale)",
        ).pack(anchor="w", padx=12, pady=(8, 2))
        ttk.Entry(
            mode_frame,
            textvariable=self.volunteer_var,
        ).pack(fill="x", padx=12, pady=(0, 8))

        self.generate_button = ttk.Button(
            container,
            text="Genera PDF",
            command=self.generate,
        )
        self.generate_button.pack(pady=(8, 8), ipadx=24, ipady=6)
        ttk.Label(
            container,
            textvariable=self.status_var,
            wraplength=680,
            justify="center",
        ).pack()
        log_frame = ttk.LabelFrame(container, text="Log elaborazione")
        log_frame.pack(fill="both", expand=True, pady=(12, 0))
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=8,
            wrap="word",
            font=("Consolas", 9),
            state="disabled",
        )
        self.log_text.pack(fill="both", expand=True, padx=6, pady=6)
        self._set_log("Nessun errore. Il log verrà aggiornato durante l'elaborazione.")

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

    def _set_log(self, text: str) -> None:
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.insert("1.0", text)
        self.log_text.configure(state="disabled")

    def generate(self) -> None:
        source = self.input_var.get().strip()
        output = self.output_var.get().strip()
        volunteer_var = getattr(self, "volunteer_var", None)
        volunteer = volunteer_var.get().strip() if volunteer_var else ""
        if not source:
            self._set_log("Errore: selezionare un file Excel.")
            messagebox.showerror("File mancante", "Seleziona un file Excel.")
            return
        if not output:
            self._set_log("Errore: selezionare una cartella di destinazione.")
            messagebox.showerror(
                "Cartella mancante", "Seleziona una cartella di destinazione."
            )
            return

        self.generate_button.configure(state="disabled")
        self.status_var.set("Generazione in corso…")
        self._set_log("Elaborazione del file Excel in corso…")
        self.update_idletasks()
        try:
            mode = self.mode_var.get()
            if volunteer:
                result = generate_documents(
                    source,
                    output,
                    mode=mode,
                    volunteer_filter=volunteer,
                )
            else:
                result = generate_documents(source, output, mode=mode)
        except (OSError, ValueError) as exc:
            self.status_var.set("Generazione non completata.")
            self._set_log(str(exc))
            messagebox.showerror(
                "Impossibile generare i PDF",
                "La generazione non è stata completata. "
                "Consulta il riquadro Log elaborazione per i dettagli.",
            )
        else:
            subject = (
                "capogruppo delegato"
                if self.mode_var.get() == "delegato"
                else (
                    "volontario selezionato"
                    if volunteer
                    else "capogruppo volontario"
                )
            )
            self.status_var.set(
                f"Completato: {len(result.appointment_files)} PDF per "
                f"{subject} generati."
            )
            self._set_log(
                f"Operazione completata senza errori.\n"
                f"PDF generati: {len(result.appointment_files)}\n"
                f"Cartella: {Path(output)}"
            )
            messagebox.showinfo(
                "Generazione completata",
                f"Creati {len(result.appointment_files)} PDF per {subject} "
                f"e la guida in:\n{Path(output)}",
            )
        finally:
            self.generate_button.configure(state="normal")


def launch_gui() -> None:
    app = App()
    app.mainloop()
