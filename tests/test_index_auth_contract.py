from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
HTML = INDEX.read_text(encoding="utf-8")
LOGIN = ROOT / "login.html"
LOGIN_HTML = LOGIN.read_text(encoding="utf-8")


def test_dedicated_login_page_has_accessible_required_credentials():
    assert '<form id="login-form">' in LOGIN_HTML
    assert 'id="login-email" name="email" type="email"' in LOGIN_HTML
    assert 'id="login-password" name="password" type="password"' in LOGIN_HTML
    assert 'id="login-status" class="status" role="status" aria-live="polite"' in LOGIN_HTML
    assert LOGIN_HTML.count("required>") >= 2
    assert 'id="submit-login" type="submit">Entrar no projeto</button>' in LOGIN_HTML


def test_dedicated_login_uses_auth_api_and_resumes_selected_project():
    assert "api('/auth/login'" in LOGIN_HTML
    assert "await api('/auth/me')" in LOGIN_HTML
    assert "sessionStorage.setItem('kalatrace_access_token',token)" in LOGIN_HTML
    assert "nextUrl.searchParams.set('enterProject',project)" in LOGIN_HTML
    assert "'https://kalatrace-desenvolvimento.onrender.com'" in LOGIN_HTML
    assert "service_role" not in LOGIN_HTML.lower()


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
    modal_position = HTML.index('<dialog id="kt-auth-modal"')
    handler_position = HTML.index("const authForm = document.getElementById('kt-auth-form')")
    assert handler_position > modal_position
    assert "authForm.addEventListener('submit', window.ktLogin)" in HTML

def test_project_selection_precedes_authentication_and_entering_project_is_guarded():
    workspace_start = HTML.index('id="ob-workspace"')
    project_card = HTML.index("onclick=\"obOpenProject('MEDIKALAT')\"", workspace_start)
    assert workspace_start < project_card
    start = HTML.index("async function obEnterProject()")
    end = HTML.index("</script>", start)
    entry_flow = HTML[start:end]
    assert "if(!authenticated)" in entry_flow
    assert "return obRedirectToLogin(selected);" in entry_flow
    assert "await window.ktApi('/auth/me')" in entry_flow
    assert entry_flow.index("if(!authenticated)") < entry_flow.index("await ktLoadProjects()")
    assert "loginUrl.searchParams.set('continue',project)" in HTML
    assert "const resume=window.KT_AUTH_CONTINUE" in HTML


def test_api_base_defaults_to_deployed_render_service_and_allows_override():
    assert "window.KALATRACE_API_BASE || 'https://kalatrace-desenvolvimento.onrender.com'" in HTML
    assert "window.KALATRACE_API_BASE || 'http://127.0.0.1:8000'" not in HTML
    assert "fetch(KT_API_BASE+path" in HTML


def test_splash_transition_is_independent_of_auth_bootstrap():
    fallback_start = HTML.index('<script id="kt-splash-fallback">')
    workspace_start = HTML.index("<!-- 3. WORKSPACE -->")
    app_bootstrap_start = HTML.index("const forms=[")
    auth_binding_start = HTML.index("const authForm = document.getElementById('kt-auth-form')")

    fallback = HTML[fallback_start:workspace_start]
    assert fallback_start < workspace_start < app_bootstrap_start < auth_binding_start
    assert "window.setTimeout(function ()" in fallback
    assert "splash.hidden = true" in fallback
    assert "welcome.hidden = false" in fallback
    assert "if (window.KT_SKIP_SPLASH) return;" in fallback
    assert "setTimeout(function(){ obFade('ob-splash','ob-welcome'); }, 2200)" not in HTML

def test_platform_entry_button_opens_project_selector_without_auth_or_inline_global_handler():
    assert '<button class="ob-btn-primary" id="ob-enter-platform-btn" type="button">Entrar na plataforma</button>' in HTML
    assert 'onclick="window.ktShowLoginFromWelcome()' not in HTML
    fallback_start = HTML.index('<script id="kt-splash-fallback">')
    fallback_end = HTML.index("</script>", fallback_start)
    fallback = HTML[fallback_start:fallback_end]
    assert "window.ktShowProjectsFromWelcome = function ()" in fallback
    assert "entryButton.addEventListener('click'" in fallback
    assert "welcome.classList.add('hide')" in fallback
    assert "workspace.hidden = false" in fallback
    assert "window.ktOpenAuth" not in fallback
    assert '<script id="kt-platform-entry-handler">' not in HTML


def test_workspace_transition_displays_project_picker_without_login_gate():
    start = HTML.index("async function obGoWorkspace()")
    end = HTML.index("// 3 -> 4", start)
    flow = HTML[start:end]
    assert "obFade('ob-welcome','ob-workspace')" in flow
    assert "ktEnsureAuth" not in flow


def test_cross_script_handlers_are_exported_explicitly_before_boot():
    main_script_start = HTML.index("/* Expose handlers explicitly for later inline scripts and HTML onclicks.")
    forms_init = HTML.index("const forms=[")
    api_client_init = HTML.index("const KT_API_BASE =")
    assert main_script_start < api_client_init < forms_init
    for name in ("ktLogin", "ktSetAuthIdentity", "ktApi", "ktToken", "ktOpenAuth", "ktCloseAuth"):
        assert f"window.{name} = {name};" in HTML
    assert "authForm.addEventListener('submit', window.ktLogin)" in HTML
    assert "window.ktSetAuthIdentity(null)" in HTML
    assert "window.ktApi('/auth/me')" in HTML


def test_later_ui_handlers_are_explicitly_exported_for_html_callbacks():
    for name in ("obGoWorkspace", "obEnterProject", "ktRoboticsRefresh", "ktAgentRefresh", "ktInfrastructureRefresh", "ktWatchdogRefresh"):
        assert f"window.{name} = {name};" in HTML

def test_auth_globals_have_an_independent_early_fallback():
    fallback_start = HTML.index('<script id="kt-auth-bootstrap-fallback">')
    splash_start = HTML.index('<script id="kt-splash-fallback">')
    main_start = HTML.index("/* Expose handlers explicitly for later inline scripts and HTML onclicks.")
    assert fallback_start < splash_start < main_start
    fallback = HTML[fallback_start:HTML.index("</script>", fallback_start)]
    assert "window.ktLogin = async function (event)" in fallback
    assert "window.ktSetAuthIdentity = function (user)" in fallback
    assert "window.ktApi = async function (path, options)" in fallback
    assert "window.ktEnsureAuth = async function ()" in fallback
    assert "https://kalatrace-desenvolvimento.onrender.com" in fallback
    assert "authForm.addEventListener('submit', window.ktLogin)" in HTML


def test_favicon_uses_an_asset_inside_the_github_pages_project_path():
    assert 'rel="icon" href="/kalatrace_desenvolvimento/assets/asset_eb3da0044c.png" type="image/png"' in HTML

def test_tabler_icons_stylesheet_uses_official_jsdelivr_package_path():
    assert 'https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.49.0/dist/tabler-icons.min.css' in HTML
    assert 'cdnjs.cloudflare.com/ajax/libs/tabler-icons/2.44.0/iconfont/tabler-icons.min.css' not in HTML

def test_project_selector_contains_all_expected_project_choices():
    selector_start = HTML.index('id="ob-workspace"')
    selector_end = HTML.index("<!-- 4. PROJECT LOADING -->", selector_start)
    selector = HTML[selector_start:selector_end]
    for project in ("MEDIKALAT", "SkinMap", "YANSIX", "Turkista", "Robótica", "Agente Local", "Novo projeto"):
        assert project in selector
    for placeholder in ("Em construção", "Ativo · bakuchiol + resveratrol"):
        assert placeholder in selector

def test_enter_project_button_has_explicit_listener_and_visible_error_feedback():
    assert '<button class="ob-btn-primary" id="ob-enter-btn" type="button" disabled>Entrar no projeto</button>' in HTML
    assert 'onclick="obEnterProject()"' not in HTML
    assert "button.addEventListener('click', async function(event)" in HTML
    assert "window.obEnterProject()" in HTML
    assert 'id="ob-project-entry-status" role="status" aria-live="polite"' in HTML
    assert "button.textContent = 'Tentar entrar novamente'" in HTML


def test_enter_project_awaits_auth_then_reveals_kalatrace_app():
    start = HTML.index("async function obEnterProject()")
    end = HTML.index("</script>", start)
    flow = HTML[start:end]
    assert "if(!authenticated)" in flow
    assert "return obRedirectToLogin(selected);" in flow
    assert "ktSelectProject(selected)" in flow
    assert "await new Promise(resolve=>window.setTimeout(resolve,480))" in flow
    assert "app.style.display=''" in flow
    assert "return true;" in flow
    assert "window.KT_SKIP_SPLASH=true;" in HTML
    assert "const result=await window.obEnterProject();" in HTML

def test_primary_auth_modal_is_forced_visible_above_onboarding():
    start = HTML.index("function ktOpenAuth(message='')")
    end = HTML.index("async function ktLogin", start)
    opener = HTML[start:end]
    assert "modal.hidden=false;" in opener
    assert "modal.showModal()" in opener
    assert "modal.open" in opener
    assert "modal.close()" in opener
    assert "modal.hidden=true;" in opener
    assert 'dialog id="kt-auth-modal"' in HTML
    assert '#kt-auth-modal[open]{display:flex!important}' in HTML
    assert "function obRedirectToLogin(projectSlug)" in HTML
    assert "window.location.assign(loginUrl.href)" in HTML

def test_enter_project_uses_standalone_login_instead_of_modal_prompt():
    start = HTML.index("function obRedirectToLogin(projectSlug)")
    end = HTML.index("// 4 -> app", start)
    redirect = HTML[start:end]
    assert "new URL('login.html',window.location.href)" in redirect
    assert "window.location.assign(loginUrl.href)" in redirect
    assert "return 'login-redirecting'" in redirect
    assert "Abrindo tela de login…" in HTML
    assert "Entre com sua conta KALATRACE na janela de autenticação para continuar." not in HTML


def test_login_page_uses_same_origin_session_and_continue_flag():
    assert "window.location.replace(nextUrl.href)" in LOGIN_HTML
    assert "new URL('index.html',window.location.href)" in LOGIN_HTML
    assert "params.get('continue')" in LOGIN_HTML
    assert "enterProject" in LOGIN_HTML

def test_return_from_login_skips_parallel_bootstrap_auth_validation():
    bootstrap_start = HTML.index("const ktResumeRequested=new URLSearchParams(window.location.search).has('enterProject');")
    bootstrap_end = HTML.index("const graphScreen=document.getElementById('screen-grafo');", bootstrap_start)
    bootstrap = HTML[bootstrap_start:bootstrap_end]

    assert "if(!ktResumeRequested)" in bootstrap
    assert "window.ktSetAuthIdentity(null)" in bootstrap
    assert bootstrap.index("if(!ktResumeRequested)") < bootstrap.index("window.ktSetAuthIdentity(null)")
    assert "The resume handler below owns session validation" in bootstrap


def test_project_resume_does_not_clear_session_on_temporary_api_failure():
    start = HTML.index("async function obEnterProject(){")
    end = HTML.index("</script>", start)
    flow = HTML[start:end]

    assert "if(error&&(error.status===401||error.status===403))" in flow
    assert "else{\n      throw error;\n    }" in flow
    assert "if(!authenticated)" in flow
