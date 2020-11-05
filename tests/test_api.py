# -*- coding: utf-8 -*-

from py_querybuilder.api import QueryBuilder

from .fixtures import filters, query


this_package = __name__.split(".")[0]


def assert_sql_equal(first, second):
    assert QueryBuilder.format_sql(first) == QueryBuilder.format_sql(second)


class TestQueryBuilder:
    def test_init(self):
        assert QueryBuilder(this_package, filters)._fields == {
            "title": {"label": "Title", "type": "text"},
            "url": {"label": "URL", "type": "text"},
            "word_count": {"label": "Word Count", "type": "integer"},
            "rating": {"label": "Rating", "type": "number"},
            "is_redirect": {"label": "Is Redirect", "type": "radio"},
            "published": {"label": "Published", "type": "switch"},
            "updated_date": {"label": "Updated Date", "type": "date"},
            "user_roles": {"label": "User Roles", "type": "multiselect"},
            "author_status": {"label": "Author Status", "type": "select"},
        }

    def test_render(self):
        qb = QueryBuilder(this_package, filters)
        sql_query, sql_params = qb.render("query.sql", query)

        assert_sql_equal(
            sql_query,
            """SELECT *
            FROM my_table
            WHERE (is_redirect = ? AS "Is Redirect"
                AND updated_date >= ? AS "Updated Date"
                AND title IS NOT NULL AS "Title"
                AND url ~* ? AS "URL"
                AND word_count < ? AS "Word Count"
                AND rating > ? AS "Rating"
                AND (author_status != ? AS "Author Status"
                        OR user_roles in (?, ?, ?) AS "User Roles"))""",
        )
        assert sql_params == [
            False,
            "2020-08-20",
            "France",
            420,
            4.2,
            "terminated",
            "expert",
            "site_contributor",
            "staff",
        ]

    def test_render_pruning_fields(self):
        qb = QueryBuilder(this_package, filters)
        sql_query, sql_params = qb.render(
            "query.sql",
            {
                "combinator": "and",
                "rules": [
                    {
                        "field": "is_redirect",
                        "operator": "equal",
                        "value": True,
                    },
                    {
                        "field": "unknown",
                        "operator": "equal",
                        "value": "N/A",
                    },
                    {
                        "combinator": "or",
                        "rules": [
                            {
                                "field": "unknown",
                                "operator": "null",
                            },
                            {
                                "field": "user_roles",
                                "operator": "in",
                                "value": ["expert", "site_contributor"],
                            },
                            {
                                "combinator": "or",
                                "rules": [
                                    {
                                        "field": "word_count",
                                        "operator": "less",
                                        "value": 420,
                                    },
                                    {
                                        "field": "unknown",
                                        "operator": "not_null",
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
        )
        assert_sql_equal(
            sql_query,
            """SELECT *
            FROM my_table
            WHERE (is_redirect = ? AS "Is Redirect"
                AND (user_roles in (?,
                                    ?) AS "User Roles"
                        OR word_count < ? AS "Word Count"))
            """,
        )
        assert sql_params == [
            True,
            "expert",
            "site_contributor",
            420,
        ]
