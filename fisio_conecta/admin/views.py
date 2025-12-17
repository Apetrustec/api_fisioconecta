from fisio_conecta import models as m
from fisio_conecta.pessoa import serializers as pessoaserializers
from fisio_conecta.atendimento import serializers as atendimentoserializers
from fisio_conecta.avaliacao import serializers as AvaliacoesSerializer
from fisio_conecta.admin import serializers as adminserializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from fisio_conecta.permissions import IsAdmin
from fisio_conecta.authentications import FirebaseAuthentication
from fisio_conecta.pessoa.filters import PessoaFilter
from fisio_conecta.atendimento.filters import AtendimentoFilter
from fisio_conecta.avaliacao.filters import AvaliacaoFilter
from django.db.models import Count,Q
from fisio_conecta.utils import formatarTelefone
from fisio_conecta.integracoes.send_zapi import SendZapi







class LoginAdmin(APIView):
    """
    endpoint feito para fazer login admin
    """
    def get(self, request):
        try:
            email = request.query_params.get('email')

            admin = m.Administrador.objects.filter(pessoa__email=email).first()

            if not admin:
                return Response({"error": "Você não tem permissão para executar essa ação."}, status=403)
            
            return Response(status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Erro interno: {str(e)}")
            return Response({"error": f"Erro interno: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            

class PessoaAdminView(APIView):
    """
    Endpoint feito para listar todas as pessoas cadastradas no sistema.
    Apenas administradores.
    """

    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAdmin]

    def get(self, request):
        try:

            admin = m.Administrador.objects.filter(pessoa__email=request.user_data.get("email")).first()
            if not admin:
                return Response({"error": "Você não tem permissão para executar essa ação."}, status=403)

            filterset = PessoaFilter(request.GET, queryset=m.Pessoa.objects.all().order_by('-id_pessoa'))
            if not filterset.is_valid():
                return Response(filterset.errors, status=400)

            pessoas = filterset.qs
            paginator = PageNumberPagination()
            paginator.page_size = 10  
            paginator.page_size_query_param = 'page_size'
            paginator.max_page_size = 100

            result_page = paginator.paginate_queryset(pessoas, request)
            serializer = pessoaserializers.PessoaCompletoSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)
    

        except Exception as e:
            return Response({"error": f"Erro ao listar pessoas: {str(e)}"}, status=500)
        
    def put(self, request):
        id = request.query_params.get("id_pessoa", None)
        
        pessoa = m.Pessoa.objects.get(id_pessoa=id)
        
        if not pessoa:
            return Response({"error": "Pessoa não encontrada."}, status=404)
        
        serializer = pessoaserializers.PessoaSerializer(pessoa, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
class AtendimentoAdminView(APIView):
    """
    Endpoint feito para listar todos os atendimentos cadastrados no sistema.
    Apenas administradores.
    """
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAdmin]

    def get(self, request):
        try:
            admin = m.Administrador.objects.filter(pessoa__email=request.user_data.get("email")).first()
            if not admin:
                return Response({"error": "Você não tem permissão para executar essa ação."}, status=403)

            atendimento_id = request.query_params.get("id", None)
            if atendimento_id:
                atendimento = m.Atendimento.objects.filter(id=atendimento_id).first()
                if not atendimento:
                    return Response({"error": "Atendimento não encontrado."}, status=404)

                serializer = atendimentoserializers.ResponseAtendimentoSerializer(atendimento)
                return Response(serializer.data)

            # caso contrário, aplica filtro
            filterset = AtendimentoFilter(request.GET, queryset=m.Atendimento.objects.all())
            if not filterset.is_valid():
                return Response(filterset.errors, status=400)

            atendimentos = filterset.qs

            # paginação
            paginator = PageNumberPagination()
            paginator.page_size = 10
            paginator.page_size_query_param = 'page_size'
            paginator.max_page_size = 100

            result_page = paginator.paginate_queryset(atendimentos, request)
            serializer = atendimentoserializers.ResponseAtendimentoSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)

        except Exception as e:
            return Response({"error": f"Erro ao listar atendimentos: {str(e)}"}, status=500)
           

