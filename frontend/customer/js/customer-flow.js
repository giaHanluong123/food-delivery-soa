const CORE_API_BASE_URL = "http://localhost:8001";
const LAST_ORDER_STORAGE_KEY = "customer_last_order";
const CHECKOUT_REDIRECT_PENDING_KEY = "customer_checkout_redirect_pending";
const CHECKOUT_REDIRECT_TTL_MS = 30000;

function setPendingCheckoutRedirect(data) {
  sessionStorage.setItem(
    CHECKOUT_REDIRECT_PENDING_KEY,
    JSON.stringify({
      ...data,
      created_at_ms: Date.now()
    })
  );
}

function getPendingCheckoutRedirect() {
  try {
    const raw = sessionStorage.getItem(CHECKOUT_REDIRECT_PENDING_KEY);
    if (!raw) {
      return null;
    }

    const parsed = JSON.parse(raw);

    if (!parsed || !parsed.order_id || !parsed.user_id) {
      sessionStorage.removeItem(CHECKOUT_REDIRECT_PENDING_KEY);
      return null;
    }

    const createdAtMs = Number(parsed.created_at_ms || 0);
    const isExpired = !createdAtMs || Date.now() - createdAtMs > CHECKOUT_REDIRECT_TTL_MS;

    if (isExpired) {
      sessionStorage.removeItem(CHECKOUT_REDIRECT_PENDING_KEY);
      return null;
    }

    return parsed;
  } catch (error) {
    console.error("Không đọc được redirect pending state:", error);
    sessionStorage.removeItem(CHECKOUT_REDIRECT_PENDING_KEY);
    return null;
  }
}

function clearPendingCheckoutRedirect() {
  sessionStorage.removeItem(CHECKOUT_REDIRECT_PENDING_KEY);
}

function buildTrackingUrl(orderId, userId) {
  const targetUrl = new URL("./tracking.html", window.location.href);
  targetUrl.searchParams.set("order_id", String(orderId));
  targetUrl.searchParams.set("user_id", String(userId));
  return targetUrl.toString();
}

function redirectToTracking(orderId, userId) {
  const targetUrl = buildTrackingUrl(orderId, userId);
  window.location.assign(targetUrl);
}
const CART_STORAGE_KEY = "customer_demo_cart";

function formatCurrency(value) {
  return Number(value || 0).toLocaleString("vi-VN") + " VNĐ";
}

function getQueryParam(name) {
  const params = new URLSearchParams(window.location.search);
  return params.get(name);
}

async function fetchJson(url) {
  const response = await fetch(url, {
    method: "GET",
    headers: {
      "Content-Type": "application/json"
    }
  });

  const rawText = await response.text();

  let data;
  try {
    data = JSON.parse(rawText);
  } catch {
    data = rawText;
  }

  if (!response.ok) {
    throw new Error(`HTTP ${response.status} - ${typeof data === "string" ? data : JSON.stringify(data)}`);
  }

  return data;
}

function getCart() {
  try {
    const raw = localStorage.getItem(CART_STORAGE_KEY);
    if (!raw) {
      return {
        restaurant_id: null,
        restaurant_name: "",
        items: []
      };
    }

    const parsed = JSON.parse(raw);

    return {
      restaurant_id: parsed.restaurant_id || null,
      restaurant_name: parsed.restaurant_name || "",
      items: Array.isArray(parsed.items) ? parsed.items : []
    };
  } catch (error) {
    console.error("Không đọc được cart từ localStorage:", error);
    return {
      restaurant_id: null,
      restaurant_name: "",
      items: []
    };
  }
}

function saveCart(cart) {
  localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(cart));
}

function clearCart() {
  localStorage.removeItem(CART_STORAGE_KEY);
}

function getCartCount() {
  const cart = getCart();
  return cart.items.reduce((sum, item) => sum + Number(item.quantity || 0), 0);
}

function updateCartCountBadges() {
  const elements = document.querySelectorAll("[data-cart-count]");
  const count = getCartCount();

  elements.forEach((element) => {
    element.textContent = count;
  });
}

