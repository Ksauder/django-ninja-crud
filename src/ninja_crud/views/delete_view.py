from typing import TYPE_CHECKING, Any

from django.db.models import Model
from django.http import HttpRequest
from pydantic import BaseModel

from ninja_crud.views.api_view import APIView
from ninja_crud.views.types import Decorator, ModelGetter, ModelHook

if TYPE_CHECKING:
    from ninja_crud.viewsets import APIViewSet


class DeleteView(APIView):
    """
    Declarative class-based view for deleting a model instance in Django Ninja.

    This class provides a standard implementation for a delete view, which retrieves
    a single model instance based on the path parameters and deletes it. It is
    intended to be used in viewsets or as standalone views to simplify the creation
    of delete endpoints.

    Takes every `APIView` argument (see `APIView` for their descriptions), with
    defaults `methods=["DELETE"]`, `path="/{id}"` and `response_status=204`. Does
    not inherit the viewset's `default_response_body` or `default_request_body`.

    Args:
        get_model ((HttpRequest, BaseModel | None) -> Model, optional): Retrieves model
            instance. Default uses path parameters (e.g., `self.model.objects.get(id=path_parameters.id)`
            for `/{id}` path). Useful for customizing model retrieval logic.
            Should have the signature:
            - `(request: HttpRequest, path_parameters: BaseModel | None) -> Model`
        pre_delete ((HttpRequest, Model) -> None, optional): A callable to perform
            pre-delete operations on the model instance. Does nothing by default.
            Useful for additional operations before deleting the instance.
        post_delete ((HttpRequest, Model) -> None, optional): A callable to perform
            post-delete operations on the model instance. By default, it does nothing.
            Useful for additional operations after deleting the instance.

    Example:
    ```python
    from ninja import NinjaAPI
    from ninja_crud import views, viewsets

    from examples.models import Department

    api = NinjaAPI()

    # Usage as a class attribute in a viewset:
    class DepartmentViewSet(viewsets.APIViewSet):
        api = api
        model = Department

        delete_department = views.DeleteView()

    # Usage as a standalone view:
    views.DeleteView(
        name="delete_department",
        model=Department
    ).add_view_to(api)
    ```
    """

    def __init__(
        self,
        methods: list[str] | set[str] | None = None,
        path: str = "/{id}",
        *,
        name: str | None = None,
        response_status: int = 204,
        response_body: Any = None,
        responses: dict[int, Any] | None = None,
        model: type[Model] | None = None,
        path_parameters: type[BaseModel] | None = None,
        query_parameters: type[BaseModel] | None = None,
        request_body: type[BaseModel] | None = None,
        decorators: list[Decorator] | None = None,
        operation_kwargs: dict[str, Any] | None = None,
        get_model: ModelGetter | None = None,
        pre_delete: ModelHook | None = None,
        post_delete: ModelHook | None = None,
    ) -> None:
        super().__init__(
            methods=methods or ["DELETE"],
            path=path,
            name=name,
            response_status=response_status,
            response_body=response_body,
            responses=responses,
            model=model,
            path_parameters=path_parameters,
            query_parameters=query_parameters,
            request_body=request_body,
            decorators=decorators,
            operation_kwargs=operation_kwargs,
        )
        self.get_model = get_model or self._default_get_model
        self.pre_delete = pre_delete or (lambda request, instance: None)
        self.post_delete = post_delete or (lambda request, instance: None)

    def handler(
        self,
        request: HttpRequest,
        path_parameters: BaseModel | None,
        query_parameters: BaseModel | None,
        request_body: BaseModel | None,
    ) -> None:
        instance = self.get_model(request, path_parameters)
        self.pre_delete(request, instance)
        instance.delete()
        self.post_delete(request, instance)

    def get_default_response_body(self, api_viewset_class: type["APIViewSet"]) -> Any:
        return None

    def get_default_request_body(self, api_viewset_class: type["APIViewSet"]) -> Any:
        return None
