INSERT INTO user (user_id, user_name, phone, password_hash) VALUES
    ('u001', 'ZhangSan', '13800000001', 'scrypt:32768:8:1$A7S6Jk4gRfMaQtiz$24be248aa213907ab0a90ee1d8d06a7a7afa49bdf715c8b69c37a8be3abd63b33ed2ba6428c3d1cfa33a41db459913f20a746ed1f4925d8a2ee70fb0e6b4f4e2'),
    ('u002', 'LiSi', '13800000002', 'scrypt:32768:8:1$A7S6Jk4gRfMaQtiz$24be248aa213907ab0a90ee1d8d06a7a7afa49bdf715c8b69c37a8be3abd63b33ed2ba6428c3d1cfa33a41db459913f20a746ed1f4925d8a2ee70fb0e6b4f4e2'),
    ('u003', 'WangWu', '13800000003', 'scrypt:32768:8:1$A7S6Jk4gRfMaQtiz$24be248aa213907ab0a90ee1d8d06a7a7afa49bdf715c8b69c37a8be3abd63b33ed2ba6428c3d1cfa33a41db459913f20a746ed1f4925d8a2ee70fb0e6b4f4e2'),
    ('u004', 'ZhaoLiu', '13800000004', 'scrypt:32768:8:1$A7S6Jk4gRfMaQtiz$24be248aa213907ab0a90ee1d8d06a7a7afa49bdf715c8b69c37a8be3abd63b33ed2ba6428c3d1cfa33a41db459913f20a746ed1f4925d8a2ee70fb0e6b4f4e2');

INSERT INTO item (item_id, item_name, category, price, status, seller_id) VALUES
    ('i001', 'CalculusBook', 'Book', 20, 0, 'u001'),
    ('i002', 'DeskLamp', 'DailyGoods', 35, 1, 'u002'),
    ('i003', 'Microcontroller', 'Electronics', 80, 0, 'u001'),
    ('i004', 'Chair', 'Furniture', 50, 1, 'u003'),
    ('i005', 'WaterBottle', 'DailyGoods', 15, 0, 'u004');

INSERT INTO orders (order_id, item_id, buyer_id, order_date) VALUES
    ('o001', 'i002', 'u001', '2024-05-01'),
    ('o002', 'i004', 'u002', '2024-05-03');
