{% extends 'emails/base_report.rst' %}
{% load i18n %}

{% block content %}

**{% trans "ERROS ENCONTRADOS" %}**
=====================
{% for tipo, mensagens in report_data.erros.items %}
    **{{ tipo.nome|upper }} - {{ tipo.sigla|upper }}**
    {% for m in mensagens %}
    * {{ m }}
    {% endfor %}
{% empty %}
  *{% trans "Nenhum erro encontrado" %}*
{% endfor %}


**{% trans "INFORMAÇÕES ADICIONAIS" %}**
==========================
{% for tipo, mensagens in report_data.infos.items %}
    {{ tipo.nome|upper }} - {{ tipo.sigla|upper }}
    {% for m in mensagens %}
        * {{ m }}
    {% endfor %}
{% empty %}
  *{% trans "Nenhuma informação adicional gerada" %}*
{% endfor %}

{% endblock content %}