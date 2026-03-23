const fallbackPayload = {
  app: {
    name: "Any-API-Check",
    workspace: "i:/xianyu_op/any-api-check",
    mode: "browser fallback",
    generated_at: new Date().toLocaleString("zh-CN"),
  },
  selected_site_id: "demo-1",
  sites: [
    {
      id: "demo-1",
      name: "Main Relay",
      url: "https://api.demo-relay.com",
      api_key: "sk-demo-main",
      api_key_masked: "sk-d***main",
      type: "paid",
      tags: ["anthropic", "openai"],
      tags_text: "anthropic, openai",
      balance: 92.6,
      balance_unit: "USD",
      last_query_time: "2026-03-10 20:12:31",
      notes: "主力中转站",
      checkin_url: "https://api.demo-relay.com/console/personal",
      checkin_api_path: "/api/user/checkin",
      session_cookie: "session=demo; cf_clearance=demo",
      session_cookie_masked: "session=***",
      checkin_headers_text: "{}",
      provider_template: "custom",
      waf_cookie_names: ["cf_clearance"],
      waf_cookie_names_text: "cf_clearance",
      checkin_cookie_updated_at: "2026-03-10 18:42:00",
      checkin_user_id: "1001",
      balance_auth_type: "bearer",
      log_auth_type: "url_key",
      proxy: "",
      jwt_token: "",
      endpoint_balance_subscription: "",
      endpoint_balance_usage: "",
      endpoint_logs: "",
      has_cookie: true,
      status: "healthy",
      recharge_records: [],
    },
    {
      id: "demo-2",
      name: "Backup Relay",
      url: "https://relay-backup.example",
      api_key: "sk-demo-backup",
      api_key_masked: "sk-d***kup",
      type: "free",
      tags: ["backup"],
      tags_text: "backup",
      balance: 8.2,
      balance_unit: "USD",
      last_query_time: "",
      notes: "",
      checkin_url: "",
      checkin_api_path: "/api/user/checkin",
      session_cookie: "",
      session_cookie_masked: "",
      checkin_headers_text: "{}",
      provider_template: "custom",
      waf_cookie_names: [],
      waf_cookie_names_text: "",
      checkin_cookie_updated_at: "",
      checkin_user_id: "",
      balance_auth_type: "bearer",
      log_auth_type: "url_key",
      proxy: "",
      jwt_token: "",
      endpoint_balance_subscription: "",
      endpoint_balance_usage: "",
      endpoint_logs: "",
      has_cookie: false,
      status: "warning",
      recharge_records: [],
    },
  ],
  metrics: {
    total_sites: 2,
    usd_total: 100.8,
    token_total: 0,
    low_balance_count: 1,
    cookie_enabled_count: 1,
    auto_query_label: "未启用",
    auto_checkin_label: "未启用",
    today_checkin_success: 1,
    today_checkin_failed: 0,
  },
  activity: [
    {
      time: "20:12:31",
      title: "Main Relay · 余额查询完成",
      description: "剩余 92.6 USD",
      kind: "success",
    },
    {
      time: "19:42:03",
      title: "Backup Relay · 低余额",
      description: "建议补充额度或切换站点",
      kind: "warning",
    },
  ],
  checkin_logs: [
    {
      id: "chk-demo-1",
      time: "2026-03-10 09:00:00",
      site_name: "Main Relay",
      site_id: "demo-1",
      success: true,
      quota_awarded: 0.5,
      message: "签到成功",
    },
  ],
  site_model_cards: [
    {
      site_id: "demo-1",
      site_name: "Main Relay",
      url: "https://api.demo-relay.com",
      discovered_count: 3,
      stream_ok_count: 2,
      stream_failed_count: 1,
      nonstream_ok_count: 3,
      nonstream_failed_count: 0,
      last_checked_at: "2026-03-10 20:16:00",
    },
    {
      site_id: "demo-2",
      site_name: "Backup Relay",
      url: "https://relay-backup.example",
      discovered_count: 1,
      stream_ok_count: 0,
      stream_failed_count: 0,
      nonstream_ok_count: 0,
      nonstream_failed_count: 0,
      last_checked_at: "",
    },
  ],
  site_models_by_site: {
    "demo-1": [
      {
        site_id: "demo-1",
        model_id: "claude-sonnet-4-5-20250929",
        display_name: "Claude Sonnet 4.5",
        source: "api_models",
        discovered_at: "2026-03-10 20:11:00",
        updated_at: "2026-03-10 20:16:00",
        last_stream_status: "success",
        last_stream_checked_at: "2026-03-10 20:16:00",
        last_stream_latency_ms: 1820,
        last_nonstream_status: "success",
        last_nonstream_checked_at: "2026-03-10 20:15:42",
        last_nonstream_latency_ms: 1260,
        last_message: "模型可用",
        last_request_format: "claude_messages",
        last_preset_id: "anthropic_cli_real",
      },
      {
        site_id: "demo-1",
        model_id: "claude-opus-4-5-20251101",
        display_name: "Claude Opus 4.5",
        source: "api_models",
        discovered_at: "2026-03-10 20:11:00",
        updated_at: "2026-03-10 20:16:10",
        last_stream_status: "failed",
        last_stream_checked_at: "2026-03-10 20:16:10",
        last_stream_latency_ms: 2200,
        last_nonstream_status: "success",
        last_nonstream_checked_at: "2026-03-10 20:15:52",
        last_nonstream_latency_ms: 1330,
        last_message: "流式探测失败",
        last_request_format: "claude_messages",
        last_preset_id: "anthropic_cli_real",
      },
      {
        site_id: "demo-1",
        model_id: "gpt-4.1",
        display_name: "GPT-4.1",
        source: "api_models",
        discovered_at: "2026-03-10 20:11:00",
        updated_at: "2026-03-10 20:16:08",
        last_stream_status: "success",
        last_stream_checked_at: "2026-03-10 20:16:08",
        last_stream_latency_ms: 940,
        last_nonstream_status: "success",
        last_nonstream_checked_at: "2026-03-10 20:15:36",
        last_nonstream_latency_ms: 710,
        last_message: "模型可用",
        last_request_format: "openai_chat",
        last_preset_id: "openai_relay",
      },
    ],
    "demo-2": [
      {
        site_id: "demo-2",
        model_id: "gpt-4.1-mini",
        display_name: "GPT-4.1 mini",
        source: "api_models",
        discovered_at: "2026-03-10 20:14:00",
        updated_at: "2026-03-10 20:14:00",
        last_stream_status: "",
        last_stream_checked_at: "",
        last_stream_latency_ms: null,
        last_nonstream_status: "",
        last_nonstream_checked_at: "",
        last_nonstream_latency_ms: null,
        last_message: "",
        last_request_format: "",
        last_preset_id: "",
      },
    ],
  },
  site_models: [],
  settings: {
    autostart: false,
    minimize_to_tray: true,
    low_balance_threshold: 10,
    logs_page_size: 50,
    action_log_max_rows: 500,
    auto_query_enabled: false,
    auto_query_interval: 30,
    auto_checkin_enabled: false,
    auto_checkin_time: "09:00",
    enable_api_log: false,
    theme: "light",
    use_background_image: false,
  },
  test_meta: {
    presets: [
      { id: "anthropic_cli_real", name: "Claude CLI Real", request_format: "claude_messages", request_format_name: "Claude Messages" },
      { id: "anthropic_relay", name: "Anthropic Relay", request_format: "claude_messages", request_format_name: "Claude Messages" },
      { id: "openai_relay", name: "OpenAI Relay", request_format: "openai_chat", request_format_name: "OpenAI Chat Completions" },
      { id: "openai_responses", name: "OpenAI Responses", request_format: "openai_responses", request_format_name: "OpenAI Responses" },
    ],
    default_preset: "anthropic_cli_real",
    models: [
      { id: "claude-sonnet-4-5-20250929", name: "Sonnet 4.5" },
      { id: "claude-opus-4-5-20251101", name: "Opus 4.5" },
      { id: "gpt-4.1", name: "GPT-4.1" },
    ],
    default_model: "claude-sonnet-4-5-20250929",
    default_with_thinking: true,
    default_with_system: true,
    request_formats: [
      { id: "claude_messages", name: "Claude Messages" },
      { id: "openai_chat", name: "OpenAI Chat Completions" },
      { id: "openai_responses", name: "OpenAI Responses" },
    ],
  },
  providers: [
    {
      id: "custom",
      name: "Custom",
      description: "自定义站点，不提供默认签到策略。",
      login_path: "/login",
      sign_in_path: "/api/user/checkin",
      user_info_path: "/api/user/self",
      waf_cookie_names: [],
      supports_cookie_auth: true,
      supports_browser_login: false,
      auto_checkin_via_user_info: false,
      is_builtin: true,
    },
    {
      id: "newapi",
      name: "NewAPI",
      description: "标准 NewAPI / OneAPI 兼容站点。",
      login_path: "/login",
      sign_in_path: "/api/user/checkin",
      user_info_path: "/api/user/self",
      waf_cookie_names: [],
      supports_cookie_auth: true,
      supports_browser_login: false,
      auto_checkin_via_user_info: false,
      is_builtin: true,
    },
    {
      id: "newapi-waf",
      name: "NewAPI + WAF",
      description: "带 WAF 的 NewAPI / OneAPI 兼容站点。",
      login_path: "/login",
      sign_in_path: "/api/user/checkin",
      user_info_path: "/api/user/self",
      waf_cookie_names: ["acw_tc"],
      supports_cookie_auth: true,
      supports_browser_login: true,
      auto_checkin_via_user_info: false,
      is_builtin: true,
    },
    {
      id: "anyrouter",
      name: "AnyRouter",
      description: "AnyRouter 兼容站点模板。",
      login_path: "/login",
      sign_in_path: "/api/user/sign_in",
      user_info_path: "/api/user/self",
      waf_cookie_names: ["acw_tc", "cdn_sec_tc", "acw_sc__v2"],
      supports_cookie_auth: true,
      supports_browser_login: true,
      auto_checkin_via_user_info: false,
      is_builtin: true,
    },
    {
      id: "agentrouter",
      name: "AgentRouter",
      description: "AgentRouter 兼容站点模板。",
      login_path: "/login",
      sign_in_path: "",
      user_info_path: "/api/user/self",
      waf_cookie_names: ["acw_tc"],
      supports_cookie_auth: true,
      supports_browser_login: true,
      auto_checkin_via_user_info: true,
      is_builtin: true,
    },
  ],
  detection_runs: [
    {
      id: "det-demo-1",
      site_id: "demo-1",
      run_type: "connectivity",
      status: "success",
      started_at: "2026-03-10 20:10:00",
      finished_at: "2026-03-10 20:10:01",
      request_format: "",
      model_id: "",
      detected_model: "",
      message: "连接成功",
    },
  ],
  action_logs: [
    {
      id: "act-demo-1",
      created_at: "2026-03-10 20:15:00",
      action_key: "save_site",
      site_id: "demo-1",
      success: false,
      title: "保存站点",
      message: "示例错误日志",
    },
  ],
  chart_data: {
    balance: {
      names: ["Main Relay", "Backup Relay"],
      values: [92.6, 8.2],
      types: ["paid", "free"],
    },
    type: {
      labels: ["付费站", "公益站"],
      counts: [1, 1],
      balances: [92.6, 8.2],
    },
    checkin: {
      days: Array.from({ length: 30 }, (_, i) => { const d = new Date(); d.setDate(d.getDate() - 29 + i); return String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0"); }),
      success: Array.from({ length: 30 }, () => Math.floor(Math.random() * 3)),
      failed: Array.from({ length: 30 }, () => Math.floor(Math.random() * 2)),
      quota: Array.from({ length: 30 }, () => +(Math.random() * 2).toFixed(2)),
    },
    recharge: {
      months: ["25-04","25-05","25-06","25-07","25-08","25-09","25-10","25-11","25-12","26-01","26-02","26-03"],
      values: [0, 20, 0, 50, 10, 0, 30, 0, 15, 0, 0, 0],
    },
  },
};

const pageMeta = {
  overview: { title: "总览", subtitle: "查看关键指标和最近活动" },
  sites: { title: "站点管理", subtitle: "维护中转站配置和签到参数" },
  checkin: { title: "签到中心", subtitle: "执行单站或批量签到" },
  models: { title: "模型记录", subtitle: "查看可用模型与调用汇总" },
  console: { title: "验证与对话", subtitle: "做连通性、真伪验证和对话测试" },
};

const selectedRequiredActions = new Set([
  "save_site",
  "delete_selected",
  "query_site_balance",
  "cookie_balance",
  "browser_login_helper",
  "query_site_logs",
  "sync_site_models",
  "probe_site_models_stream",
  "probe_site_models_nonstream",
  "probe_single_model_stream",
  "probe_single_model_nonstream",
  "checkin_current",
  "waf_helper",
  "detection_history",
  "test_connectivity",
  "test_authenticity",
  "send_chat",
]);

const state = {
  payload: null,
  selectedSiteId: null,
  selectedProviderId: null,
  selectedDetectionRunId: null,
  activePage: "overview",
  search: "",
  busy: false,
  bootstrapped: false,
  logsBySite: {},
  detectionRunsBySite: {},
  detectionEvidenceByRun: {},
  actionLogs: [],
  lastTestResult: null,
  checkinFilter: { date: "recent", status: "all" },
  modelProbeForm: {
    presetId: "",
    modelId: "",
  },
  selectedCustomPresetId: null,
  settingsForm: {
    autostart: false,
    minimize_to_tray: true,
    low_balance_threshold: 10,
    logs_page_size: 50,
    action_log_max_rows: 500,
    auto_query_enabled: false,
    auto_query_interval: 30,
    auto_checkin_enabled: false,
    auto_checkin_time: "09:00",
    enable_api_log: false,
    theme: "flatly",
    use_background_image: false,
  },
  consoleForm: {
    presetId: "",
    modelId: "",
    withThinking: true,
    withSystem: true,
    message: "你好，请回复当前模型名称和提供商。",
  },
  consoleViewerTab: "detail",
};

pageMeta.models = {
  title: "模型连通性",
  subtitle: "按站点查看模型列表，以及流式 / 非流式探测结果",
};

function qs(selector) {
  return document.querySelector(selector);
}

pageMeta.settings = {
  title: "设置中心",
  subtitle: "应用设置、自定义请求预设和调试开关",
};

pageMeta.models = {
  title: "模型连通性",
  subtitle: "按站点查看模型列表，以及流式 / 非流式探测结果",
};

function qsa(selector) {
  return Array.from(document.querySelectorAll(selector));
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function toNumber(value, defaultValue = 0) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : defaultValue;
}

function formatTime(value) {
  if (!value) return "--";
  if (typeof value === "number") {
    const ms = value > 1e12 ? value : value * 1000;
    return new Date(ms).toLocaleString("zh-CN");
  }
  return String(value);
}

function fmtBalance(site) {
  if (!site) return "--";
  const unit = site.balance_unit || "USD";
  const amount = toNumber(site.balance, 0);
  if (unit === "USD") return `$${amount.toFixed(2)}`;
  return `${amount.toLocaleString("zh-CN")} ${unit}`;
}

function siteStatusText(site) {
  if (!site) return "未知";
  if (site.status === "warning") return "低余额";
  if (site.status === "muted") return "未配置";
  return "正常";
}

function getSites() {
  return state.payload?.sites || [];
}

function getSelectedSite() {
  return getSites().find((site) => site.id === state.selectedSiteId) || null;
}

function getProviders() {
  return state.payload?.providers || fallbackPayload.providers || [];
}

function getProviderById(providerId) {
  return getProviders().find((item) => item.id === providerId) || null;
}

function getSelectedProvider() {
  return getProviderById(state.selectedProviderId) || null;
}

function getDetectionRuns() {
  if (state.selectedSiteId && state.detectionRunsBySite[state.selectedSiteId]) {
    return state.detectionRunsBySite[state.selectedSiteId];
  }
  const payloadRuns = state.payload?.detection_runs || [];
  if ((payloadRuns || []).every((run) => !run.site_id || run.site_id === state.selectedSiteId)) {
    return payloadRuns;
  }
  return [];
}

function getActionLogs() {
  return state.actionLogs.length ? state.actionLogs : state.payload?.action_logs || fallbackPayload.action_logs || [];
}

function renderProviderSummary(providerId) {
  const providerSummary = qs("#site-provider-summary");
  if (!providerSummary) return;
  const provider = getProviderById(providerId || "custom");
  if (!provider) {
    providerSummary.textContent = "未找到 Provider 策略";
    return;
  }
  const wafNames = (provider.waf_cookie_names || []).join(", ") || "无";
  providerSummary.textContent = `${provider.description || provider.name} | 登录页 ${provider.login_path || "/login"} | 签到接口 ${provider.sign_in_path || "自动"} | WAF Cookie ${wafNames}`;
}

function renderProviderList() {
  const list = qs("#provider-list");
  if (!list) return;
  const providers = getProviders();
  if (!providers.length) {
    list.innerHTML = `<div class="provider-item"><strong>暂无 Provider</strong><span>点击"新增 Provider"创建自定义策略。</span></div>`;
    return;
  }
  list.innerHTML = providers
    .map((provider) => {
      const active = provider.id === state.selectedProviderId ? "active" : "";
      const readonly = provider.is_builtin ? "readonly" : "";
      const wafNames = (provider.waf_cookie_names || []).join(", ") || "无";
      return `
        <article class="provider-item ${active} ${readonly}" data-provider-id="${escapeHtml(provider.id)}">
          <strong>${escapeHtml(provider.name || provider.id)}</strong>
          <span>${escapeHtml(provider.description || "无描述")}</span>
          <span>${provider.is_builtin ? "内置" : "自定义"} | WAF: ${escapeHtml(wafNames)}</span>
        </article>
      `;
    })
    .join("");
}

function renderProviderEditor() {
  const provider = getSelectedProvider();
  const note = qs("#provider-builtin-note");
  if (!provider) {
    [
      "provider-name",
      "provider-description",
      "provider-login-path",
      "provider-sign-in-path",
      "provider-user-info-path",
      "provider-api-user-key",
      "provider-waf-cookie-names",
    ].forEach((id) => setInputValue(id, ""));
    if (qs("#provider-supports-cookie-auth")) qs("#provider-supports-cookie-auth").checked = false;
    if (qs("#provider-supports-browser-login")) qs("#provider-supports-browser-login").checked = false;
    if (qs("#provider-auto-checkin-via-user-info")) qs("#provider-auto-checkin-via-user-info").checked = false;
    if (note) note.textContent = "选择自定义 Provider 后可编辑。";
    return;
  }

  setInputValue("provider-name", provider.name || "");
  setInputValue("provider-description", provider.description || "");
  setInputValue("provider-login-path", provider.login_path || "/login");
  setInputValue("provider-sign-in-path", provider.sign_in_path || "");
  setInputValue("provider-user-info-path", provider.user_info_path || "/api/user/self");
  setInputValue("provider-api-user-key", provider.api_user_key || "new-api-user");
  setInputValue("provider-waf-cookie-names", (provider.waf_cookie_names || []).join(", "));
  if (qs("#provider-supports-cookie-auth")) qs("#provider-supports-cookie-auth").checked = Boolean(provider.supports_cookie_auth);
  if (qs("#provider-supports-browser-login")) qs("#provider-supports-browser-login").checked = Boolean(provider.supports_browser_login);
  if (qs("#provider-auto-checkin-via-user-info")) qs("#provider-auto-checkin-via-user-info").checked = Boolean(provider.auto_checkin_via_user_info);
  if (note) {
    note.textContent = provider.is_builtin
      ? "内置 Provider 仅供查看，不能直接修改或删除。"
      : "自定义 Provider 可保存和删除。";
  }
}

function getFilteredSites() {
  const keyword = state.search.trim().toLowerCase();
  const sites = getSites();
  if (!keyword) return sites;
  return sites.filter((site) => {
    const name = String(site.name || "").toLowerCase();
    const url = String(site.url || "").toLowerCase();
    return name.includes(keyword) || url.includes(keyword);
  });
}

function getTestMeta() {
  return state.payload?.test_meta || fallbackPayload.test_meta;
}

function getSiteModelCards() {
  return state.payload?.site_model_cards || fallbackPayload.site_model_cards || [];
}

function getSiteModels(siteId = state.selectedSiteId) {
  if (!siteId) return [];
  const payloadModels = state.payload?.site_models_by_site || fallbackPayload.site_models_by_site || {};
  return payloadModels[siteId] || [];
}

function getPresetById(presetId) {
  return (getTestMeta().presets || []).find((item) => String(item.id) === String(presetId)) || null;
}

function getModelOptions(siteId = state.selectedSiteId) {
  const siteSpecific = getSiteModels(siteId);
  if (siteSpecific.length) {
    return siteSpecific.map((item) => ({
      id: String(item.model_id || ""),
      name: item.display_name || item.model_id || "",
      source: item.source || "site",
    }));
  }
  const modelMap = new Map();
  (getTestMeta().models || []).forEach((item) => {
    const modelId = String(item.id || "").trim();
    if (!modelId || modelMap.has(modelId)) return;
    modelMap.set(modelId, {
      id: modelId,
      name: item.name || modelId,
      source: "fallback",
    });
  });
  return Array.from(modelMap.values());
}

function getCustomPresets() {
  return state.payload?.custom_presets || [];
}

function getSelectedCustomPreset() {
  return getCustomPresets().find((item) => String(item.id) === String(state.selectedCustomPresetId)) || null;
}

function ensureShellEnhancements() {
  const menu = qs(".menu");
  if (menu && !menu.querySelector('[data-page="settings"]')) {
    const button = document.createElement("button");
    button.className = "menu-item";
    button.dataset.page = "settings";
    button.innerHTML = `<span class="menu-icon">⚙</span><span>设置</span>`;
    menu.appendChild(button);
  }

  const pageLabelMap = {
    overview: "总览",
    sites: "站点中心",
    checkin: "签到中心",
    models: "模型连通性",
    console: "验证与对话",
    settings: "设置",
  };
  Object.entries(pageLabelMap).forEach(([pageName, label]) => {
    const button = menu?.querySelector(`[data-page="${pageName}"]`);
    const textNode = button?.querySelector("span:last-child");
    if (textNode) textNode.textContent = label;
  });

  const workspace = qs(".workspace");
  if (workspace && !workspace.querySelector('[data-page-panel="settings"]')) {
    const section = document.createElement("section");
    section.className = "page";
    section.dataset.pagePanel = "settings";
    workspace.appendChild(section);
  }

  const labelMap = {
    query_site_balance: "API 余额",
    cookie_balance: "账户信息",
    browser_login_helper: "获取登录态",
    waf_helper: "刷新 WAF Cookie",
  };
  Object.entries(labelMap).forEach(([action, label]) => {
    qsa(`[data-action="${action}"]`).forEach((button) => {
      button.textContent = label;
    });
  });

  if (!qs("#site-balance-summary")) {
    const actionStrip = qs('.page[data-page-panel="sites"] .action-strip');
    if (actionStrip && actionStrip.parentElement) {
      const summary = document.createElement("div");
      summary.id = "site-balance-summary";
      summary.className = "inline-note";
      actionStrip.insertAdjacentElement("afterend", summary);
    }
  }
}

function ensureSettingsDefaults() {
  const settings = state.payload?.settings || fallbackPayload.settings || {};
  state.settingsForm = {
    autostart: Boolean(settings.autostart),
    minimize_to_tray: Boolean(settings.minimize_to_tray),
    low_balance_threshold: toNumber(settings.low_balance_threshold, 10),
    logs_page_size: toNumber(settings.logs_page_size, 50),
    action_log_max_rows: toNumber(settings.action_log_max_rows, 500),
    auto_query_enabled: Boolean(settings.auto_query_enabled),
    auto_query_interval: toNumber(settings.auto_query_interval, 30),
    auto_checkin_enabled: Boolean(settings.auto_checkin_enabled),
    auto_checkin_time: settings.auto_checkin_time || "09:00",
    enable_api_log: Boolean(settings.enable_api_log),
    theme: settings.theme || "flatly",
    use_background_image: Boolean(settings.use_background_image),
  };
  const customPresets = getCustomPresets();
  if (!customPresets.find((item) => item.id === state.selectedCustomPresetId)) {
    state.selectedCustomPresetId = customPresets[0]?.id || null;
  }
}

function modelStatusText(status) {
  if (status === "success") return "可用";
  if (status === "failed") return "失败";
  return "--";
}

function exportData(scope) {
  const ts = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
  let data, filename;
  if (scope === "sites") {
    data = getSites().map((s) => ({ name: s.name, url: s.url, type: s.type, tags: s.tags_text, api_balance: s.api_balance, api_balance_unit: s.api_balance_unit, account_balance: s.account_balance, last_query_time: s.api_last_query_time, status: s.status, notes: s.notes }));
    filename = `sites_${ts}.json`;
  } else if (scope === "checkin") {
    data = (state.payload?.checkin_logs || []).map((l) => ({ time: l.time, site: l.site_name, success: l.success, quota: l.quota_awarded, message: l.message }));
    filename = `checkin_${ts}.json`;
  } else if (scope === "detection") {
    const runs = [];
    for (const [siteId, arr] of Object.entries(state.detectionRunsBySite || {})) {
      for (const r of arr) runs.push({ site_id: siteId, ...r });
    }
    data = runs;
    filename = `detection_${ts}.json`;
  } else {
    data = { sites: getSites(), checkin_logs: state.payload?.checkin_logs || [], metrics: state.payload?.metrics || {}, settings: state.settingsForm, exported_at: new Date().toISOString() };
    filename = `any_api_check_export_${ts}.json`;
  }
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
  showToast("导出完成", `已导出 ${filename}`);
}

function showToast(title, message) {
  const root = qs("#toast-root");
  if (!root) return;
  const toast = document.createElement("div");
  toast.className = "toast";
  toast.innerHTML = `<strong>${escapeHtml(title)}</strong><span>${escapeHtml(message || "")}</span>`;
  root.appendChild(toast);
  setTimeout(() => {
    toast.remove();
  }, 2600);
}

function appendConsoleLines(lines) {
  if (!Array.isArray(lines) || !lines.length) return;
  const output = qs("#console-output");
  if (!output) return;
  const next = [...lines, output.textContent || ""].filter(Boolean).join("\n");
  output.textContent = next;
}

function ensureConsoleDefaults() {
  const meta = getTestMeta();
  const presets = meta.presets || [];
  const presetIds = new Set(presets.map((item) => String(item.id)));
  if (!presetIds.has(state.consoleForm.presetId)) {
    state.consoleForm.presetId = String(meta.default_preset || presets[0]?.id || "");
  }
  state.consoleForm.modelId = String(state.consoleForm.modelId || "").trim();
  if (!["detail", "request", "response"].includes(state.consoleViewerTab)) {
    state.consoleViewerTab = "detail";
  }
}

function syncConsoleDraftFromInputs() {
  const preset = qs("#console-preset");
  if (preset) state.consoleForm.presetId = preset.value || state.consoleForm.presetId;

  state.consoleForm.modelId = String(qs("#console-model")?.value || "").trim();

  const thinking = qs("#console-thinking");
  if (thinking) state.consoleForm.withThinking = thinking.value === "true";

  const system = qs("#console-system");
  if (system) state.consoleForm.withSystem = system.value === "true";

  const message = qs("#console-message");
  if (message) state.consoleForm.message = message.value || "";
}

function applyConsoleViewerState() {
  qsa("[data-console-view]").forEach((button) => {
    button.classList.toggle("active", button.dataset.consoleView === state.consoleViewerTab);
  });
  qsa("[data-console-panel]").forEach((panel) => {
    panel.classList.toggle("active", panel.dataset.consolePanel === state.consoleViewerTab);
  });
}

function ensureModelProbeDefaults() {
  const presets = getTestMeta().presets || [];
  const presetIds = new Set(presets.map((item) => String(item.id)));
  if (!presetIds.has(state.modelProbeForm.presetId)) {
    state.modelProbeForm.presetId = String(
      presets.find((item) => item.id === "openai_relay")?.id || presets[0]?.id || "",
    );
  }
  state.modelProbeForm.modelId = String(state.modelProbeForm.modelId || "").trim();
}

function syncModelProbeDraftFromInputs() {
  const preset = qs("#models-probe-preset");
  if (preset) state.modelProbeForm.presetId = preset.value || state.modelProbeForm.presetId;
  state.modelProbeForm.modelId = String(qs("#models-probe-model")?.value || "").trim();
}

function hydrate(payload) {
  state.payload = payload || fallbackPayload;
  ensureShellEnhancements();
  const ids = new Set(getSites().map((site) => site.id));
  const persistedSiteId = (() => {
    try {
      return window.localStorage?.getItem("selected_site_id") || "";
    } catch {
      return "";
    }
  })();
  const firstModelSiteId = Object.keys(state.payload?.site_models_by_site || {})[0] || "";
  const preferredSiteId =
    (ids.has(persistedSiteId) && persistedSiteId)
    || (ids.has(state.selectedSiteId) && state.selectedSiteId)
    || (ids.has(firstModelSiteId) && firstModelSiteId)
    || (ids.has(state.payload.selected_site_id) && state.payload.selected_site_id)
    || getSites()[0]?.id
    || null;
  state.selectedSiteId = preferredSiteId;
  if (state.payload) {
    state.payload.site_models = getSiteModels(state.selectedSiteId);
  }
  const providerIds = new Set(getProviders().map((provider) => provider.id));
  if (!providerIds.has(state.selectedProviderId)) {
    const customProvider = getProviders().find((provider) => !provider.is_builtin);
    state.selectedProviderId = customProvider?.id || getProviders()[0]?.id || null;
  }
  ensureConsoleDefaults();
  ensureModelProbeDefaults();
  ensureSettingsDefaults();
  renderAll();
}

function setActivePage(pageName) {
  if (!pageMeta[pageName]) return;
  const previousPage = state.activePage;
  state.activePage = pageName;
  qsa("[data-page]").forEach((button) => {
    button.classList.toggle("active", button.dataset.page === pageName);
  });
  qsa("[data-page-panel]").forEach((panel) => {
    panel.classList.toggle("active", panel.dataset.pagePanel === pageName);
  });
  updateTopbar();

  // 切换到总览页面时重新渲染图表，确保图表正确显示
  if (pageName === "overview") {
    queueMicrotask(() => {
      renderCharts();
    });
  }

  if (pageName === "console" && previousPage !== "console" && state.selectedSiteId && !state.busy) {
    queueMicrotask(() => invokeAction("detection_history"));
  }
}

function updateTopbar() {
  const meta = pageMeta[state.activePage] || pageMeta.overview;
  const selected = getSelectedSite();
  qs("#page-title").textContent = meta.title;
  qs("#page-subtitle").textContent = meta.subtitle;
  qs("#selected-site-pill").textContent = selected ? `${selected.name} · ${siteStatusText(selected)}` : "未选择站点";
  qs("#rail-site-count").textContent = `${getSites().length} 个站点`;
  qs("#rail-generated-at").textContent = `更新: ${state.payload?.app?.generated_at || "--"}`;
}

function renderSettings() {
  ensureSettingsDefaults();
  const section = qs('[data-page-panel="settings"]');
  if (!section) return;

  const formats = getTestMeta().request_formats || [];
  const customPresets = getCustomPresets();
  const selectedPreset = getSelectedCustomPreset();
  const sf = state.settingsForm;

  section.innerHTML = `
    <div class="settings-page">
      <div class="settings-header">
        <h2>设置</h2>
        <button class="btn primary" data-action="save_settings">保存全部设置</button>
      </div>
      <div class="settings-cards">
        <article class="settings-card">
          <div class="settings-card__icon">🖥</div>
          <div class="settings-card__body">
            <h3>基础</h3>
            <p class="settings-card__desc">应用启动与窗口行为</p>
            <div class="toggle-list">
              <label class="toggle-row"><span>开机启动</span><input id="settings-autostart" type="checkbox" class="toggle" ${sf.autostart ? "checked" : ""} /></label>
              <label class="toggle-row"><span>最小化到托盘</span><input id="settings-minimize-to-tray" type="checkbox" class="toggle" ${sf.minimize_to_tray ? "checked" : ""} /></label>
            </div>
          </div>
        </article>
        <article class="settings-card">
          <div class="settings-card__icon">⏱</div>
          <div class="settings-card__body">
            <h3>自动化</h3>
            <p class="settings-card__desc">定时查询与签到</p>
            <div class="toggle-list">
              <label class="toggle-row"><span>自动查询余额</span><input id="settings-auto-query-enabled" type="checkbox" class="toggle" ${sf.auto_query_enabled ? "checked" : ""} /></label>
              <label class="toggle-row"><span>自动签到</span><input id="settings-auto-checkin-enabled" type="checkbox" class="toggle" ${sf.auto_checkin_enabled ? "checked" : ""} /></label>
            </div>
            <div class="field-grid two" style="margin-top:10px">
              <label class="field"><span>查询间隔（分钟）</span><input id="settings-auto-query-interval" class="input" type="number" value="${escapeHtml(sf.auto_query_interval)}" /></label>
              <label class="field"><span>签到时间</span><input id="settings-auto-checkin-time" class="input" type="time" value="${escapeHtml(sf.auto_checkin_time)}" /></label>
            </div>
          </div>
        </article>
        <article class="settings-card">
          <div class="settings-card__icon">📊</div>
          <div class="settings-card__body">
            <h3>数据</h3>
            <p class="settings-card__desc">阈值、日志与存储</p>
            <div class="toggle-list">
              <label class="toggle-row"><span>启用调试日志</span><input id="settings-enable-api-log" type="checkbox" class="toggle" ${sf.enable_api_log ? "checked" : ""} /></label>
            </div>
            <div class="field-grid three" style="margin-top:10px">
              <label class="field"><span>低余额阈值</span><input id="settings-low-balance-threshold" class="input" type="number" value="${escapeHtml(sf.low_balance_threshold)}" /></label>
              <label class="field"><span>日志分页大小</span><input id="settings-logs-page-size" class="input" type="number" value="${escapeHtml(sf.logs_page_size)}" /></label>
              <label class="field"><span>日志保留条数</span><input id="settings-action-log-max-rows" class="input" type="number" value="${escapeHtml(sf.action_log_max_rows)}" /></label>
            </div>
          </div>
        </article>
        <article class="settings-card">
          <div class="settings-card__icon">💾</div>
          <div class="settings-card__body">
            <h3>数据导出</h3>
            <p class="settings-card__desc">导出站点、签到、检测等数据</p>
            <div class="action-strip" style="margin-top:10px">
              <button class="btn secondary" onclick="exportData('sites')">导出站点</button>
              <button class="btn secondary" onclick="exportData('checkin')">导出签到</button>
              <button class="btn secondary" onclick="exportData('detection')">导出检测</button>
              <button class="btn primary" onclick="exportData('all')">导出全部</button>
            </div>
          </div>
        </article>
      </div>
      <article class="card panel settings-preset-panel">
        <div class="panel-head">
          <h2>自定义预设</h2>
          <div class="row-actions">
            <button id="new-custom-preset" class="btn tiny">新增</button>
            <button class="btn tiny" data-action="save_custom_preset">保存预设</button>
            <button class="btn tiny danger" data-action="delete_custom_preset">删除</button>
          </div>
        </div>
        <div class="preset-layout">
          <div id="custom-preset-list" class="provider-list"></div>
          <div class="preset-editor">
            <div class="field-grid two">
              <label class="field"><span>预设 ID</span><input id="custom-preset-id" class="input" type="text" value="${escapeHtml(selectedPreset?.id || "")}" placeholder="custom_demo" /></label>
              <label class="field"><span>名称</span><input id="custom-preset-name" class="input" type="text" value="${escapeHtml(selectedPreset?.name || "")}" /></label>
              <label class="field full"><span>描述</span><input id="custom-preset-description" class="input" type="text" value="${escapeHtml(selectedPreset?.description || "")}" /></label>
              <label class="field"><span>请求格式</span>
                <select id="custom-preset-request-format" class="input">
                  ${formats.map((item) => `<option value="${escapeHtml(item.id)}" ${item.id === (selectedPreset?.request_format || "") ? "selected" : ""}>${escapeHtml(item.name || item.id)}</option>`).join("")}
                </select>
              </label>
              <label class="field"><span>Endpoint</span><input id="custom-preset-endpoint" class="input" type="text" value="${escapeHtml(selectedPreset?.endpoint || "")}" placeholder="/v1/chat/completions" /></label>
              <label class="field"><span>认证 Header</span><input id="custom-preset-auth-header" class="input" type="text" value="${escapeHtml(selectedPreset?.auth_header || "Authorization")}" /></label>
              <label class="field"><span>认证前缀</span><input id="custom-preset-auth-prefix" class="input" type="text" value="${escapeHtml(selectedPreset?.auth_prefix || "Bearer ")}" /></label>
            </div>
            <details class="preset-advanced" open>
              <summary>高级配置</summary>
              <div class="field-grid">
                <label class="field"><span>Headers JSON</span><textarea id="custom-preset-headers" class="input area" rows="3">${escapeHtml(selectedPreset?.headers_text || "{}")}</textarea></label>
                <label class="field"><span>Body Template JSON</span><textarea id="custom-preset-body-template" class="input area" rows="6">${escapeHtml(selectedPreset?.body_template_text || "{}")}</textarea></label>
                <label class="field"><span>Thinking JSON</span><textarea id="custom-preset-thinking-config" class="input area" rows="3">${escapeHtml(selectedPreset?.thinking_config_text || "{}")}</textarea></label>
              </div>
              <div class="toggle-list" style="margin-top:10px">
                <label class="toggle-row"><span>支持 thinking</span><input id="custom-preset-supports-thinking" type="checkbox" class="toggle" ${selectedPreset?.supports_thinking ? "checked" : ""} /></label>
                <label class="toggle-row"><span>注入 CLI tools</span><input id="custom-preset-include-cli-tools" type="checkbox" class="toggle" ${selectedPreset?.include_cli_tools ? "checked" : ""} /></label>
                <label class="toggle-row"><span>注入 CLI system</span><input id="custom-preset-include-cli-system" type="checkbox" class="toggle" ${selectedPreset?.include_cli_system ? "checked" : ""} /></label>
              </div>
            </details>
          </div>
        </div>
      </article>
    </div>
  `;

  const list = qs("#custom-preset-list");
  if (list) {
    list.innerHTML = customPresets.length
      ? customPresets
          .map(
            (item) => `
              <article class="provider-item ${item.id === state.selectedCustomPresetId ? "active" : ""}" data-custom-preset-id="${escapeHtml(item.id)}">
                <strong>${escapeHtml(item.name || item.id)}</strong>
                <span>${escapeHtml(item.request_format || "--")} · ${escapeHtml(item.endpoint || "--")}</span>
              </article>
            `,
          )
          .join("")
      : `<div class="provider-item"><strong>暂无自定义预设</strong><span>点击"新增"创建一个。</span></div>`;
  }
}

function setInputValue(id, value) {
  const element = qs(`#${id}`);
  if (!element) return;
  element.value = value ?? "";
}

function renderSites() {
  renderSiteList();
  renderSiteEditor();
  renderProviderList();
  renderProviderEditor();
}

function renderCheckin() {
  const metrics = state.payload?.metrics || {};
  const cards = [
    {
      label: "今日签到成功",
      value: metrics.today_checkin_success || 0,
      hint: "仅今日",
    },
    {
      label: "今日签到失败",
      value: metrics.today_checkin_failed || 0,
      hint: "需要排查",
    },
    {
      label: "可直接签到站点",
      value: metrics.cookie_enabled_count || 0,
      hint: "已配置 Cookie",
    },
    {
      label: "低余额站点",
      value: metrics.low_balance_count || 0,
      hint: "优先处理",
    },
  ];

  qs("#checkin-summary").innerHTML = cards
    .map(
      (item) => `
      <article class="metric">
        <span>${escapeHtml(item.label)}</span>
        <strong>${escapeHtml(item.value)}</strong>
        <small>${escapeHtml(item.hint)}</small>
      </article>
    `,
    )
    .join("");

  const rows = state.payload?.checkin_logs || [];

  // 应用筛选
  const { date: dateFilter, status: statusFilter } = state.checkinFilter;
  const now = new Date();
  const todayStr = now.toISOString().slice(0, 10);
  const yesterday = new Date(now);
  yesterday.setDate(yesterday.getDate() - 1);
  const yesterdayStr = yesterday.toISOString().slice(0, 10);
  const weekAgo = new Date(now);
  weekAgo.setDate(weekAgo.getDate() - 7);
  const weekAgoStr = weekAgo.toISOString().slice(0, 10);

  const filtered = rows.filter((log) => {
    const logDate = (log.time || "").slice(0, 10);
    if (dateFilter === "recent" && logDate !== todayStr && logDate !== yesterdayStr) return false;
    if (dateFilter === "7d" && logDate < weekAgoStr) return false;
    if (statusFilter === "success" && !log.success) return false;
    if (statusFilter === "fail" && log.success) return false;
    return true;
  });

  // 同步筛选按钮激活状态
  document.querySelectorAll("[data-checkin-date]").forEach((btn) => btn.classList.toggle("active", btn.dataset.checkinDate === dateFilter));
  document.querySelectorAll("[data-checkin-status]").forEach((btn) => btn.classList.toggle("active", btn.dataset.checkinStatus === statusFilter));

  qs("#checkin-logs-body").innerHTML = filtered.length
    ? filtered
        .slice(0, 120)
        .map(
          (log) => `
          <tr>
            <td>${escapeHtml(log.time || "--")}</td>
            <td>${escapeHtml(log.site_name || "--")}</td>
            <td>${log.success ? "成功" : "失败"}</td>
            <td>${escapeHtml(String(log.quota_awarded ?? 0))}</td>
            <td>${escapeHtml(log.message || "")}</td>
          </tr>
        `,
        )
        .join("")
    : `<tr><td colspan="5">暂无匹配的签到记录</td></tr>`;
}

function aggregateModelUsage(items) {
  const modelMap = new Map();
  items.forEach((item) => {
    const model =
      String(item.model_name || item.model || item.model_id || item.token_name || "unknown").trim() || "unknown";
    const prompt = toNumber(item.prompt_tokens, 0);
    const completion = toNumber(item.completion_tokens, 0);
    const totalTokens = prompt + completion || toNumber(item.total_tokens, 0);
    const quota = toNumber(item.quota, 0);
    const current = modelMap.get(model) || { model, count: 0, tokens: 0, quota: 0 };
    current.count += 1;
    current.tokens += totalTokens;
    current.quota += quota;
    modelMap.set(model, current);
  });
  return Array.from(modelMap.values()).sort((a, b) => b.count - a.count);
}

function renderModels() {
  ensureModelProbeDefaults();
  const section = qs('[data-page-panel="models"]');
  if (!section) return;

  section.innerHTML = `
    <div class="models-layout">
      <article class="card panel">
        <div class="panel-head">
          <h2>站点模型概览</h2>
          <span class="pill info">按站点聚合</span>
        </div>
        <div id="model-site-cards" class="site-model-card-grid"></div>
      </article>
      <article class="card panel">
        <div class="panel-head">
          <h2>模型连通性</h2>
          <span id="models-count" class="pill info">0</span>
        </div>
        <div id="model-site-summary" class="kv-list"></div>
        <div id="models-probe-controls" class="field-grid two"></div>
        <div class="action-strip">
          <button class="btn secondary" data-action="sync_site_models">获取模型列表</button>
          <button class="btn secondary" data-action="probe_site_models_stream">全量流式探测</button>
          <button class="btn secondary" data-action="probe_site_models_nonstream">全量非流探测</button>
          <button class="btn secondary" data-action="probe_single_model_stream">单模型流式</button>
          <button class="btn secondary" data-action="probe_single_model_nonstream">单模型非流</button>
        </div>
        <div class="table-wrap">
          <table class="table compact">
            <thead>
              <tr>
                <th>名称</th>
                <th>模型 ID</th>
                <th>流式</th>
                <th>流式延迟</th>
                <th>非流</th>
                <th>非流延迟</th>
                <th>请求格式</th>
                <th>备注</th>
              </tr>
            </thead>
            <tbody id="models-catalog-body"></tbody>
          </table>
        </div>
      </article>
    </div>
    <div class="card panel">
      <div class="panel-head">
        <h2>调用记录（当前站点）</h2>
        <div class="row-actions">
          <button class="btn tiny" data-action="query_site_logs">刷新记录</button>
        </div>
      </div>
      <div class="table-wrap">
        <table class="table compact">
          <thead>
            <tr>
              <th>模型</th>
              <th>调用数</th>
              <th>Tokens</th>
              <th>额度</th>
            </tr>
          </thead>
          <tbody id="models-usage-body"></tbody>
        </table>
      </div>
    </div>
  `;

  const siteCards = getSiteModelCards();
  const siteModels = getSiteModels();
  const selectedSite = getSelectedSite();
  const presets = getTestMeta().presets || [];
  const modelOptions = getModelOptions();
  const selectedPreset = getPresetById(state.modelProbeForm.presetId);

  qs("#models-count").textContent = `${siteModels.length} 个`;
  qs("#model-site-cards").innerHTML = siteCards.length
    ? siteCards
        .map(
          (card) => `
          <article class="site-model-card ${card.site_id === state.selectedSiteId ? "active" : ""}" data-model-site-id="${escapeHtml(card.site_id)}">
            <div class="site-model-card__head">
              <strong>${escapeHtml(card.site_name || card.site_id)}</strong>
              <span>${escapeHtml(card.discovered_count || 0)} models</span>
            </div>
            <div class="site-model-card__meta">${escapeHtml(card.url || "--")}</div>
            <div class="site-model-card__stats">
              <span>流式 ${escapeHtml(String(card.stream_ok_count || 0))} / ${escapeHtml(String(card.stream_failed_count || 0))}</span>
              <span>非流 ${escapeHtml(String(card.nonstream_ok_count || 0))} / ${escapeHtml(String(card.nonstream_failed_count || 0))}</span>
            </div>
            <div class="site-model-card__foot">最近检测：${escapeHtml(card.last_checked_at || "--")}</div>
          </article>
        `,
        )
        .join("")
    : `<div class="inline-note">还没有模型状态。先选站点并点击"获取模型列表"。</div>`;

  const summaryRows = selectedSite
    ? [
        { label: "站点", value: selectedSite.name || "--" },
        { label: "地址", value: selectedSite.url || "--" },
        { label: "已发现模型", value: String(siteModels.length) },
        { label: "当前预设", value: selectedPreset?.name || state.modelProbeForm.presetId || "--" },
        { label: "请求格式", value: selectedPreset?.request_format_name || selectedPreset?.request_format || "--" },
      ]
    : [{ label: "提示", value: "先选择站点后再做模型探测" }];
  qs("#model-site-summary").innerHTML = summaryRows
    .map(
      (row) => `
        <div class="kv">
          <strong>${escapeHtml(row.label)}</strong>
          <span>${escapeHtml(row.value)}</span>
        </div>
      `,
    )
    .join("");

  qs("#models-probe-controls").innerHTML = `
    <label class="field">
      <span>探测预设</span>
      <select id="models-probe-preset" class="input">
        ${presets
          .map(
            (item) =>
              `<option value="${escapeHtml(item.id)}" ${
                item.id === state.modelProbeForm.presetId ? "selected" : ""
              }>${escapeHtml(item.name || item.id)}</option>`,
          )
          .join("")}
      </select>
    </label>
    <label class="field">
      <span>单模型探测</span>
      <input id="models-probe-model" class="input" list="models-probe-options" value="${escapeHtml(
        state.modelProbeForm.modelId || "",
      )}" placeholder="输入或选择模型 ID" />
      <datalist id="models-probe-options">
        ${modelOptions
          .map((item) => `<option value="${escapeHtml(item.id)}">${escapeHtml(item.name || item.id)}</option>`)
          .join("")}
      </datalist>
    </label>
  `;

  qs("#models-catalog-body").innerHTML = siteModels.length
    ? siteModels
        .map(
          (model) => `
          <tr>
            <td>${escapeHtml(model.display_name || model.model_id)}</td>
            <td>${escapeHtml(model.model_id || "")}</td>
            <td>${escapeHtml(modelStatusText(model.last_stream_status))}</td>
            <td>${escapeHtml(formatTime(model.last_stream_latency_ms))}</td>
            <td>${escapeHtml(modelStatusText(model.last_nonstream_status))}</td>
            <td>${escapeHtml(formatTime(model.last_nonstream_latency_ms))}</td>
            <td>${escapeHtml(model.last_request_format || "--")}</td>
            <td>${escapeHtml(model.last_message || "--")}</td>
          </tr>
        `,
        )
        .join("")
    : `<tr><td colspan="8">当前站点还没有模型列表。先点击"获取模型列表"。</td></tr>`;

  const selectedId = state.selectedSiteId || "";
  const logs = state.logsBySite[selectedId]?.items || [];
  const usage = aggregateModelUsage(logs);
  qs("#models-usage-body").innerHTML = usage.length
    ? usage
        .map(
          (row) => `
          <tr>
            <td>${escapeHtml(row.model)}</td>
            <td>${escapeHtml(String(row.count))}</td>
            <td>${escapeHtml(row.tokens.toLocaleString("zh-CN"))}</td>
            <td>${escapeHtml(row.quota.toFixed(2))}</td>
          </tr>
        `,
        )
        .join("")
    : `<tr><td colspan="4">暂无调用记录。选站点后点击"刷新记录"。</td></tr>`;
}

function renderConsole() {
  ensureConsoleDefaults();
  const meta = getTestMeta();
  const presets = meta.presets || [];
  const models = getModelOptions();
  const selectedPreset = getPresetById(state.consoleForm.presetId);

  qs("#console-config").innerHTML = `
    <label class="field">
      <span>请求预设</span>
      <select id="console-preset" class="input">
        ${presets
          .map(
            (item) =>
              `<option value="${escapeHtml(item.id)}" ${
                item.id === state.consoleForm.presetId ? "selected" : ""
              }>${escapeHtml(item.name || item.id)}</option>`,
          )
          .join("")}
      </select>
    </label>
    <label class="field">
      <span>模型</span>
      <input id="console-model" class="input" list="console-model-options" value="${escapeHtml(
        state.consoleForm.modelId || "",
      )}" placeholder="输入或选择模型 ID" />
      <datalist id="console-model-options">
        ${models
          .map((item) => `<option value="${escapeHtml(item.id)}">${escapeHtml(item.name || item.id)}</option>`)
          .join("")}
      </datalist>
    </label>
    <div class="inline-note field full">当前请求格式：${escapeHtml(
      selectedPreset?.request_format_name || selectedPreset?.request_format || "--",
    )}</div>
    <label class="field full">
      <span>消息</span>
      <textarea id="console-message" class="input area" rows="4">${escapeHtml(state.consoleForm.message)}</textarea>
    </label>
    <label class="field">
      <span>思考开关</span>
      <select id="console-thinking" class="input">
        <option value="true" ${state.consoleForm.withThinking ? "selected" : ""}>开启</option>
        <option value="false" ${!state.consoleForm.withThinking ? "selected" : ""}>关闭</option>
      </select>
    </label>
    <label class="field">
      <span>系统提示</span>
      <select id="console-system" class="input">
        <option value="true" ${state.consoleForm.withSystem ? "selected" : ""}>开启</option>
        <option value="false" ${!state.consoleForm.withSystem ? "selected" : ""}>关闭</option>
      </select>
    </label>
  `;

  const result = state.lastTestResult || {};
  const requestText = result.request ? JSON.stringify(result.request, null, 2) : "";
  const responseText = String(result.response_text || "");
  qs("#console-request").textContent = requestText;
  qs("#console-response").textContent = responseText;

  const runs = getDetectionRuns();
  qs("#console-history-body").innerHTML = runs.length
    ? runs
        .map(
          (run) => `
          <tr data-run-id="${escapeHtml(run.id || "")}" class="${run.id === state.selectedDetectionRunId ? "active" : ""}">
            <td>${escapeHtml(run.started_at || "--")}</td>
            <td>${escapeHtml(run.run_type || "--")}</td>
            <td>${escapeHtml(run.status || "--")}</td>
            <td>${escapeHtml(run.request_format || "--")}</td>
            <td>${escapeHtml(run.detected_model || run.model_id || "--")}</td>
            <td>${escapeHtml(run.message || "")}</td>
          </tr>
        `,
        )
        .join("")
    : `<tr><td colspan="6">暂无检测记录</td></tr>`;

  const evidence = state.selectedDetectionRunId ? state.detectionEvidenceByRun[state.selectedDetectionRunId] : null;
  const detailBox = qs("#console-history-detail");
  if (detailBox) {
    detailBox.textContent = evidence
      ? JSON.stringify(
          {
            request: evidence.request || {},
            parsed_result: evidence.parsed_result || {},
            response_text: evidence.response_text || "",
          },
          null,
          2,
        )
      : "选择一条检测历史后，这里会显示请求、响应和解析结果。";
  }
}

function renderOverview() {
  const metrics = state.payload?.metrics || {};
  const cards = [
    { label: "站点总数", value: metrics.total_sites || 0, hint: "当前已登记站点" },
    { label: "API 余额", value: `$${toNumber(metrics.usd_total, 0).toFixed(2)}`, hint: "按 API Key 查询聚合" },
    {
      label: "今日签到",
      value: `${metrics.today_checkin_success || 0}/${(metrics.today_checkin_success || 0) + (metrics.today_checkin_failed || 0)}`,
      hint: "成功 / 总次数",
    },
    { label: "已获取登录态", value: metrics.cookie_enabled_count || 0, hint: "可读取账户信息的站点" },
  ];

  qs("#metric-grid").innerHTML = cards
    .map(
      (item) => `
        <article class="metric">
          <span>${escapeHtml(item.label)}</span>
          <strong>${escapeHtml(item.value)}</strong>
          <small>${escapeHtml(item.hint)}</small>
        </article>
      `,
    )
    .join("");

  const site = getSelectedSite();
  const snapshot = site
    ? [
        { title: "站点", value: site.name || "--" },
        { title: "地址", value: site.url || "--" },
        { title: "API 余额", value: `${toNumber(site.api_balance, 0).toFixed(2)} ${site.api_balance_unit || "USD"}` },
        { title: "账户信息", value: `${toNumber(site.account_balance, 0).toFixed(2)} ${site.account_balance_unit || "USD"}` },
      ]
    : [{ title: "提示", value: "请先在站点中心选择站点" }];

  qs("#overview-site-snapshot").innerHTML = snapshot
    .map(
      (row) => `
        <div class="kv">
          <strong>${escapeHtml(row.title)}</strong>
          <span>${escapeHtml(row.value)}</span>
        </div>
      `,
    )
    .join("");

  const activities = state.payload?.activity || [];
  qs("#overview-activity").innerHTML = activities.length
    ? activities
        .slice(0, 8)
        .map(
          (item) => `
          <article class="event">
            <div class="event-time">${escapeHtml(item.time || "--")}</div>
            <div class="event-title">${escapeHtml(item.title || "")}</div>
            <p>${escapeHtml(item.description || "")}</p>
          </article>
        `,
        )
        .join("")
    : `<article class="event"><div class="event-title">暂无活动</div><p>执行一次查询、获取登录态或签到后会显示在这里。</p></article>`;

  renderActionLogsOverview();
  renderCharts();
}

/* ── ECharts 可视化 ── */
const chartInstances = {};
function getChart(domId) {
  const dom = qs("#" + domId);
  if (!dom) return null;
  if (chartInstances[domId]) {
    chartInstances[domId].resize();
    return chartInstances[domId];
  }
  if (typeof echarts === "undefined") return null;
  const inst = echarts.init(dom);
  chartInstances[domId] = inst;
  return inst;
}

function renderCharts() {
  const cd = state.payload?.chart_data;
  if (!cd) return;
  renderBalanceChart(cd.balance);
  renderTypeChart(cd.type);
  renderCheckinChart(cd.checkin);
  renderRechargeChart(cd.recharge);
}

function renderBalanceChart(data) {
  if (!data || !data.names?.length) return;
  const chart = getChart("chart-balance");
  if (!chart) return;
  const colorMap = { paid: "#0f766e", free: "#f59e0b", subscription: "#6366f1" };

  // 如果站点数量超过 20 个，增加图表高度并启用滚动
  const siteCount = data.names.length;
  const chartDom = document.getElementById("chart-balance");
  if (siteCount > 20) {
    const dynamicHeight = Math.max(400, siteCount * 25);
    chartDom.style.height = dynamicHeight + "px";
    chart.resize();
  }

  chart.setOption({
    title: { text: `余额排名 (共 ${siteCount} 个站点)`, left: "center", textStyle: { fontSize: 14 } },
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    grid: { left: 12, right: 20, bottom: 12, top: 40, containLabel: true },
    dataZoom: siteCount > 20 ? [
      { type: "slider", yAxisIndex: 0, width: 20, right: 5, start: 0, end: Math.min(100, 2000 / siteCount) },
      { type: "inside", yAxisIndex: 0 }
    ] : [],
    xAxis: { type: "value", name: "余额" },
    yAxis: { type: "category", data: data.names, axisLabel: { fontSize: 11 } },
    series: [{
      type: "bar",
      data: data.values.map((v, i) => ({ value: v, itemStyle: { color: colorMap[data.types[i]] || "#0f766e" } })),
      barMaxWidth: 20,
      label: { show: true, position: "right", fontSize: 11, formatter: "{c}" },
    }],
  });
}

function renderTypeChart(data) {
  if (!data || !data.labels?.length) return;
  const chart = getChart("chart-type");
  if (!chart) return;
  const colors = ["#0f766e", "#f59e0b", "#6366f1", "#ec4899"];
  chart.setOption({
    title: { text: "站点类型分布", left: "center", textStyle: { fontSize: 14 } },
    tooltip: { trigger: "item", formatter: "{b}: {c} 个 ({d}%)" },
    legend: { bottom: 8, textStyle: { fontSize: 11 } },
    color: colors,
    series: [{
      type: "pie",
      radius: ["38%", "62%"],
      center: ["50%", "46%"],
      avoidLabelOverlap: true,
      itemStyle: { borderRadius: 6, borderColor: "#fff", borderWidth: 2 },
      label: { formatter: "{b}\n{c} 个", fontSize: 12 },
      data: data.labels.map((l, i) => ({ name: l, value: data.counts[i] })),
    }],
  });
}

function renderCheckinChart(data) {
  if (!data || !data.days?.length) return;
  const chart = getChart("chart-checkin");
  if (!chart) return;
  chart.setOption({
    title: { text: "签到趋势（近 30 天）", left: "center", textStyle: { fontSize: 14 } },
    tooltip: { trigger: "axis" },
    legend: { bottom: 4, textStyle: { fontSize: 11 } },
    grid: { left: 12, right: 12, bottom: 36, top: 40, containLabel: true },
    xAxis: { type: "category", data: data.days, boundaryGap: false, axisLabel: { fontSize: 10 } },
    yAxis: [
      { type: "value", name: "次数", splitLine: { lineStyle: { type: "dashed" } } },
      { type: "value", name: "额度", splitLine: { show: false } },
    ],
    series: [
      { name: "成功", type: "line", data: data.success, smooth: true, areaStyle: { opacity: 0.15 }, itemStyle: { color: "#0f766e" } },
      { name: "失败", type: "line", data: data.failed, smooth: true, areaStyle: { opacity: 0.1 }, itemStyle: { color: "#b5333b" } },
      { name: "获得额度", type: "bar", yAxisIndex: 1, data: data.quota, barMaxWidth: 12, itemStyle: { color: "#f59e0b", opacity: 0.7 } },
    ],
  });
}

function renderRechargeChart(data) {
  if (!data || !data.months?.length) return;
  const chart = getChart("chart-recharge");
  if (!chart) return;
  chart.setOption({
    title: { text: "充值趋势（近 12 个月）", left: "center", textStyle: { fontSize: 14 } },
    tooltip: { trigger: "axis" },
    grid: { left: 12, right: 12, bottom: 12, top: 40, containLabel: true },
    xAxis: { type: "category", data: data.months, axisLabel: { fontSize: 11 } },
    yAxis: { type: "value", name: "金额", splitLine: { lineStyle: { type: "dashed" } } },
    series: [{
      type: "line",
      data: data.values,
      smooth: true,
      areaStyle: { color: { type: "linear", x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: "rgba(99,102,241,0.3)" }, { offset: 1, color: "rgba(99,102,241,0.02)" }] } },
      itemStyle: { color: "#6366f1" },
      label: { show: true, position: "top", fontSize: 10, formatter: (p) => p.value > 0 ? p.value : "" },
    }],
  });
}

