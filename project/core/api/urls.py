from rest_framework import routers

from .views import (
    CouncilViewSet, SessionViewSet, DeputyViewSet, VoteViewSet,
    StatisticByDeputyViewSet
)


router = routers.DefaultRouter()

router.register(r'council', CouncilViewSet, base_name='council')
router.register(r'session', SessionViewSet, base_name='session')
router.register(r'deputy', DeputyViewSet, base_name='deputy')
router.register(r'vote', VoteViewSet, base_name='vote')
router.register(
    r'statistic-deputy',
    StatisticByDeputyViewSet,
    base_name='statistic-deputy'
)


urlpatterns = router.urls
