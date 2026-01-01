SELECT name, email FROM users WHERE age > 25;
SELECT * FROM products WHERE price < 100 AND category = 'electronics';
INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com');
UPDATE users SET email = 'newemail@example.com' WHERE id = 1;
DELETE FROM users WHERE age < 18;
SELECT name FROM users ORDER BY created_at DESC LIMIT 10;
SELECT * FROM orders WHERE status IN ('pending', 'shipped');
