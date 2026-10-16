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
