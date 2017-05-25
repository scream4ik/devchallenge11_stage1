from django.test import TestCase

from ..models import Vote, Voice, Council, Session, Deputy
from ..utils import recalc_vote_results


class RecalcVoteResultsTest(TestCase):
    """
    Тесты для функции recalc_vote_results
    """
    def setUp(self):
        council = Council.objects.create(title='Броварська міська рада')
        session = Session.objects.create(
            title='18 чергова сесія', date='2016-09-22'
        )
        self.vote = Vote.objects.create(
            council=council, session=session, result=2
        )

        self.deputy1 = Deputy.objects.create(
            full_name='Іваненко Валерій Іванович'
        )
        self.deputy2 = Deputy.objects.create(
            full_name='Веремчук Ірина Сергіївна'
        )
        Voice.objects.create(deputy=self.deputy1, vote=self.vote, result=1)
        Voice.objects.create(deputy=self.deputy2, vote=self.vote, result=1)

    def test_recalc_vote_results(self):
        self.assertEqual(self.vote.agree, 0)
        self.assertEqual(self.vote.result, 2)

        recalc_vote_results(self.vote)

        self.assertEqual(self.vote.agree, 2)
        self.assertEqual(self.vote.result, 1)
