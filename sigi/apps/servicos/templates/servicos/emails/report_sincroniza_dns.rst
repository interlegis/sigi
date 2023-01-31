{% extends 'emails/base_report.rst' %}
{% load i18n %}

{% block content %}
{% for uf, dados in report_data.items %}
{% if dados.erros or dados.infos or dados.sumario.total > 0 or dados.sumario.novos > 0 or dados.sumario.atualizados > 0 or dados.sumario.desativados > 0 or dados.sumario.ignorados > 0 %}
**{{ uf|upper }}**
=========================================

{% if dados.sumario.total > 0 or dados.sumario.novos > 0 or dados.sumario.atualizados > 0 or dados.sumario.desativados > 0 or dados.sumario.ignorados > 0%}
  **{% trans "SUMÁRIO" %}:**

  - Total de registros no DNS: {{ dados.sumario.total }}
  - Registros criados no SIGI: {{ dados.sumario.novos }}
  - Registros atualizados no SIGI: {{ dados.sumario.atualizados }}
  - Registros desativados no SIGI: {{ dados.sumario.desativados }}
  - Registros do DNS ignorados: {{ dados.sumario.ignorados }}
{% endif %}
{% if dados.erros %}

  **{% trans "ERROS" %}:**

  {% for m in dados.erros %}
  * {{ m }}
  {% endfor %}
{% endif %}

{% if dados.infos %}

  **{% trans "INFORMAÇÕES ADICIONAIS" %}:**

  {% for m in dados.infos %}
    * {{ m }}
  {% endfor %}
{% endif %}
{% endif %}
{% endfor %}

{% endblock content %}