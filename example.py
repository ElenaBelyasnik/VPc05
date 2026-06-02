import database

# Создаём экземпляр класса Database
db = database.Database("base.db")

# Подключаемся к базе данных
db.connect()

# Создаём таблицу users
db.create_table("users", "id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, age INTEGER, email TEXT")

# Вставляем одну запись
user_id = db.insert_one("users", {"name": "Алексей", "age": 30, "email": "alex@example.com"})
print(f"Вставлен пользователь с ID: {user_id}")

# Вставляем несколько записей
db.insert_many("users", [
    {"name": "Мария", "age": 25, "email": "maria@example.com"},
    {"name": "Иван", "age": 35, "email": "ivan@example.com"},
    {"name": "Ольга", "age": 28, "email": "olga@example.com"}
])
print("Вставлено несколько пользователей")

# Читаем все записи
all_users = db.fetch_all("SELECT * FROM users")
print(f"\nВсе пользователи ({len(all_users)}):")
for user in all_users:
    print(f"  ID: {user['id']}, Имя: {user['name']}, Возраст: {user['age']}, Email: {user['email']}")

# Читаем одну запись
single_user = db.fetch_one("SELECT * FROM users WHERE id = ?", (2,))
print(f"\nОдин пользователь (ID=2): {single_user}")

# Обновляем одну запись
updated_count = db.update_one("users", {"age": 31}, "id = ?", (1,))
print(f"\nОбновлено записей: {updated_count}")

# Обновляем несколько записей (список словарей с разными данными)
db.update_one("users", {"age": 26}, "name = ?", ("Мария",))
print("Обновлены данные для Марии")

# Проверяем количество записей
count = db.get_count("SELECT COUNT(*) FROM users")
print(f"\nВсего пользователей в БД: {count}")

# Получаем список всех таблиц
tables = db.get_tables()
print(f"\nТаблицы в БД: {tables}")

# Получаем информацию о структуре таблицы
table_info = db.get_table_info("users")
print(f"\nСтруктура таблицы users:")
for col in table_info:
    print(f"  {col['name']} ({col['type']})")

# Проверяем существование таблицы
exists = db.table_exists("users")
print(f"\nТаблица users существует: {exists}")

# Удаляем одну запись
delete_count = db.delete_one("users", "name = ?", ("Ольга",))
print(f"\nУдалено записей (Ольга): {delete_count}")

# Удаляем несколько записей
delete_count = db.delete_many("users", "age < ?", (30,))
print(f"Удалено записей (возраст < 30): {delete_count}")

# Читаем оставшиеся записи
remaining_users = db.fetch_all("SELECT * FROM users")
print(f"\nОставшиеся пользователи ({len(remaining_users)}):")
for user in remaining_users:
    print(f"  ID: {user['id']}, Имя: {user['name']}, Возраст: {user['age']}")

# Выполняем произвольный запрос
rows_affected = db.execute("UPDATE users SET age = age + 1")
print(f"\nОбновлены возрасты всех пользователей (+1 год), затронуто записей: {rows_affected}")

# Проверяем целостность БД
is_ok = db.integrity_check()
print(f"\nПроверка целостности БД: {'OK' if is_ok else 'ERROR'}")

# Отключаемся от базы данных
db.disconnect()
print("\nСоединение закрыто")
