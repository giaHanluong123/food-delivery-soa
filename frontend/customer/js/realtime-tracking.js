const WS_BASE_URL = "ws://localhost:8000";
const API_BASE_URL = "http://localhost:8000";
const CHECKOUT_REDIRECT_PENDING_KEY = "customer_checkout_redirect_pending";
const LAST_ORDER_STORAGE_KEY = "customer_last_order";

const connectBtn = document.getElementById("connectBtn");
const disconnectBtn = document.getElementById("disconnectBtn");
const clearLogBtn = document.getElementById("clearLogBtn");
const paymentPaidBtn = document.getElementById("paymentPaidBtn");
const paymentFailedBtn = document.getElementById("paymentFailedBtn");

const orderIdInput = document.getElementById("orderIdInput");
const connectionStatus = document.getElementById("connectionStatus");
const currentOrderId = document.getElementById("currentOrderId");
const currentPaymentId = document.getElementById("currentPaymentId");
const currentUserId = document.getElementById("currentUserId");
const currentOrderStatus = document.getElementById("currentOrderStatus");
const lastEventType = document.getElementById("lastEventType");
const timelineList = document.getElementById("timelineList");
const eventLog = document.getElementById("eventLog");

let socket = null;
let activeOrderId = null;

let manualDisconnect = false;
let reconnectAttempt = 0;
let reconnectTimer = null;

let heartbeatInterval = null;
let lastPongAt = null;

let activePaymentId = null;
let activeUserId = null;

const HEARTBEAT_INTERVAL_MS = 15000;
const HEARTBEAT_TIMEOUT_MS = 30000;
const RECONNECT_DELAY_MS = 3000;
const MAX_RECONNECT_ATTEMPTS = 10;

function getQueryParam(name) {
  const params = new URLSearchParams(window.location.search);
  return params.get(name);
}

function safeParseJson(rawValue) {
  try {
    return JSON.parse(rawValue);
  } catch {
    return null;
  }
}

function getLastOrderFromStorage() {
  const raw = localStorage.getItem(LAST_ORDER_STORAGE_KEY);
  if (!raw) {
    return null;
  }
  return safeParseJson(raw);
}

function clearCustomerCartAfterSuccessfulRedirect() {
  try {
    localStorage.removeItem("customer_demo_cart");
  } catch (error) {
    console.error("Không clear được customer_demo_cart:", error);
  }
}

function setConnectionStatus(text, typeClass) {
  connectionStatus.textContent = text;
  connectionStatus.className = `badge ${typeClass}`;
}

function appendLog(title, payload) {
  const line = document.createElement("div");
  line.className = "event-log-line";

  const now = new Date().toLocaleString("vi-VN");
  const body = typeof payload === "string" ? payload : JSON.stringify(payload, null, 2);

  line.textContent = `[${now}] ${title}\n${body}`;
  eventLog.prepend(line);
}

function addTimelineItem(event) {
  const item = document.createElement("li");
  item.className = "timeline-item";

  const eventType = event.event_type || "unknown_event";
  const message = event.message || "Không có message";
  const status = event.status || "-";
  const sourceService = event.source_service || "-";
  const now = new Date().toLocaleString("vi-VN");

  item.innerHTML = `
    <div class="event-type">${eventType}</div>
    <div class="message">${message}</div>
    <div class="meta">
      status: ${status} | source: ${sourceService} | time: ${now}
    </div>
  `;

  timelineList.prepend(item);
}

function updateSummary(event) {
  currentOrderStatus.textContent = event.status || "-";
  lastEventType.textContent = event.event_type || "-";
}

function handleRealtimeEvent(event) {
  appendLog("Realtime event received", event);

  if (event.event_type === "pong") {
    lastPongAt = Date.now();
    return;
  }

  addTimelineItem(event);
  updateSummary(event);
}

function clearReconnectTimer() {
  if (reconnectTimer) {
    clearTimeout(reconnectTimer);
    reconnectTimer = null;
  }
}

function stopHeartbeat() {
  if (heartbeatInterval) {
    clearInterval(heartbeatInterval);
    heartbeatInterval = null;
  }
}