window.addEventListener("resize", () => {
  Object.values(chartInstances).forEach((c) => c.resize());
});

function renderSiteList() {
  const list = qs("#site-list");
  const sites = getFilteredSites();
  if (!sites.length) {
    list.innerHTML = `<div class="site-item"><strong>无匹配站点</strong><span>尝试调整搜索关键字。</span></div>`;
    return;
  }

  // 按类型分组
  const typeMap = {
    paid: { label: "付费站", sites: [], color: "#0f766e" },
    free: { label: "公益站", sites: [], color: "#f59e0b" },
    subscription: { label: "订阅站", sites: [], color: "#6366f1" }
  };

  sites.forEach((site) => {
    const type = site.type || "paid";
    if (typeMap[type]) {
      typeMap[type].sites.push(site);
    }
  });

  // 每个类型内按 API 余额降序排序
  Object.values(typeMap).forEach((group) => {
    group.sites.sort((a, b) => {
      const balanceA = toNumber(a.api_balance, 0);
      const balanceB = toNumber(b.api_balance, 0);
      return balanceB - balanceA;
    });
  });

  // 初始化折叠状态（如果没有保存过）
  if (!state.siteGroupCollapsed) {
    state.siteGroupCollapsed = {
      paid: false,
      free: false,
      subscription: false
    };
  }

  // 渲染分组列表
  let html = "";
  Object.entries(typeMap).forEach(([type, group]) => {
    if (group.sites.length === 0) return;

    const isCollapsed = state.siteGroupCollapsed[type] || false;
    const arrowIcon = isCollapsed ? "▶" : "▼";

    html += `
      <div class="site-group">
        <div class="site-group-header" style="border-left: 3px solid ${group.color}" data-toggle-group="${type}">
          <div style="display: flex; align-items: center; gap: 8px;">
            <span class="site-group-arrow">${arrowIcon}</span>
            <strong>${escapeHtml(group.label)}</strong>
          </div>
          <span>${group.sites.length} 个站点</span>
        </div>
        <div class="site-group-content ${isCollapsed ? 'collapsed' : ''}">
    `;

    group.sites.forEach((site) => {
      const active = site.id === state.selectedSiteId ? "active" : "";
      html += `
        <article class="site-item ${active}" data-site-id="${escapeHtml(site.id)}">
          <strong>${escapeHtml(site.name || "未命名站点")}</strong>
          <span>${escapeHtml(site.url || "--")}</span>
          <span>API ${escapeHtml(toNumber(site.api_balance, 0).toFixed(2))} ${escapeHtml(site.api_balance_unit || "USD")} · ${escapeHtml(siteStatusText(site))}</span>
        </article>
      `;
    });

    html += `</div></div>`;
  });

  list.innerHTML = html;

  // 绑定折叠/展开事件
  qsa("[data-toggle-group]").forEach((header) => {
    header.addEventListener("click", (e) => {
      const groupType = header.dataset.toggleGroup;
      state.siteGroupCollapsed[groupType] = !state.siteGroupCollapsed[groupType];
      renderSiteList();
    });
  });
}

