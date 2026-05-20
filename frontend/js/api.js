// ===== API CONFIGURATION =====
const API_BASE = "https://ai-based-rural-delivery-management-system.onrender.com";

// ===== API ENDPOINTS (matched exactly to FastAPI backend) =====
const ENDPOINTS = {
  // Auth
  REGISTER:         `${API_BASE}/api/auth/register`,
  LOGIN:            `${API_BASE}/api/auth/login`,

  // Forgot Password
  FORGOT_PASSWORD: `${API_BASE}/api/auth/forgot-password`,
  VERIFY_OTP:      `${API_BASE}/api/auth/verify-otp`,
  RESET_PASSWORD: `${API_BASE}/api/auth/reset-password`,
  
  // Orders
  ORDER_CREATE:     `${API_BASE}/api/orders/create`,
  ORDERS_ALL:       `${API_BASE}/api/orders/all`,
  ORDERS_MY:        `${API_BASE}/api/orders/my`,
  OPTIMIZE_ROUTE:   `${API_BASE}/api/orders/optimize-route`,
  HUBS:             `${API_BASE}/api/orders/hubs`,
  AGENTS:           `${API_BASE}/api/orders/agents`,
  DASHBOARD_ADMIN:  `${API_BASE}/api/orders/dashboard/admin`,
  DASHBOARD_AGENT:  `${API_BASE}/api/orders/dashboard/agent`,

  // Hubs
  HUB_ADD:          `${API_BASE}/api/hubs/add`,
  HUBS_LIST:        `${API_BASE}/api/hubs/`,

  // Delivery
  DELIVERY_ASSIGN:  `${API_BASE}/api/delivery/assign`,
  DELIVERY_MY:      `${API_BASE}/api/delivery/my`,
  DELIVERY_MARK_DELIVERED: (id) => `${API_BASE}/api/delivery/${id}/delivered`,

  // ML
  ML_AUTO_ASSIGN:   `${API_BASE}/api/ml/auto-assign`,
  ML_PREDICT: `${API_BASE}/api/ml/predict-demand`,

};

// ===== REQUEST HELPER =====
async function apiRequest(url, method = 'GET', body = null, requiresAuth = true) {
  const headers = { 'Content-Type': 'application/json' };

  if (requiresAuth) {
  const token = localStorage.getItem('rd_token');
  if (!token) {
    clearAuth();
    redirectToLogin();
    return;
  }
  headers['Authorization'] = `Bearer ${token}`;
}
  const config = { method, headers };
  if (body && method !== 'GET') {
    config.body = JSON.stringify(body);
  }

  try {
    const response = await fetch(url, config);

    const text = await response.text();
    console.log("🔥 RAW RESPONSE:", text);

    let data;
    try {
      data = JSON.parse(text);
    } catch (e) {
      data = { message: text };
    }

    if (response.status === 401) {
      clearAuth();
      redirectToLogin();
      return;
    }

    if (!response.ok) {
      console.log("❌ ERROR DATA:", data);

      throw new Error(
        data.detail?.[0]?.msg ||
        data.detail ||
        data.message ||
        JSON.stringify(data)
      );
    }

    return data;

  } catch (error) {
    if (error.name === 'TypeError') {
      throw new Error('Network error. Please check backend server.');
    }
    throw error;
  }
}
// ===== API METHODS =====
const API = {

  // --- AUTH ---
  // POST /api/auth/register  body: { name, phone, password, role }
  async register(name, email, phone, password, role) {
  const mappedRole = role === "customer" ? "user" : role;

  return apiRequest(ENDPOINTS.REGISTER, 'POST', {
    name,
    email,   
    phone,
    password,
    role: mappedRole
  }, false);
},

  // POST /api/auth/login  body: { phone, password }
  async login(phone, email, password) {
  return apiRequest(ENDPOINTS.LOGIN, 'POST', {
    phone,
    email,
    password
  }, false);
},

  // ===== FORGOT PASSWORD =====

// POST /api/auth/forgot-password
async forgotPassword(data) {
  return apiRequest(
    ENDPOINTS.FORGOT_PASSWORD,
    'POST',
    data,
    false
  );
},

// POST /api/auth/verify-otp
async verifyOTP(data) {
  return apiRequest(
    ENDPOINTS.VERIFY_OTP,
    'POST',
    data,
    false
  );
},

// POST /api/auth/reset-password
async resetPassword(data) {
  return apiRequest(
    ENDPOINTS.RESET_PASSWORD,
    'POST',
    data,
    false
  );
},
  // --- ORDERS ---
  // POST /api/orders/create  body: { receiver, phone, package_type, weight, address, latitude, longitude }
  async createOrder(orderData) {
    return apiRequest(ENDPOINTS.ORDER_CREATE, 'POST', orderData);
  },

  // GET /api/orders/all
  async getAllOrders() {
    return apiRequest(ENDPOINTS.ORDERS_ALL);
  },

  // GET /api/orders/my
  async getMyOrders() {
    return apiRequest(ENDPOINTS.ORDERS_MY);
  },

  // GET /api/orders/optimize-route
  async optimizeRoute() {
    return apiRequest(ENDPOINTS.OPTIMIZE_ROUTE);
  },

  // GET /api/orders/agents
  async getOrderAgents() {
    return apiRequest(ENDPOINTS.AGENTS);
  },

  // GET /api/orders/dashboard/admin
  async getAdminDashboard() {
    return apiRequest(ENDPOINTS.DASHBOARD_ADMIN);
  },

  // GET /api/orders/dashboard/agent
  async getAgentDashboard() {
    return apiRequest(ENDPOINTS.DASHBOARD_AGENT);
  },

  // --- HUBS ---
  // POST /api/hubs/add  body: { name, latitude, longitude }
  async addHub(name, latitude, longitude) {
    return apiRequest(ENDPOINTS.HUB_ADD, 'POST', { name, latitude, longitude });
  },

  // GET /api/hubs/
  async getHubs() {
    return apiRequest(ENDPOINTS.HUBS_LIST);
  },

  // --- DELIVERY ---
  // POST /api/delivery/assign  body: { order_id, agent_id }
  async assignDelivery(order_id, agent_id) {
    return apiRequest(ENDPOINTS.DELIVERY_ASSIGN, 'POST', { order_id, agent_id });
  },

  // GET /api/delivery/my
  async getMyDeliveries() {
    return apiRequest(ENDPOINTS.DELIVERY_MY);
  },

  // PUT /api/delivery/{id}/delivered
  async markDelivered(id) {
    return apiRequest(ENDPOINTS.DELIVERY_MARK_DELIVERED(id), 'PUT');
  },

  // --- ML ---
  // POST /api/ml/auto-assign
  async mlAutoAssign() {
    return apiRequest(ENDPOINTS.ML_AUTO_ASSIGN, 'POST');
  },

  // POST /api/ml/predict-demand
  async mlPredictDemand() {
    return apiRequest(ENDPOINTS.ML_PREDICT, 'POST');
  },

  async getAgentLocations() {
  return apiRequest(`${API_BASE}/api/tracking/all`);
}
};

