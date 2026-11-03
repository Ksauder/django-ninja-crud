from typing import Any

from django.db.models import Model
from django.http import HttpRequest
from pydantic import BaseModel

from ninja_crud.views.api_view import APIView
from ninja_crud.views.types import Decorator, ModelGetter


class ReadView(APIView):
    """
    Declarative class-based view for reading a model instance in Django Ninja.

    This class provides a standard implementation for a read view, which retrieves
    a single model instance based on the path parameters. It is intended to be used
    in viewsets or as standalone views to simplify the creation of read endpoints.

    Args:
        name (str | None, optional): View function name. Defaults to `None`. If None,
            uses class attribute name in viewsets or "handler" for standalone views.
        methods (list[str] | set[str], optional): HTTP methods. Defaults to `["GET"]`.
        path (str, optional): URL path. Defaults to `"/{id}"`.
        response_status (int, optional): HTTP response status code. Defaults to `200`.
        response_body (Any, optional): Response body type. Defaults to `None`.
            If None, uses the default response body of the viewset.
        model (type[django.db.models.Model], optional): Associated Django model.
            Inherits from viewset if not provided. Defaults to `None`.
        path_parameters (type[BaseModel], optional): Path parameters type.
            Defaults to `None`. If not provided, resolved from the path and model.
        get_model ((HttpRequest, BaseModel | None) -> Model, optional): Retrieves model
            instance. Default uses path parameters (e.g., `self.model.objects.get(id=path_parameters.id)`
            for `/{id}` path). Useful for customizing model retrieval logic.
            Should have the signature:
            - `(request: HttpRequest, path_parameters: Optional[BaseModel]) -> Model`
        decorators (list[Callable], optional): View function decorators
            (applied in reverse order). Defaults to `None`.
        operation_kwargs (dict[str, Any], optional): Additional operation
            keyword arguments. Defaults to `None`.

    Example:
    ```python
    from ninja import NinjaAPI
    from ninja_crud import views, viewsets

    from examples.models import Department
    from examples.schemas import DepartmentOut

    api = NinjaAPI()

    # Usage as a class attribute in a viewset:
    class DepartmentViewSet(viewsets.APIViewSet):
        api = api
        model = Department
        default_response_body = DepartmentOut

        # Usage with default response body:
        read_department = views.ReadView()

        # Usage with explicit response body:
        read_department = views.ReadView(response_body=DepartmentOut)

    # Usage as a standalone view:
    views.ReadView(
        name="read_department",
        model=Department,
        response_body=DepartmentOut,
    ).add_view_to(api)
    ```
    """

    def __init__(
        self,
        name: str | None = None,
        methods: list[str] | set[str] | None = None,
        path: str = "/{id}",
        response_status: int = 200,
        response_body: Any = None,
        model: type[Model] | None = None,
        path_parameters: type[BaseModel] | None = None,
        get_model: ModelGetter | None = None,
        decorators: list[Decorator] | None = None,
        operation_kwargs: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            name=name,
            methods=methods or ["GET"],
            path=path,
            status_code=response_status,
            response_schema=response_body,
            model=model,
            path_parameters=path_parameters,
            decorators=decorators,
            operation_kwargs=operation_kwargs,
        )
        self.get_model = get_model or self._default_get_model

    def handler(
        self,
        request: HttpRequest,
        path_parameters: BaseModel | None,
    ) -> Model:
        return self.get_model(request, path_parameters)
