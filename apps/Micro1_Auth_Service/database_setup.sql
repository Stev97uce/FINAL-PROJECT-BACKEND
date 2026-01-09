
-- Crear base de datos
CREATE DATABASE IF NOT EXISTS auth_service_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE auth_service_db;

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombres VARCHAR(255) NOT NULL,
    identificacion VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol ENUM('consultante','recepcionista','estudiante','psicologo_supervisor','administrador') NOT NULL,
    estado ENUM('pendiente_verificacion','activo','inactivo','suspendido') DEFAULT 'pendiente_verificacion',
    email_verificado BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_identificacion (identificacion)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de tokens de verificación
CREATE TABLE IF NOT EXISTS verification_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    tipo ENUM('email_verification','password_reset') NOT NULL,
    expira_en TIMESTAMP NOT NULL,
    usado BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_token (token),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de refresh tokens
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    token VARCHAR(500) UNIQUE NOT NULL,
    expira_en TIMESTAMP NOT NULL,
    revocado BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_token (token),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insertar usuario administrador inicial (password: Admin123)
INSERT INTO users (nombres, identificacion, email, telefono, password_hash, rol, estado, email_verificado)
VALUES (
    'Administrador Sistema',
    '0000000000',
    'admin@uce.edu.ec',
    '0999999999',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIvA8kRBTK',
    'administrador',
    'activo',
    TRUE
);

-- Verificar las tablas creadas
SHOW TABLES;

-- Ver estructura de la tabla users
DESCRIBE users;