function renderSiteEditor() {
  const site = getSelectedSite();
  const providers = getProviders();
  const providerSelect = qs("#site-provider-template");
  if (providerSelect) {
    providerSelect.innerHTML = providers
      .map((provider) => `<option value="${escapeHtml(provider.id)}">${escapeHtml(provider.name || provider.id)}</option>`)
      .join("");
  }
  if (!site) {
    [
      "site-name",
      "site-url",
      "site-api-key",
      "site-tags",
      "site-checkin-url",
      "site-checkin-path",
      "site-cookie",
      "site-user-id",
      "site-waf-cookies",
      "site-checkin-headers",
      "site-type",
      "site-provider-template",
      "site-balance-auth-type",
      "site-log-auth-type",
      "site-proxy",
      "site-notes",
    ].forEach((id) => setInputValue(id, ""));
    if (qs("#site-provider-summary")) qs("#site-provider-summary").textContent = "选择 Provider 后会显示接入策略说明。";
    if (qs("#site-balance-summary")) qs("#site-balance-summary").textContent = "选中站点后，这里会显示 API 余额与账户信息的差异。";
    return;
  }

  setInputValue("site-name", site.name || "");
  setInputValue("site-type", site.type || "paid");
  setInputValue("site-provider-template", site.provider_template || "custom");
  setInputValue("site-url", site.url || "");
  setInputValue("site-api-key", site.api_key || "");
  setInputValue("site-tags", site.tags_text || "");
  setInputValue("site-checkin-url", site.checkin_url || "");
  setInputValue("site-checkin-path", site.checkin_api_path || "/api/user/checkin");
  setInputValue("site-cookie", site.session_cookie || "");
  setInputValue("site-user-id", site.checkin_user_id || "");
  setInputValue("site-waf-cookies", site.waf_cookie_names_text || "");
  setInputValue("site-checkin-headers", site.checkin_headers_text || "{}");
  setInputValue("site-balance-auth-type", site.balance_auth_type || "bearer");
  setInputValue("site-log-auth-type", site.log_auth_type || "url_key");
  setInputValue("site-proxy", site.proxy || "");
  setInputValue("site-notes", site.notes || "");
  renderProviderSummary(site.provider_template || "custom");

  const summary = qs("#site-balance-summary");
  if (summary) {
    summary.innerHTML = `
      <strong>API 余额：</strong>${escapeHtml(`${toNumber(site.api_balance, 0).toFixed(2)} ${site.api_balance_unit || "USD"}`)}
      · <strong>更新时间：</strong>${escapeHtml(site.api_last_query_time || "--")}
      <br />
      <strong>账户信息：</strong>${escapeHtml(`${toNumber(site.account_balance, 0).toFixed(2)} ${site.account_balance_unit || "USD"}`)}
      · <strong>更新时间：</strong>${escapeHtml(site.account_last_query_time || "--")}
      ${site.account_status_message ? `<br /><strong>账户备注：</strong>${escapeHtml(site.account_status_message)}` : ""}
    `;
  }
}

