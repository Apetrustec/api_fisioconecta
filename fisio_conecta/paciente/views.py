from fisio_conecta import models as m
from fisio_conecta.paciente import serializers
from fisio_conecta.paciente import filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from fisio_conecta.permissions import IsLogged


class Crud(APIView):
    """
    CRUD para Paciente.
    """
    permission_classes = [IsLogged]

    def get(self, request):
        """
        Retorna dados do paciente logado.
        """
        try:
            email = request.user_data.get('email')

            if not email:
                return Response({"error": "Usuário não possui email vinculado."},
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                paciente = m.Paciente.objects.select_related('pessoa')\
                    .get(pessoa__email=email)
            except m.Paciente.DoesNotExist:
                return Response({"error": "Paciente não encontrado para este usuário."},
                                status=status.HTTP_404_NOT_FOUND)

            serializer = serializers.ResponsePacienteSerializer(paciente)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    def post(self, request):
        """
        Cria um novo paciente a partir de uma pessoa já existente.
        """
        try:
            email = self.request.user_data.get('email')

            if not email:
                raise Exception('email do usuario não encontrado')

            try:
                pessoa = m.Pessoa.objects.get(email=email, ativo=True)
            except m.Pessoa.DoesNotExist:
                return Response({"error": "Pessoa não encontrada."}, status=404)

            if m.Paciente.objects.filter(pessoa=pessoa).exists():
                return Response({"error": "Essa pessoa já está cadastrada como paciente."}, status=400)

            paciente = m.Paciente(
                pessoa=pessoa,
                altura=request.data.get('altura'),
                peso=request.data.get('peso'),
                uso_remedio_continuo=request.data.get('uso_remedio_continuo', 'nao informado'),
                observacoes_medicas=request.data.get('observacoes_medicas'),
            )
            paciente.save()

            serializer = serializers.PacienteSerializer(paciente)
            return Response(serializer.data, status=201)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
        
    def put(self, request):
        """
        Atualiza os dados do paciente vinculado ao usuário autenticado.
        """
        try:
            email = self.request.user_data.get('email')
            if not email:
                return Response({"error": "E-mail do usuário não encontrado."}, status=400)

            try:
                pessoa = m.Pessoa.objects.get(email=email, ativo=True)
            except m.Pessoa.DoesNotExist:
                return Response({"error": "Pessoa não encontrada."}, status=404)

            try:
                paciente = m.Paciente.objects.get(pessoa=pessoa)
            except m.Paciente.DoesNotExist:
                return Response({"error": "Paciente não encontrado."}, status=404)

            serializer = serializers.PacienteSerializer(paciente, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=200)

            return Response(serializer.errors, status=400)

        except Exception as e:
            return Response({"error": str(e)}, status=500)

    def delete(self, request):
        """
        Desativa o paciente vinculado ao usuário autenticado (não remove do banco).
        """
        try:
            email = self.request.user_data.get('email')
            if not email:
                return Response({"error": "E-mail do usuário não encontrado."}, status=400)

            try:
                pessoa = m.Pessoa.objects.get(email=email, ativo=True)
            except m.Pessoa.DoesNotExist:
                return Response({"error": "Pessoa não encontrada."}, status=404)

            try:
                paciente = m.Paciente.objects.get(pessoa=pessoa)
            except m.Paciente.DoesNotExist:
                return Response({"error": "Paciente não encontrado."}, status=404)

            paciente.ativo = False
            paciente.save(update_fields=['ativo'])

            return Response({"message": "Paciente desativado com sucesso."}, status=204)

        except Exception as e:
            return Response({"error": str(e)}, status=500)