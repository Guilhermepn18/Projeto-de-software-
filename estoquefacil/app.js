(() => {
  "use strict";
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  let products = [];
  let activeFilter = "all";
  let toastTimer;

  function money(value) { return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(value); }
  function localDateValue(date = new Date()) { return `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,"0")}-${String(date.getDate()).padStart(2,"0")}`; }
  function shortDate(date = new Date()) { return new Intl.DateTimeFormat("pt-BR", { day: "2-digit", month: "short" }).format(date).replace(".", ""); }
  function stateOf(product) { if (product.quantity <= 0) return "zero"; if (product.quantity <= product.minimum) return "low"; return "ok"; }
  function stateLabel(state) { return ({ zero: "Zerado", low: "Baixo", ok: "Estoque OK" })[state]; }
  function counts() { return { all: products.length, zero: products.filter(p => stateOf(p) === "zero").length, low: products.filter(p => stateOf(p) === "low").length, ok: products.filter(p => stateOf(p) === "ok").length }; }
  function escapeHTML(value) { return String(value).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]); }
  function showToast(message) { const toast = $("#toast"); toast.textContent = message; toast.classList.add("show"); clearTimeout(toastTimer); toastTimer = setTimeout(() => toast.classList.remove("show"), 2800); }

  async function api(path, options = {}) {
    const response = await fetch(path, {
      ...options,
      headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(body.error || "Não foi possível concluir a operação.");
    return body;
  }

  async function refreshProducts() {
    products = await api("/api/products");
    populateSelect();
    renderHome();
    renderStock();
  }

  function navigate(screenName, filter) {
    const target = $(`#screen-${screenName}`);
    if (!target) return;
    $$(".screen").forEach(screen => screen.classList.toggle("active", screen === target));
    $$(".nav-item").forEach(item => {
      const active = item.dataset.screen === screenName;
      item.classList.toggle("active", active);
      if (active) item.setAttribute("aria-current", "page"); else item.removeAttribute("aria-current");
    });
    if (screenName === "stock") { if (filter) setFilter(filter); renderStock(); }
    if (screenName === "entry") populateSelect();
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function setFilter(filter) {
    activeFilter = filter;
    $$(".filter-tab").forEach(button => {
      const active = button.dataset.filter === filter;
      button.classList.toggle("active", active);
      button.setAttribute("aria-pressed", String(active));
    });
  }

  function renderHome() {
    const c = counts();
    const attention = c.zero + c.low;
    $("#stat-products").textContent = c.all;
    $("#stat-low").textContent = attention;
    $("#stat-zero").textContent = c.zero;
    $("#missing-copy").textContent = `${attention} ${attention === 1 ? "produto precisa" : "produtos precisam"} de atenção`;
  }

  function renderStock() {
    const c = counts();
    const attention = c.zero + c.low;
    $("#count-all").textContent = c.all;
    $("#count-zero").textContent = c.zero;
    $("#count-low").textContent = attention;
    $("#count-ok").textContent = c.ok;
    $("#alert-title").textContent = `${attention} ${attention === 1 ? "produto precisa" : "produtos precisam"} de reposição`;
    $("#alert-description").textContent = `${c.zero} ${c.zero === 1 ? "produto está zerado" : "produtos estão zerados"} e ${c.low} ${c.low === 1 ? "está com estoque baixo" : "estão com estoque baixo"}.`;
    $("#stock-alert").hidden = attention === 0;
    const query = $("#stock-search").value.trim().toLocaleLowerCase("pt-BR");
    let filtered = products.filter(p => p.name.toLocaleLowerCase("pt-BR").includes(query));
    if (activeFilter === "zero") filtered = filtered.filter(p => stateOf(p) === "zero");
    if (activeFilter === "low") filtered = filtered.filter(p => stateOf(p) === "low" || stateOf(p) === "zero");
    if (activeFilter === "ok") filtered = filtered.filter(p => stateOf(p) === "ok");
    const labels = { all: "Todos os produtos", zero: "Produtos zerados", low: "Produtos para reposição", ok: "Estoque normal" };
    $("#list-heading-title").textContent = labels[activeFilter];
    $("#list-count").textContent = `${filtered.length} ${filtered.length === 1 ? "item" : "itens"}`;
    $("#stock-list").innerHTML = filtered.map(p => {
      const state = stateOf(p);
      return `<article class="product-card is-${state}"><span class="product-avatar" aria-hidden="true">${escapeHTML(p.emoji || "📦")}</span><div class="product-info"><strong>${escapeHTML(p.name)}</strong><small>Estoque mínimo: ${Number(p.minimum)} un.</small><span class="status-pill ${state}">${stateLabel(state)}</span></div><div class="product-quantity"><strong>${Number(p.quantity)}</strong><small>unidades</small></div></article>`;
    }).join("");
    $("#empty-state").hidden = filtered.length > 0;
    $("#stock-list").hidden = filtered.length === 0;
    renderHome();
  }

  function populateSelect() {
    const select = $("#product-select");
    if (!select) return;
    const current = select.value;
    select.innerHTML = '<option value="">Selecione um produto</option>' + products.slice().sort((a, b) => a.name.localeCompare(b.name, "pt-BR")).map(p => `<option value="${p.id}">${escapeHTML(p.name)}</option>`).join("");
    if (products.some(p => String(p.id) === current)) select.value = current;
  }

  function updateTotal() {
    const q = Number($("#quantity").value), cost = Number($("#unit-cost").value);
    const valid = Number.isFinite(q) && q > 0 && Number.isFinite(cost) && cost > 0;
    $("#entry-total").textContent = money(valid ? q * cost : 0);
    $("#total-detail").textContent = valid ? `${q} unidade(s) × ${money(cost)}` : "Informe quantidade e custo unitário";
  }

  async function submitEntry(event) {
    event.preventDefault();
    const error = $("#entry-error");
    error.hidden = true;
    const productId = Number($("#product-select").value);
    const quantity = Number($("#quantity").value);
    const unitCost = Number($("#unit-cost").value);
    const date = $("#entry-date").value;
    let message = "";
    if (!productId) message = "Selecione um produto para continuar.";
    else if (!Number.isInteger(quantity) || quantity <= 0) message = "Informe uma quantidade inteira maior que zero.";
    else if (!Number.isFinite(unitCost) || unitCost <= 0) message = "Informe um custo unitário maior que zero.";
    else if (!date) message = "Informe a data da entrada.";
    if (message) { error.textContent = message; error.hidden = false; return; }

    const submitButton = $("#entry-form button[type='submit']");
    submitButton.disabled = true;
    try {
      const result = await api("/api/movements", {
        method: "POST",
        body: JSON.stringify({
          productId, type: "ENTRADA", quantity, unitCost, date,
          supplier: $("#supplier").value.trim(), unit: $("#unit").value,
          notes: $("#notes").value.trim(),
        }),
      });
      await refreshProducts();
      const updated = result.product;
      $("#success-message").textContent = `${quantity} unidade(s) de ${updated.name} adicionadas ao estoque. Novo saldo: ${updated.quantity} unidade(s).`;
      const dialog = $("#success-dialog");
      if (typeof dialog.showModal === "function") dialog.showModal(); else showToast("Entrada registrada e estoque atualizado.");
      $("#entry-form").reset();
      $("#entry-date").value = localDateValue();
      updateTotal();
    } catch (err) {
      error.textContent = err.message || "Não foi possível registrar a entrada. Confira se o backend está em execução.";
      error.hidden = false;
    } finally {
      submitButton.disabled = false;
    }
  }

  async function resetDemo() {
    if (!window.confirm("Deseja restaurar os dados iniciais de demonstração? As movimentações registradas no banco serão apagadas.")) return;
    try {
      await api("/api/reset-demo", { method: "POST", body: JSON.stringify({}) });
      $("#stock-search").value = "";
      setFilter("all");
      await refreshProducts();
      navigate("home");
      showToast("Dados de demonstração restaurados.");
    } catch (err) {
      showToast(err.message || "Não foi possível restaurar os dados.");
    }
  }

  async function init() {
    $("#today-label").textContent = shortDate();
    $("#entry-date").value = localDateValue();
    $$('[data-screen]').forEach(button => button.addEventListener("click", event => {
      if (button.matches("a")) event.preventDefault();
      navigate(button.dataset.screen, button.dataset.filter);
    }));
    $$(".filter-tab").forEach(button => button.addEventListener("click", () => { setFilter(button.dataset.filter); renderStock(); }));
    $("#stock-search").addEventListener("input", renderStock);
    $("#entry-form").addEventListener("submit", submitEntry);
    $("#quantity").addEventListener("input", updateTotal);
    $("#unit-cost").addEventListener("input", updateTotal);
    $("#reset-demo").addEventListener("click", resetDemo);
    $("#success-view-stock").addEventListener("click", () => { $("#success-dialog").close(); $("#stock-search").value = ""; setFilter("all"); navigate("stock"); });
    $("#success-close").addEventListener("click", () => { $("#success-dialog").close(); navigate("home"); });
    try {
      await refreshProducts();
    } catch (err) {
      showToast("Backend indisponível. Execute 'python app.py' e abra http://127.0.0.1:5000.");
      $("#entry-error").textContent = "Não foi possível conectar ao backend. Execute o servidor Flask e recarregue a página.";
    }
  }

  document.addEventListener("DOMContentLoaded", init);
})();
