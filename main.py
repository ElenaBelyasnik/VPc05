from database import Database
from typing import Optional


def find_movies_by_genre(genre: str, db_path: str = "base.db") -> list:
    """
    Найти все фильмы по жанру.

    Args:
        genre: Жанр для поиска (например, 'Thriller').
        db_path: Путь к файлу базы данных.

    Returns:
        Список фильмов с информацией о рейтинге и ссылкой на IMDB.
    """
    db = Database(db_path)
    
    query = """
        SELECT rank, title, year, genre, imdb_rating, imdb_link
        FROM movies
        WHERE genre LIKE ?
        ORDER BY imdb_rating DESC
    """
    
    params = (f'%{genre}%',)
    
    movies = db.fetch_all(query, params)
    return movies


def delete_movies_older_than(year: int, db_path: str = "base.db") -> int:
    """
    Удалить все фильмы, выпущенные раньше указанного года.

    Args:
        year: Граничный год (удаляются фильмы со годом выпуска < year).
        db_path: Путь к файлу базы данных.

    Returns:
        Количество удалённых записей.
    """
    db = Database(db_path)
    
    query = """
        DELETE FROM movies
        WHERE year < ?
    """
    
    params = (year,)
    
    deleted_count = db.execute(query, params, commit=True)
    
    # Оптимизация базы данных после удаления
    db.vacuum()
    
    return deleted_count


def get_all_genres(db_path: str = "base.db") -> list:
    """
    Получить уникальный список всех жанров из базы данных.

    Args:
        db_path: Путь к файлу базы данных.

    Returns:
        Список уникальных жанров.
    """
    db = Database(db_path)
    
    query = """
        SELECT DISTINCT genre FROM movies ORDER BY genre
    """
    
    genres_raw = db.fetch_all(query)
    # Разбиваем составные жанры (например, "Drama | Thriller" -> ["Drama", "Thriller"])
    all_genres = set()
    for item in genres_raw:
        for genre in item['genre'].split('|'):
            all_genres.add(genre.strip())
    
    return sorted(list(all_genres))


def get_top_movies(limit: int = 5, db_path: str = "base.db") -> list:
    """
    Получить топ фильмов по рейтингу.

    Args:
        limit: Количество фильмов для возврата.
        db_path: Путь к файлу базы данных.

    Returns:
        Список топ фильмов.
    """
    db = Database(db_path)
    
    query = """
        SELECT rank, title, year, genre, imdb_rating, imdb_link
        FROM movies
        ORDER BY imdb_rating DESC
        LIMIT ?
    """
    
    movies = db.fetch_all(query, (limit,))
    return movies


def get_movies_count(db_path: str = "base.db") -> int:
    """
    Получить общее количество фильмов в базе.

    Args:
        db_path: Путь к файлу базы данных.

    Returns:
        Количество фильмов.
    """
    db = Database(db_path)
    
    query = "SELECT COUNT(*) FROM movies"
    count = db.get_count(query)
    return count


def add_movie(title: str, year: int, genre: str, imdb_rating: float, 
              imdb_link: str, db_path: str = "base.db") -> Optional[int]:
    """
    Добавить новый фильм в базу данных.

    Args:
        title: Название фильма.
        year: Год выпуска.
        genre: Жанр.
        imdb_rating: Рейтинг IMDB.
        imdb_link: Ссылка на IMDB.
        db_path: Путь к файлу базы данных.

    Returns:
        ID вставленной записи или None при ошибке.
    """
    db = Database(db_path)
    
    query = """
        INSERT INTO movies (title, year, genre, imdb_rating, imdb_link)
        VALUES (?, ?, ?, ?, ?)
    """
    
    try:
        with db.get_cursor(commit=True) as cursor:
            cursor.execute(query, (title, year, genre, imdb_rating, imdb_link))
            row_id = cursor.lastrowid
            print(f"Фильм успешно добавлен! ID: {row_id}")
            return row_id
    except Exception as e:
        print(f"Ошибка при добавлении фильма: {e}")
        return None


