DROP TABLE IF EXISTS salesoptimizer.product_supplier;

CREATE TABLE salesoptimizer.product_supplier (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    product_code    VARCHAR(128)    NOT NULL,
    supplier        VARCHAR(256)    NOT NULL,
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP 
                                    ON UPDATE CURRENT_TIMESTAMP,

    -- One product can have multiple suppliers, but the same pair appears once
    UNIQUE KEY uq_product_supplier (product_code, supplier),

    -- Fast lookups
    INDEX idx_product_code (product_code),
    INDEX idx_supplier     (supplier)
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci;