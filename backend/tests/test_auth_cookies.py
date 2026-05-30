from api.routes import create_app


def test_local_auth_cookie_uses_app_specific_non_secure_lax_cookie(tmp_path, monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "development")
    monkeypatch.delenv("FF_AUTH_COOKIE_SECURE", raising=False)
    monkeypatch.delenv("FF_AUTH_COOKIE_SAMESITE", raising=False)
    monkeypatch.delenv("FF_AUTH_COOKIE_NAME", raising=False)
    app = create_app({"RUNTIME_DIR": tmp_path})
    client = app.test_client()

    response = client.post(
        "/api/auth/login",
        json={"username": "designer1", "password": "designer123"},
    )

    assert response.status_code == 200
    cookies = response.headers.getlist("Set-Cookie")
    auth_cookie = next(cookie for cookie in cookies if cookie.startswith("textile_os_auth="))
    assert "SameSite=Lax" in auth_cookie
    assert "Secure" not in auth_cookie
    assert any(cookie.startswith("ff_auth=;") for cookie in cookies)


def test_me_ignores_legacy_ff_auth_cookie(tmp_path, monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "development")
    app = create_app({"RUNTIME_DIR": tmp_path})
    client = app.test_client()

    client.set_cookie("ff_auth", "legacy-token-from-another-localhost-app")
    response = client.get("/api/auth/me")

    assert response.status_code == 401


def test_me_uses_configured_auth_cookie(tmp_path, monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "development")
    app = create_app({"RUNTIME_DIR": tmp_path})
    client = app.test_client()

    login = client.post(
        "/api/auth/login",
        json={"username": "ftc1", "password": "ftcmember123"},
    )
    assert login.status_code == 200

    response = client.get("/api/auth/me")

    assert response.status_code == 200
    assert response.get_json()["user"]["role"] == "ftc_member"
