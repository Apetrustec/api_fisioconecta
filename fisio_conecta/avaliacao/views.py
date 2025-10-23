from fisio_conecta import models as m
from fisio_conecta.authentications import FirebaseAuthentication
from fisio_conecta.permissions import IsFisioterapeuta, IsLogged, IsPaciente
from . import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Avg
from django.db.models import Q



class AvaliacaoCrud(APIView):
    """
    POST, PUT E DEL de Avaliacao.
    """
    permission_classes = [IsLogged]

    def post(self, request): 
        try:
            atendimento_id = request.data.get('atendimento', None)
            destinatario_id = request.data.get('destinatario', None) # atualmente ta sendo mandando o id ou do paciente ou do fisioterapeuta
            nota_gent = int(request.data.get('nota_gent') or 5)
            nota_educ = int(request.data.get('nota_educ') or 5)
            nota_pont = int(request.data.get('nota_pont') or 5)
            comentario = request.data.get('comentario', None)

            if not atendimento_id:
                return Response({"error": "ID do atendimento é obrigatório."}, status=400)
            if not destinatario_id:
                return Response({"error": "ID do destinatário é obrigatório."}, status=400)

            try:
                atendimento = m.Atendimento.objects.get(id_atendimento=atendimento_id)
            except m.Atendimento.DoesNotExist:
                return Response({"error": "Atendimento não encontrado."}, status=404)

            try:
                autor = m.Pessoa.objects.get(email=request.user_data.get('email'))
            except m.Pessoa.DoesNotExist:
                return Response({"error": "Autor não encontrado."}, status=404)

            paciente = m.Paciente.objects.filter(id_paciente=destinatario_id).first() #precisa ser modificado
            fisio = m.Fisioterapeuta.objects.filter(id_fisio=destinatario_id).first()
            pessoa = m.Pessoa.objects.filter(
                Q(id_pessoa=destinatario_id) |
                Q(paciente__id_paciente=destinatario_id) |
                Q(fisioterapeuta__id_fisio=destinatario_id)
            ).first()

            destinatario = pessoa

            if atendimento.status != 2:
                return Response({
                    "error": "Não é possível cadastrar avaliações para atendimentos que ainda não ocorreram."
                }, status=400)

            avaliacao = m.Avaliacao.objects.create(
                atendimento=atendimento,
                autor=autor,
                destinatario=destinatario,
                nota_gent=nota_gent,
                nota_educ=nota_educ,
                nota_pont=nota_pont,
                comentario=comentario
            )

            avaliacoes = m.Avaliacao.objects.filter(destinatario=destinatario, ativo=True)
            medias = avaliacoes.aggregate(
                media_gent=Avg("nota_gent"),
                media_educ=Avg("nota_educ"),
                media_pont=Avg("nota_pont"),
            )
            media_final = (
                (medias["media_gent"] or 0) +
                (medias["media_educ"] or 0) +
                (medias["media_pont"] or 0)
            ) / 3
            media_final = round(media_final, 2)
            print(media_final)

            if paciente:
                paciente.nota_paciente = media_final
                paciente.save(update_fields=["nota_paciente"])
            elif fisio:
                fisio.nota_fisioterapeuta = media_final
                fisio.save(update_fields=["nota_fisioterapeuta"])

            serializer = serializers.AvaliacaoSerializer(avaliacao)
            return Response(serializer.data, status=201)

        except Exception as e:
            return Response({"error": str(e)}, status=500)


    def put(self, request):
        """
        Atualiza uma avaliação existente.
        """
        try:
            id_avaliacao = request.query_params.get('id', None)
            pessoa = m.Pessoa.objects.get(email=request.user_data.get('email'))

            if not id_avaliacao:
                return Response({"error": "ID da avaliação não fornecido."}, status=400)

            try:
                avaliacao = m.Avaliacao.objects.get(id_avaliacao=id_avaliacao)
            except m.Avaliacao.DoesNotExist:
                return Response({"error": "Avaliação não encontrada."}, status=404)
            
            if pessoa != avaliacao.autor and pessoa != avaliacao.destinatario:
                return Response({"error": "Você não tem permissão para atualizar esta avaliação."}, status=403)

            serializer = serializers.AvaliacaoSerializer(avaliacao, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=200)

            return Response({"error": serializer.errors}, status=400)

        except Exception as e:
            return Response({"error": str(e)}, status=500)


    def delete(self, request):
        """
        desativa uma avaliação
        """
        try:
            id_avaliacao = request.query_params.get('id', None)
            pessoa = m.Pessoa.objects.get(email=request.user_data.get('email'))

            if not id_avaliacao:
                return Response({"error": "ID da avaliação não fornecido."}, status=400)

            try:
                avaliacao = m.Avaliacao.objects.get(id_avaliacao=id_avaliacao)
                
                if pessoa != avaliacao.autor and pessoa != avaliacao.destinatario:
                    return Response({"error": "Você não tem permissão para atualizar esta avaliação."}, status=403)
                
                if avaliacao.ativo == False:
                    return Response ({"error":"Essa avaliação já está desativada."}, status=400)
            
                avaliacao.ativo = False
                avaliacao.save(update_fields=['ativo'])
                return Response(status=204)
            except m.Avaliacao.DoesNotExist:
                return Response({"error": "Avaliação não encontrada."}, status=404)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
        