function startHeartbeat() {
  stopHeartbeat();
  lastPongAt = Date.now();

  heartbeatInterval = setInterval(() => {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      return;
    }

    const now = Date.now();

    if (lastPongAt && now - lastPongAt > HEARTBEAT_TIMEOUT_MS) {
      appendLog("Heartbeat timeout", {
        message: "Không nhận được pong từ server, sẽ đóng socket để reconnect"
      });
      socket.close();
      return;
    }

    try {
      socket.send("ping");
      appendLog("Heartbeat ping", {
        order_id: activeOrderId
      });
    } catch (error) {
      appendLog("Heartbeat send error", String(error));
    }
  }, HEARTBEAT_INTERVAL_MS);
}

function cleanupSocket() {
  stopHeartbeat();

  if (socket) {
    socket.onopen = null;
    socket.onmessage = null;
    socket.onerror = null;
    socket.onclose = null;
    socket = null;
  }
}

function scheduleReconnect() {
  if (manualDisconnect) {
    return;
  }

  if (!activeOrderId) {
    return;
  }

  if (reconnectAttempt >= MAX_RECONNECT_ATTEMPTS) {
    setConnectionStatus("Reconnect thất bại", "disconnected");
    appendLog("Reconnect stopped", {
      reason: "Đã vượt quá số lần reconnect tối đa",
      max_attempts: MAX_RECONNECT_ATTEMPTS
    });
    return;
  }

  clearReconnectTimer();

  reconnectAttempt += 1;

  setConnectionStatus(`Mất kết nối - thử lại lần ${reconnectAttempt}`, "neutral");
  appendLog("Scheduling reconnect", {
    order_id: activeOrderId,
    reconnect_attempt: reconnectAttempt,
    delay_ms: RECONNECT_DELAY_MS
  });

  reconnectTimer = setTimeout(() => {
    connectRealtime(activeOrderId, true);
  }, RECONNECT_DELAY_MS);
}

function connectRealtime(orderId, isReconnect = false) {
  if (!orderId) {
    alert("Vui lòng nhập order_id trước khi kết nối.");
    return;
  }

  manualDisconnect = false;
  clearReconnectTimer();

  if (socket) {
    cleanupSocket();
  }

  activeOrderId = String(orderId);
  currentOrderId.textContent = activeOrderId;
  orderIdInput.value = activeOrderId;

  const wsUrl = `${WS_BASE_URL}/realtime/ws/orders/${activeOrderId}`;
  socket = new WebSocket(wsUrl);

  setConnectionStatus(isReconnect ? "Đang reconnect..." : "Đang kết nối...", "neutral");
  appendLog(isReconnect ? "Reconnecting WebSocket" : "Connecting WebSocket", wsUrl);

  socket.onopen = () => {
    reconnectAttempt = 0;
    setConnectionStatus("Đã kết nối", "connected");
    appendLog("WebSocket connected", { order_id: activeOrderId });
    startHeartbeat();
  };

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      handleRealtimeEvent(data);
    } catch (error) {
      appendLog("Parse error", String(error));
    }
  };

  socket.onerror = () => {
    appendLog("WebSocket error", "Có lỗi xảy ra trong quá trình kết nối");
  };

  socket.onclose = () => {
    stopHeartbeat();
    setConnectionStatus("Đã ngắt kết nối", "disconnected");
    appendLog("WebSocket closed", { order_id: activeOrderId });

    cleanupSocket();
    scheduleReconnect();
  };
}

function disconnectRealtime() {
  manualDisconnect = true;
  clearReconnectTimer();
  stopHeartbeat();

  if (socket) {
    socket.close();
  }

  setConnectionStatus("Đã ngắt kết nối thủ công", "disconnected");
  appendLog("Manual disconnect", {
    order_id: activeOrderId
  });
}

