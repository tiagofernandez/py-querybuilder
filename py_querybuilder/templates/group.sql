{% if rules|length > 1 %}
(
{% endif %}

{% for rule in rules %}
    {% include "rule.sql" %}

    {% if not loop.last %}
        {{ combinator | sqlsafe }}
    {% endif %}
{% endfor %}

{% if rules|length > 1 %}
)
{% endif %}
