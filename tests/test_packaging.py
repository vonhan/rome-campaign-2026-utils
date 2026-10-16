from pathlib import Path

import pytest

SPEC = Path("RomeCampaignPDF.spec")
WORKFLOW = Path(".github/workflows/build-windows.yml")

# Nomi dei file che l'utente non tecnico deve trovare nel pacchetto scaricato.
FILE_ATTESI = ("Guida-uso.pdf", "README.md", "RomeCampaignPDF.exe", "SHA256SUMS.txt")


@pytest.fixture(scope="module")
def spec() -> str:
    return SPEC.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def workflow() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def test_spec_includes_assets_and_disables_upx(spec: str) -> None:
    assert '("assets/icon.png", "assets")' in spec
    assert '("assets/Rome_campaign_2026_logo.png", "assets")' in spec
    # UPX aumenta i falsi positivi antivirus sull'eseguibile distribuito.
    assert "upx=False" in spec


def test_workflow_runs_tests_and_publishes_artifact(workflow: str) -> None:
    assert "python -m pytest" in workflow
    assert "actions/upload-artifact@v4" in workflow
    assert "name: RomeCampaignPDF-Windows" in workflow
    assert "path: release" in workflow
    assert "if-no-files-found: error" in workflow


def test_workflow_waits_for_the_windowed_executable(spec: str, workflow: str) -> None:
    """L'EXE è compilato con console=False.

    Invocarlo con l'operatore `&` non ne attende la fine e lascia
    $LASTEXITCODE a $null: `$null -ne 0` è vero, quindi `exit $LASTEXITCODE`
    terminava lo step con successo saltando silenziosamente la generazione del
    checksum. Serve un'attesa esplicita con un codice di uscita affidabile.
    """
    assert "console=False" in spec
    assert "--guide-only" in workflow
    assert "Start-Process" in workflow
    assert "-Wait -PassThru" in workflow
    assert "$processo.ExitCode" in workflow
    assert "exit $LASTEXITCODE" not in workflow


def test_workflow_generates_the_checksum(workflow: str) -> None:
    assert "Get-FileHash" in workflow
    assert "-Algorithm SHA256" in workflow
    assert "SHA256SUMS.txt" in workflow


def test_workflow_fails_when_the_package_is_incomplete(workflow: str) -> None:
    """Rete di sicurezza: la build deve rompersi se un file non viene prodotto."""
    for nome in FILE_ATTESI:
        assert nome in workflow, f"{nome} non è verificato dal workflow"
    assert "File mancanti nel pacchetto" in workflow
    assert "File vuoti nel pacchetto" in workflow


def test_workflow_stops_on_first_error(workflow: str) -> None:
    # Senza questo, un errore non terminante lascerebbe proseguire lo step.
    assert workflow.count('$ErrorActionPreference = "Stop"') >= 3
