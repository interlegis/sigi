{% extends 'emails/base_email.rst' %}
{% load i18n %}

{% block content %}
{% blocktrans %}UM ERRO OCORREU NO PROCESSO DE IMPORTAÇÃO DE {{ process_name }}{% endblocktrans %}

{% trans "VERIFIQUE O LOG DO SIGI PARA MAIORES DETALHES" %}

* {% trans "Data/hora de execução" %}: {% now 'SHORT_DATETIME_FORMAT' %}

::{% autoescape off %}{% for error_row in traceback %}
  {{ error_row }}
{% endfor %}
{% endautoescape %}

{% endblock content %}