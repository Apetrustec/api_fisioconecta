from fisio_conecta.models import Paciente
from rest_framework import serializers
from fisio_conecta.pessoa.serializers import DadosBasicosPessoaSerializer



class PacienteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Paciente
        fields = '__all__'

class ResponsePacienteSerializer(serializers.ModelSerializer):
    pessoa = DadosBasicosPessoaSerializer(read_only=True)

    class Meta:
        model = Paciente
        fields = [
            'id_paciente',
            'ativo',
            'nota_paciente',
            'altura',
            'peso',
            'uso_remedio_continuo',
            'observacoes_medicas',
            'pessoa',
            'resumo_caso'
        ]