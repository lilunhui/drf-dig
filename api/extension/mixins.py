from rest_framework import mixins
from rest_framework.response import Response
from api.extension import return_code


class DigCreateModelMixin(mixins.CreateModelMixin):
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        # 1/异常处理
        if not serializer.is_valid():
            return Response({'code': return_code.VALIDATE_ERROR, 'detail': serializer.errors})
        # 2/使用钩子保存数据
        res = self.perform_create(serializer)
        # 3/返回处理数据
        return res or Response({'code': return_code.SUCCESS, 'data': serializer.data})


class DigListModelMixin(mixins.ListModelMixin):
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response({"code": return_code.SUCCESS, 'data': serializer.data})

        serializer = self.get_serializer(queryset, many=True)
        return Response({"code": return_code.SUCCESS, 'data': serializer.data})


class DigDestroyModelMixin(mixins.DestroyModelMixin):
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        res = self.perform_destroy(instance)
        return res or Response({"code": return_code.SUCCESS})


class DigUpdateModelMixin(mixins.UpdateModelMixin):
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if not serializer.is_valid():
            return Response({"code": return_code.VALIDATE_ERROR, 'detail': serializer.errors})
        res = self.perform_update(serializer)
        return res or Response({"code": return_code.SUCCESS, 'data': serializer.data})
