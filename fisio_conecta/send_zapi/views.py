
from datetime import timezone
from fisio_conecta.models import CodigoVerificacao
from fisio_conecta.utils import formatarTelefone, gerar_codigo_verificacao
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from dotenv import load_dotenv
from os import getenv
from fisio_conecta import models as m
from fisio_conecta.authentications import FirebaseAuthentication
from fisio_conecta.integracoes.send_zapi import SendZapi
from fisio_conecta.permissions import IsAdmin, IsLogged





load_dotenv()

IS_PRODUCTION = True if getenv('IS_PRODUCTION', 'True') == 'True' else False

class Conexao(APIView):
	# authentication_classes = [FirebaseAuthentication]
	# permission_classes = [IsAdmin]


	def get(self, request): # Criar conexão com whatsapp
		try:
			send_zapi = SendZapi()
			json = send_zapi.conectar_whatsapp()
			return Response(json, status=HTTP_200_OK)
		except Exception as e:
			print(str(e))
			return Response(str(e), status=HTTP_400_BAD_REQUEST)


	def put (self, request): # Confirma conexão com whatsapp
		try:
			url = 'https://api.fisioconecta.com.br/sendzapi/webhook/' if IS_PRODUCTION else 'https://teste-api.fisioconecta.com.br/sendzapi/webhook/'
			send_zapi = SendZapi()
			json = send_zapi.criar_webhook('Apetrus Webhook', url)
			send_zapi.atualizar_evento_webhook(json['webhookId'], connectionUpdate=True)
			return Response(status=HTTP_200_OK)
		except Exception as e:
			print(str(e))
			return Response(str(e), status=HTTP_400_BAD_REQUEST)


	def delete(self, request): # Criar conexão com whatsapp
		try:
			url = 'https://api.fisioconecta.com.br/sendzapi/webhook/' if IS_PRODUCTION else 'https://teste-api.fisioconecta.com.br/sendzapi/webhook/'
			send_zapi = SendZapi()
			json = send_zapi.desconectar_whatsapp()
			try:
				webhooks = send_zapi.pegar_webhooks_cadastrados()
				for webhook in webhooks:
					if url == webhook.get('url'):
						send_zapi.deletar_webhook(webhook.get('webhookId'))
						try:
							send_zapi.deletar_webhook(webhook.get('webhookId')) # Não apagar
						except:
							print('Realmente foi interrompida')
			except:
				print(str(e))
			return Response(json, status=HTTP_200_OK)
		except Exception as e:
			print(str(e))
			return Response(str(e), status=HTTP_400_BAD_REQUEST)

# VAI SER UTILIZADO NA PROXIMA ATUALIZAÇÃO ---------------------------------------------------------------------------------------------
class EnviarCodigoVerificacao(APIView):
    permission_classes = [IsLogged]

    def post(self, request):
        try:
            pessoa = m.Pessoa.objects.get(email=request.user_data.get('email'))

            if not pessoa:
                raise Exception('Pessoa não encontrada.')


            celular = request.data.get('celular', None)
            if not celular:
                raise Exception('O número do celular é obrigatório.')

            codigo_verificacao = gerar_codigo_verificacao(usuario_utilizador=pessoa)

            mensagem = f"Seu código de verificação é: {codigo_verificacao.codigo}"

            numero_formatado = f'55{formatarTelefone(celular, ddi=False)}'

            send_zapi = SendZapi()
            json = send_zapi.enviar_mensagem_texto(mensagem, numero_formatado)

            return Response(json, status=HTTP_200_OK)

        except Exception as e:
            print(str(e))
            return Response({'error': str(e)}, status=HTTP_400_BAD_REQUEST)
		

class VerificaCodigoWhatsApp(APIView):
    permission_classes = [IsLogged]

    def post(self, request):
        try:
            pessoa = m.Pessoa.objects.get(email=request.user_data.get('email'))
            codigo_digitado = request.data.get('codigo', None)
			
            if not pessoa:
                raise Exception('usuario não encontrado')

            if not codigo_digitado:
                raise Exception('O código é obrigatório.')

            codigo_verificacao = CodigoVerificacao.objects.filter(codigo=codigo_digitado, usuario_utilizador=pessoa).first()

            if not codigo_verificacao:
                raise Exception('Código inválido ou não encontrado.')

            if codigo_verificacao.expira_em < timezone.now():
                raise Exception('O código expirou.')

            if codigo_verificacao.usado:
                raise Exception('O código já foi utilizado.')

            codigo_verificacao.usado = True
            codigo_verificacao.save()

            return Response({'message': 'Código verificado com sucesso.'}, status=HTTP_200_OK)

        except Exception as e:
            print(str(e))
            return Response({'error': str(e)}, status=HTTP_400_BAD_REQUEST)
# -------------------------------------------------------------------------------------------------------------------------------------------------       
        
@api_view(['POST', 'GET', 'PUT', 'DELETE'])
def webhook(request):
	# print(request.data)
	# print(request.query_params)
	return Response(status=HTTP_200_OK)
