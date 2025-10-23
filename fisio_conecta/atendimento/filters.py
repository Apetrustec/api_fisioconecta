import django_filters
from fisio_conecta import models as m
from django.db.models import Q



class NumberInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    pass


class AtendimentoFilter(django_filters.FilterSet):
    nome = django_filters.CharFilter(method='filter_nome')
    paciente = django_filters.NumberFilter(field_name='paciente_id', lookup_expr='exact')
    fisioterapeuta = django_filters.NumberFilter(field_name='fisioterapeuta_id', lookup_expr='exact')
    especialidade = django_filters.NumberFilter(field_name='especialidade_id', lookup_expr='exact')
    status = NumberInFilter(field_name='status', lookup_expr='in')
    data_inicio = django_filters.DateFilter(field_name='data_hora', lookup_expr='date__gte')
    data_fim = django_filters.DateFilter(field_name='data_hora', lookup_expr='date__lte')
    is_retorno = django_filters.BooleanFilter(field_name='is_retorno', lookup_expr='exact')
    
    def filter_nome(self, queryset, name, value):
        return queryset.filter(
            Q(fisioterapeuta__pessoa__nome__icontains=value) |
            Q(paciente__pessoa__nome__icontains=value)
        )

    class Meta:
        model = m.Atendimento
        fields = [
            'nome',
            'paciente',
            'fisioterapeuta',
            'especialidade',
            'status',
            'data_inicio',
            'data_fim',
            'is_retorno',
        ]