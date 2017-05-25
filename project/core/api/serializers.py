from rest_framework import serializers

from ..models import Council, Session, Vote, Deputy, Voice
from .mixins import VoteSerializerMixin


class CouncilSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели Council
    """
    class Meta:
        model = Council
        fields = '__all__'


class SessionSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели Session
    """
    class Meta:
        model = Session
        fields = '__all__'


class DeputySerializer(serializers.ModelSerializer):
    """
    Сериализатор модели Deputy
    """

    class Meta:
        model = Deputy
        fields = '__all__'


class VoteListSerializer(
    VoteSerializerMixin,
    serializers.HyperlinkedModelSerializer
):
    """
    Сериализатор списка модели Vote
    """
    class Meta:
        model = Vote
        fields = ('url', 'title', 'types_display', 'result_display',
                  'council', 'session')


class VoteDetailSerializer(
    VoteSerializerMixin,
    serializers.HyperlinkedModelSerializer
):
    """
    Сериализатор деталей модели Vote
    """
    voices = serializers.SerializerMethodField()

    class Meta:
        model = Vote
        fields = '__all__'

    @staticmethod
    def get_voices(obj):
        voices = Voice.objects.filter(vote=obj)
        serializer = VoiceSerializer(voices, many=True)
        return serializer.data


class VoiceSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели Voice
    """
    result_display = serializers.SerializerMethodField()
    deputy_display = serializers.SerializerMethodField()

    class Meta:
        model = Voice
        fields = ('result_display', 'deputy_display')

    @staticmethod
    def get_result_display(obj):
        return obj.get_result_display()

    @staticmethod
    def get_deputy_display(obj):
        return obj.deputy.full_name
