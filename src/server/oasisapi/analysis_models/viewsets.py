from __future__ import absolute_import

from django_filters import rest_framework as filters
from rest_framework import viewsets

from ..filters import CreatedModifiedFilterSet
from .models import AnalysisModel
from .serializers import AnalysisModelSerializer


class AnalysisModelFilter(CreatedModifiedFilterSet):
    class Meta:
        model = AnalysisModel
        fields = [
            'id',
            'supplier_id',
            'version_id',
        ]


class AnalysisModelViewSet(viewsets.ModelViewSet):
    """ Returns a list of Analysis Model objects

        ### Available filters
        - id
        - supplier_id
        - version_id
        - created, created_lte, created_gte
        - modified, modified_lte, modified_gte

        `e.g. ?created_gte=2018-01-01&created_lte=2018-02-01`
    """

    queryset = AnalysisModel.objects.all()
    serializer_class = AnalysisModelSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = AnalysisModelFilter

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super(AnalysisModelViewSet, self).update(request, *args, **kwargs)