function renderActionLogsOverview() {
  const logsBody = qs("#overview-action-logs-body");
  if (!logsBody) return;
  const actionLogs = getActionLogs();
  logsBody.innerHTML = actionLogs.length
    ? actionLogs
        .map(
          (log) => `
          <tr>
            <td>${escapeHtml(log.created_at || "--")}</td>
            <td>${escapeHtml(log.title || log.action_key || "--")}</td>
            <td>${log.success ? "成功" : "失败"}</td>
            <td>${escapeHtml(log.site_id || "--")}</td>
            <td>${escapeHtml(log.message || "")}</td>
          </tr>
        `,
        )
        .join("")
    : `<tr><td colspan="5">暂无动作日志</td></tr>`;
}

function renderAll() {
  ensureShellEnhancements();
  updateTopbar();
  renderOverview();
  renderActionLogsOverview();
  renderSites();
  renderCheckin();
  renderModels();
  renderConsole();
  renderSettings();
}

function collectSitePayload() {
  return {
    name: qs("#site-name")?.value || "",
    type: qs("#site-type")?.value || "paid",
    url: qs("#site-url")?.value || "",
    api_key: qs("#site-api-key")?.value || "",
    tags_text: qs("#site-tags")?.value || "",
    checkin_url: qs("#site-checkin-url")?.value || "",
    checkin_api_path: qs("#site-checkin-path")?.value || "/api/user/checkin",
    session_cookie: qs("#site-cookie")?.value || "",
    checkin_user_id: qs("#site-user-id")?.value || "",
    waf_cookie_names_text: qs("#site-waf-cookies")?.value || "",
    checkin_headers_text: qs("#site-checkin-headers")?.value || "{}",
    balance_auth_type: qs("#site-balance-auth-type")?.value || "bearer",
    log_auth_type: qs("#site-log-auth-type")?.value || "url_key",
    proxy: qs("#site-proxy")?.value || "",
    notes: qs("#site-notes")?.value || "",
    provider_template: qs("#site-provider-template")?.value || "custom",
  };
}