function syncTrackingContext() {
  const lastOrder = getLastOrderFromStorage();

  const orderIdFromQuery = getQueryParam("order_id");
  const userIdFromQuery = getQueryParam("user_id");

  if (orderIdFromQuery) {
    activeOrderId = String(orderIdFromQuery);
  } else if (lastOrder?.order_id) {
    activeOrderId = String(lastOrder.order_id);
  } else {
    activeOrderId = null;
  }

  if (lastOrder?.payment_id) {
    activePaymentId = Number(lastOrder.payment_id);
  } else {
    activePaymentId = null;
  }

  if (userIdFromQuery) {
    activeUserId = Number(userIdFromQuery);
  } else if (lastOrder?.user_id) {
    activeUserId = Number(lastOrder.user_id);
  } else {
    activeUserId = null;
  }

  orderIdInput.value = activeOrderId || "";
  currentOrderId.textContent = activeOrderId || "-";
  currentPaymentId.textContent = activePaymentId || "-";
  currentUserId.textContent = activeUserId || "-";

  appendLog("Tracking context loaded", {
    order_id: activeOrderId,
    payment_id: activePaymentId,
    user_id: activeUserId,
    from_storage: lastOrder || null
  });

  // Chỉ clear cart khi chắc chắn tracking đã mở được đúng order vừa tạo
  if (
    lastOrder?.checkout_completed &&
    activeOrderId &&
    String(lastOrder.order_id) === String(activeOrderId)
  ) {
    clearCustomerCartAfterSuccessfulRedirect();
    sessionStorage.removeItem(CHECKOUT_REDIRECT_PENDING_KEY);

    appendLog("Checkout redirect finalized", {
      order_id: activeOrderId,
      action: "cart_cleared_and_pending_redirect_removed"
    });
  }
}
function validatePaymentContext() {
  if (!activeOrderId) {
    alert("Không tìm thấy order_id. Hãy quay lại checkout hoặc nhập order_id hợp lệ.");
    return false;
  }

  if (!activePaymentId) {
    alert("Không tìm thấy payment_id. Hãy tạo order từ checkout trước để frontend lưu payment_id.");
    return false;
  }

  if (!activeUserId) {
    alert("Không tìm thấy user_id. Hãy mở tracking từ flow checkout hoặc truyền user_id qua query.");
    return false;
  }

  return true;
}

async function triggerPaymentCallback(paymentStatus) {
  if (!validatePaymentContext()) {
    return;
  }

  const payload = {
    payment_id: Number(activePaymentId),
    payment_status: paymentStatus,
    gateway_transaction_id: `DEMO-TXN-${Date.now()}`,
    callback_message:
      paymentStatus === "paid"
        ? "Thanh toán thành công từ frontend tracking"
        : "Thanh toán thất bại từ frontend tracking",
    order_id: Number(activeOrderId),
    user_id: Number(activeUserId)
  };

  appendLog("Calling payment callback orchestration", payload);

  try {
    const response = await fetch(`${API_BASE_URL}/orchestrations/payment-callback`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    const rawText = await response.text();

    let data;
    try {
      data = JSON.parse(rawText);
    } catch {
      data = rawText;
    }

    appendLog("Payment callback response", data);

    if (!response.ok) {
      throw new Error(
        `Payment callback thất bại. HTTP ${response.status}. Response: ${
          typeof data === "string" ? data : JSON.stringify(data)
        }`
      );
    }

    alert(
      paymentStatus === "paid"
        ? "Đã giả lập thanh toán thành công."
        : "Đã giả lập thanh toán thất bại."
    );
  } catch (error) {
    appendLog("Payment callback error", String(error));
    alert("Có lỗi khi gọi payment callback. Xem log để biết chi tiết.");
  }
}

connectBtn.addEventListener("click", () => {
  const orderId = orderIdInput.value.trim();
  connectRealtime(orderId);
});

disconnectBtn.addEventListener("click", () => {
  disconnectRealtime();
});

clearLogBtn.addEventListener("click", () => {
  eventLog.innerHTML = "";
  timelineList.innerHTML = "";
  currentOrderStatus.textContent = "-";
  lastEventType.textContent = "-";
});

paymentPaidBtn.addEventListener("click", () => {
  triggerPaymentCallback("paid");
});

paymentFailedBtn.addEventListener("click", () => {
  triggerPaymentCallback("failed");
});

window.addEventListener("beforeunload", () => {
  manualDisconnect = true;
  clearReconnectTimer();
  stopHeartbeat();

  if (socket) {
    socket.close();
  }
});

window.addEventListener("DOMContentLoaded", () => {
  syncTrackingContext();

  if (activeOrderId) {
    connectRealtime(activeOrderId);
  } else {
    appendLog("Tracking init", {
      message: "Chưa có order_id để tự động kết nối realtime"
    });
  }
});