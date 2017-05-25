from django.core.management.base import BaseCommand
from django.conf import settings

from ...models import Council, Session, Vote, Deputy, Voice
from ...utils import recalc_vote_results, read_pdf_table

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pandas.core.series import Series
import tqdm

from typing import Optional
from io import FileIO, StringIO
import re
from datetime import datetime, date
import os
from multiprocessing import Process, Queue


class Command(BaseCommand):
    """
    Команда для парсинга данных из pdf файла и сохранения данных в базу данных
    """
    queue = Queue()
    pdf_files = []
    pbars = []

    def handle(self, *args, **options):
        for x in os.listdir(settings.PDF_FILES_PATH):
            if x.endswith('.pdf'):
                self.pdf_files.append(os.path.join(settings.PDF_FILES_PATH, x))

        procs = []
        for file_path in self.pdf_files:
            infile = open(file_path, 'rb')
            pdf_pages_count = len(list(PDFPage.get_pages(infile)))

            proc = Process(
                target=self.get_vote_results_data,
                kwargs={
                    'file_path': file_path,
                    'infile': infile,
                    'pdf_pages_count': pdf_pages_count
                }
            )
            self.pbars.append(tqdm.tqdm(total=pdf_pages_count))
            proc.start()
            procs.append(proc)

        listener = Process(target=self.listener)
        listener.start()

        for proc in procs:
            proc.join()

        self.queue.put(None)
        listener.join()

    def listener(self):
        """
        Обновляем прогресс у прогресс-бара
        """
        for index in iter(self.queue.get, None):
            if index is None:
                continue
            self.pbars[index].update()

    def get_vote_results_data(
            self, file_path: str, infile: FileIO, pdf_pages_count: int
    ):
        """
        Информационные данные о голосовании
        """
        for page in range(pdf_pages_count):
            index = self.pdf_files.index(file_path)
            self.queue.put(index)
            text = self.get_pdf_page_text(infile, page)
            data = text.split('\n')

            # Голосование растянуто на две страницы и мы сейчас на второй стр
            if 'Система поіменного голосування "Рада Голос"' not in text:
                continue

            # Городской совет (например: Броварська міська рада)
            council_title = self.get_council_title(data)
            council, created = Council.objects.get_or_create(
                title=council_title
            )

            # Сессия (например: 18 чергова сесія)
            session_title = self.get_session_title(data)
            # Дата сессии (например: 22.09.16)
            session_date = self.get_session_date(session_title)

            session, created = Session.objects.get_or_create(
                title=session_title, date=session_date
            )

            # Название голосования (например: Про затвердження порядку денного)
            vote_title = self.get_vote_title(text)
            # Тип голосования (например: За основу)
            vote_type = self.get_vote_type(text)

            # Сохраняем данные голосования
            vote, created = Vote.objects.get_or_create(
                title=vote_title,
                types=vote_type,
                council=council,
                session=session
            )

            # Обрабатываем данные с таблиц
            self.get_vote_result_table(vote, page, file_path)

            # Пересчитываем результаты голосования
            recalc_vote_results(vote)

    @staticmethod
    def get_pdf_page_text(infile: FileIO, page: int) -> str:
        """
        Получаем текстовое содержимое указанного файла на указанной странице
        """
        output = StringIO()
        manager = PDFResourceManager()
        converter = TextConverter(manager, output, laparams=LAParams())
        interpreter = PDFPageInterpreter(manager, converter)

        for current_page in PDFPage.get_pages(infile, [page]):
            interpreter.process_page(current_page)

        # Получаем текст из StringIO
        text = output.getvalue()

        # Очищаем данные
        converter.close()
        output.close()

        return text

    @staticmethod
    def get_council_title(data: list) -> str:
        """
        Получаем название сессии
        """
        return next(filter(lambda x: x.endswith('рада'), data))

    @staticmethod
    def get_session_title(data: list) -> str:
        """
        Получаем название голосования
        """
        return next(filter(lambda x: re.search(r'(\d+.\d+.\d+)', x), data))

    @staticmethod
    def get_session_date(string: str) -> date:
        """
        Получаем дату сессии созыва из строки
        """
        match = re.search(r'(\d+.\d+.\d+)', string)
        if match:
            return datetime.strptime(match.group(), '%d.%m.%y').date()
        raise ValueError(
            'В строке должна присутствовать дата в формате dd.mm.yy'
        )

    @staticmethod
    def get_vote_title(string: str) -> str:
        """
        Получаем название голосования ис строки
        """
        match = re.search(
            r'Результат поіменного голосування:(.*)№:', string, flags=re.DOTALL
        )
        if match:
            # Переходы на новую строку и множественные пробелы
            # заменяем на один пробел
            return re.sub('(\\n| )+', ' ', match.group(1).rstrip('\n').strip())
        raise ValueError('Название голосования не найдено')

    @staticmethod
    def get_vote_type(string: str) -> Optional[int]:
        """
        Получаем тип голосования из строки.
        Тип есть не у всех голосований.
        """
        match = re.search(
            r'(За основу|За пропозицію|В цілому|За правку)', string
        )
        if match:
            return next(
                filter(lambda x: x[1] == match.group(), Vote.TYPES)
            )[0]
        return None

    def get_vote_result_table(self, vote: Vote, page: int, file_path: str):
        """
        Обрабатываем данные с таблиц
        """
        df = read_pdf_table(
            file_path, **{'pages': page, 'silent': True}
        )

        # На странице может не быть таблиц
        if df is None:
            return

        head = list(df.head())
        active_deputies = []

        # Таблица слева
        full_name1 = df[head[1]].fillna('')
        if len(head) == 8:
            vote_result1 = df[head[3]].fillna('')
        else:
            vote_result1 = df[head[2]].fillna('')

        active_deputies += self.create_voice(vote, full_name1, vote_result1)

        # Таблица справа
        if len(head) == 8:
            full_name2 = df[head[5]].fillna('')
            vote_result2 = df[head[7]].fillna('')
        else:
            full_name2 = df[head[4]].fillna('')
            vote_result2 = df[head[5]].fillna('')

        active_deputies += self.create_voice(vote, full_name2, vote_result2)

        # Возможно сменился состав депутатов. Удаляем которых больше нет
        Voice.objects.filter(vote=vote)\
                     .exclude(deputy__in=active_deputies)\
                     .delete()

    @staticmethod
    def create_voice(
            vote: Vote, full_name: Series, vote_result: Series
    ) -> list:
        """
        Сохраняем данные таблиц
        """
        active_deputies = []

        for i in range(1, len(full_name)):
            # Если не указано значение голосования - из-за длинного имени
            # ячейка занимает 2 строки
            if not vote_result[i]:
                if i + 1 < len(full_name):
                    full_name[i + 1] = '{} {}'.format(full_name[i],
                                                      full_name[i + 1])
                continue

            # Получаем депутата
            deputy, created = Deputy.objects.get_or_create(
                full_name=full_name[i].strip()
            )
            active_deputies.append(deputy.pk)

            if full_name[i].strip() == '2':
                raise AssertionError

            # Получаем значение голосования
            voice_result = next(
                filter(lambda x: x[1] == vote_result[i], Voice.RESULT)
            )

            # Сохраняем результаты
            Voice.objects.get_or_create(
                deputy=deputy, vote=vote, result=voice_result[0]
            )

        return active_deputies