function collectProviderPayload() {
  return {
    provider_id: state.selectedProviderId,
    name: qs("#provider-name")?.value || "",
    description: qs("#provider-description")?.value || "",
    login_path: qs("#provider-login-path")?.value || "/login",
    sign_in_path: qs("#provider-sign-in-path")?.value || "",
    user_info_path: qs("#provider-user-info-path")?.value || "/api/user/self",
    api_user_key: qs("#provider-api-user-key")?.value || "new-api-user",
    waf_cookie_names: (qs("#provider-waf-cookie-names")?.value || "")
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean),
    supports_cookie_auth: Boolean(qs("#provider-supports-cookie-auth")?.checked),
    supports_browser_login: Boolean(qs("#provider-supports-browser-login")?.checked),
    auto_checkin_via_user_info: Boolean(qs("#provider-auto-checkin-via-user-info")?.checked),
  };
}

function collectModelProbePayload() {
  state.modelProbeForm.presetId = qs("#models-probe-preset")?.value || state.modelProbeForm.presetId;
  state.modelProbeForm.modelId = qs("#models-probe-model")?.value || state.modelProbeForm.modelId;
  return {
    preset_id: state.modelProbeForm.presetId,
    model_id: state.modelProbeForm.modelId,
  };
}

function collectSettingsPayload() {
  state.settingsForm = {
    autostart: Boolean(qs("#settings-autostart")?.checked),
    minimize_to_tray: Boolean(qs("#settings-minimize-to-tray")?.checked),
    low_balance_threshold: toNumber(qs("#settings-low-balance-threshold")?.value, 10),
    logs_page_size: toNumber(qs("#settings-logs-page-size")?.value, 50),
    action_log_max_rows: toNumber(qs("#settings-action-log-max-rows")?.value, 500),
    auto_query_enabled: Boolean(qs("#settings-auto-query-enabled")?.checked),
    auto_query_interval: toNumber(qs("#settings-auto-query-interval")?.value, 30),
    auto_checkin_enabled: Boolean(qs("#settings-auto-checkin-enabled")?.checked),
    auto_checkin_time: qs("#settings-auto-checkin-time")?.value || "09:00",
    enable_api_log: Boolean(qs("#settings-enable-api-log")?.checked),
    theme: state.settingsForm.theme || "flatly",
    use_background_image: false,
  };
  return { ...state.settingsForm };
}

