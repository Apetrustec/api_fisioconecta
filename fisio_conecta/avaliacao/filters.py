import django_filters
from fisio_conecta.models import Avaliacao
from django.db.models import F, FloatField
from django.db.models.functions import Cast, Round

class AvaliacaoFilter(django_filters.FilterSet):
    nome = django_filters.CharFilter(field_name='autor__nome', lookup_expr='icontains')
    sobrenome = django_filters.CharFilter(field_name='autor__sobrenome', lookup_expr='icontains')
    atendimento = django_filters.CharFilter(field_name='atendimento__id_atendimento', lookup_expr='icontains')
    data = django_filters.DateFromToRangeFilter(field_name='data')
    nota_ed = django_filters.NumberFilter(field_name='nota_educ', lookup_expr='gte') # NOTA DE EDUCAÇÃO 
    nota_pont = django_filters.NumberFilter(field_name='nota_pont', lookup_expr='gte') # NOTA DE PONTUALIDADE 
    nota_gent = django_filters.NumberFilter(field_name='nota_gent', lookup_expr='gte') # NOTA DE GENTILEZA
    nota = django_filters.NumberFilter(method='filter_nota')

    def filter_nota(self, queryset, name, value):
            queryset = queryset.annotate(
                media=(
                    (Cast(F('nota_educ'), FloatField()) +
                    Cast(F('nota_pont'), FloatField()) +
                    Cast(F('nota_gent'), FloatField())) / 3.0
                )
            )
            queryset = queryset.annotate(media_round=Round('media', 1))
            return queryset.filter(media_round__gte=value)



    class Meta:
        model = Avaliacao
        fields = ['atendimento', 'data', 'nota_ed', 'nota_pont', 'nota_gent','nota']


