const INTEGRATION_API_BASE_URL = "http://localhost:8000";

const createOrderBtn = document.getElementById("createOrderBtn");
const goTrackingBtn = document.getElementById("goTrackingBtn");
const resultBox = document.getElementById("resultBox");

function getNumberValue(id) {
  return Number(document.getElementById(id).value);
}

function getStringValue(id) {
  return document.getElementById(id).value.trim();
}

function renderResult(data) {
  resultBox.textContent = JSON.stringify(data, null, 2);
}

async function createOrder() {
  const payload = {
    user_id: getNumberValue("userId"),
    restaurant_id: getNumberValue("restaurantId"),
    address_id: getNumberValue("addressId"),
    payment_method: getStringValue("paymentMethod"),
    shipping_fee: getNumberValue("shippingFee"),
    note: getStringValue("note"),
    items: [
      {
        menu_item_id: getNumberValue("menuItemId"),
        quantity: getNumberValue("quantity"),
        toppings: []
      }
    ]
  };

  renderResult({ message: "Đang tạo đơn hàng...", payload });

  try {
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
      data = { raw_response: rawText };
    }

    renderResult({
      http_status: response.status,
      ok: response.ok,
      data
    });

    if (!response.ok || !data.success) {
      alert("Tạo đơn thất bại. Xem result box để biết chi tiết.");
      return;
    }

    const orderId = data?.data?.order?.id;
    if (!orderId) {
      alert("Không lấy được order_id từ response.");
      return;
    }

    const shouldGo = confirm(`Tạo đơn thành công. Order ID = ${orderId}. Chuyển sang tracking realtime?`);
    if (shouldGo) {
      window.location.href = `./tracking.html?order_id=${orderId}&user_id=${payload.user_id}`;
    }
  } catch (error) {
    renderResult({
      error_name: error?.name || "UnknownError",
      error_message: error?.message || String(error),
      hint: "Mo DevTools > Console/Network de xem loi chi tiet"
    });

    alert("Có lỗi khi gọi API create-order. Xem result box và Console để biết chi tiết.");
  }
}
function openTrackingManually() {
  const orderId = prompt("Nhập order_id để mở tracking:");
  if (!orderId) {
    return;
  }

  window.location.href = `./tracking.html?order_id=${orderId}`;
}

createOrderBtn.addEventListener("click", createOrder);
goTrackingBtn.addEventListener("click", openTrackingManually);