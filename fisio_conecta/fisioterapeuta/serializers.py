from fisio_conecta import models as m
from rest_framework import serializers
from fisio_conecta.pessoa import serializers as pessoaSerializers


class AllFisioterapeutaSerializer(serializers.ModelSerializer):
    especialidades = serializers.SerializerMethodField()
    
    def get_especialidades(self, obj):
        especialidades_ativas = m.Fisio_especialidade.objects.filter(
            fisioterapeuta=obj
        ).select_related('especialidade')

        return [
            {
                "id": fe.especialidade.id_especialidade,
                "nome": fe.especialidade.nome
            }
            for fe in especialidades_ativas
        ]

    class Meta:
        model = m.Fisioterapeuta
        fields = '__all__'
 

class FisioterapeutaSerializer(serializers.ModelSerializer):
    """
    Retorna dados de fisioterapeuta.
    """
    
    especialidades = serializers.SerializerMethodField()
    pessoa = pessoaSerializers.PessoaSerializer(read_only=True)
    
    def get_especialidades(self, obj):
        especialidades_ativas = m.Fisio_especialidade.objects.filter(
            fisioterapeuta=obj,
            ativo=True
        ).select_related('especialidade')

        return [
            {
                "id": fe.especialidade.id_especialidade,
                "nome": fe.especialidade.nome
            }
            for fe in especialidades_ativas
        ]

    class Meta:
        model = m.Fisioterapeuta
        fields = [
            'id_fisio',
            'crefito',
            'valor_atendimento',
            'qtd_atendimentos',
            'ativo',
            'pessoa',
            'especialidades',
        ]


class TodosFisioSerializer(serializers.ModelSerializer):
    """
    Serializer para a classe Fisioterapeuta.
    """
    
    especialidades = serializers.SerializerMethodField()
    pessoa = pessoaSerializers.PessoaSerializer(read_only=True)
    
    def get_especialidades(self, obj):
        especialidades_ativas = m.Fisio_especialidade.objects.filter(
            fisioterapeuta=obj
        ).select_related('especialidade')

        return [
            {
                "id": fe.especialidade.id_especialidade,
                "nome": fe.especialidade.nome
            }
            for fe in especialidades_ativas
        ]

    class Meta:
        model = m.Fisioterapeuta
        fields = [
            'id_fisio',
            'crefito',
            'valor_atendimento',
            'qtd_atendimentos',
            'ativo',
            'pessoa',
            'especialidades',
        ]

class CamposBasicoFisioSerializer(serializers.ModelSerializer):
    especialidades = serializers.SerializerMethodField()
    pessoa = pessoaSerializers.DadosBasicosPessoaSerializer(read_only=True)

    def get_especialidades(self, obj):
        especialidades_ativas = m.Fisio_especialidade.objects.filter(
            fisioterapeuta=obj
        ).select_related('especialidade')

        return [
            {
                "id": fe.especialidade.id_especialidade,
                "nome": fe.especialidade.nome
            }
            for fe in especialidades_ativas
        ]

    class Meta:
        model = m.Fisioterapeuta
        fields = [
            'id_fisio',
            'nota_fisioterapeuta',
            'valor_atendimento',
            'crefito',
            'pessoa',
            'especialidades',
        ]

    