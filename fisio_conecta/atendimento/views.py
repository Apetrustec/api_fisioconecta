from fisio_conecta import models as m
from fisio_conecta.authentications import FirebaseAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from fisio_conecta.atendimento.serializers import AtendimentoSerializer,ResponseAtendimentoSerializer
from rest_framework.pagination import PageNumberPagination
from .filters import AtendimentoFilter
from fisio_conecta.permissions import IsLogged,IsPaciente,IsFisioterapeuta
from django.db.models import Q
from fisio_conecta.integracoes.send_zapi import SendZapi
from fisio_conecta.notificacoes.utils import enviar_notificacao
from fisio_conecta.utils import formatarTelefone, formatar_data_hora,gerar_codigo_seguranca


class AtendimentoCrud(APIView):
    """
    CRUD para Atendimento.
    """
    permission_classes  = [IsLogged]
    """
    GET RETORNA TODOS OS ATENDIMENTOS DA PESSOA QUE ESTÁ LOGADA.
    """
    def get(self, request):
        id_atendimento = request.query_params.get('id', None)
        pessoa_email = request.user_data.get('email')

        try:

            if id_atendimento:
                try:
                    atendimento = m.Atendimento.objects.select_related(
                        'paciente__pessoa',
                        'fisioterapeuta__pessoa',
                        'especialidade',
                        'endereco'
                    ).get(
                        Q(paciente__pessoa__email=pessoa_email) | Q(fisioterapeuta__pessoa__email=pessoa_email),
                        id_atendimento=id_atendimento
                    )
                except m.Atendimento.DoesNotExist:
                    return Response({"error": "Atendimento não encontrado."}, status=404)

                serializer = ResponseAtendimentoSerializer(atendimento)
                return Response(serializer.data)

            queryset = m.Atendimento.objects.filter(
                Q(paciente__pessoa__email=pessoa_email) | Q(fisioterapeuta__pessoa__email=pessoa_email)
            ).select_related(
                'paciente__pessoa',
                'fisioterapeuta__pessoa',
                'especialidade',
                'endereco'
            ).order_by('data_hora')

            filtro = AtendimentoFilter(request.GET, queryset=queryset)
            if not filtro.is_valid():
                return Response(filtro.errors, status=status.HTTP_400_BAD_REQUEST)

            queryset = filtro.qs.distinct()

            paginator = PageNumberPagination()
            paginator.page_size = 10
            paginator.page_size_query_param = 'page_size'
            paginator.max_page_size = 100

            result_page = paginator.paginate_queryset(queryset, request)
            serializer = ResponseAtendimentoSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def post(self, request):
        """
        Criação de um novo atendimento 
        """
        try:
            fisioterapeuta_id = request.data.get('id_fisioterapeuta')
            especialidade_id = request.data.get('especialidade')
            data_hora = request.data.get('data_hora')
            
            if not fisioterapeuta_id:
                raise Exception('Fisioterapeuta não informado')
            
            if not especialidade_id:
                raise Exception('Especialidade do Fisioterapeuta não foi informado')
            
            if not data_hora:
                raise Exception('Você precisa selecionar um horario para o atendimento')
            
            paciente = m.Paciente.objects.filter(pessoa__email = request.user_data.get('email')).select_related("pessoa__endereco").first()
            if not paciente:
                return Response({"error": "Paciente não encontrado."}, status=404)
            
            fisioterapeuta = m.Fisioterapeuta.objects.filter(id_fisio=fisioterapeuta_id).first()
            if not fisioterapeuta:
                return Response({"error": "Fisioterapeuta não encontrado."}, status=404)
            
            endereco = paciente.pessoa.endereco
            if not endereco:
                return Response({"error:" "Endereço do paciente não encontrado"}, status=400)
            
            atendimento = m.Atendimento(
                paciente=paciente,
                fisioterapeuta=fisioterapeuta,
                especialidade=m.Especialidade.objects.filter(id_especialidade=especialidade_id).first() if especialidade_id else None,
                data_hora=data_hora,
                endereco=endereco
            )
            atendimento.save()

            serializer = ResponseAtendimentoSerializer(atendimento)
            return Response(serializer.data, status=201)
        
        except Exception as e:
            return Response({"error": f"Erro ao criar atendimento: {str(e)}"}, status=500)
        
    def patch(self, request):
        """
        Atualiza um atendimento.
        """
        try:
            id_atendimento = request.query_params.get('id', None)
            if not id_atendimento:
                return Response({"error": "ID do atendimento não fornecido."}, status=400)

            pessoa_email = request.user_data.get('email')

            
            atendimento = m.Atendimento.objects.filter(
                Q(id_atendimento=id_atendimento) & 
                (Q(paciente__pessoa__email=pessoa_email) | Q(fisioterapeuta__pessoa__email=pessoa_email))
            ).first()

            if not atendimento:
                return Response({"error": "Atendimento não encontrado."}, status=404)

            serializer = AtendimentoSerializer(atendimento, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=200)

            return Response(serializer.errors, status=400)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
        
    def delete(self, request):
        """
        Marca um atendimento como cancelado com base no ID.
        """
        try:
            id_atendimento = request.query_params.get('id', None)
            if not id_atendimento:
                return Response({"error": "ID do atendimento não fornecido."}, status=400)
            
            motivo_cancelamento = request.data.get('motivo_cancelamento')
            if not motivo_cancelamento:
                return Response({"error": "Motivo de cancelamento não fornecido."}, status=400)

            pessoa_email = request.user_data.get('email')

            atendimento = m.Atendimento.objects.filter(
                Q(id_atendimento=id_atendimento) & 
                (Q(paciente__pessoa__email=pessoa_email) | Q(fisioterapeuta__pessoa__email=pessoa_email))
            ).select_related("paciente__pessoa", "fisioterapeuta__pessoa").first()

            if not atendimento:
                return Response({"error": "Atendimento não encontrado."}, status=404)

            atendimento.status = 3  # 3 = Cancelado
            atendimento.motivo_cancelamento = motivo_cancelamento
            atendimento.save(update_fields=['status','motivo_cancelamento'])

            foi_paciente = atendimento.paciente and atendimento.paciente.pessoa.email == pessoa_email
            foi_fisioterapeuta = atendimento.fisioterapeuta and atendimento.fisioterapeuta.pessoa.email == pessoa_email

            sendzapi = SendZapi()

            data = formatar_data_hora(atendimento.data_hora)

            if foi_paciente and atendimento.fisioterapeuta:
                destino = atendimento.fisioterapeuta.pessoa
                try:
                    telefone = formatarTelefone(destino.telefone)
                    texto = (
                        f"Olá {destino.nome}, o paciente {atendimento.paciente.pessoa.nome} "
                        f"cancelou o atendimento marcado para "
                        f"{data}."
                    )
                    sendzapi.enviar_mensagem_texto(texto, telefone)
                except Exception as e:
                    print(f"Erro ao enviar mensagem WhatsApp para o fisioterapeuta: {str(e)}")

                try:
                    enviar_notificacao(
                        title="Atendimento cancelado",
                        body=f"O paciente {atendimento.paciente.pessoa.nome} cancelou o atendimento "
                            f"para {atendimento.data_hora.strftime('%d/%m/%Y %H:%M')}.",
                        pessoa=destino
                    )
                except Exception as e:
                    print(f"Erro ao enviar notificação para o fisioterapeuta: {str(e)}")

            elif foi_fisioterapeuta and atendimento.paciente:
                destino = atendimento.paciente.pessoa
                try:
                    telefone = formatarTelefone(destino.telefone)
                    texto = (
                        f"Olá {destino.nome}, o fisioterapeuta {atendimento.fisioterapeuta.pessoa.nome} "
                        f"cancelou o seu atendimento marcado para "
                        f"{data}."
                    )
                    sendzapi.enviar_mensagem_texto(texto, telefone)
                except Exception as e:
                    print(f"Erro ao enviar mensagem WhatsApp para o paciente: {str(e)}")

                try:
                    enviar_notificacao(
                        title="Atendimento cancelado",
                        body=f"O fisioterapeuta {atendimento.fisioterapeuta.pessoa.nome} cancelou o atendimento "
                            f"para {atendimento.data_hora.strftime('%d/%m/%Y %H:%M')}.",
                        pessoa=destino
                    )
                except Exception as e:
                    print(f"Erro ao enviar notificação para o paciente: {str(e)}")

            return Response({"message": "Atendimento cancelado com sucesso."}, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)

