from pathlib import Path


def test_windows_packaging_includes_logo_tests_and_guide_smoke_check() -> None:
    spec = Path("RomeCampaignPDF.spec").read_text(encoding="utf-8")
    workflow = Path(".github/workflows/build-windows.yml").read_text(
        encoding="utf-8"
    )

    assert '("assets/icon.png", "assets")' in spec
    assert '("assets/Rome_campaign_2026_logo.png", "assets")' in spec
    assert "upx=False" in spec
    assert "python -m pytest" in workflow
    assert "--guide-only (Join-Path $release" in workflow
    assert "Get-FileHash" in workflow
    assert "SHA256SUMS.txt" in workflow
    assert "path: release" in workflow
    assert "name: RomeCampaignPDF-Windows" in workflow
    assert "actions/upload-artifact@v4" in workflow
