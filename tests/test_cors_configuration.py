from integrations.cors import get_cors_origins


PAGES_ORIGIN = "https://turkista.github.io"


def test_default_cors_origins_include_local_development_and_published_frontend():
    origins = get_cors_origins({})

    assert "http://127.0.0.1:5500" in origins
    assert "http://localhost:5500" in origins
    assert PAGES_ORIGIN in origins


def test_custom_cors_origins_do_not_drop_the_published_frontend():
    origins = get_cors_origins({
        "KALATRACE_CORS_ORIGINS": "https://dev.example.com, https://staging.example.com"
    })

    assert origins == [
        "https://dev.example.com",
        "https://staging.example.com",
        PAGES_ORIGIN,
    ]


def test_cors_origins_are_trimmed_and_deduplicated():
    origins = get_cors_origins({
        "KALATRACE_CORS_ORIGINS": " https://dev.example.com,https://dev.example.com, "
    })

    assert origins == ["https://dev.example.com", PAGES_ORIGIN]