function addToCart(payload) {
  const cart = getCart();

  if (
    cart.restaurant_id &&
    Number(cart.restaurant_id) !== Number(payload.restaurant_id) &&
    cart.items.length > 0
  ) {
    const shouldReplace = confirm(
      "Giỏ hàng hiện đang chứa món của nhà hàng khác. Bạn có muốn xóa giỏ cũ để thêm món mới không?"
    );

    if (!shouldReplace) {
      return false;
    }

    cart.restaurant_id = null;
    cart.restaurant_name = "";
    cart.items = [];
  }

  cart.restaurant_id = Number(payload.restaurant_id);
  cart.restaurant_name = payload.restaurant_name;

  const existingItem = cart.items.find(
    (item) => Number(item.menu_item_id) === Number(payload.menu_item_id)
  );

  if (existingItem) {
    existingItem.quantity += Number(payload.quantity);
  } else {
    cart.items.push({
      menu_item_id: Number(payload.menu_item_id),
      name: payload.name,
      price: Number(payload.price),
      quantity: Number(payload.quantity)
    });
  }

  saveCart(cart);
  updateCartCountBadges();
  return true;
}

function changeCartItemQuantity(menuItemId, delta) {
  const cart = getCart();

  cart.items = cart.items
    .map((item) => {
      if (Number(item.menu_item_id) === Number(menuItemId)) {
        return {
          ...item,
          quantity: Number(item.quantity) + Number(delta)
        };
      }
      return item;
    })
    .filter((item) => item.quantity > 0);

  if (cart.items.length === 0) {
    cart.restaurant_id = null;
    cart.restaurant_name = "";
  }

  saveCart(cart);
}

function removeCartItem(menuItemId) {
  const cart = getCart();

  cart.items = cart.items.filter(
    (item) => Number(item.menu_item_id) !== Number(menuItemId)
  );

  if (cart.items.length === 0) {
    cart.restaurant_id = null;
    cart.restaurant_name = "";
  }

  saveCart(cart);
}

function calculateCartSubtotal(cart) {
  return cart.items.reduce((sum, item) => {
    return sum + Number(item.price) * Number(item.quantity);
  }, 0);
}

async function loadRestaurantsPage() {
  const restaurantList = document.getElementById("restaurantList");
  const restaurantState = document.getElementById("restaurantState");
  const keywordInput = document.getElementById("keywordInput");
  const searchBtn = document.getElementById("searchBtn");

  async function renderRestaurants(keyword = "") {
    restaurantList.innerHTML = "";
    restaurantState.textContent = "Đang tải danh sách nhà hàng...";

    try {
      const url = keyword
        ? `${CORE_API_BASE_URL}/restaurants/search?keyword=${encodeURIComponent(keyword)}`
        : `${CORE_API_BASE_URL}/restaurants/active/list`;

      const restaurants = await fetchJson(url);

      if (!Array.isArray(restaurants) || restaurants.length === 0) {
        restaurantState.textContent = "Không tìm thấy nhà hàng phù hợp.";
        return;
      }

      restaurantState.textContent = `Tìm thấy ${restaurants.length} nhà hàng.`;

      restaurants.forEach((restaurant) => {
        const card = document.createElement("div");
        card.className = "card";

        card.innerHTML = `
          <h3>${restaurant.name}</h3>
          <p>${restaurant.description || "Chưa có mô tả"}</p>
          <p>${restaurant.address_line || ""}, ${restaurant.district || ""}, ${restaurant.city || ""}</p>
          <span class="badge">Rating: ${restaurant.rating_avg ?? "-"}</span>
          <span class="badge">${restaurant.is_active ? "Đang hoạt động" : "Tạm dừng"}</span>
          <br>
          <a class="btn" href="./menu.html?restaurant_id=${restaurant.id}">Xem menu</a>
        `;

        restaurantList.appendChild(card);
      });
    } catch (error) {
      console.error(error);
      restaurantState.textContent = "Không tải được danh sách nhà hàng. Hãy kiểm tra core-service.";
    }
  }

  searchBtn.addEventListener("click", () => {
    const keyword = keywordInput.value.trim();
    renderRestaurants(keyword);
  });

  renderRestaurants();
}

