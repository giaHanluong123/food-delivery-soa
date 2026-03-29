# Database Design - Food Delivery SOA Demo

## 1. Tổng quan phân chia dữ liệu theo service

### Core Service
- users
- addresses
- restaurants
- menu_items
- toppings
- order_headers
- order_items
- order_item_toppings
- reviews

### Delivery Service
- shippers
- delivery_orders
- delivery_status_logs

Redis:
- shipper_location:{shipper_id}
- order_tracking:{order_id}

### Payment Service
- payment_transactions
- payment_logs

### Notification Service
- notifications
- notification_logs

### Integration Service
- Không lưu DB trong bản demo

---

## 2. Core Service Tables

### 2.1. users
- id
- full_name
- email
- phone
- password_hash
- role
- is_active
- created_at
- updated_at

### 2.2. addresses
- id
- user_id
- contact_name
- phone
- address_line
- ward
- district
- city
- latitude
- longitude
- is_default
- created_at
- updated_at

### 2.3. restaurants
- id
- name
- description
- phone
- address_line
- ward
- district
- city
- latitude
- longitude
- rating_avg
- is_active
- created_at
- updated_at

### 2.4. menu_items
- id
- restaurant_id
- name
- description
- price
- is_available
- image_url
- created_at
- updated_at

### 2.5. toppings
- id
- menu_item_id
- name
- price
- is_available
- created_at
- updated_at

### 2.6. order_headers
- id
- order_code
- user_id
- restaurant_id
- address_id
- order_status
- payment_status
- delivery_status
- subtotal_amount
- shipping_fee
- total_amount
- note
- created_at
- updated_at

### 2.7. order_items
- id
- order_id
- menu_item_id
- item_name
- unit_price
- quantity
- line_total
- created_at

### 2.8. order_item_toppings
- id
- order_item_id
- topping_id
- topping_name
- topping_price
- quantity
- line_total
- created_at

### 2.9. reviews
- id
- order_id
- user_id
- restaurant_id
- shipper_id
- restaurant_rating
- shipper_rating
- comment
- created_at
- updated_at

---

## 3. Delivery Service Tables

### 3.1. shippers
- id
- full_name
- phone
- email
- password_hash
- vehicle_type
- status
- current_latitude
- current_longitude
- is_active
- created_at
- updated_at

### 3.2. delivery_orders
- id
- order_id
- order_code
- shipper_id
- pickup_address
- delivery_address
- pickup_latitude
- pickup_longitude
- delivery_latitude
- delivery_longitude
- delivery_status
- assigned_at
- picked_up_at
- delivered_at
- created_at
- updated_at

### 3.3. delivery_status_logs
- id
- delivery_order_id
- status
- note
- created_at

---

## 4. Payment Service Tables

### 4.1. payment_transactions
- id
- order_id
- order_code
- transaction_code
- provider
- payment_method
- amount
- status
- provider_transaction_id
- callback_payload
- paid_at
- refunded_at
- created_at
- updated_at

### 4.2. payment_logs
- id
- payment_transaction_id
- action
- status
- message
- created_at

---

## 5. Notification Service Tables

### 5.1. notifications
- id
- user_id
- order_id
- channel
- title
- content
- status
- recipient
- created_at
- updated_at

### 5.2. notification_logs
- id
- notification_id
- event_type
- status
- message
- created_at

---

## 6. Redis Design

### 6.1. shipper_location:{shipper_id}
Ví dụ:
{
  "shipper_id": 1,
  "lat": 10.762622,
  "lng": 106.660172,
  "updated_at": "2025-01-01T10:00:00"
}

### 6.2. order_tracking:{order_id}
Ví dụ:
{
  "order_id": 1,
  "delivery_status": "delivering",
  "shipper_id": 1,
  "current_lat": 10.762622,
  "current_lng": 106.660172,
  "eta_minutes": 12,
  "updated_at": "2025-01-01T10:05:00"
}