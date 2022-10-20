{% extends 'emails/base_email.rst' %}
{% load i18n %}

{% block content %}

{% trans "Resultado da sincronização dos dados de serviços do SIGI com as instâncias instaladas no Rancher." %}

* {% trans "Data/hora de execução" %}: {% now 'SHORT_DATETIME_FORMAT' %}


**{% trans "ERROS ENCONTRADOS" %}**
=====================
{% for tipo, mensagens in erros.items %}
    **{{ tipo.nome|upper }} - {{ tipo.sigla|upper }}**
    {% for m in mensagens %}
    * {{ m }}
    {% endfor %}
{% empty %}
  *{% trans "Nenhum erro encontrado" %}*
{% endfor %}


**{% trans "INFORMAÇÕES ADICIONAIS" %}**
==========================
{% for tipo, mensagens in infos.items %}
    {{ tipo.nome|upper }} - {{ tipo.sigla|upper }}
    {% for m in mensagens %}
        * {{ m }}
    {% endfor %}
{% empty %}
  *{% trans "Nenhuma informação adicional gerada" %}*
{% endfor %}

{% endblock content %}