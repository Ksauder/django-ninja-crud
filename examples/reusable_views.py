from typing import Any
from uuid import UUID

from django.db import models
from django.http import HttpRequest
from ninja.constants import NOT_SET

from ninja_crud.views import APIView


class ReusableReadView(APIView):
    def __init__(
        self, *, response_body: Any = NOT_SET, model: type[models.Model] | None = None
    ) -> None:
        super().__init__(
            path="/{id}/reusable", methods=["GET"], response_body=response_body
        )
        self.model = model

    def handler(self, request: HttpRequest, id: UUID) -> models.Model:
        return self.model.objects.get(id=id)


class ReusableAsyncReadView(APIView):
    def __init__(
        self, *, response_body: Any = NOT_SET, model: type[models.Model] | None = None
    ) -> None:
        super().__init__(
            path="/{id}/reusable/async",
            methods=["GET"],
            response_body=response_body,
        )
        self.model = model

    async def handler(self, request: HttpRequest, id: UUID) -> models.Model:
        return await self.model.objects.aget(id=id)