async function loadMenuPage() {
  const restaurantId = getQueryParam("restaurant_id");
  const restaurantInfo = document.getElementById("restaurantInfo");
  const menuList = document.getElementById("menuList");
  const menuState = document.getElementById("menuState");

  if (!restaurantId) {
    restaurantInfo.innerHTML = `
      <div class="info-box">
        Thiếu restaurant_id. Hãy quay lại danh sách nhà hàng để chọn nhà hàng trước.
      </div>
    `;
    return;
  }

  menuState.textContent = "Đang tải menu...";

  try {
    const restaurant = await fetchJson(`${CORE_API_BASE_URL}/restaurants/${restaurantId}`);
    const menuItems = await fetchJson(`${CORE_API_BASE_URL}/restaurants/${restaurantId}/menu-items`);

    restaurantInfo.innerHTML = `
      <div class="card">
        <h3>${restaurant.name}</h3>
        <p>${restaurant.description || "Chưa có mô tả"}</p>
        <p>${restaurant.address_line || ""}, ${restaurant.district || ""}, ${restaurant.city || ""}</p>
        <span class="badge">Rating: ${restaurant.rating_avg ?? "-"}</span>
        <span class="badge">Restaurant ID: ${restaurant.id}</span>
      </div>
    `;

    menuList.innerHTML = "";

    if (!Array.isArray(menuItems) || menuItems.length === 0) {
      menuState.textContent = "Nhà hàng này hiện chưa có món nào.";
      return;
    }

    menuState.textContent = `Có ${menuItems.length} món trong menu.`;

    menuItems.forEach((item) => {
      const wrapper = document.createElement("div");
      wrapper.className = "card";

      wrapper.innerHTML = `
        <h3>${item.name}</h3>
        <p>${item.description || "Chưa có mô tả"}</p>
        <p>Giá: ${formatCurrency(item.price)}</p>
        <div class="form-group">
          <label for="qty-${item.id}">Số lượng</label>
          <input id="qty-${item.id}" type="number" min="1" value="1">
        </div>
        <button class="btn" data-add-cart="${item.id}">Thêm vào giỏ</button>
      `;

      menuList.appendChild(wrapper);

      const addBtn = wrapper.querySelector(`[data-add-cart="${item.id}"]`);
      const qtyInput = wrapper.querySelector(`#qty-${item.id}`);

      addBtn.addEventListener("click", () => {
        const quantity = Number(qtyInput.value);

        if (!quantity || quantity < 1) {
          alert("Số lượng phải lớn hơn hoặc bằng 1.");
          return;
        }

        const added = addToCart({
          restaurant_id: restaurant.id,
          restaurant_name: restaurant.name,
          menu_item_id: item.id,
          name: item.name,
          price: item.price,
          quantity: quantity
        });

        if (!added) {
          return;
        }

        alert(`Đã thêm ${quantity} x ${item.name} vào giỏ hàng.`);
      });
    });
  } catch (error) {
    console.error(error);
    menuState.textContent = "Không tải được menu. Hãy kiểm tra restaurant_id hoặc core-service.";
  }
}

