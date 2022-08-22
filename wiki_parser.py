import requests
from bs4 import BeautifulSoup
from random import randint
from sys import exit


class WikipediaParse:
    def __init__(self, headers: str):
        self.__base_url = 'https://ru.wikipedia.org/wiki/'
        self.__headers = headers

    def __second_fix(self, text):  # финальный фикс текста, вынесен чтобы не мешать
        for i in range(len(text)):
            if '[' in text[i]:
                if '[И' in text[i]:
                    rm = text[i].find('[')
                    text[i] = text[i][:rm] + text[i][-1]
                else:
                    rm = text[i].find('[')
                    text[i] = text[i][:rm] + text[i][rm + 3:]
        return text

    def __wikipedia_thisday_parse_page_ru(self, day):
        """Распарсить страницу с Википедии, соответтсвующуюю выбранному дню. Выкинуть все ненужные строчки и строчки
        с ошибками. """

        full_page = requests.get(f'{self.__base_url}{day}', headers=self.__headers)
        soup = BeautifulSoup(full_page.content, 'html.parser')
        convert = soup.findAll(['div', 'li', 'a', 'ul'], {'class': 'mw-parser-output'})

        try:
            page_text = convert[0].text.split('\n')
        except IndexError:
            exit('Неправильно введен день. Нет такой страницы!')

        borders = []
        for i in range(len(page_text)):
            if 'Категория:События' in page_text[i]:
                borders.append(i)

            if 'Категория:Родившиеся' in page_text[i]:
                borders.append(i)

        if len(borders) == 0:
            for i in range(len(page_text)):
                if 'События' in page_text[i]:
                    borders.append(i)

                if 'Родились' in page_text[i]:
                    borders.append(i)

        parse_text = page_text[borders[-2]:(borders[-1])]

        for i in range(len(parse_text)):
            if '(Источник' in parse_text[i]:
                rm_text = parse_text[i].find(' (Источник')
                parse_text[i] = parse_text[i].replace(parse_text[i][rm_text:], '')

            if not parse_text[i].endswith('.') and len(parse_text[i]) > 10:
                parse_text[i] = '{0}.'.format(parse_text[i])

            if 'XX' in parse_text[i]:
                parse_text[i] = ''

        for i in range(len(parse_text)):
            if not parse_text[i - 1].endswith('.') and parse_text[i - 1] != '':
                parse_text[i] = '{0} — {1}'.format(parse_text[i - 1][:4], parse_text[i])

                if i < (len(parse_text)) - 2:
                    if not parse_text[i + 1].startswith(parse_text[i][:4]):
                        parse_text[i + 1] = '{0} — {1}'.format(parse_text[i][:4], parse_text[i + 1])

        checked_text = []
        for i in range(len(parse_text)):
            if len(parse_text[i]) > 10 and parse_text[i][5] == '—':
                if parse_text[i][7] == ' ':
                    parse_text[i] = parse_text[i][:7] + parse_text[i][8:]
                checked_text.append(parse_text[i])
                # data_text.append(parse_text[i][:4])

        checked_text = self.__second_fix(checked_text)
        for i in range(len(checked_text)):
            checked_text[i] = checked_text[i].replace('\xa0', ' ')

        return checked_text

    def get_data_by_days(self, days: list, event_count=6):
        """Получить выбранное число событий по дням. По умолчанию 6 (интервал 4 часа)."""

        ret_data = {}
        for day in days:
            parsed_data = self.__wikipedia_thisday_parse_page_ru(day)
            rand_parsed_data = set()
            while len(rand_parsed_data) != event_count:  # по 6 постов
                rand_parsed_data.add(parsed_data[randint(0, len(parsed_data) - 1)])
            ret_data[day] = list(rand_parsed_data)

        return ret_data
