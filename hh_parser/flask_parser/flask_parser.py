import json

from flask import Blueprint, render_template, redirect
from flask import session, request, flash, redirect

import hh_parser.parser_app.hhrequest as hr
from ..models import Request
from ..database import db_session

from datetime import datetime

from sqlalchemy import desc

from flask_table import Table, Col, LinkCol

parser_blueprint = Blueprint("flask_parser", __name__)


@parser_blueprint.route("/")
def root():
    """
    Функция обработки запроса к корневой странице
    :return Страница Index
    """
    return render_template("index.html")


@parser_blueprint.route("/index")
def index():
    """
    Функция обработки запроса к странице Index
    :return Страница Index
    """
    return render_template("index.html")


@parser_blueprint.route("/requests", methods=["GET", "POST"])
def requests():
    """
    Функция обработки запроса к странице Запросы
    :return: Обработанную страницу Запросы
    """
    # Эта страница доступна только авторизованному пользователю
    if session.get("user_id"):
        # Обработка формы по запросу
        if request.method == "POST":
            # Достаем нужные данные из формы запроса
            region = request.form["Region"]
            text_request = request.form["Request"]
            o_hhrequest = hr.HHRequest(None)
            try:
                # Проверяем правильность задания региона
                j_result = o_hhrequest.set_region(region)
            except ValueError as ex:
                flash("Регион указан не правильно")
                return render_template("requests.html")
            # Берем регион из проверки
            region = j_result["items"][0]["text"]
            # Вставляем запрос в БД для обработки
            request_db = Request(
                user_id=session["user_id"],
                region=region,
                text_request=text_request,
                status=0,
                created=datetime.now()
            )
            db_session.add(request_db)
            db_session.commit()
            flash("Запрос отправлен на обработку."
                  "Его состояние можно отслеживать в истории.")
    else:
        # Если пользователь не авторизован то отправляем его в Login
        return redirect("login")
    return render_template("requests.html")


@parser_blueprint.route("/history")
def history():
    """
    Функция обработки запроса к странице История
    :return:
    """

    # Если пользователь не авторизовался, то возвращаем его к странице авторизации
    if session.get("user_id"):

        # Читаем из БД список запросов
        items = Item.get_elements()

        # Формируем таблицу
        table = ItemTable(items)

        # Возвращаем страницу с интегрированной таблицей
        return render_template("history.html", tables=table)
    else:
        return redirect("login")


class Item(object):
    """
    Класс описывающий элемент таблицы, должен обеспечить формирование списка элементов
    таблицы с результатами парсинг, где каждый элемент списка – результаты
    конкретного запроса. Т.е. класс Item как бы описывает результаты запроса.
    """

    def __init__(self, tab_id, req_id, region, text_request, status, vac_number, created):
        self.tab_id = tab_id  # номер строки в таблице
        self.request_id = req_id  # идентификатор запроса
        self.region = region  # регион
        self.text_request = text_request  # текст запроса
        self.vacancies_number = vac_number  # количество просканированных вакансий
        self.status = status  # статус запроса
        self.created = created  # дату создания запроса

    @classmethod
    def get_elements(cls):
        """
        Метод для получения списка запросов из БД
        :return: список запросов
        """
        # Читаем из БД список запросов для текущего пользователя, через класс-модель
        # Request и ORM получаем список объектов этого класса, т.е.
        # список запросов для текущего пользователя.
        rows = db_session.query(Request).filter(Request.user_id ==
                                                session["user_id"]).order_by(desc(Request.created)).all()

        # Определяем номер элемента.
        # Нумерация будет с единицы. Создаем список результатов, который потом
        # передадим в таблицу. Берем по одному экземпляру класса Request.
        id_n = 1
        items_for_table = []

        # Обрабатываем полученный список
        for row_request in rows:

            # Через объект запроса получаем атрибут с количеством вакансий по этому
            # запросу
            vac_numbers = row_request.vacancy_number

            # Если вакансий по запросу не обнаружено, то ставим значение переменной
            # vac_numbers в ноль
            if not row_request.vacancy_number:
                vac_numbers = 0

            # Обрабатываем статус запроса
            if row_request.status == 0:
                status = "Инициализирован"
            elif row_request.status == 1:
                status = "В обработке"
            elif row_request.status == 2:
                status = "Завершен"
            else:
                status = "Неопределен"

            # Добавляем элемент в таблицу
            # Добавляем в список items_for_table экземпляр класса Item со всеми
            # необходимыми параметрами
            items_for_table.append(Item(
                id_n,
                row_request.id,
                row_request.region,
                row_request.text_request,
                status,
                vac_numbers,
                row_request.created
            ))
            id_n += 1

        return items_for_table

    # Указанный метод позволит получить из списка items_for_table экземпляр
    # класса Item по указанному идентификатору
    @classmethod
    def get_element_by_id(cls, id):
        """
        Получаем конкретный элемент из таблицы
        :param id: номер требуемего элемента
        :return: элемент из таблицы
        """
        return [i for i in cls.get_elements() if i.tab_id == id][0]