function loadCartPage() {
  const cartInfo = document.getElementById("cartInfo");
  const cartList = document.getElementById("cartList");
  const cartSummary = document.getElementById("cartSummary");
  const clearCartBtn = document.getElementById("clearCartBtn");

  function renderCart() {
    const cart = getCart();
    cartList.innerHTML = "";

    if (!cart.items.length) {
      cartInfo.innerHTML = `
        <div class="info-box">
          Giỏ hàng đang trống. Hãy quay lại menu để thêm món.
        </div>
      `;

      cartSummary.innerHTML = `
        <h3>Tạm tính: 0 VNĐ</h3>
        <a class="btn btn-secondary" href="./restaurants.html">Quay lại chọn nhà hàng</a>
      `;

      return;
    }

    cartInfo.innerHTML = `
      <div class="info-box">
        Nhà hàng hiện tại: <strong>${cart.restaurant_name}</strong><br>
        Restaurant ID: <strong>${cart.restaurant_id}</strong>
      </div>
    `;

    cart.items.forEach((item) => {
      const li = document.createElement("li");
      li.innerHTML = `
        <strong>${item.name}</strong><br>
        Đơn giá: ${formatCurrency(item.price)}<br>
        Số lượng: ${item.quantity}<br>
        Thành tiền: ${formatCurrency(item.price * item.quantity)}<br>
        <button class="btn" data-plus="${item.menu_item_id}">+1</button>
        <button class="btn btn-secondary" data-minus="${item.menu_item_id}">-1</button>
        <button class="btn btn-secondary" data-remove="${item.menu_item_id}">Xóa</button>
      `;
      cartList.appendChild(li);
    });

    const subtotal = calculateCartSubtotal(cart);

    cartSummary.innerHTML = `
      <h3>Tạm tính: ${formatCurrency(subtotal)}</h3>
      <a class="btn" href="./checkout.html">Tiếp tục checkout</a>
      <a class="btn btn-secondary" href="./menu.html?restaurant_id=${cart.restaurant_id}">Quay lại menu</a>
    `;

    document.querySelectorAll("[data-plus]").forEach((button) => {
      button.addEventListener("click", () => {
        changeCartItemQuantity(button.dataset.plus, 1);
        updateCartCountBadges();
        renderCart();
      });
    });

    document.querySelectorAll("[data-minus]").forEach((button) => {
      button.addEventListener("click", () => {
        changeCartItemQuantity(button.dataset.minus, -1);
        updateCartCountBadges();
        renderCart();
      });
    });

    document.querySelectorAll("[data-remove]").forEach((button) => {
      button.addEventListener("click", () => {
        removeCartItem(button.dataset.remove);
        updateCartCountBadges();
        renderCart();
      });
    });
  }

  clearCartBtn.addEventListener("click", () => {
    const shouldClear = confirm("Bạn có chắc muốn xóa toàn bộ giỏ hàng?");
    if (!shouldClear) {
      return;
    }

    clearCart();
    updateCartCountBadges();
    renderCart();
  });

  renderCart();
}

window.addEventListener("DOMContentLoaded", () => {
  updateCartCountBadges();

  if (document.body.dataset.page === "customer-restaurants") {
    loadRestaurantsPage();
  }

  if (document.body.dataset.page === "customer-menu") {
    loadMenuPage();
  }

  if (document.body.dataset.page === "customer-cart") {
    loadCartPage();
  }

  if (document.body.dataset.page === "customer-checkout") {
    loadCheckoutPage();
  }
});

const INTEGRATION_API_BASE_URL = "http://localhost:8000";

function renderCheckoutSummary(cart) {
  const checkoutSummary = document.getElementById("checkoutSummary");
  if (!checkoutSummary) {
    return;
  }

  const subtotal = calculateCartSubtotal(cart);
  const deliveryFee = 15000;
  const total = subtotal + deliveryFee;

  checkoutSummary.innerHTML = `
    <h3>Tóm tắt đơn hàng</h3>
    <p>Nhà hàng: <strong>${cart.restaurant_name}</strong></p>
    <p>Số món: <strong>${cart.items.length}</strong></p>
    <p>Tạm tính: <strong>${formatCurrency(subtotal)}</strong></p>
    <p>Phí giao hàng demo: <strong>${formatCurrency(deliveryFee)}</strong></p>
    <p>Tổng cộng: <strong>${formatCurrency(total)}</strong></p>
  `;
}

function renderCheckoutCartInfo(cart) {
  const checkoutCartInfo = document.getElementById("checkoutCartInfo");
  const checkoutState = document.getElementById("checkoutState");

  if (!checkoutCartInfo || !checkoutState) {
    return;
  }

  if (!cart.items.length) {
    checkoutState.textContent = "Giỏ hàng đang trống. Hãy quay lại menu để thêm món trước khi checkout.";
    checkoutCartInfo.innerHTML = `
      <div class="info-box">
        Chưa có món nào trong giỏ hàng.
      </div>
    `;
    return false;
  }

  checkoutState.textContent = "Đã tải dữ liệu checkout.";
  checkoutCartInfo.innerHTML = `
    <div class="card">
      <h3>Thông tin giỏ hàng hiện tại</h3>
      <p>Nhà hàng: <strong>${cart.restaurant_name}</strong></p>
      <p>Restaurant ID: <strong>${cart.restaurant_id}</strong></p>
      <ul class="list">
        ${cart.items.map((item) => `
          <li>
            <strong>${item.name}</strong><br>
            Đơn giá: ${formatCurrency(item.price)}<br>
            Số lượng: ${item.quantity}<br>
            Thành tiền: ${formatCurrency(item.price * item.quantity)}
          </li>
        `).join("")}
      </ul>
    </div>
  `;

  return true;
}

