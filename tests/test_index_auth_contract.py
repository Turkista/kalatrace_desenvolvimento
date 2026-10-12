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


def test_api_base_defaults_to_deployed_render_service_and_allows_override():
    assert "window.KALATRACE_API_BASE || 'https://kalatrace-desenvolvimento.onrender.com'" in HTML
    assert "window.KALATRACE_API_BASE || 'http://127.0.0.1:8000'" not in HTML
    assert "fetch(KT_API_BASE+path" in HTML


def test_splash_transition_is_independent_of_auth_bootstrap():
    fallback_start = HTML.index('<script id="kt-splash-fallback">')
    workspace_start = HTML.index("<!-- 3. WORKSPACE -->")
    app_bootstrap_start = HTML.index("const forms=[")
    auth_binding_start = HTML.index("document.getElementById('kt-auth-form').addEventListener")

    fallback = HTML[fallback_start:workspace_start]
    assert fallback_start < workspace_start < app_bootstrap_start < auth_binding_start
    assert "window.setTimeout(function ()" in fallback
    assert "splash.hidden = true" in fallback
    assert "welcome.hidden = false" in fallback
    assert "setTimeout(function(){ obFade('ob-splash','ob-welcome'); }, 2200)" not in HTML


def test_platform_entry_button_opens_auth_without_waiting_for_api():
    assert 'id="ob-enter-platform-btn" type="button" onclick="window.ktShowLoginFromWelcome(); return false;"' in HTML
    fallback_start = HTML.index('<script id="kt-splash-fallback">')
    fallback_end = HTML.index("</script>", fallback_start)
    fallback = HTML[fallback_start:fallback_end]
    assert "window.ktShowLoginFromWelcome = function ()" in fallback
    assert "modal.style.setProperty('display', 'flex', 'important')" in fallback
    assert "modal.style.setProperty('z-index', '2147483647', 'important')" in fallback
    assert "window.KT_AUTH_CONTINUE = function ()" in fallback
    assert "showLogin('Entre com sua conta KALATRACE para continuar.')" in fallback
    assert '<script id="kt-platform-entry-handler">' not in HTML


def test_workspace_registers_login_continuation_before_auth_check():
    start = HTML.index("async function obGoWorkspace()")
    end = HTML.index("// 3 -> 4", start)
    flow = HTML[start:end]
    assert flow.index("window.KT_AUTH_CONTINUE=obGoWorkspace") < flow.index("ktEnsureAuth")



def test_workspace_registers_login_continuation_before_auth_check():
    start = HTML.index("async function obGoWorkspace()")
    end = HTML.index("// 3 -> 4", start)
    flow = HTML[start:end]
    assert flow.index("window.KT_AUTH_CONTINUE=obGoWorkspace") < flow.index("ktEnsureAuth")
    assert "msg.textContent='Verificando sua sessão KALATRACE…'" in flow
