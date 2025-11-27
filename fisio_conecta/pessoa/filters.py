import django_filters
from fisio_conecta import models as m

class PessoaFilter(django_filters.FilterSet):
    """
    Filtros básicos para Pessoa.
    - tipo_usuario = 1 (Paciente), 2 (Fisioterapeuta)
    - ativo = True/False
    - nome contém (busca por nome)
    """
    nome = django_filters.CharFilter(field_name="nome", lookup_expr="icontains")
    sobrenome = django_filters.CharFilter(field_name="sobrenome", lookup_expr="icontains")
    email = django_filters.CharFilter(field_name="email", lookup_expr="icontains")
    tipo_usuario = django_filters.NumberFilter(field_name="tipo_usuario")
    ativo = django_filters.BooleanFilter(field_name="ativo")
    ativo_fisioterapeuta = django_filters.BooleanFilter(field_name="fisioterapeuta__ativo")
    ativo_paciente = django_filters.BooleanFilter(field_name="paciente__ativo")
    crefito = django_filters.CharFilter(field_name="fisioterapeuta__crefito", lookup_expr="icontains")

    class Meta:
        model = m.Pessoa
        fields = ["tipo_usuario", "ativo", "nome", "sobrenome", "email", "ativo_fisioterapeuta", "ativo_paciente", "crefito"]