def interactive_add_movie(db_path: str = "base.db"):
    """
    Интерактивный диалог для добавления нового фильма.
    """
    print("\n" + "-" * 45)
    print("Добавление нового фильма")
    print("-" * 45)
    
    title = input("Название фильма: ").strip()
    if not title:
        print("Ошибка: название фильма не может быть пустым.")
        return
    
    try:
        year = int(input("Год выпуска: ").strip())
    except ValueError:
        print("Ошибка: год должен быть числом.")
        return
    
    genre = input("Жанр (например, Drama | Thriller): ").strip()
    if not genre:
        print("Ошибка: жанр не может быть пустым.")
        return
    
    try:
        imdb_rating = float(input("Рейтинг IMDB: ").strip())
    except ValueError:
        print("Ошибка: рейтинг должен быть числом.")
        return
    
    imdb_link = input("Ссылка на IMDB: ").strip()
    if not imdb_link:
        print("Ошибка: ссылка не может быть пустой.")
        return
    
    add_movie(title, year, genre, imdb_rating, imdb_link, db_path)


def interactive_search_by_genre(db_path: str = "base.db"):
    """
    Интерактивный поиск фильмов по жанру.
    """
    print("\n" + "-" * 45)
    print("Поиск фильмов по жанру")
    print("-" * 45)

    genres = get_all_genres(db_path)
    
    print("\nДоступные жанры:")
    for i, genre in enumerate(genres, 1):
        print(f"  {i}. {genre}")
    
    while True:
        try:
            choice = int(input(f"\nВыберите жанр (1-{len(genres)}): ").strip())
            if 1 <= choice <= len(genres):
                selected_genre = genres[choice - 1]
                break
            else:
                print(f"Выберите число от 1 до {len(genres)}")
        except ValueError:
            print("Введите корректное число.")
    
    print(f"\nПоиск фильмов в жанре: {selected_genre}\n")
    print("-" * 45)
    
    movies = find_movies_by_genre(selected_genre, db_path)
    
    if not movies:
        print("Фильмы не найдены.")
        return
    
    print("\n" + "-" * 45)
    print(f"Найдено фильмов: {len(movies)}\n")
    
    for i, movie in enumerate(movies, 1):
        print(f"{i}. {movie['title']} ({movie['year']}) - Рейтинг: {movie['imdb_rating']} - {movie['imdb_link']}")


def interactive_delete_old_movies(db_path: str = "base.db"):
    """
    Интерактивное удаление фильмов старше указанного года.
    """
    print("\n" + "-" * 45)
    print("Удаление старых фильмов")
    print("-" * 45)
    
    while True:
        try:
            year_input = input("Введите год (удалятся фильмы, выпущенные до этого года): ").strip()
            cutoff_year = int(year_input)
            break
        except ValueError:
            print("Ошибка: введите корректное число.")
    
    db = Database(db_path)
    query = "SELECT COUNT(*) FROM movies WHERE year < ?"
    will_delete_count = db.get_count(query, (cutoff_year,))
    
    print(f"\nНайдено фильмов для удаления: {will_delete_count}")
    
    if will_delete_count == 0:
        print("Нет фильмов для удаления.")
        return
    
    response = input(f"Вы уверены, что хотите удалить {will_delete_count} фильмов? (да/нет): ").strip().lower()
    
    if response != 'да':
        print("Операция отменена.")
        return
    
    deleted_count = delete_movies_older_than(cutoff_year, db_path)
    
    print(f"\nУдалено фильмов: {deleted_count}")
    print("-" * 45)


def interactive_show_top_movies(db_path: str = "base.db"):
    """
    Интерактивный вывод топ фильмов по рейтингу.
    """
    print("\n" + "-" * 45)
    print("Топ фильмов по рейтингу")
    print("-" * 45)
    
    try:
        limit = int(input("Количество фильмов для вывода (по умолчанию 5): ").strip() or "5")
        if limit <= 0:
            print("Используем значение по умолчанию: 5")
            limit = 5
    except ValueError:
        print("Используем значение по умолчанию: 5")
        limit = 5
    
    movies = get_top_movies(limit, db_path)
    
    if not movies:
        print("Фильмы не найдены.")
        return
    
    print("\n" + "-" * 45)
    print(f"Топ {len(movies)} фильмов:\n")
    
    for i, movie in enumerate(movies, 1):
        print(f"{i}. {movie['title']} ({movie['year']}) - Рейтинг: {movie['imdb_rating']} - {movie['imdb_link']}")


