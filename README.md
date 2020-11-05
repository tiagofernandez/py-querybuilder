# Py-QueryBuilder

Query builder for [Python](https://python.org/) applications. Designed to work with [MUI-QueryBuilder][mui-querybuilder].

[![python](https://img.shields.io/pypi/pyversions/py-querybuilder.svg)][py-querybuilder]
[![version](https://img.shields.io/pypi/v/py-querybuilder.svg)][py-querybuilder]
[![downloads](https://img.shields.io/pypi/dm/py-querybuilder.svg)][py-querybuilder]

## Installation

Py-QueryBuilder is available as a [pypi package][py-querybuilder].

```sh
pip install py-querybuilder
```

## Usage

Here is a quick example to get you started.
First you'll need a `templates` folder in your module, containing [Jinja2][jinja2] templates with a `{{ where }}` placeholder:

```sql
SELECT *
FROM my_table
WHERE {{ where }}
```

You can now rely on the `QueryBuilder` class to render queries:

```py
from py_querybuilder import QueryBuilder

qb = QueryBuilder("app.articles", [
    {
        "label": "Article",
        "options": [
            {
                "label": "Title",
                "value": "title",
                "type": "text",
            },
            {
                "label": "URL",
                "value": "url",
                "type": "text",
            },
        ],
    },
])
sql_query, sql_params = qb.render("query.sql", {
    "combinator": "and",
    "rules": [
        {
            "field": "title",
            "operator": "contains",
            "value": "Brazil",
        },
    ],
})
```

The query is generated with [JinjaSQL][jinjasql], a template language for SQL statements and scripts.
Since it's based in [Jinja2][jinja2], you have all the power it offers: conditional statements, macros, looping constructs, blocks, inheritance, and more.
We use [sqlparse][sqlparse] to format the queries.

```sql
SELECT *
FROM my_table
WHERE title ~* ? AS "Title"
```

The default operators used for generating queries are:

```py
{
    "after": ">",
    "after_equal": ">=",
    "before": "<",
    "before_equal": "<=",
    "contains": "~*",
    "greater": ">",
    "greater_equal": ">=",
    "equal": "=",
    "in": "in",
    "less": "<",
    "less_equal": "<=",
    "not_contains": "!~*",
    "not_equal": "!=",
    "not_in": "not in",
    "not_null": "is not null",
    "null": "is null",
}
```

In case the database you're targeting uses different operators, it's possible to customize those at `QueryBuilder`'s instantiation:

```py
qb = QueryBuilder(my_module, my_query, operators={
    # Custom operators.
})
```

SQL parameters are returned from `render()` in a list of values corresponding to the placeholders that need to be bound to the query.

```py
print(sql_params)
# ["Brazil"]
```

Finally, you can now use the SQL query and its bind parameters to fetch data.
For example, in Django, you would do something like this:

```py
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute(sql_query, sql_params)

    for row in cursor.fetchall():
        # Do something with the results.
        pass
```

## API

Check out the [API documentation](https://tiagofernandez.com/py-querybuilder/).
To learn more about the query's data structure, and how filters and operators work, please refer to [MUI-QueryBuilder][mui-querybuilder].

## License

This project is licensed under the terms of the [MIT license](/LICENSE).

[jinja2]: https://jinja.palletsprojects.com/
[jinjasql]: https://github.com/hashedin/jinjasql/
[mui-querybuilder]: https://github.com/tiagofernandez/mui-querybuilder/#mui-querybuilder
[py-querybuilder]: https://pypi.org/project/py-querybuilder
[sqlparse]: https://github.com/andialbrecht/sqlparse/