function collectCustomPresetPayload() {
  return {
    id: qs("#custom-preset-id")?.value || "",
    name: qs("#custom-preset-name")?.value || "",
    description: qs("#custom-preset-description")?.value || "",
    request_format: qs("#custom-preset-request-format")?.value || "",
    endpoint: qs("#custom-preset-endpoint")?.value || "",
    auth_header: qs("#custom-preset-auth-header")?.value || "",
    auth_prefix: qs("#custom-preset-auth-prefix")?.value || "",
    headers_text: qs("#custom-preset-headers")?.value || "{}",
    body_template_text: qs("#custom-preset-body-template")?.value || "{}",
    thinking_config_text: qs("#custom-preset-thinking-config")?.value || "{}",
    supports_thinking: Boolean(qs("#custom-preset-supports-thinking")?.checked),
    include_cli_tools: Boolean(qs("#custom-preset-include-cli-tools")?.checked),
    include_cli_system: Boolean(qs("#custom-preset-include-cli-system")?.checked),
  };
}

function collectConsolePayload(action) {
  state.consoleForm.presetId = qs("#console-preset")?.value || state.consoleForm.presetId;
  state.consoleForm.modelId = qs("#console-model")?.value || state.consoleForm.modelId;
  state.consoleForm.withThinking = (qs("#console-thinking")?.value || "true") === "true";
  state.consoleForm.withSystem = (qs("#console-system")?.value || "true") === "true";
  state.consoleForm.message = qs("#console-message")?.value || "";

  const payload = {
    preset_id: state.consoleForm.presetId,
    model_id: state.consoleForm.modelId,
    with_thinking: state.consoleForm.withThinking,
    with_system: state.consoleForm.withSystem,
  };
  if (action === "send_chat") {
    payload.message = state.consoleForm.message;
  }
  return payload;
}

