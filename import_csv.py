import csv
from database import Database


def create_movies_table(db: Database) -> None:
    """Создать таблицу movies для хранения данных о фильмах."""
    db.create_table(
        "movies",
        """
        rank INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        year INTEGER,
        genre TEXT,
        duration TEXT,
        origin TEXT,
        director TEXT,
        imdb_rating REAL,
        rating_count INTEGER,
        imdb_link TEXT
        """
    )


def import_csv_to_db(csv_path: str, db_path: str = "base.db") -> None:
    """
    Импорт данных из CSV файла в базу данных SQLite.

    Args:
        csv_path: Путь к CSV файлу.
        db_path: Путь к файлу базы данных.
    """
    db = Database(db_path)
    
    # Удаляем старую таблицу если существует
    if db.table_exists("movies"):
        print("Таблица movies существует. Удаление старой таблицы...")
        db.drop_table("movies")
    
    # Создаем таблицу
    create_movies_table(db)
    print("Таблица movies создана.")
    
    # Читаем CSV файл
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data_list = []
        
        for row in reader:
            # Преобразуем данные в нужный формат
            record = {
                'rank': int(row['']),
                'title': row['Title'],
                'year': int(row['Year']),
                'genre': row['Genre'],
                'duration': row['Duration'],
                'origin': row['Origin'],
                'director': row['Director'],
                'imdb_rating': float(row['IMDB rating']),
                'rating_count': int(row['Rating count']),
                'imdb_link': row['IMDB link']
            }
            data_list.append(record)
    
    # Вставляем все записи
    count = db.insert_many("movies", data_list)
    print(f"Вставлено {count} записей в таблицу movies в БД {db_path}")


if __name__ == "__main__":
    import_csv_to_db("imdb_top_250.csv", "base.db")
