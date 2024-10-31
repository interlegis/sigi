{% extends 'emails/base_email.rst' %}
{% load i18n %}

{% block title %}
  {{ block.super }}
**{% trans "Início:" %} {{ start_time|date:"SHORT_DATETIME_FORMAT" }}**
**{% trans "Término:" %} {{ end_time|date:"SHORT_DATETIME_FORMAT" }}**

{% endblock %}

{% block content %}
{% trans "RESULTADO" %}
=========

{% for row in report_data %}{{ row }}
{% endfor %}
{% endblock content %}