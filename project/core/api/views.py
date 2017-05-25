from rest_framework import viewsets
from rest_framework.exceptions import ParseError
from rest_framework.response import Response

from .serializers import (
    CouncilSerializer, SessionSerializer, DeputySerializer, VoteListSerializer,
    VoteDetailSerializer
)
from ..models import Council, Session, Deputy, Vote, Voice

from datetime import datetime


class CouncilViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API точка позволяющая просматривать городские советы
    """
    queryset = Council.objects.all()
    serializer_class = CouncilSerializer


class SessionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API точка позволяющая просматривать сессии
    """
    queryset = Session.objects.all()
    serializer_class = SessionSerializer


class DeputyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API точка позволяющая просматривать депутатов
    """
    queryset = Deputy.objects.all()
    serializer_class = DeputySerializer


class VoteViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API точка позволяющая просматривать голосования
    """
    queryset = Vote.objects.select_related('council', 'session')
    serializer_class = VoteListSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = VoteDetailSerializer(
            instance, context={'request': request}
        )
        return Response(serializer.data)


class StatisticByDeputyViewSet(viewsets.GenericViewSet):
    """
    Статистика в процентах по депутатам, которые раще голосуют одинаково
    односительно заданного депутата.
    ФИО депутата необходимо задать GET параметром "q".
    Для фильрации данных по дате необходимо задать GET параметр "date"
        - опционально
        - формат: dd-mm-YYYY
    """
    @staticmethod
    def list(request, *args, **kwargs):
        if not request.GET.get('q'):
            raise ParseError(
                detail='Необходимо указать GET параметр "q" с ФИО депутата'
            )

        date = None
        if request.GET.get('date'):
            try:
                date = datetime.strptime(
                    request.GET['date'], "%d-%m-%Y"
                ).date()
            except ValueError:
                raise ParseError('Формат даты не соответствует dd-mm-YYYY')

        try:
            search_deputy = Deputy.objects.get(full_name=request.GET['q'])
        except Deputy.DoesNotExist:
            raise ParseError(
                detail='Депутат {} не найден'.format(request.GET['q'])
            )

        search_deputy_voices = Voice.objects.filter(deputy=search_deputy)\
                                            .values_list('result', flat=True)
        if date is not None:
            search_deputy_voices = search_deputy_voices.filter(
                vote__session__date=date
            )

        result = {}
        vote_count = Vote.objects.count()

        for deputy in Deputy.objects.exclude(pk=search_deputy.pk):
            v = Voice.objects.filter(deputy=deputy)\
                             .values_list('result', flat=True)
            if date is not None:
                v = v.filter(vote__session__date=date)
            q = len([i for i, j in zip(search_deputy_voices, v) if i == j])
            result[deputy.full_name] = q * 100 / vote_count

        return Response(result)
