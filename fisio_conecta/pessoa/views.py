from fisio_conecta import models as m
from fisio_conecta.pessoa import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from fisio_conecta.permissions import IsLogged
from rest_framework.exceptions import ValidationError



class CreatePessoa(APIView):
    """
    Classe para criar de Pessoa.
    """
        
    def post(self, request):
        """
        Cria uma nova pessoa.
        """
        try:
        
            cpf = request.data.get('cpf')
            email = request.data.get('email')
            nome = request.data.get('nome')
            endereco_campos = ['cep', 'logradouro', 'bairro', 'cidade', 'estado']
            tipo_usuario = request.data.get('tipo_usuario')


            if not tipo_usuario:
                return Response({"error": "Tipo de usuário não foi enviado."}, status=400) 

            if not email:
                return Response({"error": "Email não foi enviado."}, status=400)
            if m.Pessoa.objects.filter(email=email).exists():
                return Response({"error": "Pessoa com esse email já existe."}, status=400)

            if not nome:
                return Response({"error": "Nome não foi enviado."}, status=400)

            endereco = None

            if any(request.data.get(campo) for campo in endereco_campos):
                endereco = m.Endereco(
                    cep=request.data.get('cep'),
                    logradouro=request.data.get('logradouro'),
                    bairro=request.data.get('bairro'),
                    numero=request.data.get('numero'),
                    complemento=request.data.get('complemento'),
                    cidade=request.data.get('cidade'),
                    estado=request.data.get('estado')
                )
                endereco.save()

            pessoa = m.Pessoa(
                nome=nome,
                sobrenome=request.data.get('sobrenome'),
                cpf=cpf,
                email=email,
                telefone=request.data.get('telefone'),
                data_nascimento=request.data.get('data_nascimento'),
                sexo=request.data.get('sexo'),
                descricao=request.data.get('descricao'),
                url_imagem_perfil=request.data.get('url_imagem_perfil'),
                endereco=endereco,
                tipo_usuario=tipo_usuario
            )

            pessoa.save()

            serializer = serializers.PessoaSerializer(pessoa)
            return Response(serializer.data, status=201)
        
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        
        
class GerenciaPessoa (APIView):
    """
    Classe para CRUD de Pessoa.
    """

    permission_classes = [IsLogged] # Só permite acesso caso esteja logado

    def get(self, request):
        """
        Retorna os dados de uma pessoa.
        """
        
        try:
            pessoa = m.Pessoa.objects.get(email=request.user_data.get('email'))
            serializer = serializers.PessoaSerializer(pessoa)
            return Response(serializer.data, status=200)
        except m.Pessoa.DoesNotExist:
            return Response({"error": "Pessoa não encontrada"}, status=404)
        
        
    def put(self, request):
        try:
            pessoa = m.Pessoa.objects.get(email=request.user_data.get('email'))
        except m.Pessoa.DoesNotExist:
            return Response({"error": "Pessoa não encontrada."}, status=404)

        serializer = serializers.PessoaSerializer(pessoa, data=request.data, partial=True)

        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=200)
        except ValidationError as ve:
            primeiro_campo = next(iter(ve.detail))
            mensagem = ve.detail[primeiro_campo][0]
            return Response({"error": str(mensagem)}, status=400)
            
        
        
    def delete(self, request):
        """
        Desativa uma pessoa.
        """
            
        try:
            safe = request.query_params.get('safe', '').lower() == 'true'
            if safe:
                pessoa = m.Pessoa.objects.get(email=request.user_data.get('email'))
                pessoa.ativo = False
                pessoa.save(update_fields=['ativo'])
                return Response({"message": "Pessoa desativada com sucesso"}, status=204)
            else:
                pessoa = m.Pessoa.objects.get(email=request.user_data.get('email'))
                pessoa.delete()
                return Response({"message": "Pessoa deletada com sucesso"}, status=204)
        except m.Pessoa.DoesNotExist:
            return Response({"error": "Pessoa não encontrada"}, status=404)

        
        
