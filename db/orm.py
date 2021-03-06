from __future__ import annotations
import inspect
import sqlite3


SQLITE_TYPE_MAP = {
    int: 'INTEGER',
    float: 'REAL',
    str: 'TEXT',
    bytes: 'BLOB',
    bool: 'INTEGER',
}
CREATE_TABLE_SQL = 'CREATE TABLE {name} ({fields});'
SELECT_TABLES_SQL = "SELECT name FROM sqlite_master WHERE type = 'table';"
INSERT_SQL = "INSERT INTO {table} ({fields}) VALUES ({placeholders});"
SELECT_ALL_SQL = "SELECT {fields} from {table};"
SELECT_WHERE_SQL = "SELECT {fields} from {table} WHERE {query};"


class Database:
    _instance = None

    def __new__(cls, db_name: str) -> None:
        if not cls._instance:
            cls._instance = object.__new__(cls, db_name)
            cls._instance._connection = sqlite3.Connection(db_name)
        return cls._instance

    # def __init__(self):
    #     self._cursor = self._connection.cursor()

    def create(self, table: Table):
        self._execute(table._get_create_sql())

    def _execute(self, sql, params):
        if params:
            return self._connection.execute(sql, params)
        return self._connection.execute(sql)

    @property
    def tables(self):
        return [row[0] for row in self._execute(SELECT_TABLES_SQL).fetchall()]

    def save(self, instance):
        sql, values = instance._get_insert_sql()
        cursor = self._execute(sql, values)
        cursor._data['id'] = cursor.lastrowid

    def all(self, table: Table):
        sql, fields = table._get_select_all_sql()
        result = []
        for row in self._execute(sql).fetchall():
            data = dict(zip(fields, row))
            result.append(table(**data))
        return result

    def get(self, table, id):
        sql, fields, params = table._get_select_where_sql(id=id)
        row = self._execute(sql, params).fetchone()
        data = dict(zip(fields, row))
        return table(**data)


class Table:
    def __init__(self, **kwargs):
        self._data = {
            'id': None,
        }
        for key, value in kwargs.items():
            self._data[key] = value

    def __getattribute__(self, key):
        _data = object.__getattribute__(self, '_data')
        if key in _data:
            return _data[key]
        return object.__getattribute__(self, key)

    @classmethod
    def _get_name(cls):
        return cls.__name__.lower()

    @classmethod
    def _get_create_sql(cls):
        fields = [
            ('id', 'INTEGER PRIMARY KEY AUTOINCREMENT')
        ]
        for name, field in inspect.getmembers(cls):
            if isinstance(field, Column):
                fields.append((name, field.sql_type))
            elif isinstance(field, ForeignKey):
                fields.append((name + '_id', 'INTEGER'))
        fields = [' '.join(field) for field in fields]
        return CREATE_TABLE_SQL.format(cls._get_name, fields=', '.join(fields))

    def _get_insert_sql(self):
        cls = self.__class__
        fields = []
        placeholders = []
        values = []

        for name, field in inspect.getmembers(cls):
            if isinstance(field, Column):
                fields.append(name)
                values.append(getattr(self, name))
                placeholders.append('?')

        sql = INSERT_SQL.format(
            name=self.__class__.__name__.lower(),
            fields=', '.join(fields),
            placeholders=', '.join(placeholders),
        )
        return sql, values

    @classmethod
    def _get_select_all_sql(cls):
        fields = ['id']
        for name, field in inspect.getmembers(cls):
            if isinstance(field, Column):
                fields.append(name)
        sql = SELECT_ALL_SQL.format(
            fields=', '.join(fields),
            table=cls._get_name()
        )
        return sql, fields

    def _get_select_where_sql(self, **kwargs):
        fields = ['id']
        table = kwargs['table']
        for name, field in inspect.getmembers(table):
            if isinstance(field, Column):
                fields.append(name)

        filters = []
        params = []

        for key, value in kwargs.items():
            filters.append(key + ' = ?')
            params.append(value)

        sql = SELECT_WHERE_SQL.format(
            fields=', '.join(fields),
            table=table._get_name(),
            params=' AND '.join(filters),
        )
        return sql, fields, params


class Column:
    def __init__(self, type: type) -> None:
        self.type = type

    @property
    def sql_type(self):
        return SQLITE_TYPE_MAP[self.type]


class ForeignKey:
    def __init__(self, table: Table):
        self.table = table