class RelatorioView(APIView):

    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAdmin]

    def get(self, request):

        admin = m.Administrador.objects.filter(pessoa__email=request.user_data.get("email")).first()
        if not admin:
            return Response({"error": "Você não tem permissão para executar essa ação."}, status=403)

        fisio_stats = m.Fisioterapeuta.objects.aggregate(
            total=Count('id_fisio'),
            ativos=Count('id_fisio', filter=Q(ativo=True)),
            inativos=Count('id_fisio', filter=Q(ativo=False))
        )
        
        paciente_stats = m.Paciente.objects.aggregate(
            total=Count('id_paciente'),
            ativos=Count('id_paciente', filter=Q(ativo=True)),
            inativos=Count('id_paciente', filter=Q(ativo=False))
        )

        atendimento_stats = m.Atendimento.objects.aggregate(
            total=Count('id_atendimento'),
            agendado=Count('status',filter=Q(status=5)),
            cancelado=Count('status',filter=Q(status=3)),
            concluidos=Count('status',filter=Q(status=2))
            
        )

        avaliacao_stats = m.Avaliacao.objects.aggregate(
            total=Count('id_avaliacao'),
            positivas=Count('id_avaliacao', filter=Q(nota_gent__gte=4, nota_educ__gte=4, nota_pont__gte=4)),
            negativas=Count('id_avaliacao', filter=Q(nota_gent__lte=2, nota_educ__lte=2, nota_pont__lte=2))
        )


        data = {
            "total_fisio": fisio_stats['total'],
            "total_fisio_ativos": fisio_stats['ativos'],
            "total_fisio_inativos": fisio_stats['inativos'],
            "total_pacientes": paciente_stats['total'],
            "total_pacientes_ativos": paciente_stats['ativos'],
            "total_pacientes_inativos": paciente_stats['inativos'],
            "total_atendimentos": atendimento_stats['total'],
            "atendimentos_agendado": atendimento_stats['agendado'],
            "atendimentos_cancelado": atendimento_stats['cancelado'],
            "atendimentos_concluidos": atendimento_stats['concluidos'],
            "total_avaliacoes": avaliacao_stats['total'],
            "total_avaliacoes_positivas": avaliacao_stats['positivas'],
            "total_avaliacoes_negativas": avaliacao_stats['negativas']
        }

        return Response(data)
    
class MudarStatusPacienteView(APIView):
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAdmin]

    def put(self, request):
        """
        Endpoint feito para o administrador mudar o status de um fisioterapeuta.
        """
        id_paciente = request.query_params.get("id_paciente", None)

        admin = m.Administrador.objects.filter(pessoa__email=request.user_data.get("email")).first()
        if not admin:
            return Response({"error": "Você não tem permissão para executar essa ação."}, status=403)

        if not id_paciente:
            return Response({"error": "ID do paciente não fornecido."}, status=400)
        try:
            paciente = m.Paciente.objects.get(id_paciente=id_paciente)
        except m.Paciente.DoesNotExist:
            raise Exception("Paciente não encontrado.")
        if paciente.ativo == True:
            paciente.ativo = False
        else:
            paciente.ativo = True
            sendzapi = SendZapi()
            try:
                telefone = formatarTelefone(paciente.pessoa.telefone)
                texto = (
                            "Olá " + str(paciente.pessoa.nome) + ",\n\n"
                            "Que bom ter você aqui. O seu acesso ao Fisio Conecta foi liberado com sucesso.\n\n"
                            "A partir de agora, você pode encontrar o fisioterapeuta ideal para cuidar da sua evolução  e melhorar o seu bem-estar.\n\n"
                            "Que essa nova etapa seja leve, tranquila e cheia de boas descobertas.\n\n"
                            "E lembre-se, estamos ao seu lado em cada passo do caminho.\n\n"
                            "Conte com a gente sempre que precisar. #vqv"
                        )
                sendzapi.enviar_mensagem_texto(texto, telefone)
            except Exception as e:
                print(f"Erro ao enviar mensagem WhatsApp para o administrador: {str(e)}")
        paciente.save()
        return Response({"status": "Status do paciente alterado com sucesso."})


class MudarStatusFisioterapeutaView(APIView):
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAdmin]
    def put(self, request):
        """
        Endpoint feito para o administrador mudar o status de um fisioterapeuta.
        """
        id_fisio = request.query_params.get("id_fisio", None)

        admin = m.Administrador.objects.filter(pessoa__email=request.user_data.get("email")).first()
        if not admin:
            return Response({"error": "Você não tem permissão para executar essa ação."}, status=403)

        if not id_fisio:
            return Response({"error": "ID do fisioterapeuta não fornecido."}, status=400)
        
        fisioterapeuta = m.Fisioterapeuta.objects.filter(id_fisio=id_fisio).first()

        try:
            fisioterapeuta = m.Fisioterapeuta.objects.get(id_fisio=id_fisio)
        except m.Fisioterapeuta.DoesNotExist:
            raise Exception("Fisioterapeuta não encontrado.")
        if fisioterapeuta.ativo == True:
            fisioterapeuta.ativo = False
        else:
            fisioterapeuta.ativo = True
            sendzapi = SendZapi()
            try:
                telefone = formatarTelefone(fisioterapeuta.pessoa.telefone)
                texto = (
                            "Olá " + str(fisioterapeuta.pessoa.nome) + ",\n\n"
                            "O seu acesso à plataforma Fisio Conecta foi liberado com sucesso.\n\n"
                            "Agora você já pode iniciar a sua atuação como profissional parceiro.\n\n"
                            "Desejamos que essa nova etapa seja leve, produtiva e cheia de boas conexões.\n\n"
                            "Conte com a gente sempre que precisar.\n\n"
                            "Estamos aqui para caminhar com você.#vqv"
                        )
                sendzapi.enviar_mensagem_texto(texto, telefone)
            except Exception as e:
                print(f"Erro ao enviar mensagem WhatsApp para o administrador: {str(e)}")

        fisioterapeuta.save()
        return Response({"status": "Status do fisioterapeuta alterado com sucesso."})
    