async function backendAction(action, payload = {}) {
  if (window.pywebview?.api?.run_action) {
    return window.pywebview.api.run_action(action, state.selectedSiteId, payload);
  }
  return mockAction(action);
}

function routeAfterAction(action) {
  if (["checkin_current", "checkin_all", "checkin_logs", "waf_helper"].includes(action)) {
    setActivePage("checkin");
  } else if ([
    "query_site_logs",
    "sync_site_models",
    "probe_site_models_stream",
    "probe_site_models_nonstream",
    "probe_single_model_stream",
    "probe_single_model_nonstream",
  ].includes(action)) {
    setActivePage("models");
  } else if (["test_connectivity", "test_authenticity", "send_chat", "detection_history"].includes(action)) {
    setActivePage("console");
  } else if (["save_settings", "save_custom_preset", "delete_custom_preset"].includes(action)) {
    setActivePage("settings");
  } else if (["add_site", "save_site", "delete_selected", "add_provider", "save_provider", "delete_provider"].includes(action)) {
    setActivePage("sites");
  }
}

function setBusy(nextBusy) {
  state.busy = nextBusy;
  qsa("[data-action]").forEach((button) => {
    button.disabled = nextBusy;
  });
}

async function invokeAction(action) {
  if (state.busy) return;
  if (selectedRequiredActions.has(action) && !state.selectedSiteId) {
    showToast("操作中断", "请先选择站点");
    return;
  }

  // 对于需要站点数据的操作，如果当前有未保存的站点编辑，先自动保存
  const needsSiteData = ["query_site_balance", "cookie_balance", "browser_login_helper", "query_site_logs", "checkin_current", "waf_helper"];
  if (needsSiteData.includes(action) && state.selectedSiteId) {
    const currentSite = getSelectedSite();
    const formName = qs("#site-name")?.value || "";
    const formUrl = qs("#site-url")?.value || "";

    // 检测是否有未保存的修改
    const hasUnsavedChanges = (
      (formName && formName !== (currentSite?.name || "")) ||
      (formUrl && formUrl !== (currentSite?.url || ""))
    );

    if (hasUnsavedChanges) {
      try {
        const sitePayload = collectSitePayload();
        const saveResult = await backendAction("save_site", sitePayload);
        if (saveResult?.payload) {
          hydrate(saveResult.payload);
        }
        showToast("自动保存", "已保存站点信息");
      } catch (error) {
        showToast("保存失败", "请先手动保存站点");
        return;
      }
    }
  }

  let payload = {};
  if (action === "save_site") payload = collectSitePayload();
  if (action === "save_provider" || action === "delete_provider") payload = collectProviderPayload();
  if (action === "detection_evidence") payload = { run_id: state.selectedDetectionRunId };
  if (["test_authenticity", "send_chat"].includes(action)) payload = collectConsolePayload(action);
  if (action === "save_settings") payload = collectSettingsPayload();
  if (action === "save_custom_preset") payload = collectCustomPresetPayload();
  if (action === "delete_custom_preset") payload = { id: state.selectedCustomPresetId };
  if ([
    "probe_site_models_stream",
    "probe_site_models_nonstream",
    "probe_single_model_stream",
    "probe_single_model_nonstream",
  ].includes(action)) payload = collectModelProbePayload();
  if (action === "checkin_all") payload = { open_browser: true };
  if (action === "browser_login_helper") payload = { timeout_seconds: 180 };

  if (["test_authenticity", "send_chat"].includes(action) && !String(payload.model_id || "").trim()) {
    showToast("操作中断", "请先选择或输入模型");
    return;
  }
  if (["probe_single_model_stream", "probe_single_model_nonstream"].includes(action) && !String(payload.model_id || "").trim()) {
    showToast("操作中断", "单模型探测前请先选择或输入模型");
    return;
  }

  setBusy(true);
  try {
    const result = await backendAction(action, payload);
    const title = result?.title || action;
    const message = result?.message || "";
    const isSuccess = Boolean(result?.success);

    if (result?.payload) {
      hydrate(result.payload);
    }
    if (result?.data?.logs && state.selectedSiteId) {
      state.logsBySite[state.selectedSiteId] = result.data.logs;
    }
    if (result?.data?.checkin_logs && state.payload) {
      state.payload.checkin_logs = result.data.checkin_logs;
    }
    if (result?.data?.runs && state.selectedSiteId) {
      state.detectionRunsBySite[state.selectedSiteId] = result.data.runs;
      if (state.payload) state.payload.detection_runs = result.data.runs;
      if (!state.selectedDetectionRunId && result.data.runs.length) {
        state.selectedDetectionRunId = result.data.runs[0].id || null;
      }
    }
    if (result?.data?.evidence) {
      const runId = result.data.evidence.run_id || state.selectedDetectionRunId;
      if (runId) {
        state.selectedDetectionRunId = runId;
        state.detectionEvidenceByRun[runId] = result.data.evidence;
      }
      state.consoleViewerTab = "detail";
    }
    if (result?.data?.provider_id) {
      state.selectedProviderId = result.data.provider_id;
    }
    if (result?.data?.preset_id !== undefined) {
      state.selectedCustomPresetId = result.data.preset_id || null;
    }
    if (result?.data?.logs) {
      state.actionLogs = result.data.logs;
      if (state.payload) state.payload.action_logs = result.data.logs;
    }
    if (result?.data?.result && ["test_connectivity", "test_authenticity", "send_chat"].includes(action)) {
      state.lastTestResult = result.data.result;
      state.consoleViewerTab = "response";
    }
    if (result?.data?.site_models && state.payload && state.selectedSiteId) {
      state.payload.site_models_by_site = state.payload.site_models_by_site || {};
      state.payload.site_models_by_site[state.selectedSiteId] = result.data.site_models;
      state.payload.site_models = result.data.site_models;
    }
    if (!result?.payload) {
      renderAll();
    }

    appendConsoleLines(result?.output_lines || [`[${formatTime(new Date())}] ${title}: ${message}`]);
    showToast(isSuccess ? title : `失败: ${title}`, message);
    routeAfterAction(action);
    if (isSuccess && action === "detection_history" && state.selectedDetectionRunId) {
      const detailResult = await backendAction("detection_evidence", { run_id: state.selectedDetectionRunId });
      if (detailResult?.data?.evidence) {
        state.detectionEvidenceByRun[state.selectedDetectionRunId] = detailResult.data.evidence;
        renderConsole();
      }
    }
    if (isSuccess && ["test_connectivity", "test_authenticity", "send_chat"].includes(action) && state.selectedSiteId) {
      const historyResult = await backendAction("detection_history", { limit: 20 });
      if (historyResult?.data?.runs) {
        state.detectionRunsBySite[state.selectedSiteId] = historyResult.data.runs;
        if (state.payload) state.payload.detection_runs = historyResult.data.runs;
        if (historyResult.data.runs.length) {
          state.selectedDetectionRunId = historyResult.data.runs[0].id || null;
          const detailResult = await backendAction("detection_evidence", { run_id: state.selectedDetectionRunId });
          if (detailResult?.data?.evidence && state.selectedDetectionRunId) {
            state.detectionEvidenceByRun[state.selectedDetectionRunId] = detailResult.data.evidence;
          }
        }
        renderConsole();
      }
    }
    if (action !== "action_logs") {
      const logsResult = await backendAction("action_logs", { limit: 30 });
      if (logsResult?.data?.logs) {
        state.actionLogs = logsResult.data.logs;
        if (state.payload) state.payload.action_logs = logsResult.data.logs;
        renderOverview();
      }
    }
  } catch (error) {
    showToast("请求异常", error?.message || String(error));
    appendConsoleLines([`[${formatTime(new Date())}] 请求异常: ${error?.message || String(error)}`]);
  } finally {
    setBusy(false);
  }
}