def interactive_show_movies_count(db_path: str = "base.db"):
    """
    Показывает количество фильмов в базе.
    """
    print("\n" + "-" * 45)
    print("Количество фильмов в базе")
    print("-" * 45)
    
    count = get_movies_count(db_path)
    print(f"\nВсего фильмов в базе: {count}")


def import_database_from_csv(csv_path: str = "imdb_top_250.csv", db_path: str = "base.db") -> None:
    """
    Перезагрузить базу данных из CSV файла.

    Args:
        csv_path: Путь к CSV файлу.
        db_path: Путь к файлу базы данных.
    """
    print("\n" + "-" * 45)
    print("Перезагрузка базы данных")
    print("-" * 45)
    
    # Проверка существования CSV файла
    import os
    if not os.path.exists(csv_path):
        print(f"Ошибка: файл {csv_path} не найден.")
        return
    
    # Подтверждение
    response = input("Это удалит все текущие данные и загрузит заново из CSV. Продолжить? (да/нет): ").strip().lower()
    
    if response != 'да':
        print("Операция отменена.")
        return
    
    # Импорт
    try:
        from import_csv import import_csv_to_db
        import_csv_to_db(csv_path, db_path)
        print("\nБазa данных успешно перезалита!")
    except Exception as e:
        print(f"Ошибка при перезагрузке БД: {e}")


def find_movies_by_title(search_word: str, db_path: str = "base.db") -> list:
    """
    Найти фильмы по подстроке в названии.

    Args:
        search_word: Подстрока для поиска в названии.
        db_path: Путь к файлу базы данных.

    Returns:
        Список фильмов с информацией о рейтинге и ссылкой на IMDB.
    """
    db = Database(db_path)
    
    query = """
        SELECT rank, title, year, genre, imdb_rating, imdb_link
        FROM movies
        WHERE UPPER(title) LIKE ?
        ORDER BY imdb_rating DESC
    """
    
    params = (f'%{search_word.upper()}%',)
    
    movies = db.fetch_all(query, params)
    return movies


def interactive_search_by_title(db_path: str = "base.db"):
    """
    Интерактивный поиск фильмов по подстроке в названии.
    """
    print("\n" + "-" * 45)
    print("Поиск фильма по названию")
    print("-" * 45)
    
    search_word = input("Введите слово для поиска в названии: ").strip()
    
    if not search_word:
        print("Ошибка: слово для поиска не может быть пустым.")
        return
    
    print(f"\nПоиск фильмов с названием содержащим: '{search_word}'\n")
    print("-" * 45)
    
    movies = find_movies_by_title(search_word, db_path)
    
    if not movies:
        print("Фильмы не найдены.")
        return
    
    print("\n" + "-" * 45)
    print(f"Найдено фильмов: {len(movies)}\n")
    
    for i, movie in enumerate(movies, 1):
        print(f"{i}. {movie['title']} ({movie['year']}) - Рейтинг: {movie['imdb_rating']} - {movie['imdb_link']}")


def get_top_movies_after_year(year: int, limit: int = 10, db_path: str = "base.db") -> list:
    """
    Получить топ фильмов после указанного года по рейтингу.

    Args:
        year: Граничный год (показываются фильмы со годом выпуска > year).
        limit: Количество фильмов для возврата.
        db_path: Путь к файлу базы данных.

    Returns:
        Список топ фильмов.
    """
    db = Database(db_path)
    
    query = """
        SELECT rank, title, year, genre, imdb_rating, imdb_link
        FROM movies
        WHERE year > ?
        ORDER BY imdb_rating DESC
        LIMIT ?
    """
    
    movies = db.fetch_all(query, (year, limit))
    return movies