function collectCheckoutFormData() {
  const userId = Number(document.getElementById("userIdInput").value);
  const customerName = document.getElementById("customerNameInput").value.trim();
  const customerPhone = document.getElementById("customerPhoneInput").value.trim();
  const addressLine = document.getElementById("addressLineInput").value.trim();
  const ward = document.getElementById("wardInput").value.trim();
  const district = document.getElementById("districtInput").value.trim();
  const city = document.getElementById("cityInput").value.trim();
  const note = document.getElementById("noteInput").value.trim();
  const paymentMethod = document.getElementById("paymentMethodInput").value;

  if (!userId || userId < 1) {
    throw new Error("User ID phải lớn hơn hoặc bằng 1.");
  }

  if (!customerName) {
    throw new Error("Bạn chưa nhập tên người nhận.");
  }

  if (!customerPhone) {
    throw new Error("Bạn chưa nhập số điện thoại.");
  }

  if (!addressLine) {
    throw new Error("Bạn chưa nhập địa chỉ giao hàng.");
  }

  if (!district) {
    throw new Error("Bạn chưa nhập quận/huyện.");
  }

  if (!city) {
    throw new Error("Bạn chưa nhập tỉnh/thành phố.");
  }

  return {
    userId,
    customerName,
    customerPhone,
    addressLine,
    ward,
    district,
    city,
    note,
    paymentMethod,
    fullAddress: [addressLine, ward, district, city].filter(Boolean).join(", ")
  };
}

async function createAddressForCheckout(formData) {
  const addressPayload = {
    user_id: formData.userId,
    contact_name: formData.customerName,
    phone: formData.customerPhone,
    address_line: formData.addressLine,
    ward: formData.ward || null,
    district: formData.district || null,
    city: formData.city,
    latitude: null,
    longitude: null,
    is_default: false
  };

  const response = await fetch(`${CORE_API_BASE_URL}/addresses`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(addressPayload)
  });

  const rawText = await response.text();

  let data;
  try {
    data = JSON.parse(rawText);
  } catch {
    data = rawText;
  }

  if (!response.ok) {
    throw new Error(
      `Tạo address thất bại. HTTP ${response.status}. Response: ${
        typeof data === "string" ? data : JSON.stringify(data)
      }`
    );
  }

  return data;
}