function bindEvents() {
  qsa("[data-page]").forEach((button) => {
    button.addEventListener("click", () => {
      setActivePage(button.dataset.page || "overview");
    });
  });

  document.addEventListener("click", (event) => {
    const pageButton = event.target.closest("[data-page]");
    if (pageButton) {
      setActivePage(pageButton.dataset.page || "overview");
      return;
    }
    const actionButton = event.target.closest("[data-action]");
    if (actionButton) {
      invokeAction(actionButton.dataset.action || "");
      return;
    }
    const jumpButton = event.target.closest("[data-page-jump]");
    if (jumpButton) {
      setActivePage(jumpButton.dataset.pageJump || "overview");
      return;
    }
    const siteItem = event.target.closest("[data-site-id]");
    if (siteItem) {
      state.selectedSiteId = siteItem.dataset.siteId || null;
      try {
        window.localStorage?.setItem("selected_site_id", state.selectedSiteId || "");
      } catch {}
      if (state.payload) {
        state.payload.detection_runs = state.detectionRunsBySite[state.selectedSiteId] || [];
        state.payload.site_models = getSiteModels(state.selectedSiteId);
      }
      ensureConsoleDefaults();
      ensureModelProbeDefaults();
      renderAll();
      if (state.activePage === "console" && state.selectedSiteId) {
        invokeAction("detection_history");
      }
      return;
    }
    const modelSiteItem = event.target.closest("[data-model-site-id]");
    if (modelSiteItem) {
      state.selectedSiteId = modelSiteItem.dataset.modelSiteId || null;
      try {
        window.localStorage?.setItem("selected_site_id", state.selectedSiteId || "");
      } catch {}
      if (state.payload) {
        state.payload.detection_runs = state.detectionRunsBySite[state.selectedSiteId] || [];
        state.payload.site_models = getSiteModels(state.selectedSiteId);
      }
      ensureConsoleDefaults();
      ensureModelProbeDefaults();
      renderAll();
      return;
    }
    const providerItem = event.target.closest("[data-provider-id]");
    if (providerItem) {
      state.selectedProviderId = providerItem.dataset.providerId || null;
      renderProviderList();
      renderProviderEditor();
      return;
    }
    const customPresetItem = event.target.closest("[data-custom-preset-id]");
    if (customPresetItem) {
      state.selectedCustomPresetId = customPresetItem.dataset.customPresetId || null;
      renderSettings();
      return;
    }
    if (event.target.closest("#new-custom-preset")) {
      state.selectedCustomPresetId = null;
      renderSettings();
      return;
    }
    const consoleViewButton = event.target.closest("[data-console-view]");
    if (consoleViewButton) {
      state.consoleViewerTab = consoleViewButton.dataset.consoleView || "detail";
      applyConsoleViewerState();
      return;
    }
    const checkinDateBtn = event.target.closest("[data-checkin-date]");
    if (checkinDateBtn) {
      state.checkinFilter.date = checkinDateBtn.dataset.checkinDate || "recent";
      renderCheckin();
      return;
    }
    const checkinStatusBtn = event.target.closest("[data-checkin-status]");
    if (checkinStatusBtn) {
      state.checkinFilter.status = checkinStatusBtn.dataset.checkinStatus || "all";
      renderCheckin();
      return;
    }
    const historyRow = event.target.closest("[data-run-id]");
    if (historyRow) {
      syncConsoleDraftFromInputs();
      state.selectedDetectionRunId = historyRow.dataset.runId || null;
      state.consoleViewerTab = "detail";
      renderConsole();
      invokeAction("detection_evidence");
    }
  });

  qs("#site-search")?.addEventListener("input", (event) => {
    state.search = event.target.value || "";
    renderSiteList();
  });

  document.addEventListener("change", (event) => {
    const target = event.target;
    if (target?.id === "models-probe-preset") {
      syncModelProbeDraftFromInputs();
      state.modelProbeForm.presetId = target.value || "";
      renderModels();
      return;
    }
    if (target?.id === "models-probe-model") {
      state.modelProbeForm.modelId = target.value || "";
      return;
    }
    if (target?.id === "console-preset") {
      syncConsoleDraftFromInputs();
      state.consoleForm.presetId = target.value || "";
      renderConsole();
      return;
    }
    if (target?.id === "console-model") {
      state.consoleForm.modelId = target.value || "";
    }
  });

  qs("#clear-console")?.addEventListener("click", () => {
    qs("#console-output").textContent = "";
    showToast("已清空", "状态输出区已清空");
  });

  qs("#site-provider-template")?.addEventListener("change", (event) => {
    renderProviderSummary(event.target.value || "custom");
  });
}

function mockAction(action) {
  if (action === "query_site_logs") {
    return {
      success: true,
      title: "当前站点日志",
      message: "已加载 3 条日志（模拟）",
      data: {
        logs: {
          total: 3,
          items: [
            {
              model_name: "claude-sonnet-4-5-20250929",
              prompt_tokens: 890,
              completion_tokens: 1321,
              quota: 0.78,
            },
            {
              model_name: "claude-sonnet-4-5-20250929",
              prompt_tokens: 650,
              completion_tokens: 910,
              quota: 0.45,
            },
            {
              model_name: "gpt-4.1",
              prompt_tokens: 1200,
              completion_tokens: 1500,
              quota: 0.96,
            },
          ],
        },
      },
      output_lines: ["[mock] query_site_logs"],
    };
  }

  if (action === "sync_site_models") {
    return {
      success: true,
      title: "获取模型列表",
      message: "已获取模型列表（模拟）",
      payload: state.payload || fallbackPayload,
      data: {
        result: {
          success: true,
          message: "已获取模型列表（模拟）",
          models: getSiteModels(),
        },
        site_models: getSiteModels(),
      },
      output_lines: ["[mock] sync_site_models"],
    };
  }

  if ([
    "probe_site_models_stream",
    "probe_site_models_nonstream",
    "probe_single_model_stream",
    "probe_single_model_nonstream",
  ].includes(action)) {
    return {
      success: true,
      title: "模型连通性探测",
      message: "模型探测完成（模拟）",
      payload: state.payload || fallbackPayload,
      data: {
        result: {
          success: true,
          message: "模型探测完成（模拟）",
          results: getSiteModels().map((item) => ({
            model_id: item.model_id,
            success: true,
            message: "模型可用",
            latency_ms: 800,
            request_format: item.last_request_format || "openai_chat",
          })),
        },
        site_models: getSiteModels(),
      },
      output_lines: ["[mock] model probe done"],
    };
  }

  if (["test_authenticity", "send_chat", "test_connectivity"].includes(action)) {
    return {
      success: true,
      title: "模拟测试",
      message: "浏览器 fallback 模式返回模拟结果",
      data: {
        result: {
          request: { url: "https://example.com/v1/messages", headers: { Authorization: "***" }, body: { mock: true } },
          response_text: "fallback mode: this is a mock response",
          status_lines: ["[mock] connected", "[mock] done"],
        },
      },
      output_lines: ["[mock] test flow done"],
    };
  }

  if (action === "browser_login_helper") {
    return {
      success: true,
      title: "浏览器登录助手",
      message: "已回收浏览器登录态（模拟）",
      payload: state.payload || fallbackPayload,
      data: {
        result: {
          success: true,
          message: "已检测到浏览器登录态，Cookie 已回收",
          user_id: "1001",
          current_url: "https://example.com/console",
        },
      },
      output_lines: ["[mock] browser_login_helper"],
    };
  }

  if (action === "detection_history") {
    return {
      success: true,
      title: "检测历史",
      message: "已加载 1 条检测记录（模拟）",
      data: {
        runs: fallbackPayload.detection_runs,
      },
      output_lines: ["[mock] detection history loaded"],
    };
  }

  if (action === "detection_evidence") {
    return {
      success: true,
      title: "检测详情",
      message: "已加载检测详情（模拟）",
      data: {
        evidence: {
          id: "evd-demo-1",
          run_id: state.selectedDetectionRunId || "det-demo-1",
          request: { url: "https://example.com/v1/messages", headers: { Authorization: "***" }, body: { mock: true } },
          response_text: "fallback mode: this is a mock response",
          parsed_result: { detected_model: "mock-model", is_authentic: false },
        },
      },
      output_lines: ["[mock] detection evidence loaded"],
    };
  }

  if (action === "action_logs") {
    return {
      success: true,
      title: "动作日志",
      message: "已加载动作日志（模拟）",
      data: { logs: fallbackPayload.action_logs },
      output_lines: ["[mock] action_logs"],
    };
  }

  if (action === "add_provider") {
    const providerId = `provider-${Date.now()}`;
    const provider = {
      id: providerId,
      name: "自定义 Provider",
      description: "",
      login_path: "/login",
      sign_in_path: "/api/user/checkin",
      user_info_path: "/api/user/self",
      api_user_key: "new-api-user",
      waf_cookie_names: [],
      supports_cookie_auth: true,
      supports_browser_login: false,
      auto_checkin_via_user_info: false,
      is_builtin: false,
    };
    return {
      success: true,
      title: "新增 Provider",
      message: "已创建 Provider（模拟）",
      payload: {
        ...(state.payload || fallbackPayload),
        providers: [...getProviders(), provider],
      },
      data: { provider_id: providerId },
      output_lines: ["[mock] add_provider"],
    };
  }

  if (action === "save_provider" || action === "delete_provider") {
    return {
      success: true,
      title: action === "save_provider" ? "保存 Provider" : "删除 Provider",
      message: "Provider 操作完成（模拟）",
      payload: state.payload || fallbackPayload,
      data: { provider_id: state.selectedProviderId },
      output_lines: [`[mock] ${action}`],
    };
  }

  return {
    success: true,
    title: "模拟动作",
    message: `${action} 已执行（fallback）`,
    payload: action === "reload_preview" || action === "refresh_sites" ? fallbackPayload : undefined,
    output_lines: [`[mock] ${action}`],
  };
}

async function bootstrapFromBackend() {
  if (!window.pywebview?.api?.bootstrap) return false;
  const payload = await window.pywebview.api.bootstrap();
  hydrate(payload);
  state.bootstrapped = true;
  return true;
}

function bootstrapFallback() {
  hydrate(fallbackPayload);
}

async function start() {
  bindEvents();
  bootstrapFallback();
  try {
    await bootstrapFromBackend();
  } catch (error) {
    appendConsoleLines([`[bootstrap] backend bootstrap failed: ${error?.message || String(error)}`]);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  start().catch((error) => {
    appendConsoleLines([`[fatal] ${error?.message || String(error)}`]);
    showToast("启动失败", error?.message || String(error));
  });
});

window.addEventListener("pywebviewready", async () => {
  try {
    await bootstrapFromBackend();
  } catch (error) {
    appendConsoleLines([`[pywebviewready] ${error?.message || String(error)}`]);
  }
});
