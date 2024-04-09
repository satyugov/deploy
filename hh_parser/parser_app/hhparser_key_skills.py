import json

# HHParserKeySkills класс предназначен для обработки описаний вакансий
# полученных с сайта hh.ru
# В каждом описании вакансии парсер определяет какие технологии были
# востребованы и возвращает их список

class HHParserKeySkills():
    def __init__(self):
        self._l_found_technology = []

    def parse(self, vacancy: json) -> list:
        """

        :param vacancy:  принимает словарь с параметрами вакансии
        :return:
        """
        self._l_found_technology = []
        # обращаемся к значению словаря по ключу и получаем список словарей навыков
        # текущей вакансии, например: [{"name": "Python"}, {"name": "Linux"}]
        self._l_skills = vacancy["key_skills"]
        if self._l_skills:
            self._find_technology()
        else:
            # Если навыков повакансии не обнаружно, то список оставляем пустым
            self._l_found_technology =[]
        # В итоговом списке навыков убираем дубли
        return list(set(self._l_found_technology))

    def _find_technology(self) -> None:
        """
        Метод для определения ключевых слов по технологиям
        В нем перебираем словари списка, получаем в каждом словаре
        название навыков и вносим их в список l_found_technology
        :return:
        """
        for tec_dic in self._l_skills:
            self._l_found_technology.append(tec_dic["name"])

if __name__ == "__main__":
    pass