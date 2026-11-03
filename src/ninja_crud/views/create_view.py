from typing import Any, cast

from django.db.models import ManyToManyField, Model
from django.http import HttpRequest
from pydantic import BaseModel

from ninja_crud.views.api_view import APIView
from ninja_crud.views.types import Decorator, ModelGetter, ModelHook


class CreateView(APIView):
    """
    Declarative class-based view for creating a model instance in Django Ninja.

    This class provides a standard implementation for a create view, which creates a
    new model instance based on the request body and saves it to the database. It is
    intended to be used in viewsets or as standalone views to simplify the creation of
    create endpoints.

    Takes every `APIView` argument (see `APIView` for their descriptions), with
    defaults `methods=["POST"]`, `path="/"`, `response_status=201` and
    `response_body=None`.

    Args:
        init_model ((HttpRequest, BaseModel | None) -> Model, optional): Initializes
            the model instance. Default creates a new instance of the model with no
            arguments: `lambda request, path_parameters: self.model()`.
            Useful for customizing model initialization logic, e.g., setting default
            values, using request's user, using path parameters, etc.
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
        create_department = views.CreateView()

        # Usage with explicit request and response bodies:
        create_department = views.CreateView(
            request_body=DepartmentIn,
            response_body=DepartmentOut,
        )

    # Usage as a standalone view:
    views.CreateView(
        name="create_department",
        model=Department,
        request_body=DepartmentIn,
        response_body=DepartmentOut,
    ).add_view_to(api)
    ```
    """

    def __init__(
        self,
        methods: list[str] | set[str] | None = None,
        path: str = "/",
        *,
        name: str | None = None,
        response_status: int = 201,
        response_body: Any = None,
        responses: dict[int, Any] | None = None,
        model: type[Model] | None = None,
        path_parameters: type[BaseModel] | None = None,
        query_parameters: type[BaseModel] | None = None,
        request_body: type[BaseModel] | None = None,
        decorators: list[Decorator] | None = None,
        operation_kwargs: dict[str, Any] | None = None,
        init_model: ModelGetter | None = None,
        pre_save: ModelHook | None = None,
        post_save: ModelHook | None = None,
    ) -> None:
        super().__init__(
            methods=methods or ["POST"],
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
        self.init_model = init_model or self._default_init_model
        self.pre_save = pre_save or (lambda request, instance: instance.full_clean())
        self.post_save = post_save or (lambda request, instance: None)

    def handler(
        self,
        request: HttpRequest,
        path_parameters: BaseModel | None,
        query_parameters: BaseModel | None,
        request_body: BaseModel,
    ) -> Model:
        instance = self.init_model(request, path_parameters)

        m2m_fields_to_set = []
        for field, value in request_body.model_dump().items():
            if isinstance(instance._meta.get_field(field), ManyToManyField):
                m2m_fields_to_set.append((field, value))
            else:
                setattr(instance, field, value)

        self.pre_save(request, instance)
        instance.save()
        self.post_save(request, instance)

        for field, value in m2m_fields_to_set:
            getattr(instance, field).set(value)

        return instance

    def _default_init_model(
        self, request: HttpRequest, path_parameters: BaseModel | None
    ) -> Model:
        return cast(type[Model], self.model)()
