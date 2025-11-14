from rest_framework import serializers
from fisio_conecta import models as m
from fisio_conecta.pessoa.serializers import DadosBasicosPessoaSerializer

class AdminSerializer(serializers.ModelSerializer):
    pessoa = DadosBasicosPessoaSerializer(read_only=True)
    
    class Meta:
        model = m.Administrador
        fields = '__all__'