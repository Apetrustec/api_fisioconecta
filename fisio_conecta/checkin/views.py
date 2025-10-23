from fisio_conecta import models as m
from fisio_conecta.authentications import FirebaseAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from fisio_conecta.permissions import IsLogged
from fisio_conecta.checkin import serializers


class CheckinView(APIView):
    permission_classes = [IsLogged]

    def post(self, request):
        """
        Endpoint para registrar check-in ou check-out de um atendimento.
        Espera os seguintes dados no corpo da requisição:
        - atendimento_id: ID do atendimento
        - tipo: 'in' para check-in, 'out' para check-out
        - pergunta_dor: Nota de 0 a 10
        - pergunta_mudanca: Nota de 0 a 10
        - pergunta_bem_estar: Nota de 0 a 10
        - pergunta_confianca: Nota de 0 a 10
        """
        atendimento_id = request.data.get('atendimento_id')
        tipo = request.data.get('tipo')
        pergunta_dor = request.data.get('pergunta_dor')
        pergunta_mudanca = request.data.get('pergunta_mudanca')
        pergunta_bem_estar = request.data.get('pergunta_bem_estar')
        pergunta_confianca = request.data.get('pergunta_confianca')


        if not all([atendimento_id, tipo, pergunta_dor is not None, pergunta_mudanca is not None,
                    pergunta_bem_estar is not None, pergunta_confianca is not None]):
            return Response({"error": "Todos os campos são obrigatórios."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            atendimento = m.Atendimento.objects.get(id_atendimento=atendimento_id)
        except m.Atendimento.DoesNotExist:
            return Response({"error": "Atendimento não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        if tipo not in ['in', 'out']:
            return Response({"error": "Tipo inválido. Use 'in' para check-in ou 'out' para check-out."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            checkin = m.CheckInOut.objects.create(
                atendimento=atendimento,
                tipo=tipo,
                pergunta_dor=pergunta_dor,
                pergunta_mudanca=pergunta_mudanca,
                pergunta_bem_estar=pergunta_bem_estar,
                pergunta_confianca=pergunta_confianca
            )
            return Response({"message": "Check-in/out registrado com sucesso.", "checkin_id": checkin.id},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CheckInOutPorPaciente(APIView):
    """
    Retorna o histórico de check-ins e check-outs de um paciente específico.
    """
    permission_classes = [IsLogged]

    def get(self, request, pk):
        try:
            paciente = m.Paciente.objects.filter(pk=pk).first()
            if not paciente:
                return Response({'error': 'Paciente não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

            queryset = m.CheckInOut.objects.filter(atendimento__paciente=paciente).order_by('-criado_em')

            if not queryset.exists():
                return Response({'message': 'Nenhum registro de check-in ou check-out encontrado.'}, status=status.HTTP_204_NO_CONTENT)

            serializer = serializers.CheckInOutAggregateSerializer()
            aggregated_data = serializer.to_representation(queryset, reverse=True)
            print(aggregated_data)

            return Response(aggregated_data, status=status.HTTP_200_OK)

        except Exception as e:
            print("Erro em CheckInOutPorPaciente.get:", str(e))
            return Response({'error': 'Erro interno no servidor.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)