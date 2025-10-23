from rest_framework import serializers
from fisio_conecta.models import Avaliacao
import fisio_conecta.atendimento.serializers as atendimentoSerializers
import fisio_conecta.pessoa.serializers as pessoaSerializers

class AvaliacaoSerializer(serializers.ModelSerializer):
    
    autor= pessoaSerializers.DadosBasicosPessoaSerializer()
    # destinatario = pessoaSerializers.DadosBasicosPessoaSerializer()
    paciente = serializers.SerializerMethodField()
    fisioterapeuta = serializers.SerializerMethodField()
    atendimento = atendimentoSerializers.MinAtendimentoSerializer()
    
    class Meta:
        model = Avaliacao
        fields = '__all__'

    def get_paciente(self, obj):
        if obj.destinatario.tipo_usuario == 1:  # paciente
            return pessoaSerializers.DadosBasicosPessoaSerializer(obj.destinatario).data
        return None

    def get_fisioterapeuta(self, obj):
        if obj.destinatario.tipo_usuario == 2:  # fisioterapeuta
            return pessoaSerializers.DadosBasicosPessoaSerializer(obj.destinatario).data
        return None
    
class NotaSerializer(serializers.Serializer):
    nota = serializers.FloatField()

class SerializerAvaliacaoAdmin(serializers.ModelSerializer):

    autor= pessoaSerializers.DadosBasicosPessoaSerializer()
    destinatario = pessoaSerializers.DadosBasicosPessoaSerializer()
    atendimento = atendimentoSerializers.MinAtendimentoSerializer()

    class Meta:
        model = Avaliacao
        fields = '__all__'