# Создание таблицы для вывода на странице История
class ItemTable(Table):
    """
    Класс должен обеспечить формирование таблицы с
    результатами, куда и будет передан отмеченный выше список элементов.
    """

    # Атрибуты таблицы, которые будут использованы при ввыоде ее на экран
    # Настраиваем Bootstrap-стилизацию таблицы
    classes = ["table", "table-bordered"]

    # Создаем колонки с указанными заголовками
    tab_id = Col("Номер запроса")
    region = Col("Регион")
    text_request = Col("Запрос")
    vacancies_number = Col("Кол-во вакансий")
    status = Col("Статус")
    created = Col("Создан")

    # Этому атрибуту уделим особое внимание. Это будет ссылка с надписью:
    # «Смотреть», при нажатии на которую мы сможем перейти на страницу с
    # детальной информацией по запросу.
    # При переходе будет запускаться контроллер single_item модуля flask_parser и
    # принимать идентификатор записи таблицы. Создадим этот контроллер
    name = LinkCol("Смотреть", "flask_parser.single_item", url_kwargs=dict(id="tab_id"))


@parser_blueprint.route("/item/<int:id>", methods=["GET", "POST"])
def single_item(id):
    # Эта страница доступна только для авторизованного пользователя
    if session["user_id"]:

        # Достаем из списка требуемый элемент
        element = Item.get_element_by_id(id)

        # Достаем из БД имя файла с результатами обработки запроса
        row: Request = (db_session.query(Request).
                        filter(Request.id == element.request_id).one())
        if row.file_name is not None:

            # Читаем результаты обработки запроса из файла
            with open(row.file_name, "r") as f:
                result: json = json.load(f)

            # Обрабатываем результаты запроса. Извлекаем из словаря навыки из описания, ключевые навыки, зарплату
            description_skills: dict = result["description"]
            key_skills: dict = result["keyskills"]
            salary_avager: dict = result["salary"]

            # Для навыков из описания
            sum_description: list = []
            for key, value in list(description_skills.items())[:10]:
                sum_description.append(key + "-" + str(value) + "%")

            # Для навыков из ключевых навыков
            sum_keyskills: list = []
            for key, value in list(key_skills.items())[:10]:
                sum_keyskills.append(key + "-" + str(value) + "%")

            # Для зарплат
            sum_salaries: list = []
            for key, value in salary_avager.items():
                sum_salaries.append(key + "   от: " + '{:6.0f}'.format(value[0]) +
                                    "₽.  до: " + '{:6.0f}'.format(value[1]) + "₽.")

            # Возвращаем страницу с результатами запроса
            return render_template(
                "request-view.html",
                description=sum_description,
                keyskills=sum_keyskills,
                salaries=sum_salaries
            )
        else:
            return render_template(
                "request-view.html",
                description=[],
                keyskills=[],
                salaries=[]
            )
    else:
        return redirect("/login")