class PropostaAtendimento(APIView):
    """
    CRUD para a proposta de um atendimento.
    """
    authentication_classes = [FirebaseAuthentication]
    permissions_classes = [IsPaciente]

    def post(self, request):
        try:
            especialidade_id = request.data.get('especialidade')
            data_hora = request.data.get('data_hora')
            valor_maximo_proposta = request.data.get('valor_maximo_proposta')
            local_atendimento = request.data.get('local_atendimento')      

            if not especialidade_id:
                raise Exception('Especialidade do Fisioterapeuta não foi informada')
            
            if not data_hora:
                raise Exception('Você precisa selecionar um horário para o atendimento')
                     
            paciente = m.Paciente.objects.filter(
                pessoa__email=request.user_data.get('email')
            ).select_related("pessoa__endereco").first()

            if not paciente:
                return Response({"error": "Paciente não encontrado."}, status=404)         

            endereco = None
            if not local_atendimento:
                endereco = getattr(paciente.pessoa, "endereco", None)
                if not endereco:
                    return Response({"error": "Endereço do paciente não encontrado"}, status=400)

            atendimento = m.Atendimento(
                paciente=paciente,
                especialidade=m.Especialidade.objects.filter(id_especialidade=especialidade_id).first(),
                data_hora=data_hora,
                endereco=endereco if endereco else None,
                local_atendimento=local_atendimento if local_atendimento else None,
                valor_maximo_proposta=valor_maximo_proposta,
                status=4,
                isProposta=True
            )
            atendimento.save()

            fisioterapeutas = m.Fisioterapeuta.objects.filter(
                especialidades__id_especialidade=especialidade_id,
                ativo=True,
                valor_atendimento__lte=valor_maximo_proposta
            )
            
            send_zapi = SendZapi()
            data = formatar_data_hora(atendimento.data_hora)
            # AQUI É O ENVIO DE MENSAGEM PARA WHATSAPP PARA O FISIOTERAPEUTA 
            for fisio in fisioterapeutas: 
                try:
                    telefone_fisioterapeuta = formatarTelefone(fisio.pessoa.telefone)
                    texto = (
                        f"Olá {fisio.pessoa.nome}, "
                        f"um paciente ({paciente.pessoa.nome}) criou uma proposta de atendimento "
                        f"para o dia {data}."
                        f"Você pode aceitar esse atendimento pelo app."
                    )
                    recebedor = telefone_fisioterapeuta
                    send_zapi.enviar_mensagem_texto(texto, recebedor)
                except Exception as e:
                    print(f"Erro ao enviar mensagem WhatsApp para o paciente: {str(e)}")

            # ISSO AQUI DEVE SER MUDADO PARA MULTICAST ----------------------------------------------------------------------------
            for fisio in fisioterapeutas:
                enviar_notificacao(
                    title="Nova proposta de atendimento",
                    body=f"Paciente {paciente.pessoa.nome} propôs um atendimento",
                    pessoa=fisio.pessoa
                )
            # -----------------------------------------------------------------------------------------------------------------------
            serializer = AtendimentoSerializer(atendimento)
            return Response(serializer.data, status=201)

        except Exception as e:
            print("Erro:", str(e))
            return Response({"error": f"Erro ao criar atendimento: {str(e)}"}, status=500)
        

