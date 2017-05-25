from .models import Vote, Voice

from tabula.wrapper import jar_path, localize_file, build_options

import os
import subprocess
from subprocess import DEVNULL
import json
import pandas as pd
import io


def recalc_vote_results(vote: Vote):
    """
    Функция перерасчёта результатов голосования
    """
    vote.agree = Voice.objects.filter(vote=vote, result=1).count()
    vote.disagree = Voice.objects.filter(vote=vote, result=2).count()
    vote.abstained = Voice.objects.filter(vote=vote, result=3).count()
    vote.did_not_participate = Voice.objects.filter(vote=vote, result=4)\
                                            .count()
    vote.absent = Voice.objects.filter(vote=vote, result=5).count()

    if vote.agree > vote.disagree:
        vote.result = 1
    else:
        vote.result = 2

    vote.save()


def read_pdf_table(input_path, **kwargs):
    """
    Мы делаем копию функции read_pdf_table из библиотеки tabula
    из-за того, что родная функция выводит stderr.
    Мы же направляем вывод stderr в /dev/null
    """
    output_format = kwargs.get('output_format', 'dataframe')

    if output_format == 'dataframe':
        kwargs.pop('format', None)

    elif output_format == 'json':
        kwargs['format'] = 'JSON'

    options = build_options(kwargs)
    path, is_url = localize_file(input_path)
    args = ["java", "-jar", jar_path] + options + [path]

    try:
        output = subprocess.check_output(args, stderr=DEVNULL)
    finally:
        if is_url:
            os.unlink(path)

    if len(output) == 0:
        return

    encoding = kwargs.get('encoding', 'utf-8')

    fmt = kwargs.get('format')
    if fmt == 'JSON':
        return json.loads(output.decode(encoding))

    else:
        return pd.read_csv(io.BytesIO(output), encoding=encoding)
