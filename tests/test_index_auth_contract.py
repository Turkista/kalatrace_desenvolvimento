from pathlib import Path

INDEX = Path(__file__).resolve().parents[1] / "index.html"
HTML = INDEX.read_text(encoding="utf-8")


def test_login_form_has_accessible_required_credentials():
    assert '<div id="kt-auth-modal" role="dialog" aria-modal="true"' in HTML
    assert '<form id="kt-auth-form">' in HTML
    assert 'id="kt-auth-email" name="email" type="email"' in HTML
    assert 'id="kt-auth-password" name="password" type="password"' in HTML
    assert HTML.count("required>") >= 2
    assert 'id="kt-auth-msg" role="status" aria-live="polite"' in HTML


def test_login_uses_existing_auth_api_and_tab_scoped_token():
    assert "ktApi('/auth/login'" in HTML
    assert "ktApi('/auth/me')" in HTML
    assert "sessionStorage.setItem('kalatrace_access_token',token)" in HTML
    assert "sessionStorage.getItem('kalatrace_access_token')" in HTML
    assert "localStorage.setItem('kalatrace_access_token'" not in HTML
    assert "service_role" not in HTML.lower()


def test_logout_clears_local_token_even_if_api_logout_fails():
    start = HTML.index("async function ktLogout()")
    end = HTML.index("function ktFormData(", start)
    logout = HTML[start:end]
    assert "await ktApi('/auth/logout'" in logout
    assert "finally{" in logout
    assert "sessionStorage.removeItem('kalatrace_access_token')" in logout
    assert "document.getElementById('app-root').style.display='none'" in logout

def test_auth_handlers_are_bound_after_modal_markup_exists():
    modal_position = HTML.index('<div id="kt-auth-modal"')
    handler_position = HTML.index("document.getElementById('kt-auth-form').addEventListener")
    assert handler_position > modal_position

def test_workspace_requires_authentication_before_project_selection():
    start = HTML.index("async function obGoWorkspace()")
    end = HTML.index("// 3 -> 4", start)
    workspace_flow = HTML[start:end]
    assert "if(!(await ktEnsureAuth()))" in workspace_flow
    assert "window.KT_AUTH_CONTINUE=obGoWorkspace" in workspace_flow
    assert workspace_flow.index("ktEnsureAuth") < workspace_flow.index("obFade")
    assert "const resume=window.KT_AUTH_CONTINUE" in HTML
