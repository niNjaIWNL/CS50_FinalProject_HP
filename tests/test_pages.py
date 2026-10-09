from cs50_final_active import create_app


def test_home_page():
    app = create_app()
    app.config.update(TESTING=True)
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"Flask is running inside a uv-managed project." in response.data