class GetPropostas(APIView):
    """
    Endpoint feito para retornar as proposta para o  fisioterapeuta ja filtrando pela especialidade do fisioterapeuta
    e retornando apenas os que ainda não foram aceitos por outro fisioterapeuta.
    """
    authentication_classes = [FirebaseAuthentication]
    permissions_classes = [IsFisioterapeuta]

    def get(self, request):

        fisioterapeuta = m.Fisioterapeuta.objects.filter(pessoa__email=request.user_data.get('email')).first()

        if not fisioterapeuta.ativo:
            return Response({"error": "Fisioterapeuta não encontrado."}, status=status.HTTP_403_FORBIDDEN)

        try:
            especialidades_fisioterapeuta = fisioterapeuta.especialidades.all()

            queryset = m.Atendimento.objects.filter(
                isProposta=True,
                status=4,  # Aguardando aprovação
                especialidade__in=especialidades_fisioterapeuta,
                fisioterapeuta__isnull=True,
                valor_maximo_proposta__gte=fisioterapeuta.valor_atendimento,
            ).exclude(
                respostas__fisioterapeuta=fisioterapeuta,
                respostas__status=3  # Exclui propostas que o fisio recusou 
            ).select_related(
                'paciente__pessoa', 'especialidade', 'endereco'
            ).order_by('data_hora')

            filtro = AtendimentoFilter(request.GET, queryset=queryset)
            if not filtro.is_valid():
                return Response(filtro.errors, status=status.HTTP_400_BAD_REQUEST)

            queryset = filtro.qs.distinct()

            paginator = PageNumberPagination()
            paginator.page_size = 10
            paginator.page_size_query_param = 'page_size'
            paginator.max_page_size = 100

            result_page = paginator.paginate_queryset(queryset, request)
            serializer = ResponseAtendimentoSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class AceitarAtendimento(APIView):
    """
    Endpoint para o fisioterapeuta aceitar uma proposta.
    """
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsFisioterapeuta]

    def put(self, request, atendimento_id):
        fisioterapeuta = m.Fisioterapeuta.objects.filter(
            pessoa__email=request.user_data.get('email')
        ).first()

        if not fisioterapeuta:
            return Response({"error": "Fisioterapeuta não encontrado."}, status=404)

        try:
            atendimento = m.Atendimento.objects.get(
                id_atendimento=atendimento_id, status=4
            )
        except m.Atendimento.DoesNotExist:
            return Response(
                {"error": "Atendimento não encontrado ou já não está disponível."},
                status=404,
            )

        if not atendimento.isProposta:
            if atendimento.fisioterapeuta and atendimento.fisioterapeuta != fisioterapeuta:
                return Response(
                    {"error": "Você não tem permissão para aceitar este atendimento."},
                    status=403,
                )

            atendimento.status = 5
            atendimento.save(update_fields=['status'])

        else:
            if m.RespostaFisioterapeuta.objects.filter(
                atendimento=atendimento, fisioterapeuta=fisioterapeuta, status=3
            ).exists():
                return Response({"error": "Você já recusou esta proposta."}, status=400)

            resposta, created = m.RespostaFisioterapeuta.objects.get_or_create(
                atendimento=atendimento,
                fisioterapeuta=fisioterapeuta,
                defaults={'status': 2}  # 2 = aceito
            )
            if not created:
                resposta.status = 2
                resposta.save(update_fields=['status'])

            if not atendimento.fisioterapeuta:
                atendimento.fisioterapeuta = fisioterapeuta
                atendimento.status = 5
                atendimento.save(update_fields=['fisioterapeuta', 'status'])

        data = formatar_data_hora(atendimento.data_hora)
        send_zapi = SendZapi()
        codigo = gerar_codigo_seguranca()

        # Envia mensagem para fisioterapeuta
        try:
            telefone_fisio = formatarTelefone(atendimento.fisioterapeuta.pessoa.telefone)
            send_zapi.enviar_mensagem_texto(
                texto=(
                    f"Olá {atendimento.fisioterapeuta.pessoa.nome}, você aceitou o atendimento de {atendimento.paciente.pessoa.nome} para o dia {data}. "
                    f"Por motivos de segurança, informe o código {codigo} antes de começar o atendimento."
                ),
                recebedor=telefone_fisio
            )
        except Exception as e:
            print(f"Erro ao enviar mensagem WhatsApp para o fisioterapeuta: {str(e)}")

        # Envia mensagem para paciente
        try:
            telefone_paciente = formatarTelefone(atendimento.paciente.pessoa.telefone)
            send_zapi.enviar_mensagem_texto(
                texto=(
                    f"Olá {atendimento.paciente.pessoa.nome}, o fisioterapeuta {fisioterapeuta.pessoa.nome} aceitou seu atendimento para o dia {data}. "
                    f"Por motivos de segurança, solicite o código {codigo} antes de começar o atendimento. "
                    f"O código informado deve ser igual ao desta mensagem."
                ),
                recebedor=telefone_paciente
            )
        except Exception as e:
            print(f"Erro ao enviar mensagem WhatsApp para o paciente: {str(e)}")

        # Envia notificação push para o paciente
        try:
            enviar_notificacao(
                title="Seu atendimento foi aceito!",
                body=f"O fisioterapeuta {fisioterapeuta.pessoa.nome} aceitou seu atendimento.",
                pessoa=atendimento.paciente.pessoa
            )
        except Exception as e:
            print(f"Erro ao enviar notificação para paciente: {str(e)}")

        return Response({"message": "Atendimento aceito com sucesso."}, status=200)

