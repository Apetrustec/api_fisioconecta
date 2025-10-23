from rest_framework import serializers
from fisio_conecta.models import Atendimento
from fisio_conecta.endereco.serializers import EnderecoSerializer
from fisio_conecta.paciente.serializers import ResponsePacienteSerializer
from fisio_conecta.pessoa.serializers import DadosBasicosPessoaSerializer
from fisio_conecta.fisioterapeuta.serializers import CamposBasicoFisioSerializer
from fisio_conecta import models as m
from django.utils import timezone
from datetime import timezone as dt_timezone


class AtendimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Atendimento
        fields = '__all__'


class DateTimeUTCField(serializers.DateTimeField):
    def to_representation(self, value):
        if not value:
            return None
        
        if timezone.is_naive(value):
            v = timezone.make_aware(value, dt_timezone.utc)
        else:
            v = timezone.localtime(value, dt_timezone.utc)
            
        return f"{v.strftime('%Y-%m-%dT%H:%M:%S')}+00:00"
    
class ResponseAtendimentoSerializer(serializers.ModelSerializer):
    paciente = ResponsePacienteSerializer(read_only=True)
    fisioterapeuta = CamposBasicoFisioSerializer(read_only=True)
    especialidade = serializers.SerializerMethodField()
    data_hora = DateTimeUTCField()

    def get_especialidade(self, obj):
        if obj.especialidade:
            return {
                "id": obj.especialidade.id_especialidade,
                "nome": obj.especialidade.nome
            }
        return None

    class Meta:
        model = Atendimento
        fields = [
            'id_atendimento',
            'data_hora',
            'status',
            'paciente',
            'fisioterapeuta',
            'especialidade',
            'local_atendimento',
            'fez_checkin',
            'fez_checkout',
        ]
        
class MinAtendimentoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Atendimento
        fields = [
            'id_atendimento',
            'data_hora',
            'status'
        ]