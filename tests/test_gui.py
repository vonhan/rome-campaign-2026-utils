from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from src import gui
from src.gui import App
from src.service import GenerationResult


class _Variable:
    def __init__(self, value: str = "") -> None:
        self.value = value

    def get(self) -> str:
        return self.value

    def set(self, value: str) -> None:
        self.value = value


class _Button:
    def __init__(self) -> None:
        self.states: list[str] = []

    def configure(self, *, state: str) -> None:
        self.states.append(state)


@pytest.mark.parametrize(
    ("mode", "expected_subject"),
    [
        ("delegato", "capogruppo delegato"),
        ("volontario", "capogruppo volontario"),
    ],
)
def test_gui_forwards_selected_mode_and_reports_subject(
    monkeypatch, tmp_path: Path, mode: str, expected_subject: str
) -> None:
    captured: dict[str, str] = {}
    messages: list[str] = []
    logs: list[str] = []

    def generate_documents(source: str, output: str, *, mode: str):
        captured["source"] = source
        captured["output"] = output
        captured["mode"] = mode
        return GenerationResult(
            appointment_files=(tmp_path / "result.pdf",),
            guide_file=tmp_path / "Guida-uso.pdf",
        )

    monkeypatch.setattr(gui, "generate_documents", generate_documents)
    monkeypatch.setattr(
        gui.messagebox,
        "showinfo",
        lambda _title, text: messages.append(text),
    )

    app = SimpleNamespace(
        input_var=_Variable("input.xlsx"),
        output_var=_Variable(str(tmp_path)),
        mode_var=_Variable(mode),
        status_var=_Variable(),
        generate_button=_Button(),
        _set_log=logs.append,
        update_idletasks=lambda: None,
    )

    App.generate(app)

    assert captured == {
        "source": "input.xlsx",
        "output": str(tmp_path),
        "mode": mode,
    }
    assert expected_subject in app.status_var.get()
    assert expected_subject in messages[0]
    assert app.generate_button.states == ["disabled", "normal"]
    assert logs[-1].startswith("Operazione completata senza errori.")


def test_gui_writes_generation_error_to_log(monkeypatch, tmp_path: Path) -> None:
    logs: list[str] = []
    dialogs: list[str] = []

    def fail_generation(*_args, **_kwargs):
        raise ValueError(
            "Sono stati rilevati 2 errori nel file Excel.\n"
            "- Foglio 'Appuntamenti' - cella G3: formato non valido.\n"
            "- Foglio 'Appuntamenti' - cella I4: UNIONI non valida."
        )

    monkeypatch.setattr(gui, "generate_documents", fail_generation)
    monkeypatch.setattr(
        gui.messagebox,
        "showerror",
        lambda _title, text: dialogs.append(text),
    )
    app = SimpleNamespace(
        input_var=_Variable("input.xlsx"),
        output_var=_Variable(str(tmp_path)),
        mode_var=_Variable("volontario"),
        status_var=_Variable(),
        generate_button=_Button(),
        _set_log=logs.append,
        update_idletasks=lambda: None,
    )

    App.generate(app)

    assert "cella G3" in logs[-1]
    assert "cella I4" in logs[-1]
    assert "Log elaborazione" in dialogs[0]
    assert app.generate_button.states == ["disabled", "normal"]


def test_gui_forwards_selected_volunteer(monkeypatch, tmp_path: Path) -> None:
    captured: dict[str, str | None] = {}

    def generate_documents(
        source: str,
        output: str,
        *,
        mode: str,
        volunteer_filter: str | None = None,
    ):
        captured.update(
            source=source,
            output=output,
            mode=mode,
            volunteer_filter=volunteer_filter,
        )
        return GenerationResult(
            appointment_files=(tmp_path / "result.pdf",),
            guide_file=tmp_path / "Guida-uso.pdf",
        )

    monkeypatch.setattr(gui, "generate_documents", generate_documents)
    monkeypatch.setattr(gui.messagebox, "showinfo", lambda *_args: None)
    app = SimpleNamespace(
        input_var=_Variable("input.xlsx"),
        output_var=_Variable(str(tmp_path)),
        mode_var=_Variable("volontario"),
        volunteer_var=_Variable("ROSSI MARIO 111"),
        status_var=_Variable(),
        generate_button=_Button(),
        _set_log=lambda _text: None,
        update_idletasks=lambda: None,
    )

    App.generate(app)

    assert captured["mode"] == "volontario"
    assert captured["volunteer_filter"] == "ROSSI MARIO 111"
