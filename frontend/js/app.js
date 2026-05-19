// ===== APP UTILITIES =====

// Sleep helper
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// ===== TOAST NOTIFICATIONS =====
function showToast(type = 'info', title = '', message = '', duration = 4000) {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <span class="toast-icon">${icons[type] || icons.info}</span>
    <div class="toast-content">
      <div class="toast-title">${title}</div>
      ${message ? `<div class="toast-message">${message}</div>` : ''}
    </div>
    <button class="toast-close" onclick="removeToast(this.parentElement)">×</button>
  `;
  container.appendChild(toast);

  if (duration > 0) {
    setTimeout(() => removeToast(toast), duration);
  }
  return toast;
}

function removeToast(toast) {
  if (!toast || toast.classList.contains('removing')) return;
  toast.classList.add('removing');
  setTimeout(() => toast.remove(), 250);
}

// ===== BUTTON LOADING STATE =====
function setButtonLoading(btn, loading, loadingText = 'Loading...') {
  if (!btn) return;
  if (loading) {
    btn.dataset.original = btn.innerHTML;
    btn.innerHTML = `<span class="spinner"></span> ${loadingText}`;
    btn.disabled = true;
  } else {
    btn.innerHTML = btn.dataset.original || btn.innerHTML;
    btn.disabled = false;
  }
}

// ===== SHOW/HIDE LOADING OVERLAY =====
function showLoader(message = 'Loading...') {
  let overlay = document.getElementById('loading-overlay');
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.id = 'loading-overlay';
    overlay.className = 'loading-overlay';
    overlay.innerHTML = `
      <div class="loading-box">
        <div class="big-spinner"></div>
        <p class="fw-600 text-muted">${message}</p>
      </div>
    `;
    document.body.appendChild(overlay);
  }
}

function hideLoader() {
  const overlay = document.getElementById('loading-overlay');
  if (overlay) overlay.remove();
}

// ===== STATUS BADGE =====
function statusBadge(status) {
  if (!status) return '';

  const s = status.toLowerCase(); 

  const map = {
    pending: 'badge-pending',
    assigned: 'badge-assigned',
    delivered: 'badge-delivered',
    cancelled: 'badge-cancelled',
  };

  return `<span class="badge ${map[s] || 'badge-pending'}">${capitalize(s)}</span>`;
}

// ===== CAPITALIZE =====
function capitalize(str) {
  return str ? str.charAt(0).toUpperCase() + str.slice(1) : '';
}

// ===== FORMAT DATE =====
function formatDate(dateStr) {
  if (!dateStr) return 'N/A';
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
}

// ===== SIDEBAR TOGGLE =====
function initSidebar() {
  const sidebar = document.querySelector('.sidebar');
  const hamburger = document.querySelector('.hamburger');
  if (!sidebar || !hamburger) return;

  let overlay = document.querySelector('.sidebar-overlay');
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.className = 'sidebar-overlay';
    document.body.appendChild(overlay);
  }

  hamburger.addEventListener('click', () => {
    sidebar.classList.toggle('open');
    overlay.classList.toggle('active');
  });

  overlay.addEventListener('click', () => {
    sidebar.classList.remove('open');
    overlay.classList.remove('active');
  });
}

// ===== MODAL HELPERS =====
function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (!modal) return;
  document.body.appendChild(modal);
  modal.style.display = 'flex';
  modal.classList.remove('d-none');
  document.body.style.overflow = 'hidden';
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (!modal) return;
  modal.style.display = 'none';
  document.body.style.overflow = '';
}

// Close modal on overlay click
document.addEventListener('click', (e) => {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.style.display = 'none';
    document.body.style.overflow = '';
  }
});

// ===== TAB SYSTEM =====
function initTabs() {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const tabGroup = btn.closest('[data-tabs]')?.dataset.tabs || btn.dataset.tab;
      const targetId = btn.dataset.target;

      // Toggle buttons
      btn.closest('.tabs').querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      // Toggle content
      document.querySelectorAll('.tab-content').forEach(content => {
        if (content.dataset.tab === targetId) {
          content.classList.add('active');
        } else {
          content.classList.remove('active');
        }
      });
    });
  });
}

// ===== ACTIVE NAV ITEM =====
function setActiveNav() {
  const currentPage = window.location.pathname.split('/').pop();
  document.querySelectorAll('.nav-item[data-page]').forEach(item => {
    if (item.dataset.page === currentPage) {
      item.classList.add('active');
    }
  });
}

// ===== GENERATE ORDER CARD HTML =====
function generateOrderCard(order, role = 'user') {
  const actions = {
    user: `<span class="text-muted text-small">${formatDate(order.created)}</span>`,
    admin: `
      <button class="btn btn-sm btn-outline" onclick="openAssignModal('${order.id}')">Assign</button>
    `,
    agent: order.status === 'assigned' ? `
      <button class="btn btn-sm btn-secondary" onclick="markDelivered('${order.id}', this)">Mark Delivered</button>
    ` : `<span class="text-muted text-small">${statusBadge(order.status)}</span>`,
  };

  return `
    <div class="order-card" id="order-${order.id}">
      <div class="order-card-header">
        <span class="order-id">#${order.id}</span>
        ${statusBadge(order.status)}
      </div>
      <div class="order-card-body">
        <div class="order-detail">
          <span class="order-detail-icon">👤</span>
          <span class="order-detail-text fw-600">${order.customer}</span>
        </div>
        <div class="order-detail">
          <span class="order-detail-icon">📍</span>
          <span class="order-detail-text">${order.address}</span>
        </div>
        <div class="order-detail">
          <span class="order-detail-icon">🏭</span>
          <span class="order-detail-text">${order.hub}</span>
        </div>
        <div class="order-detail">
          <span class="order-detail-icon">⚖️</span>
          <span class="order-detail-text">${order.weight}</span>
        </div>
        ${order.agent ? `<div class="order-detail"><span class="order-detail-icon">🚴</span><span class="order-detail-text">${order.agent}</span></div>` : ''}
      </div>
      <div class="order-card-footer">
        ${actions[role] || actions.user}
      </div>
    </div>
  `;
}

// ===== GENERATE TABLE ROW HTML (Admin) =====
function generateOrderRow(order, agents = []) {
  const agentOptions = agents.map(a => `<option value="${a.id}">${a.name}</option>`).join('');
  return `
    <tr id="row-${order.id}">
      <td><span class="order-id">#${order.id}</span></td>
      <td class="fw-600">${order.customer}</td>
      <td>${order.address}</td>
      <td>${order.hub}</td>
      <td>${statusBadge(order.status)}</td>
      <td>${order.agent || '<span class="text-muted">Unassigned</span>'}</td>
      <td>${formatDate(order.created)}</td>
      <td>
        <div class="d-flex gap-1">
          ${order.status === 'pending' ? `<button class="btn btn-sm btn-outline" onclick="openAssignModal('${order.id}')">Assign</button>` : ''}
          <button class="btn btn-sm btn-ghost" onclick="viewOrder('${order.id}')">View</button>
        </div>
      </td>
    </tr>
  `;
}

// ===== SEARCH / FILTER ORDERS =====
function filterOrders(orders, query) {
  const q = query.toLowerCase();

  return orders.filter(o =>
    String(o.id).toLowerCase().includes(q) ||  
    (o.customer || '').toLowerCase().includes(q) ||
    (o.address || '').toLowerCase().includes(q) ||
    (o.status || '').toLowerCase().includes(q)
  );
}

// ===== SIDEBAR TEMPLATE =====
function getSidebarHTML(role) {
  const navByRole = {
    user: `
      <a class="nav-item" href="dashboard.html" data-page="dashboard.html">
        <span class="nav-icon">📦</span> My Orders
      </a>
      <a class="nav-item" href="order.html" data-page="order.html">
        <span class="nav-icon">➕</span> New Order
      </a>
    `,
    admin: `
  <a class="nav-item" href="admin.html" data-page="admin.html">
    <span class="nav-icon">📊</span> Dashboard
  </a>

  <a class="nav-item" id="admin-orders-btn">
    <span class="nav-icon">📦</span> All Orders
  </a>
`,
    agent: `
      <a class="nav-item" href="agent.html" data-page="agent.html">
        <span class="nav-icon">🚴</span> My Deliveries
      </a>
    `,
  };

  return `
    <div class="sidebar-logo">
      <div class="logo-icon">🚚</div>
      <div class="logo-text">RuralDeliver <span>Smart Logistics</span></div>
    </div>
    <nav class="sidebar-nav">
      <span class="nav-section-label">Navigation</span>
      ${navByRole[role] || navByRole.user}
    </nav>
    <div class="sidebar-footer">
      <div class="user-info">
        <div class="user-avatar">U</div>
        <div class="user-details">
          <div class="user-name">Loading...</div>
          <div class="user-role">${role}</div>
        </div>
      </div>
      <button class="btn btn-ghost btn-block logout-btn">
        🚪 Logout
      </button>
    </div>
  `;
}

// ===== TOPBAR TEMPLATE =====
function getTopbarHTML(pageTitle) {
  return `
    <div class="topbar-left">
      <button class="hamburger">☰</button>
      <h1 class="page-title">${pageTitle}</h1>
    </div>
    <div class="topbar-right">
      <div class="user-avatar" style="width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,#2563EB,#10B981);display:flex;align-items:center;justify-content:center;font-size:.875rem;font-weight:600;color:white;">U</div>
    </div>
  `;
}

// ===== INIT ALL =====
function initApp(role, pageTitle) {
  requireAuth();

  // Inject sidebar & topbar
  const sidebar = document.querySelector('.sidebar');
  const topbar = document.querySelector('.topbar');
  if (sidebar) sidebar.innerHTML = getSidebarHTML(role);
  if (topbar) topbar.innerHTML = getTopbarHTML(pageTitle);

  initUserUI();
  initSidebar();
  initTabs();
  setActiveNav();
}