from pathlib import Path

def test_deploy_files_exist():
    required=["Dockerfile","docker-compose.yml",".env.example","README_DEPLOY.md","auth.py","theme/gv_hermes_dark_v0.1.json"]
    for name in required:
        assert Path(name).exists(), name

def test_app_uses_dark_theme_and_auth():
    s=Path("app.py").read_text(encoding="utf-8")
    assert "require_login()" in s
    assert "from theme.dark_styles import get_css" in s
