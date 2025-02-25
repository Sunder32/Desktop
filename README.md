# Документация по приложению "Менеджер сотрудников"

## Содержание
1. [Обзор](#обзор)
2. [Системные требования](#системные-требования)
3. [Установка](#установка)
4. [База данных](#база-данных)
5. [Функциональность](#функциональность)
   - [Просмотр списка сотрудников](#просмотр-списка-сотрудников)
   - [Добавление сотрудников](#добавление-сотрудников)
   - [Редактирование информации](#редактирование-информации)
   - [Удаление сотрудников](#удаление-сотрудников)
   - [Генерация отчетов](#генерация-отчетов)
6. [Архитектура приложения](#архитектура-приложения)
7. [Описание классов и методов](#описание-классов-и-методов)
8. [Устранение неполадок](#устранение-неполадок)
9. [Часто задаваемые вопросы](#часто-задаваемые-вопросы)

## Обзор

"Менеджер сотрудников" — это desktop-приложение, разработанное на Python с использованием библиотеки Tkinter для управления информацией о сотрудниках компании. Приложение позволяет хранить, обновлять и анализировать данные о сотрудниках, а также генерировать отчеты в формате PDF.

Ключевые возможности:
- Просмотр списка всех сотрудников
- Добавление новых сотрудников
- Редактирование информации о существующих сотрудниках
- Удаление сотрудников из базы данных
- Генерация PDF-отчетов с корректным отображением кириллицы

## Системные требования

- Python 3.6 или выше
- MySQL сервер
- Библиотеки Python:
  - tkinter
  - mysql-connector-python
  - reportlab

## Установка

1. Установите необходимые библиотеки:
```bash
pip install mysql-connector-python reportlab
```

2. Скачайте исходный код приложения.

3. Настройте параметры подключения к базе данных в файле исходного кода (параметры host, user, password и database в методе `__init__` класса `EmployeeManager`).

4. Запустите приложение:
```bash
python employee_manager.py
```

## База данных

Приложение использует MySQL базу данных для хранения информации о сотрудниках. Структура таблицы:

```sql
CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    last_name VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    birth_date DATE,
    position VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    phone VARCHAR(20),
    email VARCHAR(255),
    start_date DATE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

## Функциональность

### Просмотр списка сотрудников

Главное окно приложения отображает список всех сотрудников с основной информацией:
- ID
- Имя
- Фамилия
- Должность

Для обновления списка используйте кнопку "Обновить список".

### Добавление сотрудников

1. Нажмите кнопку "Добавить сотрудника".
2. Заполните все обязательные поля в появившемся окне:
   - Имя
   - Фамилия
   - Дата рождения (в формате дд.мм.гггг)
   - Должность
   - Телефон
   - Email (опционально)
   - Дата начала работы (в формате дд.мм.гггг)
3. Нажмите "Сохранить".

### Редактирование информации

1. Выберите сотрудника в списке.
2. Нажмите кнопку "Редактировать сотрудника".
3. Измените необходимые данные в появившемся окне.
4. Нажмите "Сохранить".

### Удаление сотрудников

1. Выберите сотрудника в списке.
2. Нажмите кнопку "Удалить сотрудника".
3. Подтвердите действие в диалоговом окне.

### Генерация отчетов

1. Нажмите кнопку "Сгенерировать отчет".
2. Выберите место сохранения PDF-файла.
3. Отчет будет создан и сохранен в указанном месте.

Отчет содержит:
- Заголовок с текущей датой
- Таблицу сотрудников (имя, фамилия, должность, дата начала работы)
- Информацию об общем количестве сотрудников

## Архитектура приложения

Приложение построено на основе шаблона MVC (Model-View-Controller):
- **Model**: Взаимодействие с базой данных MySQL через коннектор mysql-connector-python
- **View**: Интерфейс пользователя, реализованный с помощью Tkinter
- **Controller**: Класс EmployeeManager, обрабатывающий пользовательские действия

## Описание классов и методов

### Класс EmployeeManager

**Основные методы:**

- `__init__(self, root)` — Инициализация приложения, подключение к БД
- `find_system_font(self)` — Поиск системного шрифта с поддержкой кириллицы
- `create_table(self)` — Создание таблицы в базе данных, если она не существует
- `build_interface(self)` — Создание графического интерфейса
- `refresh_list(self)` — Обновление списка сотрудников
- `add_employee_window(self)` — Открытие окна добавления сотрудника
- `edit_employee_window(self)` — Открытие окна редактирования сотрудника
- `delete_employee(self)` — Удаление выбранного сотрудника
- `employee_window(self, title, save_callback, employee_id=None)` — Создание окна формы
- `convert_date(self, date_str)` — Конвертация даты из пользовательского формата
- `add_employee(self, data)` — Добавление нового сотрудника
- `edit_employee(self, employee_id, data)` — Редактирование существующего сотрудника
- `save_employee(self, data, employee_id=None)` — Сохранение данных сотрудника
- `generate_report(self)` — Генерация PDF-отчета
- `__del__(self)` — Закрытие соединения с БД при закрытии приложения

## Устранение неполадок

### Проблемы с отображением кириллицы

**Симптом**: В PDF-отчете вместо кириллических символов отображаются квадраты или другие символы.

**Решение**: 
1. Убедитесь, что в системе установлен шрифт с поддержкой кириллицы.
2. Проверьте параметры кодировки при подключении к базе данных.

### Ошибки подключения к базе данных

**Симптом**: При запуске появляется сообщение "Ошибка подключения к БД".

**Решение**:
1. Проверьте параметры подключения (host, user, password, database).
2. Убедитесь, что MySQL сервер запущен и доступен.
3. Проверьте наличие прав у пользователя для доступа к базе данных.

### Проблемы с датами

**Симптом**: При сохранении сотрудника появляется сообщение "Неверный формат даты".

**Решение**:
1. Убедитесь, что дата вводится в формате дд.мм.гггг (например, 01.01.2023).
2. Проверьте, что введенная дата существует в календаре.

## Часто задаваемые вопросы

### Можно ли экспортировать данные в другие форматы, кроме PDF?

В текущей версии поддерживается только экспорт в PDF. Расширение функциональности для поддержки других форматов планируется в будущих версиях.

### Как изменить размер шрифта в интерфейсе?

Размер шрифта настраивается в методе `build_interface()` при настройке стиля:

```python
style = ttk.Style()
style.configure("Treeview", font=("Arial", 10))  # Изменить 10 на желаемый размер
style.configure("Treeview.Heading", font=("Arial", 10, "bold"))  # Изменить 10 на желаемый размер
```

### Как добавить дополнительные поля для информации о сотрудниках?

1. Измените структуру таблицы в базе данных, добавив новые поля.
2. Обновите метод `create_table()`.
3. Добавьте новые поля в форму редактирования в методе `employee_window()`.
4. Обновите методы `save_employee()` и `refresh_list()` для работы с новыми полями.
# Desktop
