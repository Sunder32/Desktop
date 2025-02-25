import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import mysql.connector
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from datetime import datetime
import sys
import os
import tempfile


class EmployeeManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Менеджер сотрудников")
        self.root.geometry("800x600")

        # Настройка шрифта для PDF
        self.font_path = self.find_system_font()

        # Подключение к базе данных с правильной кодировкой
        try:
            self.conn = mysql.connector.connect(
                host="it.vshp.online",
                user="st_ac68d6",
                password="26ae8c5ee970",
                database="db_ac68d6",
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci'
            )
            self.cursor = self.conn.cursor()
            self.create_table()
            self.build_interface()
        except mysql.connector.Error as err:
            messagebox.showerror("Ошибка подключения к БД", f"Не удалось подключиться к базе данных: {err}")
            root.destroy()

    def find_system_font(self):
        """Находит системный шрифт с поддержкой кириллицы"""
        if sys.platform.startswith('win'):
            # Windows
            windows_fonts_dir = os.path.join(os.environ['WINDIR'], 'Fonts')
            font_options = [
                os.path.join(windows_fonts_dir, 'arial.ttf'),
                os.path.join(windows_fonts_dir, 'tahoma.ttf'),
                os.path.join(windows_fonts_dir, 'calibri.ttf')
            ]
        elif sys.platform.startswith('darwin'):
            # macOS
            font_options = [
                '/Library/Fonts/Arial.ttf',
                '/Library/Fonts/Times New Roman.ttf',
                '/System/Library/Fonts/Helvetica.ttc'
            ]
        else:
            # Linux
            font_options = [
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
                '/usr/share/fonts/truetype/freefont/FreeSans.ttf'
            ]

        # Проверка существования файлов шрифтов
        for font in font_options:
            if os.path.exists(font):
                return font

        # Если шрифт не найден, вернем None
        return None

    def create_table(self):
        """Создает таблицу в базе данных с поддержкой UTF-8"""
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS employees (
                id INT AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
                last_name VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
                birth_date DATE,
                position VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
                phone VARCHAR(20),
                email VARCHAR(255),
                start_date DATE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci'''
        )
        self.conn.commit()

    def build_interface(self):
        """Создает пользовательский интерфейс"""
        # Настройка стиля Treeview для корректного отображения кириллицы
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

        # Рамка для таблицы с полосой прокрутки
        frame = ttk.Frame(self.root)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        # Создание таблицы сотрудников
        self.tree = ttk.Treeview(frame, columns=("ID", "Имя", "Фамилия", "Должность"),
                                 show="headings", yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)

        # Настройка колонок
        self.tree.heading("ID", text="ID")
        self.tree.heading("Имя", text="Имя")
        self.tree.heading("Фамилия", text="Фамилия")
        self.tree.heading("Должность", text="Должность")

        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Имя", width=150)
        self.tree.column("Фамилия", width=150)
        self.tree.column("Должность", width=200)

        self.tree.pack(fill="both", expand=True)

        # Рамка для кнопок
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=10)

        # Кнопки управления
        ttk.Button(button_frame, text="Добавить сотрудника", command=self.add_employee_window).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Редактировать сотрудника",
                   command=self.edit_employee_window).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Удалить сотрудника",
                   command=self.delete_employee).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Сгенерировать отчет",
                   command=self.generate_report).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Обновить список",
                   command=self.refresh_list).pack(side="left", padx=5)

        # Загрузить данные
        self.refresh_list()

    def refresh_list(self):
        """Обновляет список сотрудников в таблице"""
        # Очистка таблицы
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Загрузка данных из базы
        self.cursor.execute("SELECT id, first_name, last_name, position FROM employees ORDER BY last_name")
        for employee in self.cursor.fetchall():
            self.tree.insert("", "end", values=employee)

    def add_employee_window(self):
        """Открывает окно добавления сотрудника"""
        self.employee_window("Добавить сотрудника", self.add_employee)

    def edit_employee_window(self):
        """Открывает окно редактирования сотрудника"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите сотрудника для редактирования")
            return

        employee_id = self.tree.item(selected_item[0], "values")[0]
        self.employee_window("Редактировать сотрудника",
                             lambda data: self.edit_employee(employee_id, data),
                             employee_id)

    def delete_employee(self):
        """Удаляет выбранного сотрудника из базы данных"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите сотрудника для удаления")
            return

        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этого сотрудника?"):
            employee_id = self.tree.item(selected_item[0], "values")[0]
            self.cursor.execute("DELETE FROM employees WHERE id = %s", (employee_id,))
            self.conn.commit()
            self.refresh_list()
            messagebox.showinfo("Успех", "Сотрудник удален")

    def employee_window(self, title, save_callback, employee_id=None):
        """Создает окно для добавления/редактирования сотрудника"""
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("400x450")
        win.resizable(False, False)
        win.grab_set()  # Делаем окно модальным

        # Определение полей формы
        fields = [
            ("Имя", "first_name"),
            ("Фамилия", "last_name"),
            ("Дата рождения (дд.мм.гггг)", "birth_date"),
            ("Должность", "position"),
            ("Телефон", "phone"),
            ("Email", "email"),
            ("Дата начала работы (дд.мм.гггг)", "start_date")
        ]

        frame = ttk.Frame(win, padding=20)
        frame.pack(fill="both", expand=True)

        # Создание полей ввода
        entries = {}
        row = 0
        for label_text, field in fields:
            ttk.Label(frame, text=label_text).grid(row=row, column=0, sticky="w", padx=5, pady=5)
            entry = ttk.Entry(frame, width=30)
            entry.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
            entries[field] = entry
            row += 1

        # Если это редактирование, загружаем данные сотрудника
        if employee_id:
            self.cursor.execute("SELECT * FROM employees WHERE id = %s", (employee_id,))
            employee_data = self.cursor.fetchone()
            if employee_data:
                # Заполняем поля данными
                for i, field in enumerate(["first_name", "last_name", "birth_date",
                                           "position", "phone", "email", "start_date"]):
                    value = employee_data[i + 1]
                    # Преобразуем даты в нужный формат
                    if field in ["birth_date", "start_date"] and value:
                        value = value.strftime("%d.%m.%Y")
                    if value:
                        entries[field].insert(0, value)

        # Кнопки
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=15)

        ttk.Button(button_frame, text="Сохранить", width=15,
                   command=lambda: save_callback({field: entry.get() for field, entry in entries.items()})).pack(
            side="left", padx=5)
        ttk.Button(button_frame, text="Отмена", width=15,
                   command=win.destroy).pack(side="left", padx=5)

    def convert_date(self, date_str):
        """Конвертирует строку даты в формат для БД"""
        if not date_str:
            return None

        try:
            return datetime.strptime(date_str, "%d.%m.%Y").strftime("%Y-%m-%d")
        except ValueError:
            return None

    def add_employee(self, data):
        """Добавляет нового сотрудника"""
        self.save_employee(data)

    def edit_employee(self, employee_id, data):
        """Редактирует существующего сотрудника"""
        self.save_employee(data, employee_id)

    def save_employee(self, data, employee_id=None):
        """Сохраняет данные сотрудника в базу"""
        # Проверка данных
        for field, value in data.items():
            if not value.strip() and field not in ["email"]:  # Email может быть пустым
                messagebox.showwarning("Ошибка", f"Поле '{field}' не может быть пустым")
                return False

        # Конвертация дат
        data['birth_date'] = self.convert_date(data['birth_date'])
        data['start_date'] = self.convert_date(data['start_date'])

        if not data['birth_date'] or not data['start_date']:
            messagebox.showwarning("Ошибка", "Неверный формат даты. Используйте дд.мм.гггг")
            return False

        try:
            if employee_id:
                # Обновление существующего сотрудника
                self.cursor.execute(
                    "UPDATE employees SET first_name=%s, last_name=%s, birth_date=%s, "
                    "position=%s, phone=%s, email=%s, start_date=%s WHERE id=%s",
                    (data['first_name'], data['last_name'], data['birth_date'],
                     data['position'], data['phone'], data['email'], data['start_date'], employee_id)
                )
            else:
                # Добавление нового сотрудника
                self.cursor.execute(
                    "INSERT INTO employees (first_name, last_name, birth_date, "
                    "position, phone, email, start_date) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (data['first_name'], data['last_name'], data['birth_date'],
                     data['position'], data['phone'], data['email'], data['start_date'])
                )
            self.conn.commit()
            self.refresh_list()
            messagebox.showinfo("Успех", "Данные сохранены")
            return True
        except mysql.connector.Error as err:
            messagebox.showerror("Ошибка базы данных", f"Произошла ошибка: {err}")
            return False

    def generate_report(self):
        """Создает PDF-отчет со списком сотрудников с правильной поддержкой кириллицы"""
        # Выбор места сохранения отчета
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Сохранить отчет"
        )
        if not filename:
            return

        try:
            # Проверка наличия шрифта
            font_name = 'CustomFont'
            if self.font_path and os.path.exists(self.font_path):
                # Регистрация шрифта для PDF
                pdfmetrics.registerFont(TTFont(font_name, self.font_path))
            else:
                # Если шрифт не найден, используем стандартные шрифты
                font_name = 'Helvetica'
                messagebox.showwarning("Предупреждение",
                                       "Не найден шрифт с поддержкой кириллицы. Кириллица может отображаться некорректно.")

            # Запрос данных из базы
            self.cursor.execute(
                "SELECT first_name, last_name, position, "
                "DATE_FORMAT(start_date, '%d.%m.%Y') FROM employees ORDER BY last_name"
            )
            employees = self.cursor.fetchall()

            if not employees:
                messagebox.showwarning("Предупреждение", "Нет данных для создания отчета")
                return

            # Создание PDF документа с отступами
            doc = SimpleDocTemplate(
                filename,
                pagesize=A4,
                rightMargin=20 * mm,
                leftMargin=20 * mm,
                topMargin=20 * mm,
                bottomMargin=20 * mm
            )

            # Создание стилей с правильным шрифтом
            styles = getSampleStyleSheet()

            # Создаем свой стиль на основе Heading1 с поддержкой кириллицы
            styles.add(
                ParagraphStyle(
                    name='HeadingCyrillic',
                    parent=styles['Heading1'],
                    fontName=font_name,
                    fontSize=16,
                    alignment=1,  # По центру
                    spaceAfter=10 * mm
                )
            )

            # Создаем стиль для обычного текста с поддержкой кириллицы
            styles.add(
                ParagraphStyle(
                    name='NormalCyrillic',
                    parent=styles['Normal'],
                    fontName=font_name,
                    fontSize=10,
                    alignment=0  # По левому краю
                )
            )

            # Подготовка элементов документа
            elements = []

            # Добавление заголовка с текущей датой
            current_date = datetime.now().strftime('%d.%m.%Y')
            title = Paragraph(f"Список сотрудников на {current_date}", styles['HeadingCyrillic'])
            elements.append(title)
            elements.append(Spacer(1, 10 * mm))

            # Подготовка данных для таблицы
            column_headers = ["Имя", "Фамилия", "Должность", "Дата начала работы"]
            table_data = [column_headers]

            # Преобразуем данные для корректного отображения кириллицы
            for emp in employees:
                table_data.append(emp)

            # Создание таблицы с фиксированной шириной колонок
            table = Table(
                table_data,
                colWidths=[40 * mm, 40 * mm, 50 * mm, 40 * mm],
                repeatRows=1  # Повторять заголовок на каждой странице
            )

            # Создание стиля таблицы с поддержкой кириллицы
            table_style = TableStyle([
                # Заголовок таблицы
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), font_name),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('TOPPADDING', (0, 0), (-1, 0), 6),

                # Данные таблицы
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 1), (-1, -1), font_name),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
                ('TOPPADDING', (0, 1), (-1, -1), 4),

                # Сетка
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ])

            table.setStyle(table_style)
            elements.append(table)

            # Добавление информации о количестве сотрудников
            elements.append(Spacer(1, 10 * mm))
            employee_count = Paragraph(f"Всего сотрудников: {len(employees)}", styles['NormalCyrillic'])
            elements.append(employee_count)

            # Создание документа
            doc.build(elements)
            messagebox.showinfo("Успех", f"Отчет сохранен как {filename}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать отчет: {str(e)}")

    def __del__(self):
        """Закрывает соединение с базой данных при закрытии приложения"""
        if hasattr(self, 'conn') and self.conn.is_connected():
            self.cursor.close()
            self.conn.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = EmployeeManager(root)
    root.mainloop()