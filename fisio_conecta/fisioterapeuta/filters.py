import django_filters
from fisio_conecta.models import Fisioterapeuta

class NumberInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    pass

class FisioterapeutaFilter(django_filters.FilterSet):
    nome = django_filters.CharFilter(field_name='pessoa__nome', lookup_expr='icontains')
    sobrenome = django_filters.CharFilter(field_name='pessoa__sobrenome', lookup_expr='icontains')
    especialidade = NumberInFilter(field_name='especialidades__id_especialidade', lookup_expr='in')
    crefito = django_filters.CharFilter(lookup_expr='icontains')
    ativo = django_filters.BooleanFilter()

    class Meta:
        model = Fisioterapeuta
        fields = ['nome', 'sobrenome', 'crefito', 'especialidade', 'ativo']