class TerminarAtendimento(APIView):
    """
    Endpoint feito para finalizar um atendimento
    """
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsFisioterapeuta]

    def put(self, request, atendimento_id):
        try:
            fisioterapeuta = m.Fisioterapeuta.objects.get(pessoa__email=request.user_data.get('email'))

            if not fisioterapeuta:
                raise Exception("Você não tem permissão para executar essa ação.")

            atendimento = m.Atendimento.objects.filter(
                id_atendimento=atendimento_id,
                fisioterapeuta=fisioterapeuta
            ).first()

            if not atendimento:
                return Response({"error": "Atendimento não encontrado."}, status=404)

            atendimento.status = 2  # 2 = Realizado
            atendimento.save(update_fields=['status'])

            try:
                enviar_notificacao(
                    title="Atendimento finalizado",
                    body=f"O atendimento com {fisioterapeuta.pessoa.nome} foi finalizado. Avalie o atendimento.",
                    pessoa=atendimento.paciente.pessoa
                )
            except Exception as e:
                print(f"Erro ao enviar notificação para paciente: {str(e)}")
                
            serializer = AtendimentoSerializer(atendimento)
            return Response(serializer.data, status=200)

        except m.Fisioterapeuta.DoesNotExist:
            return Response({"error": "Você não tem permissão para executar essa ação."}, status=403)
        except Exception as e:
            return Response({"error": f"Erro ao finalizar atendimento: {str(e)}"}, status=500)
        
