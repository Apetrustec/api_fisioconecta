from firebase_admin import messaging
from django.utils.timezone import localdate
from firebase_admin import credentials, messaging, get_app
from fisio_conecta import models as m

# FISIO_APP_NAME = "fisio_conecta" 

def enviar_notificacao(title: str, body: str, pessoa=None, topic: str = "todos-usuarios"):
    """
    Envia uma notificação push pelo Firebase.
    
    - Se 'pessoa' for passado, envia para cada token individualmente.
    - Se 'pessoa' for None, envia para o tópico.
    """
    FISIO_APP_NAME = "fisio_conecta" 
    app_fisio = get_app(FISIO_APP_NAME)

    if pessoa:

        tokens = list(pessoa.dispositivos.values_list("token", flat=True))
        if not tokens:
            return False

        for token in tokens:
            message = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                token=token,
                android=messaging.AndroidConfig(
                    notification=messaging.AndroidNotification(title=title, body=body, sound="enabled"),
                    priority="high",
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(alert=messaging.ApsAlert(title=title, body=body), sound="default")
                    )
                ),
            )
            try:
                response = messaging.send(message, app=app_fisio)
            except Exception as e:
                print(f"Erro ao enviar notificação para {pessoa.email}, token {token}: {e}")
        return True

    else:
        # Envio POR TOPICOSSSSSSSSS
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            android=messaging.AndroidConfig(
                notification=messaging.AndroidNotification(title=title, body=body, sound="enabled"),
                priority="high",
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(alert=messaging.ApsAlert(title=title, body=body), sound="default")
                )
            ),
            topic=topic,
        )

        try:
            response = messaging.send(message, app=app_fisio)
            print(f"Notificação enviada para tópico '{topic}': {response}")
            return True
        except Exception as e:
            print(f"Erro ao enviar notificação para tópico '{topic}': {e}")
            return False
        
# def enviar_multicast(title: str, body: str, tokens: list[str]):
#     """
#     Envia uma notificação push para múltiplos tokens via Firebase.
    
#     Retorna um dict com sucesso e tokens inválidos.
#     """
#     if not tokens:
#         return {"success": 0, "failure": 0, "invalid_tokens": []}

#     app_fisio = get_app(FISIO_APP_NAME)

#     message = messaging.MulticastMessage(
#         tokens=tokens,
#         notification=messaging.Notification(title=title, body=body),
#         android=messaging.AndroidConfig(
#             notification=messaging.AndroidNotification(title=title, body=body, sound="enabled"),
#             priority="high",
#         ),
#         apns=messaging.APNSConfig(
#             payload=messaging.APNSPayload(
#                 aps=messaging.Aps(alert=messaging.ApsAlert(title=title, body=body), sound="default")
#             )
#         ),
#     )

#     try:
#         response = messaging.send_multicast(message, app=app_fisio)
#         invalid_tokens = [
#             tokens[i] for i, resp in enumerate(response.responses) if not resp.success
#         ]
#         return {
#             "success": response.success_count,
#             "failure": response.failure_count,
#             "invalid_tokens": invalid_tokens
#         }
#     except Exception as e:
#         print(f"Erro ao enviar multicast: {e}")
#         return {"success": 0, "failure": len(tokens), "invalid_tokens": tokens}