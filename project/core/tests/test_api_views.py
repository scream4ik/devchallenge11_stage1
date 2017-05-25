from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from ..models import Council, Session, Deputy, Vote, Voice


class TestListMixin:
    """
    Mixin класс для тестов смежных данных представления списка данных
    """
    def test_list(self):
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), self.list_response_count)
        self.assertEqual(
            tuple(next(iter(response.data)).keys()), self.list_fields
        )


class CouncilViewSetTest(TestListMixin, APITestCase):
    """
    Тестирование представления CouncilViewSet
    """
    url_list = reverse('council-list')
    list_fields = ('id', 'title')

    def setUp(self):
        Council.objects.create(title='Броварська міська рада')
        self.list_response_count = Council.objects.count()


class SessionViewSetTest(TestListMixin, APITestCase):
    """
    Тестирование представления SessionViewSet
    """
    url_list = reverse('session-list')
    list_fields = ('id', 'title', 'date')

    def setUp(self):
        Session.objects.create(title='18 чергова сесія', date='2016-09-22')
        self.list_response_count = Session.objects.count()


class DeputyViewSetTest(TestListMixin, APITestCase):
    """
    Тестирование представления DeputyViewSet
    """
    url_list = reverse('deputy-list')
    list_fields = ('id', 'full_name')

    def setUp(self):
        Deputy.objects.create(full_name='Іваненко Валерій Іванович')
        self.list_response_count = Deputy.objects.count()


class VoteViewSetTest(TestListMixin, APITestCase):
    """
    Тестирование представления VoteViewSet
    """
    url_list = reverse('vote-list')
    list_fields = ('url', 'title', 'types_display', 'result_display',
                   'council', 'session')

    def setUp(self):
        council = Council.objects.create(title='Броварська міська рада')
        session = Session.objects.create(
            title='18 чергова сесія', date='2016-09-22'
        )
        self.vote = Vote.objects.create(council=council, session=session)

        self.deputy1 = Deputy.objects.create(
            full_name='Іваненко Валерій Іванович'
        )
        self.deputy2 = Deputy.objects.create(
            full_name='Веремчук Ірина Сергіївна'
        )
        Voice.objects.create(deputy=self.deputy1, vote=self.vote, result=1)
        Voice.objects.create(deputy=self.deputy2, vote=self.vote, result=1)

        self.list_response_count = Vote.objects.count()

    def test_retrieve(self):
        response = self.client.get(reverse('vote-detail', args=[self.vote.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        fields = ('url', 'types_display', 'result_display', 'voices', 'title',
                  'types', 'agree', 'disagree', 'abstained',
                  'did_not_participate', 'absent', 'result', 'council',
                  'session')
        self.assertEqual(tuple(response.data.keys()), fields)

        voices_fields = ('result_display', 'deputy_display')
        voices_keys = tuple(next(iter(response.data['voices'])).keys())
        self.assertEqual(voices_keys, voices_fields)
        self.assertEqual(len(response.data['voices']), 2)


class StatisticByDeputyViewSetTest(APITestCase):
    """
    Тестирование представления StatisticByDeputyViewSet
    """
    url_list = reverse('statistic-deputy-list')
    deputy_name1 = 'Іваненко Валерій Іванович'
    deputy_name2 = 'Веремчук Ірина Сергіївна'

    def setUp(self):
        council = Council.objects.create(title='Броварська міська рада')
        session = Session.objects.create(
            title='18 чергова сесія', date='2016-09-22'
        )
        vote = Vote.objects.create(council=council, session=session)

        deputy1 = Deputy.objects.create(full_name=self.deputy_name1)
        deputy2 = Deputy.objects.create(full_name=self.deputy_name2)

        Voice.objects.create(deputy=deputy1, vote=vote, result=1)
        Voice.objects.create(deputy=deputy2, vote=vote, result=1)

    def test_list(self):
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['detail'],
            'Необходимо указать GET параметр "q" с ФИО депутата'
        )

        response = self.client.get('{}?q=Test'.format(self.url_list))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Депутат Test не найден')

        response = self.client.get('{}?q=Test&date=d'.format(self.url_list))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['detail'], 'Формат даты не соответствует dd-mm-YYYY'
        )

        response = self.client.get(
            '{}?q={}'.format(self.url_list, self.deputy_name1)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {self.deputy_name2: 100.0})

        response = self.client.get(
            '{}?q={}&date=20-12-2012'.format(self.url_list, self.deputy_name1)
        )
        self.assertEqual(response.data, {self.deputy_name2: 0.0})

        response = self.client.get(
            '{}?q={}&date=22-09-2016'.format(self.url_list, self.deputy_name1)
        )
        self.assertEqual(response.data, {self.deputy_name2: 100.0})
