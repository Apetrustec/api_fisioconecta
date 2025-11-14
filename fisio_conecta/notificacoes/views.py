from rest_framework import status
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from fisio_conecta.permissions import IsLogged, IsAdmin
from fisio_conecta import models as m
import firebase_admin
from firebase_admin import messaging
from fisio_conecta.authentications import FirebaseAuthentication

# from fisio_conecta.notificacoes.utils import enviar_multicast



class CadastrarDispositivo(APIView):
    """
    esse endpoint cadastra o dispositivo da pessoa e inscreve no tópico inicial de todos-usuarios 
    """
    permission_classes = [IsLogged]

    def post(self, request):
        try:
            email = request.user_data.get("email")
            pessoa = m.Pessoa.objects.get(email=email)

            if not pessoa:
                raise Exception("Pessoa não encontrada")
            

            token = request.data.get("token")
            descricao = request.data.get("descricao", "")

            if not token:
                return Response({"error": "Token é obrigatório"}, status=status.HTTP_400_BAD_REQUEST)

            dispositivo, created = m.Dispositivo.objects.get_or_create(
                pessoa=pessoa,
                token=token,
                defaults={"descricao": descricao}
            )

            if not created:
                dispositivo.descricao = descricao
                dispositivo.save(update_fields=["descricao"])

            app_fisio = firebase_admin.get_app('fisio_conecta')

            topic_name = "todos-usuarios"
            m.Topico.objects.get_or_create(pessoa=pessoa, nome=topic_name)
            messaging.subscribe_to_topic([token], topic_name, app=app_fisio)

            if pessoa.tipo_usuario == 1:
                topic_name = "user-paciente"
                m.Topico.objects.get_or_create(pessoa=pessoa, nome=topic_name)
                messaging.subscribe_to_topic([token], topic_name, app=app_fisio)

            elif pessoa.tipo_usuario == 2:
                topic_name = "user-fisioterapeuta"
                m.Topico.objects.get_or_create(pessoa=pessoa, nome=topic_name)
                messaging.subscribe_to_topic([token], topic_name, app=app_fisio)

            return Response(status=status.HTTP_201_CREATED)

        except m.Pessoa.DoesNotExist:
            return Response({"error": "Pessoa não encontrada"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class NotificacaoAdmin(APIView):
    """
    Esse endpoint serve para enviar notificação push para apenas uma pessoa 
    ou notificações por tópico conforme vem do corpo da requisição.
    """
    permission_classes = [IsAdmin]
    authentication_classes = [FirebaseAuthentication]

    def post(self, request):
        try:
            title = request.data.get("title")
            body = request.data.get("body")
            topic = request.data.get("topic")
            id_pessoa = request.data.get("id_pessoa")

            if not title or not body:
                raise Exception("Título e texto são obrigatórios")
            
            app_fisio = firebase_admin.get_app('fisio_conecta')

            # Notificação para uma pessoa específica
            if id_pessoa:
                if not m.Pessoa.objects.filter(id_pessoa=id_pessoa).exists():
                    return Response({"error": "Pessoa não encontrada"}, status=404)

                dispositivo = m.Dispositivo.objects.filter(pessoa_id=id_pessoa).last()
                token = dispositivo.token if dispositivo else None
                if not token:
                    raise Exception("Erro ao enviar notificação: dispositivo não encontrado")
                
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=title,
                        body=body,
                    ),
                    token=token,
                )

                response = messaging.send(message, app=app_fisio)

                return Response(
                    {"success": True, "firebase_response": response},
                    status=status.HTTP_200_OK,
                )
            
            # Notificação para um tópico específico
            else:
                if not topic:
                    raise Exception("Tópico é obrigatório")

                message = messaging.Message(
                    notification=messaging.Notification(
                        title=title,
                        body=body,
                    ),
                    topic=topic,
                )

                response = messaging.send(message, app=app_fisio)

                return Response(
                    {"success": True, "firebase_response": response},
                    status=status.HTTP_200_OK,
                )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)







        
        
class PushNotification(APIView):
    """
    Endpoint básico para enviar notificação push (apenas para teste).
    """
    # permission_classes = [IsAdmin]
    # authentication_classes = [FirebaseAuthentication]
    

    def post(self, request):
        try:
            title = request.data.get("title")
            body = request.data.get("body")
            token = request.data.get("token") 

            if not title or not body or not token:
                return Response(
                    {"error": "Título, corpo e token são obrigatórios"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                token=token,  
            )

            app_fisio = firebase_admin.get_app('fisio_conecta')

            response = messaging.send(message, app=app_fisio)

            return Response(
                {"success": True, "firebase_response": response},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class TestPushNotificationTopic(APIView):
    """
    Endpoint básico para enviar notificação push para um tópico.(TESTE)
    """

    def post(self, request):
        try:
            title = request.data.get("title")
            body = request.data.get("body")
            topic = request.data.get("topic", "todos-usuarios")

            if not title or not body:
                return Response(
                    {"error": "Título e corpo são obrigatórios"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                topic=topic,  
            )

            app_fisio = firebase_admin.get_app('fisio_conecta')

            response = messaging.send(message, app=app_fisio)

            return Response(
                {"success": True, "firebase_response": response},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# class TestMulticastNotification(APIView):
#     """
#     Endpoint para testar envio de notificações multicast.
#     """
#     def post(self, request):
#         title = request.data.get("title")
#         body = request.data.get("body")
#         tokens = request.data.get("tokens", [])

#         if not title or not body or not tokens:
#             return Response(
#                 {"error": "title, body e tokens são obrigatórios"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         resultado = enviar_multicast(title, body, tokens)
#         return Response({"resultado": resultado}, status=status.HTTP_200_OK)