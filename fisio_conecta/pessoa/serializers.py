from fisio_conecta import models as m
from rest_framework import serializers
from fisio_conecta.endereco import serializers as enderecoSerializers


class PessoaSerializer(serializers.ModelSerializer):
    """
    Serializer para a classe Pessoa.
    """
    
    endereco = enderecoSerializers.EnderecoSerializer(many=False)

    class Meta:
        model = m.Pessoa
        fields = '__all__'

    def update(self, instance, validated_data):
        endereco_data = validated_data.pop('endereco', None)
        super().update(instance, validated_data)
        if endereco_data:

            if instance.endereco:
                endereco_instance = instance.endereco
                for attr, value in endereco_data.items():
                    setattr(endereco_instance, attr, value)
                endereco_instance.save()
                
            else:
                novo_endereco = m.Endereco.objects.create(**endereco_data)
                instance.endereco = novo_endereco
                instance.save() 

        return instance

class DadosBasicosPessoaSerializer(serializers.ModelSerializer):
    """
    Serializer para a classe pessoa retornando dados basicos
    """
    endereco = enderecoSerializers.EnderecoSerializer(many=False)

    class Meta:
        model = m.Pessoa
        fields = ['id_pessoa','cpf','nome','sobrenome', 'email', 'telefone', 'data_nascimento', 'endereco','tipo_usuario','url_imagem_perfil','descricao']

class PessoaCompletoSerializer(serializers.ModelSerializer):
    endereco = enderecoSerializers.EnderecoSerializer(many=False)
    paciente = serializers.SerializerMethodField()
    fisioterapeuta = serializers.SerializerMethodField()

    class Meta:
        model = m.Pessoa
        fields = [
            'id_pessoa', 'nome', 'sobrenome', 'cpf', 'email', 'telefone',
            'data_nascimento', 'sexo', 'descricao', 'url_imagem_perfil',
            'endereco', 'tipo_usuario', 'paciente', 'fisioterapeuta'
        ]

    def get_paciente(self, obj):
        if obj.tipo_usuario == 1 and hasattr(obj, 'paciente'):
            from fisio_conecta.paciente.serializers import PacienteSerializer
            return PacienteSerializer(obj.paciente).data
        return None

    def get_fisioterapeuta(self, obj):
        if obj.tipo_usuario == 2 and hasattr(obj, 'fisioterapeuta'):
            from fisio_conecta.fisioterapeuta.serializers import AllFisioterapeutaSerializer
            return AllFisioterapeutaSerializer(obj.fisioterapeuta).data
        return None