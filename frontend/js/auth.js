// ===== AUTH MODULE =====

const AUTH_KEYS = {
  TOKEN: 'rd_token',
  ROLE:  'rd_role',
  USER:  'rd_user',
};

// ===== HELPERS =====
function getToken() { return localStorage.getItem(AUTH_KEYS.TOKEN); }
function getRole()  { return localStorage.getItem(AUTH_KEYS.ROLE); }
function getUser()  { const u = localStorage.getItem(AUTH_KEYS.USER); return u ? JSON.parse(u) : null; }

function setAuth(token, role, user) {
  localStorage.setItem(AUTH_KEYS.TOKEN, token);
  localStorage.setItem(AUTH_KEYS.ROLE, role);
  localStorage.setItem(AUTH_KEYS.USER, JSON.stringify(user));
}

function clearAuth() {
  localStorage.removeItem(AUTH_KEYS.TOKEN);
  localStorage.removeItem(AUTH_KEYS.ROLE);
  localStorage.removeItem(AUTH_KEYS.USER);
}

function isAuthenticated() { return !!getToken(); }

function getBasePath() {
  return window.location.pathname.includes('/pages/') ? '../' : '';
}

function redirectToLogin() {
  window.location.href = getBasePath() + 'index.html';
}

function redirectToDashboard(role) {

  const inPages = window.location.pathname.includes('/pages/');

  // already inside /pages/
  if (inPages) {

    if (role === 'admin') {
      window.location.href = 'admin.html';
    }
    else if (role === 'agent') {
      window.location.href = 'agent.html';
    }
    else {
      window.location.href = 'dashboard.html';
    }

  } 
  
  // from root index.html
  else {

    if (role === 'admin') {
      window.location.href = 'pages/admin.html';
    }
    else if (role === 'agent') {
      window.location.href = 'pages/agent.html';
    }
    else {
      window.location.href = 'pages/dashboard.html';
    }

  }
}
function requireAuth() {
  if (!isAuthenticated()) { redirectToLogin(); return false; }
  return true;
}

function redirectIfLoggedIn() {
  if (isAuthenticated()) { redirectToDashboard(getRole()); return true; }
  return false;
}

function logout() { clearAuth(); redirectToLogin(); }

// ===== LOGIN HANDLER =====
// POST /api/auth/login  body: { phone, password }
async function handleLogin(event) {
  event.preventDefault();
  const form = event.target;
  const btn  = form.querySelector('[type=submit]');
  const phone = form.querySelector('#login-phone')?.value.trim();
  const email = form.querySelector('#login-email')?.value.trim();
  const password = form.querySelector('#login-password').value;

  if ((!phone && !email) || !password) {
  showToast('error', 'Missing Fields', 'Enter phone or email and password.');
  return;
}

  setButtonLoading(btn, true, 'Signing in...');

  try {
    // Real API call: POST /api/auth/login
    const data = await API.login(phone, email, password);

    // Backend returns a JWT token string directly
    const token = typeof data === 'string' ? data : (data.access_token || data.token);

    // Decode role from JWT payload (base64 middle segment)
    let role = 'user';
    let userObj = { phone };
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      role = payload.role || payload.user_role || 'user';
     userObj = {
  id: payload.sub || payload.id,
  name: payload.name || email || phone,
  phone,
  email,
  role
};
    } catch (_) {
      // If decode fails, use mock role map for demo
      const mockRoles = { '9876540001': 'user', '9876540002': 'admin', '9876540003': 'agent' };
      role = mockRoles[phone] || 'user';
      userObj = { name: phone, phone, role };
    }

    setAuth(token, role, userObj);
    showToast('success', 'Welcome back!', 'Redirecting to your dashboard...');
    setTimeout(() => redirectToDashboard(role), 1000);

  } catch (err) {
    // Fallback to mock for demo
    const mockRoles = { '9876540001': 'user', '9876540002': 'admin', '9876540003': 'agent' };
    const identifier = phone || email;
   if (mockRoles[identifier] && password === 'demo123') {
      const role = mockRoles[phone];
      const mockUser = { name: 'Demo User', phone, role };
      setAuth('mock_jwt_' + Date.now(), role, mockUser);
      showToast('success', 'Demo Login', 'Redirecting...');
      setTimeout(() => redirectToDashboard(role), 1000);
    } else {
      showToast('error', 'Login Failed', err.message || 'Invalid credentials.');
      setButtonLoading(btn, false);
    }
  }
}

// ===== REGISTER HANDLER =====
// POST /api/auth/register  body: { name, phone, password, role }
async function handleRegister(event) {
  event.preventDefault();

  const form = event.target;
  const btn = form.querySelector('[type=submit]');

  const name = form.querySelector('#reg-name').value.trim();
  const email = form.querySelector('#reg-email').value.trim();
  const phone = form.querySelector('#reg-phone').value.trim();
  const password = form.querySelector('#reg-password').value;
  const confirmPassword = form.querySelector('#reg-confirm').value;

  const selectedRole = document.querySelector('input[name="role"]:checked')?.value;

  const roleMap = {
    user: "user",
    admin: "admin",
    agent: "agent"
  };

  const finalRole = roleMap[selectedRole] || "user";

  if (!name || !phone || !password || !finalRole) {
    showToast('error', 'Missing Fields', 'Please fill all required fields.');
    return;
  }

  if (password !== confirmPassword) {
    showToast('error', 'Password Mismatch', 'Passwords do not match.');
    return;
  }

  setButtonLoading(btn, true, 'Creating account...');

  try {

  await API.register(name, email, phone, password, finalRole);

  showToast(
    'success',
    'Registration Successful 🎉',
    'Please verify your email before login.'
  );

  form.reset();

  setTimeout(() => {
    window.location.href = '../index.html';
  }, 2000);

} catch (err) {

  showToast('error', 'Registration Failed', err.message);

  setButtonLoading(btn, false);
}
}

// ===== INIT USER UI (Sidebar / Topbar) =====
function initUserUI() {
  const user = getUser();
  if (!user) return;

  document.querySelectorAll('.user-avatar').forEach(el => {
    el.textContent = (user.name || 'U').charAt(0).toUpperCase();
  });
  document.querySelectorAll('.user-name').forEach(el => {
    el.textContent = user.name || 'User';
  });
  document.querySelectorAll('.user-role').forEach(el => {
    el.textContent = capitalize(user.role || 'user');
  });

  document.querySelectorAll('.logout-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      if (confirm('Are you sure you want to logout?')) logout();
    });
  });
}