class NegarAtendimento(APIView):
    """
    Endpoint para o fisioterapeuta recusar uma proposta ou cancelar um atendimento.
    """
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsFisioterapeuta]

    def put(self, request, atendimento_id):
        fisioterapeuta = m.Fisioterapeuta.objects.filter(
            pessoa__email=request.user_data.get('email')
        ).first()

        if not fisioterapeuta:
            return Response({"error": "Fisioterapeuta não encontrado."}, status=404)

        try:
            atendimento = m.Atendimento.objects.get(id_atendimento=atendimento_id)
        except m.Atendimento.DoesNotExist:
            return Response({"error": "Atendimento não encontrado."}, status=404)

        if not atendimento.isProposta:
            if atendimento.fisioterapeuta and atendimento.fisioterapeuta != fisioterapeuta:
                return Response(
                    {"error": "Você não tem permissão para cancelar este atendimento."},
                    status=403,
                )

            atendimento.status = 6
            atendimento.motivo_cancelamento = request.data.get("motivo", "Cancelado pelo fisioterapeuta")
            atendimento.save(update_fields=["status", "motivo_cancelamento"])

            # Envia notificação para o paciente
            try:
                enviar_notificacao(
                    title="Atendimento cancelado",
                    body=f"O fisioterapeuta {fisioterapeuta.pessoa.nome} cancelou seu atendimento.",
                    pessoa=atendimento.paciente.pessoa
                )
            except Exception as e:
                print(f"Erro ao enviar notificação para paciente: {str(e)}")

            return Response({"message": "Atendimento cancelado com sucesso."}, status=200)

        else:
            resposta, created = m.RespostaFisioterapeuta.objects.get_or_create(
                atendimento=atendimento,
                fisioterapeuta=fisioterapeuta,
                defaults={'status': 3}
            )
            if not created:
                resposta.status = 3
                resposta.save(update_fields=['status'])

            return Response({"message": "Proposta recusada com sucesso."}, status=200)

class ReagendarAtendimento(APIView):
    """
    Endpoint para um fisioterapeuta ou paciente cancelar um reagendamento.
    """
    permission_classes = [IsLogged]

    def post(self, request):
        """
        Criação de um novo atendimento (utilizado para reagendamento)
        """
        try:
            fisioterapeuta_id = request.data.get('id_fisioterapeuta')
            especialidade_id = request.data.get('especialidade')
            data_hora = request.data.get('data_hora')
            local_atendimento = request.data.get('local_atendimento')
            
            pessoa = m.Pessoa.objects.get(email=request.user_data.get('email'))

            if pessoa.tipo_usuario == 2:
                return Response({"error": "Apenas pacientes podem criar um reagendamento."}, status=403)


            if not fisioterapeuta_id:
                raise Exception('Fisioterapeuta não informado')

            if not especialidade_id:
                raise Exception('Especialidade do Fisioterapeuta não foi informado')

            if not data_hora:
                raise Exception('Você precisa selecionar um horario para o atendimento')

            paciente = m.Paciente.objects.filter(pessoa__email=request.user_data.get('email')).select_related('pessoa__endereco').first()
            if not paciente:
                return Response({"error": "Paciente não encontrado."}, status=404)

            fisioterapeuta = m.Fisioterapeuta.objects.filter(id_fisio=fisioterapeuta_id).first()
            if not fisioterapeuta:
                return Response({"error": "Fisioterapeuta não encontrado."}, status=404)

            atendimento = m.Atendimento(
                paciente=paciente,
                fisioterapeuta=fisioterapeuta,
                especialidade=(m.Especialidade.objects.filter(id_especialidade=especialidade_id).first() if especialidade_id else None),
                data_hora=data_hora,
                status=4,
                local_atendimento=(local_atendimento if local_atendimento else None),
                isProposta=False,
                is_retorno=True,
            )
            atendimento.save()

            serializer = AtendimentoSerializer(atendimento)
            return Response(serializer.data, status=201)

        except Exception as e:
            return Response({"error": f"Erro ao criar atendimento: {str(e)}"}, status=500)