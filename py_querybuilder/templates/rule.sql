{% if rule.combinator is defined %}
    {% set combinator = rule.combinator %}
    {% set rules = rule.rules %}
    {% include "group.sql" %}

{% else %}
    {% set sql_operator = operators[rule.operator] %}
    {% set sql_value = rule.value %}

    {{ rule.field | sqlsafe }} {{ sql_operator | sqlsafe }}
        {% if sql_value is defined and sql_value is not none %}
            {% if rule.operator in ('in', 'not_in') %}
                {{ sql_value | inclause }}
            {% else %}
                {{ sql_value }}
            {% endif %}
        {% endif %} as "{{ fields[rule.field].label | sqlsafe }}"
{% endif %}
