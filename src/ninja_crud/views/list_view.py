from typing import TYPE_CHECKING, Any, cast

from django.db.models import Model, QuerySet
from django.http import HttpRequest
from ninja import FilterSchema
from ninja.pagination import LimitOffsetPagination, PaginationBase, paginate
from pydantic import BaseModel

from ninja_crud.views.api_view import APIView
from ninja_crud.views.types import Decorator, QuerySetFilter, QuerySetGetter

if TYPE_CHECKING:
    from ninja_crud.viewsets import APIViewSet


class ListView(APIView):
    """
    Declarative class-based view for listing model instances in Django Ninja.

    This class provides a standard implementation for a list view, which retrieves
    a queryset of model instances based on path and query parameters provided in the
    URL. It is intended to be used in viewsets or as standalone views to simplify the
    creation of list endpoints.

    Takes every `APIView` argument (see `APIView` for their descriptions), with
    defaults `methods=["GET"]`, `path="/"`, `response_status=200` and
    `response_body=None`, which inherits the viewset's `default_response_body` as a
    list type. Does not inherit the viewset's `default_request_body`.

    Args:
        get_queryset (Callable | None, optional): Callable to retrieve the queryset.
            Default uses `self.model.objects.get_queryset()`. Useful for selecting
            related models or optimizing queries. Should have the signature:
            - `(request: HttpRequest, path_parameters: BaseModel | None) -> QuerySet`
        filter_queryset (Callable | None, optional): Callable to filter the queryset.
            Default uses `query_parameters.filter(queryset)` if `query_parameters` is a
            `ninja.FilterSchema`, otherwise filters the queryset based on the query
            parameters as keyword arguments:
            `queryset.filter(**query_parameters.model_dump(exclude_unset=True))`.
            Should have the signature:
            - `(queryset: QuerySet, query_parameters: BaseModel | None) -> QuerySet`
        pagination_class (type[PaginationBase], optional): Pagination class.
            Defaults to `LimitOffsetPagination`. If None, pagination is disabled.

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
        list_departments = views.ListView()

        # Usage with explicit response body:
        list_departments = views.ListView(response_body=list[DepartmentOut])

    # Usage as a standalone view:
    views.ListView(
        name="list_departments",
        model=Department,
        response_body=list[DepartmentOut],
    ).add_view_to(api)
    ```
    """

    def __init__(
        self,
        methods: list[str] | set[str] | None = None,
        path: str = "/",
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
        get_queryset: QuerySetGetter | None = None,
        filter_queryset: QuerySetFilter | None = None,
        pagination_class: type[PaginationBase] | None = LimitOffsetPagination,
    ) -> None:
        super().__init__(
            methods=methods or ["GET"],
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
        self.get_queryset = get_queryset or self._default_get_queryset
        self.filter_queryset = filter_queryset or self._default_filter_queryset
        self.pagination_class = pagination_class
        if self.pagination_class:
            self.decorators.append(paginate(self.pagination_class))

    def handler(
        self,
        request: HttpRequest,
        path_parameters: BaseModel | None,
        query_parameters: BaseModel | None,
        request_body: BaseModel | None,
    ) -> QuerySet[Model]:
        queryset = self.get_queryset(request, path_parameters)
        return self.filter_queryset(queryset, query_parameters)

    def get_default_response_body(self, api_viewset_class: type["APIViewSet"]) -> Any:
        default_response_body = api_viewset_class.default_response_body
        if default_response_body is None:
            return None
        return list[default_response_body]  # type: ignore[valid-type]

    def _default_get_queryset(
        self, request: HttpRequest, path_parameters: BaseModel | None
    ) -> QuerySet[Model]:
        return cast(type[Model], self.model).objects.get_queryset()

    def _default_filter_queryset(
        self, queryset: QuerySet[Model], query_parameters: BaseModel | None
    ) -> QuerySet[Model]:
        if isinstance(query_parameters, FilterSchema):
            queryset = query_parameters.filter(queryset)
        elif isinstance(query_parameters, BaseModel):
            queryset = queryset.filter(
                **query_parameters.model_dump(exclude_unset=True)
            )
        return queryset

    def get_default_request_body(self, api_viewset_class: type["APIViewSet"]) -> Any:
        return None
