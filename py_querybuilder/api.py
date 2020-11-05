# -*- coding: utf-8 -*-

import copy
import logging
from typing import List, Tuple

from jinja2 import Environment, PackageLoader

from jinjasql import JinjaSql

import sqlparse


logger = logging.getLogger(__name__)


class QueryBuilder:
    """Relies on Jinja2 templates & JinjaSql to generate SQL statements.

    Usage::

      # Assuming the target module has a template with {{ where }}:
      with open("app/articles/templates/query.sql", "r") as f:
          print(f.read())
          # SELECT *
          # FROM my_table
          # WHERE {{ where }}

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
                  "value": "France",
              },
          ],
      })

      print(sql_query)
      # SELECT *
      # FROM my_table
      # WHERE title ~* ? AS "Title"

      print(sql_params)
      # ["France"]
    """

    __env = Environment(loader=PackageLoader(__name__), autoescape=True)
    __jql = JinjaSql(__env, param_style="qmark")

    def __init__(self, package_name: str, filters: list, operators: dict = None) -> None:
        """Initializes the `QueryBuilder` instance with package name and filters.

        :param package_name: Target module containing a `templates` folder.
        :param filters: The filters object is a list of grouped dictionaries
            with label `str` and options `list` properties. Each option is a
            dictionary with label `str`, value `str`, and type `str`. The
            label can be anything, but the value must be an unique key, used
            by each field in a ruleset. In case an option's type is "select"
            or "multiselect", it will require a nested options `list` property
            with label & value items.
        :param operators: The operators object is a dictionary for translating
            known operators to their SQL equivalents.
        """
        self._tpl_env = Environment(loader=PackageLoader(package_name))  # noqa S701
        self._fields = dict(
            {
                f["value"]: {
                    "label": f["label"],
                    "type": f["type"],
                }
                for f in sum([i["options"] for i in filters or []], [])
            }.items()
        )
        self._operators = operators or {
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

    def pre_process_query(self, query: dict) -> dict:
        """Hook for pre-processing the query before rendering.

        :param query: The query to be rendered.
        :returns: A new query object, with uknown fields pruned out.
        """
        query_copy = copy.deepcopy(query)

        def prune_unknown_fields(rules):
            result = []
            for r in rules:
                if "rules" in r:
                    r["rules"] = prune_unknown_fields(r["rules"])
                    result.append(r)
                elif r["field"] in self._fields:
                    result.append(r)
            return result

        query_copy["rules"] = prune_unknown_fields(query_copy["rules"])
        return query_copy

    def render(self, template_name: str, query: dict) -> Tuple[str, List]:
        """Renders a SQL statement provided a query object.

        :param template_name: The template file under the `templates` folder.
        :param query: The query object is a recursive data structure composed of
            combinator 'str' and rules `list` properties. Each rule is an object
            with field 'str', operator 'str', and value (anything, depending on
            the field's type). In case the rule contains a combinator property,
            it's considered a nested group.

        :returns: The rendered query and its parameters.
        """
        clean_query = self.pre_process_query(query)

        group_tpl = QueryBuilder.__env.get_template("group.sql")
        where_tpl, where_params = QueryBuilder.__jql.prepare_query(
            group_tpl,
            clean_query | {"fields": self._fields, "operators": self._operators},
        )
        tpl = self._tpl_env.get_template(template_name)
        sql_query = tpl.render({"where": where_tpl})
        sql_query = QueryBuilder.format_sql(sql_query)

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"\n{sql_query}")

        return sql_query, where_params

    @staticmethod
    def format_sql(sql_query: str) -> str:
        """Formats a SQL query by uppercasing keywords and reindenting it.

        :param sql_query: The query to be formatted.
        :returns: The formatted query.
        """
        return sqlparse.format(sql_query, keyword_case="upper", reindent=True)
