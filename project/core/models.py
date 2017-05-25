from django.db import models


class Council(models.Model):
    """
    Модель городского совета
    """
    title = models.CharField('название', max_length=100, unique=True)

    class Meta:
        verbose_name = 'совет'
        verbose_name_plural = 'городской совет'
        ordering = ('title',)

    def __str__(self):
        return self.title


class Session(models.Model):
    """
    Модель сессии созыва
    """
    title = models.CharField('название', max_length=100, unique=True)
    date = models.DateField('дата')

    class Meta:
        verbose_name = 'сессию'
        verbose_name_plural = 'сессии'
        ordering = ('title',)

    def __str__(self):
        return self.title


class Vote(models.Model):
    """
    Модель информации о голосовании
    """
    TYPES = (
        (1, 'За основу'),
        (2, 'За пропозицію'),
        (3, 'В цілому'),
        (4, 'За правку'),
    )
    RESULT = (
        (1, 'Принято'),
        (2, 'Не принято'),
    )
    title = models.TextField('название')
    types = models.SmallIntegerField(
        'тип',
        choices=TYPES,
        blank=True,
        null=True
    )
    council = models.ForeignKey(Council, verbose_name='городской совет')
    session = models.ForeignKey(Session, verbose_name='сессия')
    # Результаты голосования
    agree = models.SmallIntegerField('за', default=0)
    disagree = models.SmallIntegerField('против', default=0)
    abstained = models.SmallIntegerField('воздержались', default=0)
    did_not_participate = models.SmallIntegerField(
        'не принимали участие',
        default=0
    )
    absent = models.SmallIntegerField('отсуствуют', default=0)
    result = models.SmallIntegerField(
        'решение',
        choices=RESULT,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'голосование'
        verbose_name_plural = 'голосования'

    def __str__(self):
        return self.title


class Deputy(models.Model):
    """
    Модель депутатов
    """
    full_name = models.CharField('ФИО', max_length=100, unique=True)

    class Meta:
        verbose_name = 'депутата'
        verbose_name_plural = 'депутаты'

    def __str__(self):
        return self.full_name


class Voice(models.Model):
    """
    Модель голосов депутатов в голосовании
    """
    RESULT = (
        (1, 'За'),
        (2, 'Проти'),
        (3, 'Утримався'),
        (4, 'Не голосував'),
        (5, 'Відсутній'),
    )
    deputy = models.ForeignKey(Deputy, verbose_name='депутат')
    vote = models.ForeignKey(Vote, verbose_name='голосование')
    result = models.SmallIntegerField('результат', choices=RESULT)

    class Meta:
        verbose_name = 'голос'
        verbose_name_plural = 'голоса'
        unique_together = ('deputy', 'vote')

    def __str__(self):
        return '{} - {} - {}'.format(
            self.deputy.__str__(),
            self.vote.__str__(),
            self.get_result_display()
        )
