CREATE DATABASE IF NOT EXISTS oficina_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE oficina_ai;

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(120) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(20) NOT NULL DEFAULT 'ATENDENTE',
  specialties TEXT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'ATIVO',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_users_role_status (role, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS clients (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(120) NOT NULL,
  cpf_cnpj VARCHAR(20) NULL UNIQUE,
  phone VARCHAR(30) NULL,
  email VARCHAR(120) NULL,
  address VARCHAR(255) NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'ATIVO',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_clients_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS vehicles (
  id INT AUTO_INCREMENT PRIMARY KEY,
  plate VARCHAR(12) NOT NULL UNIQUE,
  brand VARCHAR(60) NOT NULL,
  model VARCHAR(80) NOT NULL,
  year INT NULL,
  color VARCHAR(40) NULL,
  client_id INT NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_vehicles_clients FOREIGN KEY (client_id) REFERENCES clients(id),
  INDEX idx_vehicles_client (client_id),
  INDEX idx_vehicles_plate (plate)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS services (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(120) NOT NULL UNIQUE,
  description TEXT NULL,
  category VARCHAR(80) NULL,
  base_price DECIMAL(10,2) NOT NULL DEFAULT 0,
  estimated_minutes INT NOT NULL DEFAULT 60,
  active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_services_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS appointments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  scheduled_start DATETIME NOT NULL,
  scheduled_end DATETIME NOT NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'AGENDADO',
  notes TEXT NULL,
  ai_score DECIMAL(5,2) NULL,
  ai_reason VARCHAR(255) NULL,
  client_id INT NOT NULL,
  vehicle_id INT NOT NULL,
  service_id INT NOT NULL,
  technician_id INT NOT NULL,
  created_by_id INT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_appointments_clients FOREIGN KEY (client_id) REFERENCES clients(id),
  CONSTRAINT fk_appointments_vehicles FOREIGN KEY (vehicle_id) REFERENCES vehicles(id),
  CONSTRAINT fk_appointments_services FOREIGN KEY (service_id) REFERENCES services(id),
  CONSTRAINT fk_appointments_technician FOREIGN KEY (technician_id) REFERENCES users(id),
  CONSTRAINT fk_appointments_created_by FOREIGN KEY (created_by_id) REFERENCES users(id),
  INDEX idx_appointments_time (scheduled_start, scheduled_end),
  INDEX idx_appointments_tech_time (technician_id, scheduled_start, scheduled_end)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS work_orders (
  id INT AUTO_INCREMENT PRIMARY KEY,
  opening_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  closing_date DATETIME NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'ABERTA',
  problem_description TEXT NOT NULL,
  diagnosis TEXT NULL,
  labor_total DECIMAL(10,2) NOT NULL DEFAULT 0,
  parts_total DECIMAL(10,2) NOT NULL DEFAULT 0,
  total_value DECIMAL(10,2) NOT NULL DEFAULT 0,
  client_id INT NOT NULL,
  vehicle_id INT NOT NULL,
  technician_id INT NOT NULL,
  main_service_id INT NULL,
  appointment_id INT NULL UNIQUE,
  created_by_id INT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_work_orders_clients FOREIGN KEY (client_id) REFERENCES clients(id),
  CONSTRAINT fk_work_orders_vehicles FOREIGN KEY (vehicle_id) REFERENCES vehicles(id),
  CONSTRAINT fk_work_orders_technician FOREIGN KEY (technician_id) REFERENCES users(id),
  CONSTRAINT fk_work_orders_main_service FOREIGN KEY (main_service_id) REFERENCES services(id),
  CONSTRAINT fk_work_orders_appointments FOREIGN KEY (appointment_id) REFERENCES appointments(id),
  CONSTRAINT fk_work_orders_created_by FOREIGN KEY (created_by_id) REFERENCES users(id),
  INDEX idx_work_orders_status (status),
  INDEX idx_work_orders_main_service (main_service_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS work_order_items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  work_order_id INT NOT NULL,
  service_id INT NOT NULL,
  quantity INT NOT NULL DEFAULT 1,
  unit_price DECIMAL(10,2) NOT NULL DEFAULT 0,
  total DECIMAL(10,2) NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_work_order_items_order FOREIGN KEY (work_order_id) REFERENCES work_orders(id) ON DELETE CASCADE,
  CONSTRAINT fk_work_order_items_service FOREIGN KEY (service_id) REFERENCES services(id),
  INDEX idx_work_order_items_order (work_order_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS products (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(120) NOT NULL UNIQUE,
  description TEXT NULL,
  quantity INT NOT NULL DEFAULT 0,
  min_quantity INT NOT NULL DEFAULT 1,
  unit_price DECIMAL(10,2) NOT NULL DEFAULT 0,
  active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_products_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS stock_movements (
  id INT AUTO_INCREMENT PRIMARY KEY,
  product_id INT NOT NULL,
  movement_type VARCHAR(20) NOT NULL,
  quantity INT NOT NULL,
  unit_cost DECIMAL(10,2) NULL,
  reason VARCHAR(255) NULL,
  created_by_id INT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_stock_movements_product FOREIGN KEY (product_id) REFERENCES products(id),
  CONSTRAINT fk_stock_movements_user FOREIGN KEY (created_by_id) REFERENCES users(id),
  INDEX idx_stock_movements_product (product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS sales (
  id INT AUTO_INCREMENT PRIMARY KEY,
  date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  total_value DECIMAL(10,2) NOT NULL DEFAULT 0,
  status VARCHAR(30) NOT NULL DEFAULT 'PAGA',
  payment_method VARCHAR(40) NULL,
  client_id INT NULL,
  work_order_id INT NULL UNIQUE,
  created_by_id INT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_sales_clients FOREIGN KEY (client_id) REFERENCES clients(id),
  CONSTRAINT fk_sales_work_orders FOREIGN KEY (work_order_id) REFERENCES work_orders(id),
  CONSTRAINT fk_sales_created_by FOREIGN KEY (created_by_id) REFERENCES users(id),
  INDEX idx_sales_date (date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS sale_items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  sale_id INT NOT NULL,
  product_id INT NOT NULL,
  quantity INT NOT NULL DEFAULT 1,
  unit_price DECIMAL(10,2) NOT NULL DEFAULT 0,
  total DECIMAL(10,2) NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_sale_items_sale FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
  CONSTRAINT fk_sale_items_product FOREIGN KEY (product_id) REFERENCES products(id),
  INDEX idx_sale_items_sale (sale_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ai_recommendation_logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  request_type VARCHAR(60) NOT NULL,
  payload LONGTEXT NULL,
  result LONGTEXT NULL,
  user_id INT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_ai_logs_user FOREIGN KEY (user_id) REFERENCES users(id),
  INDEX idx_ai_logs_type (request_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
