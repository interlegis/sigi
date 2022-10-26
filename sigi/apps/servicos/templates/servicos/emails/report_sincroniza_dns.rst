{% extends 'emails/base_email.rst' %}
{% load i18n %}

{% block content %}

{% trans "Resultado da sincronização dos dados de serviços de registro do SIGI com os registros encontrados no DNS." %}

* {% trans "Data/hora de execução" %}: {% now 'SHORT_DATETIME_FORMAT' %}

{% for uf, dados in log.items %}
**{{ uf|upper }}**
=========================================


  **SUMÁRIO:**


  - Total de registros no DNS: {{ dados.sumario.total }}
  - Registros criados no SIGI: {{ dados.sumario.novos }}
  - Registros atualizados no SIGI: {{ dados.sumario.atualizados }}
  - Registros desativados no SIGI: {{ dados.sumario.desativados }}
  - Registros do DNS ignorados: {{ dados.sumario.ignorados }}


  **ERROS:**

  {% for m in dados.erros %}
  * {{ m }}
  {% empty %}
  *{% trans "Nenhum erro encontrado" %}*
  {% endfor %}


  **{% trans "INFORMAÇÕES ADICIONAIS" %}**

  {% for m in dados.infos %}
    * {{ m }}
  {% empty %}
    *{% trans "Nenhuma informação adicional gerada" %}*
  {% endfor %}
{% endfor %}

{% endblock content %}