// ===== MOCK DATA (fallback for demo when backend unavailable) =====
const MOCK = {
  orders: [
    { id: 1, receiver: 'Ramesh Kumar', phone: '9876540010', address: 'Village Rampur, Dist. Sagar, MP', package_type: 'General', weight: 2.5, latitude: 23.8388, longitude: 78.7378, status: 'delivered', agent_id: 1, created_at: '2024-01-15' },
    { id: 2, receiver: 'Sunita Devi',  phone: '9876540011', address: 'Gram Panchayat Khurai, Sagar',    package_type: 'Medicine', weight: 1.2, latitude: 23.7800, longitude: 78.7200, status: 'pending',   agent_id: null, created_at: '2024-01-16' },
    { id: 3, receiver: 'Mohan Lal',   phone: '9876540012', address: 'Kerai Village, Banda Road, MP',   package_type: 'Fragile', weight: 4.0, latitude: 23.9000, longitude: 78.8100, status: 'assigned',  agent_id: 2, created_at: '2024-01-17' },
    { id: 4, receiver: 'Priya Sharma',phone: '9876540013', address: 'Rehli Town, Sagar District',      package_type: 'General', weight: 0.8, latitude: 23.6500, longitude: 78.5800, status: 'pending',   agent_id: null, created_at: '2024-01-18' },
    { id: 5, receiver: 'Vijay Rao',   phone: '9876540014', address: 'Malthon, Sagar, MP',              package_type: 'General', weight: 3.1, latitude: 24.0100, longitude: 78.9200, status: 'assigned',  agent_id: 1, created_at: '2024-01-19' },
  ],
  hubs: [
    { id: 1, name: 'Hub Alpha', latitude: 23.8388, longitude: 78.7378 },
    { id: 2, name: 'Hub Beta',  latitude: 23.7800, longitude: 78.7200 },
    { id: 3, name: 'Hub Gamma', latitude: 23.9000, longitude: 78.8100 },
    { id: 4, name: 'Hub Delta', latitude: 24.0100, longitude: 78.9200 },
  ],
  agents: [
    { id: 1, name: 'Suresh Patel',  phone: '9876543210', deliveries: 14, is_active: true },
    { id: 2, name: 'Amit Singh',    phone: '9876543211', deliveries: 9,  is_active: true },
    { id: 3, name: 'Rajesh Meena', phone: '9876543212', deliveries: 7,  is_active: false },
  ],
  adminDashboard: { total_orders: 127, pending: 23, assigned: 18, delivered: 86, total_hubs: 4, total_agents: 3 },
  agentDashboard: { assigned: 3, delivered: 14, success_rate: '82%' },
};

if (typeof module !== 'undefined') module.exports = { API, MOCK, ENDPOINTS };
