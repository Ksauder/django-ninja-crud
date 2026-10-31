from datetime import date
from typing import Generic, TypeVar
from uuid import UUID

from ninja import Schema


class DepartmentIn(Schema):
    title: str


class DepartmentOut(Schema):
    id: UUID
    title: str


class EmployeeIn(Schema):
    first_name: str
    last_name: str
    birthdate: date | None = None


class EmployeeOut(Schema):
    id: UUID
    first_name: str
    last_name: str
    birthdate: date | None = None
    department_id: UUID


T = TypeVar("T")


class Paged(Schema, Generic[T]):
    items: list[T]
    count: int
