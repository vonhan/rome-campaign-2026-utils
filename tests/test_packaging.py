from pathlib import Path


def test_windows_packaging_includes_logo_tests_and_guide_smoke_check() -> None:
    spec = Path("RomeCampaignPDF.spec").read_text(encoding="utf-8")
    workflow = Path(".github/workflows/build-windows.yml").read_text(
        encoding="utf-8"
    )

    assert '("assets/icon.png", "assets")' in spec
    assert "python -m pytest" in workflow
    assert "--guide-only (Join-Path $release" in workflow
    assert "path: RomeCampaignPDF-Windows.zip" in workflow
    assert "RomeCampaignPDF-Windows.zip" in workflow
    assert "ZipFile]::CreateFromDirectory($release, $zip)" in workflow
    assert "actions/upload-artifact@v4" in workflow