function buildCreateOrderPayload(cart, formData, addressId) {
  return {
    user_id: formData.userId,
    restaurant_id: Number(cart.restaurant_id),
    address_id: Number(addressId),
    delivery_address: formData.fullAddress,
    payment_method: formData.paymentMethod === "mock_gateway" ? "demo_gateway" : formData.paymentMethod,
    shipping_fee: 15000,
    note: formData.note,
    items: cart.items.map((item) => ({
      menu_item_id: Number(item.menu_item_id),
      quantity: Number(item.quantity),
      toppings: []
    }))
  };
}
async function placeOrderFromCheckout(cart) {
  const checkoutState = document.getElementById("checkoutState");
  const checkoutResult = document.getElementById("checkoutResult");
  const placeOrderBtn = document.getElementById("placeOrderBtn");

  if (!checkoutState || !checkoutResult || !placeOrderBtn) {
    return;
  }

  try {
    placeOrderBtn.disabled = true;

    const formData = collectCheckoutFormData();

    checkoutState.textContent = "Đang tạo địa chỉ giao hàng...";
    const createdAddress = await createAddressForCheckout(formData);

    const payload = buildCreateOrderPayload(cart, formData, createdAddress.id);

    checkoutState.textContent = "Đang gửi yêu cầu create-order...";
    checkoutResult.innerHTML = `
      <h3>Address vừa tạo</h3>
      <pre>${JSON.stringify(createdAddress, null, 2)}</pre>

      <h3>Payload create-order</h3>
      <pre>${JSON.stringify(payload, null, 2)}</pre>
    `;

    const response = await fetch(`${INTEGRATION_API_BASE_URL}/orchestrations/create-order`, {
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

    if (!response.ok) {
      throw new Error(
        `Create-order thất bại. HTTP ${response.status}. Response: ${
          typeof data === "string" ? data : JSON.stringify(data)
        }`
      );
    }

    checkoutState.textContent = "Tạo đơn hàng thành công.";

    checkoutResult.innerHTML = `
      <h3>Address vừa tạo</h3>
      <pre>${JSON.stringify(createdAddress, null, 2)}</pre>

      <h3>Payload create-order</h3>
      <pre>${JSON.stringify(payload, null, 2)}</pre>

      <h3>Kết quả create-order</h3>
      <pre>${JSON.stringify(data, null, 2)}</pre>
    `;

    const orderId =
      data.order_id ||
      data.data?.order_id ||
      data.order?.id ||
      data.data?.order?.id ||
      data.data?.order?.order_id;

    const paymentId =
      data.payment_id ||
      data.data?.payment_id ||
      data.payment?.id ||
      data.data?.payment?.id;

    const userId = payload.user_id;

    if (!orderId) {
      throw new Error("API trả thành công nhưng frontend không tìm thấy order_id trong response.");
    }

    const lastOrderData = {
      order_id: Number(orderId),
      payment_id: paymentId ? Number(paymentId) : null,
      user_id: Number(userId),
      address_id: Number(createdAddress.id),
      restaurant_id: Number(cart.restaurant_id),
      restaurant_name: cart.restaurant_name,
      created_at: new Date().toISOString(),
      checkout_completed: true
    };

    localStorage.setItem(LAST_ORDER_STORAGE_KEY, JSON.stringify(lastOrderData));

    setPendingCheckoutRedirect({
      order_id: Number(orderId),
      user_id: Number(userId)
    });

    checkoutState.textContent = "Tạo đơn hàng thành công. Đang chuyển sang trang tracking...";

    const trackingUrl = buildTrackingUrl(orderId, userId);

    checkoutResult.innerHTML = `
      <h3>Address vừa tạo</h3>
      <pre>${JSON.stringify(createdAddress, null, 2)}</pre>

      <h3>Payload create-order</h3>
      <pre>${JSON.stringify(payload, null, 2)}</pre>

      <h3>Kết quả create-order</h3>
      <pre>${JSON.stringify(data, null, 2)}</pre>

      <div class="info-box" style="margin-top: 16px;">
        Đơn hàng đã tạo thành công. Nếu trang chưa tự chuyển, bấm nút bên dưới.
      </div>

      <p style="margin-top: 12px;">
        <a class="btn" href="${trackingUrl}">Đi tới tracking ngay</a>
      </p>
    `;

    setTimeout(() => {
      redirectToTracking(orderId, userId);
    }, 300);

    return;
  }
   catch (error) {
    console.error(error);
    checkoutState.textContent = "Tạo đơn hàng thất bại.";
    checkoutResult.innerHTML = `
      <h3>Lỗi</h3>
      <pre>${String(error.message || error)}</pre>
    `;
    placeOrderBtn.disabled = false;
  }
}
function loadCheckoutPage() {
  const pendingRedirect = getPendingCheckoutRedirect();
  if (pendingRedirect) {
    redirectToTracking(pendingRedirect.order_id, pendingRedirect.user_id);
    return;
  }

  const cart = getCart();
  const placeOrderBtn = document.getElementById("placeOrderBtn");
  const checkoutResult = document.getElementById("checkoutResult");

  if (checkoutResult) {
    checkoutResult.innerHTML = `
      <h3>Kết quả</h3>
      <p>Sau khi bấm "Tạo đơn hàng", kết quả API sẽ hiển thị ở đây.</p>
    `;
  }

  const cartReady = renderCheckoutCartInfo(cart);
  renderCheckoutSummary(cart);

  if (!cartReady) {
    if (placeOrderBtn) {
      placeOrderBtn.disabled = true;
    }
    return;
  }

  if (placeOrderBtn) {
    placeOrderBtn.addEventListener("click", () => {
      placeOrderFromCheckout(getCart());
    });
  }
}