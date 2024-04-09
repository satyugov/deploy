import requests as req

"""
     Класс HHRequest осуществляет обращение к сайту hh.ru с помощью api  
     для поиска вакансий по указанной тематики и обрабатывает 
     найденные объявления для получения списка требуемых технологий.
"""


class HHRequest:
    def __init__(self, hhparser):
        self._s_search_pattern = "" # запрос на парсинг, т.е. строка, по которой мы ищем данные
        self._l_ignore_terms = []
        self._l_double_terms = []
        self._s_url = "" # адрес ресурса, на который мы отправляем запрос на парсинг
        self._l_url_vacancies = [] # список ссылок на вакансии, полученные через API
        self._o_parser = hhparser # объект парсера
        self._i_region_id = 0 # идентификатор региона, по которому выполняется парсинг

    def set_search_pattern(self, pattern: str) -> None:
        """Устанавливаем текст запрос на парсинг"""
        self._s_search_pattern = pattern

    def set_url(self, url: str) -> None:
        """Устанавливаем адрес ресурса"""
        self._s_url = url

    def set_region(self, name: str) -> None:
        """
        Устанавливаем регион парсинга, например,
        {'text': 'Москва'}
        """
        j_params = {"text": name}
        j_result = req.get("http://api.hh.ru/suggests/areas", params=j_params).json()
        if j_result["items"]:
            self._i_region_id = j_result["items"][0]["id"]
            return j_result
        else:
            raise ValueError("Регион не найден.")

    def set_parser(self, hhparser):
        """Устанавливаем текущий парсер"""
        self._o_parser = hhparser

    def get_url_vacancies(self) -> list:
        """
        Определяем метод для формирования списка ссылок на вакансии,
        полученные через API.
        Например:
        [
        'https://api.hh.ru/vacancies/90415076?host=hh.ru',
        'https://api.hh.ru/vacancies/90975594?host=hh.ru',
        ]
        :return:
        """
        if not self._s_url:
            raise ValueError("Не задан адрес сайта.")

        if not self._s_search_pattern:
            raise ValueError("Не заданы критерии поиска.")

        if self._i_region_id == 0:
            raise ValueError("Не задан регион поиска.")

        self._s_url = self._s_url.replace("#", self._i_region_id)
        self._l_url_vacancies.clear()

        i_page_number = 0
        while True:
            j_params = {
                "text": self._s_search_pattern,
                "page": i_page_number,
                "per_page": 100
            }
            j_result = req.get(self._s_url, params=j_params)

            if j_result.status_code != 200:
                return []

            j_result = j_result.json()
            if not j_result["items"]:
                break

            for j_item in j_result["items"]:
                self._l_url_vacancies.append(j_item["url"])

            if j_result["page"] >= j_result["pages"] - 1:
                break
            else:
                i_page_number += 1

            return self._l_url_vacancies

    def process_url(self, url: str) -> list:
        """
        С помощью данного выражения self._o_parser.parse мы вызываем парсинг
        (метод parse()) уже с помощью конкретного парсера
        (у нас их буде три – для описания, навыков и зарплаты)
        :param url:
        :return:
        """
        return self._o_parser.parse(req.get(url).json())