class AvaliacaoPorAtendimento (APIView):
    """
    Retorna as avaliações de um atendimento
    """
    permission_classes = [IsLogged]

    def get(self, request):
        try:
            id_atend = request.query_params.get('id', None)
            pessoa = m.Pessoa.objects.get(email=request.user_data.get('email'))

            if not id_atend:
                return Response({"error": "ID do atendimento não foi enviado."}, status=400)

            try:
                atendimento = m.Atendimento.objects.get(id_atendimento=id_atend)
            except m.Atendimento.DoesNotExist:
                return Response({"error": "Atendimento não encontrado."}, status=404)
            
            if atendimento.paciente.pessoa != pessoa and atendimento.fisioterapeuta.pessoa != pessoa:
                return Response({"error": "Você não tem permissão para acessar as avaliações deste atendimento."}, status=403)

            try:
                avaliacao = m.Avaliacao.objects.filter(atendimento=atendimento)
            except m.Avaliacao.DoesNotExist:
                return Response({"error": "Nenhuma avaliação encontrada para este atendimento."}, status=404)

            serializer = serializers.AvaliacaoSerializer(avaliacao, many=True)
            return Response(serializer.data, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)  


class AvaliacaoFisioterapeuta(APIView):
    """
    Retorna as avaliações de um fisioterapeuta
    """
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsPaciente]

    def get(self, request):
        try:
            id_fisio = request.query_params.get('id', None)
            pessoa = m.Pessoa.objects.get(email=request.user_data.get('email'))
            
            if not pessoa:
                return Response({"error": "Usuário não encontrado."}, status=404)
            
            paciente = m.Paciente.objects.get(pessoa=pessoa)
            if not paciente:
                return Response({"error": "Você não é um paciente."}, status=403)

            if not id_fisio:
                return Response({"error": "ID do fisioterapeuta não foi enviado."}, status=400)

            try:
                fisioterapeuta = m.Fisioterapeuta.objects.get(id_fisio=id_fisio)
            except m.Fisioterapeuta.DoesNotExist:
                return Response({"error": "Fisioterapeuta não encontrado."}, status=404)

            avaliacao = m.Avaliacao.objects.filter(destinatario=fisioterapeuta.pessoa, ativo=True)
            serializer = serializers.AvaliacaoSerializer(avaliacao, many=True)
            return Response(serializer.data, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
        

class AvaliacaoPaciente(APIView):
    """
    Retorna as avaliações de um paciente
    """
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsFisioterapeuta]

    def get(self, request):
        try:
            id_paciente = request.query_params.get('id', None)
            pessoa = m.Pessoa.objects.get(email=request.user_data.get('email'))
            
            if not pessoa:
                return Response({"error": "Usuário não encontrado."}, status=404)
            
            fisio = m.Fisioterapeuta.objects.get(pessoa=pessoa)
            if not fisio:
                return Response({"error": "Você não é um fisioterapeuta."}, status=403)

            if not id_paciente:
                return Response({"error": "ID do paciente não foi enviado."}, status=400)

            try:
                paciente = m.Paciente.objects.get(id_paciente=id_paciente)
            except m.Paciente.DoesNotExist:
                return Response({"error": "Paciente não encontrado."}, status=404)

            avaliacao = m.Avaliacao.objects.filter(destinatario=paciente.pessoa, ativo=True)
            serializer = serializers.AvaliacaoSerializer(avaliacao, many=True)
            return Response(serializer.data, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)