class ListarAvaliacoesAdmin(APIView):
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAdmin]

    def get (self, request):
        """
        Endpoint feito para listar todas as avalições de um atendimento.
        """
        try:
            admin = m.Administrador.objects.filter(pessoa__email=request.user_data.get("email")).first()
            if not admin:
                return Response({"error": "Você não tem permissão para executar essa ação."}, status=403)

            filterset = AvaliacaoFilter(request.GET, queryset=m.Avaliacao.objects.all())
            if not filterset.is_valid():
                    return Response(filterset.errors, status=400)

            avaliacoes = filterset.qs
            paginator = PageNumberPagination()
            paginator.page_size = 10  
            paginator.page_size_query_param = 'page_size'
            paginator.max_page_size = 100

            result_page = paginator.paginate_queryset(avaliacoes, request)
            serializer = AvaliacoesSerializer.SerializerAvaliacaoAdmin(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        except Exception as e:
            return Response({"error": f"Erro ao listar avaliações: {str(e)}"}, status=500)


class EspecialidadeAdmin(APIView):
    """
    Endpoint para o administrador cadastrar especialidades.
    """
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAdmin]

    def get(self, request):
        try:
            admin = m.Administrador.objects.filter(pessoa__email=request.user_data.get("email")).first()
            if not admin:
                return Response({"error": "Você não tem permissão para executar essa ação."}, status=status.HTTP_403_FORBIDDEN)

            especialidades = m.Especialidade.objects.all()
            serializer = atendimentoserializers.EspecialidadeSerializer(especialidades, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Erro ao Listar especialidades: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        """
        Cadastra uma nova especialidade.
        """
        try:
            admin = m.Administrador.objects.filter(pessoa__email=request.user_data.get("email")).first()
            if not admin:
                return Response({"error": "Você não tem permissão para executar essa ação."}, status=403)

            nome = (request.data.get("nome") or "").strip()
            if not nome:
                return Response({"error": "Nome da especialidade não fornecido."}, status=400)

            existente = m.Especialidade.objects.filter(nome__iexact=nome).first()
            if existente:
                return Response(
                    {"error": "Especialidade já existe.", "id_especialidade": existente.id_especialidade},
                    status=409
                )

            especialidade = m.Especialidade.objects.create(nome=nome, ativo=True)
            serializer = atendimentoserializers.EspecialidadeSerializer(especialidade)
            return Response(serializer.data, status=201)

        except Exception as e:
            print(f"Erro ao cadastrar especialidade: {str(e)}")
            return Response({"error": str(e)}, status=500)

class cadastrarAdminOrGetAdmin(APIView):
    """
    Endpoint para o administrador cadastrar outros administradores.
    """
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAdmin]

    def get(self, request):
        try:
            admin = m.Administrador.objects.filter(pessoa__email=request.user_data.get("email")).first()
            if not admin:
                return Response({"error": "Você não tem permissão para executar essa ação."}, status=403)

            admins = m.Administrador.objects.all()
            serializer = adminserializers.AdminSerializer(admins, many=True)
            return Response(serializer.data, status=200)

        except Exception as e:
            return Response({"error": f"Erro ao listar administradores: {str(e)}"}, status=500)

    def post(self, request):
        try:
            admin = m.Administrador.objects.filter(pessoa__email=request.user_data.get("email")).first()
            if not admin:
                return Response({"error": "Você não tem permissão para executar essa ação."}, status=403)

            email = request.data.get("email", "").strip()
            pessoa = m.Pessoa.objects.filter(email=email).first()
            if not pessoa:
                return Response({"error": "Pessoa com esse email não encontrada."}, status=404)

            existente = m.Administrador.objects.filter(pessoa=pessoa).first()
            if existente:
                return Response({"error": "Essa pessoa já é um administrador."}, status=409)

            novo_admin = m.Administrador.objects.create(pessoa=pessoa)
            serializer = adminserializers.AdminSerializer(novo_admin)
            return Response(serializer.data, status=201)

        except Exception as e:
            return Response({"error": f"Erro ao cadastrar administrador: {str(e)}"}, status=500)
        


    