def interactive_show_top_movies_after_year(db_path: str = "base.db"):
    """
    Интерактивный вывод топ фильмов после 2015 года по рейтингу.
    """
    print("\n" + "-" * 45)
    print("Топ-10 фильмов после 2015 года")
    print("-" * 45)
    
    year = 2015
    movies = get_top_movies_after_year(year, 10, db_path)
    
    if not movies:
        print("Фильмы не найдены.")
        return
    
    print(f"\nТоп-10 фильмов, выпущенных после {year} года:\n")
    
    for i, movie in enumerate(movies, 1):
        print(f"{i}. {movie['title']} ({movie['year']}) - Рейтинг: {movie['imdb_rating']} - {movie['imdb_link']}")


def print_menu():
    """Вывод основного меню."""
    print("\n" + "-" * 45)
    print("МЕНЮ")
    print("-" * 45)
    print("1. Поиск фильмов по жанру")
    print("2. Удалить фильмы старше года")
    print("3. Добавить новый фильм")
    print("4. Показать количество фильмов в базе")
    print("5. Топ-5 фильмов по рейтингу")
    print("6. Перезалить БД из CSV")
    print("7. Поиск фильма по слову в названии")
    print("8. Топ-10 фильмов после 2015 года")
    print("0. Выход")
    print("-" * 45)


def main_cli():
    """Главная функция CLI-интерфейса."""
    db_path = "base.db"
    
    print("-" * 45)
    print("Добро пожаловать в менеджер фильмов!")
    print("-" * 45)

    while True:
        print_menu()

        choice = input("Выберите действие (0-8): ").strip()
        
        if choice == '1':
            interactive_search_by_genre(db_path)
        elif choice == '2':
            interactive_delete_old_movies(db_path)
        elif choice == '3':
            interactive_add_movie(db_path)
        elif choice == '4':
            interactive_show_movies_count(db_path)
        elif choice == '5':
            interactive_show_top_movies(db_path)
        elif choice == '6':
            import_database_from_csv("imdb_top_250.csv", db_path)
        elif choice == '7':
            interactive_search_by_title(db_path)
        elif choice == '8':
            interactive_show_top_movies_after_year(db_path)
        elif choice == '0':
            print("\nСпасибо за использование! До свидания!")
            break
        else:
            print("\nНекорректный выбор. Пожалуйста, выберите число от 0 до 8.")


def main():
    """Главная функция для поиска фильмов по жанру (старый режим)."""
    genre = "Thriller"
    
    print(f"Поиск фильмов в жанре: {genre}\n")
    print("-" * 45)
    
    movies = find_movies_by_genre(genre)
    
    if not movies:
        print("Фильмы не найдены.")
        return
    
    print("\n" + "-" * 45)
    print(f"Найдено фильмов: {len(movies)}\n")
    
    for i, movie in enumerate(movies, 1):
        print(f"{i}. {movie['title']} ({movie['year']}) - Рейтинг: {movie['imdb_rating']} - {movie['imdb_link']}")


def main_delete_old_movies():
    """Главная функция для удаления фильмов старше 2010 года (старый режим)."""
    cutoff_year = 2010
    
    print(f"Удаление фильмов, выпущенных до {cutoff_year} года...\n")
    print("-" * 45)
    
    db = Database("base.db")
    query = "SELECT COUNT(*) FROM movies WHERE year < ?"
    will_delete_count = db.get_count(query, (cutoff_year,))
    
    print(f"Найдено фильмов для удаления: {will_delete_count}")
    
    if will_delete_count == 0:
        print("Нет фильмов для удаления.")
        return
    
    response = input(f"Вы уверены, что хотите удалить {will_delete_count} фильмов? (да/нет): ").strip().lower()
    
    if response != 'да':
        print("Операция отменена.")
        return
    
    deleted_count = delete_movies_older_than(cutoff_year)
    
    print(f"\nУдалено фильмов: {deleted_count}")
    print("-" * 45)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--delete-old":
            main_delete_old_movies()
        elif sys.argv[1] == "--cli" or sys.argv[1] == "-c":
            main_cli()
        else:
            print("Неизвестный аргумент. Запуск CLI по умолчанию.")
            main_cli()
    else:
        # По умолчанию запускаем CLI-интерфейс
        main_cli()
