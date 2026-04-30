import tkinter as tk
from tkinter import messagebox, ttk
import requests
import json
import os

# Путь к файлу для сохранения избранных пользователей
FAVORITES_FILE = "favorites.json"


def load_favorites():
    """Загружает избранных пользователей из JSON-файла."""
    if os.path.exists(FAVORITES_FILE):
        try:
            with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_favorites(favorites):
    """Сохраняет избранных пользователей в JSON-файл."""
    try:
        with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
            json.dump(favorites, f, ensure_ascii=False, indent=2)
    except IOError as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить избранные: {e}")


def search_github_user():
    """Выполняет поиск пользователя GitHub через API."""
    username = entry_search.get().strip()

    # Проверка на пустой ввод
    if not username:
        messagebox.showwarning("Предупреждение", "Поле поиска не должно быть пустым!")
        return

    try:
        # Запрос к GitHub API
        response = requests.get(f"https://api.github.com/users/{username}")

        if response.status_code == 200:
            user_data = response.json()
            # Отображаем информацию о пользователе
            display_user(user_data)
        else:
            messagebox.showerror("Ошибка", "Пользователь не найден!")
            listbox_results.delete(0, tk.END)

    except requests.RequestException as e:
        messagebox.showerror("Ошибка сети", f"Не удалось подключиться к GitHub API: {e}")


def display_user(user_data):
    """Отображает информацию о найденном пользователе."""
    listbox_results.delete(0, tk.END)  # Очищаем предыдущий результат

    # Форматируем информацию для отображения
    user_info = f"{user_data.get('login', 'N/A')} | {user_data.get('name', 'N/A')}"
    listbox_results.insert(tk.END, user_info)

    # Обновляем статус пользователя в избранном
    update_favorite_status(user_data['login'])


def add_to_favorites():
    """Добавляет выбранного пользователя в избранное."""
    selection = listbox_results.curselection()
    if not selection:
        messagebox.showwarning("Предупреждение", "Выберите пользователя из списка!")
        return

    user_info = listbox_results.get(selection[0])
    username = user_info.split(' | ')[0]  # Извлекаем логин

    favorites = load_favorites()

    # Проверяем, не добавлен ли уже пользователь
    if any(fav['login'] == username for fav in favorites):
        messagebox.showinfo("Информация", "Пользователь уже в избранном!")
        return

    # Получаем полную информацию о пользователе для сохранения
    try:
        response = requests.get(f"https://api.github.com/users/{username}")
        if response.status_code == 200:
            user_data = response.json()
            favorites.append({
                'login': user_data['login'],
                'name': user_data.get('name', 'N/A'),
                'avatar_url': user_data.get('avatar_url', ''),
                'url': user_data.get('html_url', '')
            })
            save_favorites(favorites)
            messagebox.showinfo("Успех", "Пользователь добавлен в избранное!")
            update_favorite_list()
        else:
            messagebox.showerror("Ошибка", "Не удалось получить данные пользователя!")
    except requests.RequestException as e:
        messagebox.showerror("Ошибка", f"Ошибка при добавлении в избранное: {e}")


def update_favorite_list():
    """Обновляет список избранных пользователей."""
    listbox_favorites.delete(0, tk.END)
    favorites = load_favorites()
    for fav in favorites:
        listbox_favorites.insert(tk.END, f"{fav['login']} | {fav['name']}")


def update_favorite_status(username):
    """Обновляет статус избранного для текущего пользователя."""
    favorites = load_favorites()
    is_favorite = any(fav['login'] == username for fav in favorites)
    btn_favorite.config(text="Удалить из избранного" if is_favorite else "Добавить в избранное")


def remove_from_favorites():
    """Удаляет выбранного пользователя из избранного."""
    selection = listbox_favorites.curselection()
    if not selection:
        messagebox.showwarning("Предупреждение", "Выберите пользователя из списка избранного!")
        return

    favorite_info = listbox_favorites.get(selection[0])
    username = favorite_info.split(' | ')[0]

    favorites = load_favorites()
    favorites = [fav for fav in favorites if fav['login'] != username]
    save_favorites(favorites)
    messagebox.showinfo("Успех", "Пользователь удалён из избранного!")
    update_favorite_list()
    # Обновляем статус для текущего пользователя в основном списке
    current_user = listbox_results.get(0).split(' | ')[0] if listbox_results.size() > 0 else None
    if current_user:
        update_favorite_status(current_user)


# Создание главного окна
root = tk.Tk()
root.title("GitHub User Finder")
root.geometry("800x600")

# Основной фрейм
main_frame = ttk.Frame(root, padding="10")
main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Поле поиска
ttk.Label(main_frame, text="Поиск пользователя GitHub:").grid(row=0, column=0, sticky=tk.W)
entry_search = ttk.Entry(main_frame, width=40)
entry_search.grid(row=0, column=1, padx=5, pady=5)
btn_search = ttk.Button(main_frame, text="Найти", command=search_github_user)
btn_search.grid(row=0, column=2, padx=5)

# Результаты поиска
ttk.Label(main_frame, text="Результаты поиска:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
listbox_results = tk.Listbox(main_frame, height=10, width=60)
listbox_results.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

# Кнопки для работы с избранным
btn_favorite = ttk.Button(main_frame, text="Добавить в избранное", command=add_to_favorites)
btn_favorite.grid(row=3, column=0, pady=10)
btn_remove_favorite = ttk.Button(main_frame, text="Удалить из избранного", command=remove_from_favorites)
btn_remove_favorite.grid(row=3, column=1, pady=10)

# Список избранных пользователей
ttk.Label(main_frame, text="Избранные пользователи:").grid(row=4, column=0, sticky=tk.W, pady=(10, 0))
listbox_favorites = tk.Listbox(main_frame, height=10, width=60)
listbox_favorites.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

# Загрузка начальных данных
update_favorite_list()

# Запуск приложения
root.mainloop()