from datetime import datetime
from fisio_conecta import models as m
from fisio_conecta.fisioterapeuta import serializers as fisioSerializers
from fisio_conecta.fisioterapeuta import filters as fisioFilters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from fisio_conecta.permissions import IsLogged
from fisio_conecta.utils import formatarTelefone
from fisio_conecta.integracoes.send_zapi import SendZapi



class Crud (APIView):
    """
    GET, POST, PUT e DEL de Fisioterapeuta.
    """
    permission_classes = [IsLogged] 
    
    def get(self, request):
        try:
            email = request.user_data.get('email')

            if email:
                try:
                    fisioterapeuta = m.Fisioterapeuta.objects.select_related("pessoa")\
                        .prefetch_related("especialidades")\
                        .get(pessoa__email=email)

                    serializer = fisioSerializers.TodosFisioSerializer(fisioterapeuta)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                except m.Fisioterapeuta.DoesNotExist:
                    return Response({"error": "Fisioterapeuta não encontrado para este usuário."},
                                    status=status.HTTP_404_NOT_FOUND)

            queryset = m.Fisioterapeuta.objects.select_related('pessoa').prefetch_related('especialidades')
            
            filtro = fisioFilters.FisioterapeutaFilter(request.query_params, queryset=queryset)
            if not filtro.is_valid():
                return Response(filtro.errors, status=status.HTTP_400_BAD_REQUEST)
            queryset = filtro.qs.distinct()

            paginator = PageNumberPagination()
            paginator.page_size = 10
            result_page = paginator.paginate_queryset(queryset, request)
            serializer = fisioSerializers.TodosFisioSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    def post(self, request):
        """
        Cria um novo fisioterapeuta.
        """
        try:
            especialidades_ids = request.data.get('especialidades', [])
            crefito = request.data.get('crefito', None)

            pessoa = m.Pessoa.objects.get(email=request.user_data.get('email'))
            if not pessoa or pessoa.ativo is False:
                return Response({"error": "Pessoa não encontrada ou desativada"}, status=404)

            fisio = m.Fisioterapeuta.objects.filter(pessoa=pessoa).last()
            if fisio:
                return Response({"error": "Já existe um Fisioterapeuta com o id_pessoa informado"}, status=400)

            paciente = m.Paciente.objects.filter(pessoa=pessoa).last()
            if paciente:
                return Response({"error": "Existe um paciente com o id_pessoa informado"}, status=400)

            especialidades = []
            if especialidades_ids:
                especialidades = m.Especialidade.objects.filter(id_especialidade__in=especialidades_ids)
                if len(especialidades) != len(especialidades_ids):
                    return Response({"error": "Uma ou mais especialidades não foram encontradas"}, status=400)
            try:
                fisio = m.Fisioterapeuta.objects.create(
                    pessoa=pessoa,
                    valor_atendimento=request.data.get('valor_atendimento'),
                    crefito=crefito.upper() if crefito else None  # só usa se veio
                )
            except Exception as e:
                return Response({"error": str(e)}, status=400)

            if fisio and especialidades:
                try:
                    for especialidade in especialidades:
                        m.Fisio_especialidade.objects.create(
                            fisioterapeuta=fisio,
                            especialidade=especialidade,
                            ativo=True
                        )
                except Exception as e:
                    return Response({"error": str(e)}, status=400)
                
            send_zapi = SendZapi()
            admins = m.Administrador.objects.all()
            for admin  in admins: 
                try:
                    telefone = formatarTelefone(admin.pessoa.telefone)
                    texto =f'Um novo fisioterapeuta foi cadastrado. Acesse o painel administrativo para verificar.'
                    send_zapi.enviar_mensagem_texto(
                        texto=texto,
                        recebedor=telefone
                    )
                except Exception as e:
                    print(f"Erro ao enviar mensagem WhatsApp para o administrador: {str(e)}")


            serializer = fisioSerializers.FisioterapeutaSerializer(fisio)
            return Response(serializer.data, status=201)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        
        
    def put (self, request):
        """
        Atualiza os dados de um fisioterapeuta.
        """
        
        try:
            try:
                fisio = m.Fisioterapeuta.objects.get(pessoa__email=request.user_data.get('email'))
            except m.Fisioterapeuta.DoesNotExist:
                return Response({"error": "Fisioterapeuta não encontrado"}, status=404)

            if not fisio.ativo:
                return Response({"error": "Fisioterapeuta desativado"}, status=400)

            crefito = request.data.get('crefito')
            if crefito:
                crefito_upper = crefito.upper()
                if m.Fisioterapeuta.objects.exclude(id_fisio=fisio.id_fisio).filter(crefito__iexact=crefito_upper).exists():
                    return Response({"error": "Já existe um fisioterapeuta com esse CREFITO"}, status=400)
                fisio.crefito = crefito_upper

            if 'valor_atendimento' in request.data:
                try:
                    valor = float(request.data.get('valor_atendimento'))
                    if valor <= 0:
                        return Response({"error": "Valor de atendimento inválido"}, status=400)
                    fisio.valor_atendimento = valor
                except Exception as e:
                    return Response({"error": str(e)}, status=400)

            fisio.save()

            if 'especialidades' in request.data:
                especialidades_ids = request.data.get('especialidades', [])

                if not especialidades_ids:
                    return Response({"error": "Nenhuma especialidade fornecida"}, status=400)

                especialidades = m.Especialidade.objects.filter(id_especialidade__in=especialidades_ids, ativo=True)
                if len(especialidades) != len(especialidades_ids):
                    return Response({"error": "Uma ou mais especialidades não foram encontradas ou estão inativas"}, status=400)

                for esp in especialidades:
                    fisio_esp, created = m.Fisio_especialidade.objects.get_or_create(
                        fisioterapeuta=fisio,
                        especialidade=esp,
                        defaults={'ativo': True}
                    )
                    if not created and not fisio_esp.ativo:
                        fisio_esp.ativo = True
                        fisio_esp.save(update_fields=['ativo'])

            serializer = fisioSerializers.FisioterapeutaSerializer(fisio)
            return Response(serializer.data, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=400)
        
        
    def delete(self, request):
        """
        Desativa um fisioterapeuta com base no ID.
        """
        try:
            try:
                fisio = m.Fisioterapeuta.objects.get(pessoa__email=request.user_data.get('email'))
            except m.Fisioterapeuta.DoesNotExist:
                return Response({"error": "Fisioterapeuta não encontrado"}, status=404)

            if not fisio.ativo:
                return Response({"error": "Fisioterapeuta já está desativado"}, status=400)

            fisio.ativo = False
            fisio.save(update_fields=['ativo'])
            
            atendimentos_futuros = m.Atendimento.objects.filter(
                fisioterapeuta=fisio,
                data_hora__gt=datetime.now(),
                status__in=[4, 5, 6, 7]
            )

            atendimentos_futuros.update(status=3)  # Cancelado

            return Response({"message": "Fisioterapeuta desativado com sucesso"}, status=204)

        except Exception as e:
            return Response({"error": str(e)}, status=500)


class TodosPorAtendimento (APIView):
    """
    Retorna todos os fisioterapeutas disponíveis para um atendimento.
    """
    permission_classes = [IsLogged]

    def get(self, request):
        try:
            email = request.user_data.get('email')
            if not email:
                return Response({"error": "Usuário não autenticado"}, status=status.HTTP_401_UNAUTHORIZED)

            pessoa = m.Pessoa.objects.filter(email=email).only('id_pessoa').first()
            if not pessoa:
                return Response({"error": "Pessoa não encontrada"}, status=status.HTTP_404_NOT_FOUND)

            atendimentos = m.Atendimento.objects.filter(
                paciente__pessoa=pessoa,
                status=2,
                fisioterapeuta__isnull=False
            ).only('fisioterapeuta_id')

            fisio_ids = list(atendimentos.order_by().values_list('fisioterapeuta_id', flat=True).distinct())

            if not fisio_ids:
                return Response([], status=status.HTTP_200_OK)

            fisioterapeutas = m.Fisioterapeuta.objects.filter(
                id_fisio__in=fisio_ids,
               ativo=True
            ).select_related('pessoa').prefetch_related('especialidades')

            serializer = fisioSerializers.CamposBasicoFisioSerializer(fisioterapeutas, many=True)
            print(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)