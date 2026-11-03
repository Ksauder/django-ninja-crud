from typing import Any

from django.db.models import ManyToManyField, Model
from django.http import HttpRequest
from pydantic import BaseModel

from ninja_crud.views.api_view import APIView
from ninja_crud.views.types import Decorator, ModelGetter, ModelHook


class UpdateView(APIView):
    """
    Declarative class-based view for updating a model instance in Django Ninja.

    This class provides a standard implementation for an update view, which retrieves
    a single model instance based on the path parameters, updates the instance based on
    the request body, and saves the changes to the database. It is intended to be used
    in viewsets or as standalone views to simplify the creation of update endpoints.

    Takes every `APIView` argument (see `APIView` for their descriptions), with
    defaults `methods=["PUT"]`, `path="/{id}"`, `response_status=200` and
    `response_body=None`.

    Args:
        get_model ((HttpRequest, BaseModel | None) -> Model, optional): Retrieves model
            instance. Default uses path parameters (e.g., `self.model.objects.get(id=path_parameters.id)`
            for `/{id}` path). Useful for customizing model retrieval logic.
            Should have the signature:
            - `(request: HttpRequest, path_parameters: BaseModel | None) -> Model`
        pre_save ((HttpRequest, Model) -> None, optional): Pre-save operations on the
            model instance. Does a [full_clean](https://docs.djangoproject.com/en/stable/ref/models/instances/#django.db.models.Model.full_clean)
            by default.
        post_save ((HttpRequest, Model) -> None, optional): Post-save operations on the
            model instance. Does nothing by default.

    Example:
    ```python
    from ninja import NinjaAPI
    from ninja_crud import views, viewsets

    from examples.models import Department
    from examples.schemas import DepartmentIn, DepartmentOut

    api = NinjaAPI()

    # Usage as a class attribute in a viewset:
    class DepartmentViewSet(viewsets.APIViewSet):
        api = api
        model = Department
        default_request_body = DepartmentIn
        default_response_body = DepartmentOut

        # Usage with default request and response bodies:
        update_department = views.UpdateView()

        # Usage with explicit request and response bodies:
        update_department = views.UpdateView(
            request_body=DepartmentIn,
            response_body=DepartmentOut,
        )

    # Usage as a standalone view:
    views.UpdateView(
        name="update_department",
        model=Department,
        request_body=DepartmentIn,
        response_body=DepartmentOut,
    ).add_view_to(api)
    ```
    """

    def __init__(
        self,
        methods: list[str] | set[str] | None = None,
        path: str = "/{id}",
        *,
        name: str | None = None,
        response_status: int = 200,
        response_body: Any = None,
        responses: dict[int, Any] | None = None,
        model: type[Model] | None = None,
        path_parameters: type[BaseModel] | None = None,
        query_parameters: type[BaseModel] | None = None,
        request_body: type[BaseModel] | None = None,
        decorators: list[Decorator] | None = None,
        operation_kwargs: dict[str, Any] | None = None,
        get_model: ModelGetter | None = None,
        pre_save: ModelHook | None = None,
        post_save: ModelHook | None = None,
    ) -> None:
        super().__init__(
            methods=methods or ["PUT"],
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
        self.pre_save = pre_save or (lambda request, instance: instance.full_clean())
        self.post_save = post_save or (lambda request, instance: None)

    def handler(
        self,
        request: HttpRequest,
        path_parameters: BaseModel | None,
        query_parameters: BaseModel | None,
        request_body: BaseModel,
    ) -> Model:
        instance = self.get_model(request, path_parameters)

        for field, value in request_body.model_dump(exclude_unset=True).items():
            if isinstance(instance._meta.get_field(field), ManyToManyField):
                getattr(instance, field).set(value)
            else:
                setattr(instance, field, value)

        self.pre_save(request, instance)
        instance.save()
        self.post_save(request, instance)
        return instance
