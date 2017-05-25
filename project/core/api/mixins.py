from rest_framework import serializers
from rest_framework.serializers import Serializer


class VoteSerializerMixin(Serializer):
    """
    Mixin класс для сериализаторов голосования
    """
    types_display = serializers.SerializerMethodField()
    result_display = serializers.SerializerMethodField()

    @staticmethod
    def get_types_display(obj):
        """
        Тип голосования в человеко-понятном виде
        """
        return obj.get_types_display()

    @staticmethod
    def get_result_display(obj):
        """
        Решение голосования в человеко-понятном виде
        """
        return obj.get_result_display()
