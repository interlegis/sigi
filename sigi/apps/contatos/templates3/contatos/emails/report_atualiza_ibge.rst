{% extends 'emails/base_email.rst' %}
{% load i18n %}

{% block content %}
{% blocktrans with qtde=uf_novas|length%}{{ qtde }} novas UFs criadas:{% endblocktrans %}
-------------------------------------------------------------------------------

{% for uf in uf_novas %}
    * {{ uf.codigo_ibge }}: {{ uf.sigla }} - {{ uf.nome }}
{% endfor %}

{% blocktrans with qtde=uf_atualizadas|length %}{{ qtde }} UFs atualizadas:{% endblocktrans %}
-------------------------------------------------------------------------------

{% for uf in uf_atualizadas %}
    * {{ uf.codigo_ibge }}: {{ uf.sigla }} - {{ uf.nome }}
{% endfor %}

{% blocktrans with qtde=municipios_novos|length %}{{ qtde }} novos municipios criados:{% endblocktrans %}
-------------------------------------------------------------------------------

{% for m in municipios_novos %}
    * {{ m.codigo_ibge }}: {{ m.nome }}
{% endfor %}

{% blocktrans with qtde=municipios_atualizados|length %}{{ qtde }} municípios atualizados:{% endblocktrans %}
-------------------------------------------------------------------------------

{% for m in municipios_atualizados %}
    * {{ m.codigo_ibge }}: {{ m.nome }}
{% endfor %}

{% blocktrans with qtde=meso_novas|length %}{{ qtde }} novas mesorregiões:{% endblocktrans %}
-------------------------------------------------------------------------------

{% for m in meso_novas %}
    * {{ m.codigo_ibge }}: {{ m.nome }}
{% endfor %}

{% blocktrans with qtde=meso_atualizadas|length %}{{ qtde }} mesorregiões atualizadas{% endblocktrans %}
-------------------------------------------------------------------------------

{% for m in meso_atualizadas %}
    * {{ m.codigo_ibge }}: {{ m.nome }}
{% endfor %}

{% blocktrans with qtde=micro_novas|length %}{{ qtde }} novas microrregiões:{% endblocktrans %}
-------------------------------------------------------------------------------

{% for m in micro_novas %}
    * {{ m.codigo_ibge }}: {{ m.nome }}
{% endfor %}

{% blocktrans with qtde=micro_atualizadas|length%}{{ qtde }} microrregiões atualizadas:{% endblocktrans %}
-------------------------------------------------------------------------------

{% for m in micro_atualizadas %}
    * {{ m.codigo_ibge }}: {{ m.nome }}
{% endfor %}

{% endblock content %}
