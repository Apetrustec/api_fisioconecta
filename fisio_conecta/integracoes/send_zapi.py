import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

class SendZapi():
	_url = 'https://api.sendzapi.com.br/api/v2'
	_instanceId=os.getenv('SEND_ZAPI_INSTANCE_FISIOCONECTA_ID', None)
	_instanceToken=os.getenv('SEND_ZAPI_INSTANCE_FISIOCONECTA_TOKEN', None)
	_headers = {
		"Content-Type": "application/json",
		"Authorization": None,
		"Authorization": f"Bearer {_instanceToken}"
	}
	
	def __init__(self, _instanceId=None, _instanceToken=None):
		if _instanceId:
			self._instanceId = _instanceId
		if _instanceToken:
			self._instanceToken = _instanceToken

	def informacoes_instancia(self):
		request = requests.get(f'{self._url}/instance/{self._instanceId}/', headers=self._headers)
		if not request.ok:
			print(request.text)
			raise Exception('Não foi possível pegar informações da Instância.')
		return request.json()

		"""
			Exemplo de retorno
			{
       			'instanceId': '870462cc-66e1-4d2b-8c7a-49badc3e01bb',
   				'name': 'apetrus-solucoes-i1',
       			'state': 'active',
          		'connection': 'refused',
            	'createdAt': '2024-07-15T00:00:00.000Z',
             	'WhatsApp': None,
              	'Auth': {
                   	'authId': '3431fd13-daf2-410d-8f74-1f83349fced8',
                    'jwt': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJJX0lEIjoiODcwNDYyY2MtNjZlMS00ZDJiLThjN2EtNDliYWRjM2UwMWJiIiwiQl9JRCI6Ijk2N2VjZmIzLTliMzItNDJmZS04NjE3LWFjZDU0ODgzZjA0OSIsIkFfTiI6ImNvZGVjaGF0X2FwaSIsImlhdCI6MTcyMTA2Njk5OSwiZXhwIjoxNzIxMDcwNTk5LCJzdWIiOiJJX1QifQ.wFHvwdktTCpAP6Z2fZ19YH2_AxHhmxn94jjUPPiXU_0',
                    'createdAt': '2024-07-15T00:00:00.000Z',
                    'updatedAt': None
                },
                'Webhook': [],
                'Business': {
                    'businessId': '967ecfb3-9b32-42fe-8617-acd54883f049',
                    'name': 'Table Message'
                }
            }
  		"""



	def conectar_whatsapp(self):
		request = requests.get(f'{self._url}/instance/{self._instanceId}/connect', headers=self._headers)
		if not request.ok:
			print(request.text)
			raise Exception('Não foi possível conectar a Instância.')
		return request.json()


		"""
			Exemplo de retorno:
			{
       			'code': '2@cDdFVCXstDNBld/712020nEPmYQ4QXAZo6w+YWgaljc3T/rQXTFAV3L7c8wt/Ehl1xQHadZ9zzCiCPcBDtnTCXHwb5nxC0zF130=,EBLIRFdwqRaROA/9VJFy4TPdcpoDHmca1UOrXkOJ+CE=,Gyi1J2HnUQo3G0n2ytWbf1/IeBPeNbCPoMNZtqc1tz0=,F8AIfqOBcRrnTApT/0UNxCVqH92myug3L/tnoD1mNvw=',
          		'base64': 'data:image/png;base64,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'
            }
  		"""



	def desconectar_whatsapp(self):
		request = requests.delete(f'{self._url}/instance/{self._instanceId}/logout', headers=self._headers)
		if not request.ok:
			print(request.text)
			raise Exception('Não foi possível desconectar da Instância.')
		return request.json()



	# Métodos de webhook


	def criar_webhook(self, nome, url, habilitar=True):
		request = requests.post(
      		f'{self._url}/instance/{self._instanceId}/webhook',
			data=json.dumps({
				"name": nome,
				"url": url,
				"enabled": habilitar
       		}),
        	headers=self._headers
        )
		if not request.ok:
			print(request.text)
			raise Exception('Não foi possível criar webhook.')
		return request.json()


		"""
			Exemplo de retorno:
			{
				"webhookId": "b3481122-c848-445c-9493-426918ff5099",
				"name": "chatwoot-connector",
				"url": "string",
				"enabled": true,
				"createdAt": "2023-11-15T00:00:00.000Z",
				"updatedAt": null,
				"instanceInstanceId": "string"
			}
  		"""



	def pegar_webhooks_cadastrados(self):
		request = requests.get(f'{self._url}/instance/{self._instanceId}/webhook', headers=self._headers)
		if not request.ok:
			print(request.text)
			raise Exception('Não foi possível pegar webhook.')
		return request.json()

		"""
			Exemplo de retorno:
			[
				{
					"webhookId": "b3481122-c848-445c-9493-426918ff5099",
					"url": "https://chatwoot.domain.com.br",
					"name": "chatwoot-connector",
					"enabled": true,
					"createdAt": "2023-11-15T00:00:00.000Z",
					"updatedAt": null,
					"instanceInstanceId": "string",
					"WebhookEvents": {
					"webhookEventsId": "string",
					"qrcodeUpdate": false,
					"stateInstance": false,
					"messagesSet": false,
					"messagesUpsert": true,
					"messagesUpdate": false,
					"sendMessage": false,
					"contactsSet": false,
					"contactsUpsert": false,
					"contactsUpdate": false,
					"presenceUpdate": false,
					"chatsSet": false,
					"chatsUpdate": true,
					"chatsUpsert": false,
					"chatsDelete": true,
					"groupsUpsert": false,
					"groupUpdate": false,
					"groupParticipantsUpdate": false,
					"connectionUpdate": false,
					"newJwt": false,
					"createdAt": "2023-11-15T00:00:00.000Z",
					"updatedAt": null,
					"webhookWebhookId": "b3481122-c848-445c-9493-426918ff5099"
					}
				}
			]
  		"""




	def pegar_webhook(self, id_webhook):
		request = requests.get(f'{self._url}/instance/{self._instanceId}/webhook/{id_webhook}', headers=self._headers)
		if not request.ok:
			print(request.text)
			raise Exception('Não foi possível pegar webhook.')
		return request.json()

		"""
			Exemplo de retorno:
			[
				{
					"webhookId": "b3481122-c848-445c-9493-426918ff5099",
					"url": "https://chatwoot.domain.com.br",
					"name": "chatwoot-connector",
					"enabled": true,
					"createdAt": "2023-11-15T00:00:00.000Z",
					"updatedAt": null,
					"instanceInstanceId": "string",
					"WebhookEvents": {
					"webhookEventsId": "string",
					"qrcodeUpdate": false,
					"stateInstance": false,
					"messagesSet": false,
					"messagesUpsert": true,
					"messagesUpdate": false,
					"sendMessage": false,
					"contactsSet": false,
					"contactsUpsert": false,
					"contactsUpdate": false,
					"presenceUpdate": false,
					"chatsSet": false,
					"chatsUpdate": true,
					"chatsUpsert": false,
					"chatsDelete": true,
					"groupsUpsert": false,
					"groupUpdate": false,
					"groupParticipantsUpdate": false,
					"connectionUpdate": false,
					"newJwt": false,
					"createdAt": "2023-11-15T00:00:00.000Z",
					"updatedAt": null,
					"webhookWebhookId": "b3481122-c848-445c-9493-426918ff5099"
					}
				}
			]
  		"""





	def atualizar_webhook(self, id_webhook, url, habilitar=True):
		request = requests.put(
      		f'{self._url}/instance/{self._instanceId}/webhook/{id_webhook}',
			data=json.dumps({
				"url": url,
				"enabled": habilitar
       		}),
        	headers=self._headers
        )
		if not request.ok:
			print(request.text)
			raise Exception('Não foi possível atualizar webhook.')
		return request.json()


		"""
			Exemplo de retorno:
			{
				"webhookId": "b3481122-c848-445c-9493-426918ff5099",
				"name": "chatwoot-connector",
				"url": "string",
				"enabled": true,
				"createdAt": "2023-11-15T00:00:00.000Z",
				"updatedAt": null,
				"instanceInstanceId": "string"
			}
  		"""




	def atualizar_evento_webhook(self, id_webhook, **kwargs):
		data={
			"qrcodeUpdate": False,
			"stateInstance": False,
			"messagesSet": False,
			"messagesUpsert": False,
			"messagesUpdate": False,
			"sendMessage": False,
			"contactsSet": False,
			"contactsUpsert": False,
			"contactsUpdate": False,
			"presenceUpdate": False,
			"chatsSet": False,
			"chatsUpsert": False,
			"groupsUpsert": False,
			"groupUpdate": False,
			"groupParticipantsUpdate": False,
			"connectionUpdate": False,
			"newJwt": False
		}
		for chave, valor in kwargs.items():
			data[chave] = valor

		request = requests.patch(
      		f'{self._url}/instance/{self._instanceId}/webhook/{id_webhook}/events',
			data=json.dumps(data),
        	headers=self._headers
        )
		if not request.ok:
			print(request.text)
			raise Exception('Não foi possível editar eventos do webhook.')
		return request.json()


		"""
			Exemplo de retorno:
			{
				"webhookId": "b3481122-c848-445c-9493-426918ff5099",
				"url": "https://chatwoot.docmain.com",
				"name": "chatwoot-connector",
				"enabled": true,
				"createdAt": "2023-11-15T00:00:00.000Z",
				"updatedAt": null,
				"instanceInstanceId": "string",
				"WebhookEvents": {
					"webhookEventsId": "string",
					"qrcodeUpdate": false,
					"stateInstance": false,
					"messagesSet": false,
					"messagesUpsert": true,
					"messagesUpdate": false,
					"sendMessage": false,
					"contactsSet": false,
					"contactsUpsert": false,
					"contactsUpdate": false,
					"presenceUpdate": false,
					"chatsSet": false,
					"chatsUpdate": true,
					"chatsUpsert": false,
					"chatsDelete": true,
					"groupsUpsert": false,
					"groupUpdate": false,
					"groupParticipantsUpdate": false,
					"connectionUpdate": false,
					"newJwt": false,
					"createdAt": "2023-11-15T00:00:00.000Z",
					"updatedAt": null
				}
			}
  		"""



	def deletar_webhook(self, id_webhook):
		request = requests.delete(
      		f'{self._url}/instance/{self._instanceId}/webhook/{id_webhook}',
        	headers=self._headers
        )
		if not request.ok:
			print(request.text)
			raise Exception('Não foi possível deletar webhook.')
		return request.json()






	# Envio de mensagens


	def enviar_mensagem_texto(self, texto, recebedor):
		data={
			"recipient": recebedor,
			"options": {
				"delay": 0,
				"presence": "composing"
			},
			"textMessage": {
				"text": texto
			}
		}
		request = requests.post(
      		f'{self._url}/instance/{self._instanceId}/send/text',
			data=json.dumps(data),
        	headers=self._headers
        )
		if not request.ok:
			print(request.text)
			raise Exception('Não foi possível deletar webhook.')
		return request.json()

		"""
			Exemplo de retorno:
			{
				"messageId": "d052f3fd-0e9f-44ba-8a79-b5b9870bb64a",
				"keyId": "BAE58132EBC210FF",
				"keyFromMe": true,
				"keyRemoteJid": "string",
				"keyParticipant": "",
				"pushName": "",
				"contentType": "text",
				"isGroup": false,
				"content": {
					"text": "test",
					"contextInfo": {}
				},
				"source": "api",
				"messageTimestamp": 1700055820,
				"createdAt": "2023-11-15T13:43:41.261Z"
			}
  		"""





	def enviar_link(self, recebedor, link, titulo, descricao, texto, **kwargs):
		data={
			"recipient": recebedor,
			# "options": {
			# 	"delay": 0,
			# 	"presence": "composing | recording | available | unavailable",
			# 	"quoteMessageById": "string",
			# 	"groupMention": {
			# 		"hidden": True,
			# 		"everyone": True
			# 	}
			# },
			"linkPreview": {
				"link": link,
				"title": titulo,
				"description": descricao,
				"text": texto
			}
		}

		for chave, valor in kwargs.items():
			data[chave] = valor

		request = requests.post(
      		f'{self._url}/instance/{self._instanceId}/send/link-preview',
			data=json.dumps(data),
        	headers=self._headers
        )
		if not request.ok:
			print(request.text)
			raise Exception('Não foi possível deletar webhook.')
		return request.json()

		"""
			Exemplo de retorno:
			{
				"messageId": "d052f3fd-0e9f-44ba-8a79-b5b9870bb64a",
				"keyId": "BAE58132EBC210FF",
				"keyFromMe": true,
				"keyRemoteJid": "string",
				"keyParticipant": "",
				"pushName": "",
				"contentType": "text",
				"isGroup": false,
				"content": {
					"text": "test",
					"contextInfo": {}
				},
				"source": "api",
				"messageTimestamp": 1700055820,
				"createdAt": "2023-11-15T13:43:41.261Z"
			}
  		"""





	def enviar_midia(self, **kwargs):
		data={
				# "recipient": recebedor,
				# "options": {
				# 	"delay": 0,
				# 	"presence": "composing | recording | available | unavailable",
				# 	"quoteMessageById": "string",
				# 	"groupMention": {
				# 	"hidden": True,
				# 	"everyone": True
				# 	}
				# },
				# "mediaMessage": {
				# 	"mediaType": tipo,
				# 	"url": url,
				# 	# "caption": "string",
				# 	"fileName": nome_arquivo
				# }
			}

		for chave, valor in kwargs.items():
			data[chave] = valor

		request = requests.post(
      		f'{self._url}/instance/{self._instanceId}/send/media',
			data=json.dumps(data),
        	headers=self._headers
        )
		if not request.ok:
			print(request.text)
			raise Exception('Não foi possível deletar webhook.')
		return request.json()

		"""
			Exemplo de retorno:
			{
				"messageId": "d052f3fd-0e9f-44ba-8a79-b5b9870bb64a",
				"keyId": "BAE58132EBC210FF",
				"keyFromMe": true,
				"keyRemoteJid": "string",
				"keyParticipant": "",
				"pushName": "",
				"contentType": "text",
				"isGroup": false,
				"content": {
					"text": "test",
					"contextInfo": {}
				},
				"source": "api",
				"messageTimestamp": 1700055820,
				"createdAt": "2023-11-15T13:43:41.261Z"
			}
  		"""






	def enviar_midia_file(self, recebedor, delay, **kwargs):
		data={
				"recipient": recebedor,
			# 	# "caption": "string",
				"delay": delay,
			# 	"quoteMessageById": "string",
			# 	"presence": "composing | recording | available | unavailable",
			   "groupMentionHidden": True,
			   "groupMentionEveryone": True
			}

		for chave, valor in kwargs.items():
			data[chave] = valor

		request = requests.post(
      		f'{self._url}/instance/{self._instanceId}/send/media-file',
			data=json.dumps(data),
        	headers=self._headers
        )
		if not request.ok:
			print(request.text)
			raise Exception('Não foi possível deletar webhook.')
		return request.json()

		"""
			Exemplo de retorno:
			{
				"messageId": "d052f3fd-0e9f-44ba-8a79-b5b9870bb64a",
				"keyId": "BAE58132EBC210FF",
				"keyFromMe": true,
				"keyRemoteJid": "string",
				"keyParticipant": "",
				"pushName": "",
				"contentType": "text",
				"isGroup": false,
				"content": {
					"text": "test",
					"contextInfo": {}
				},
				"source": "api",
				"messageTimestamp": 1700055820,
				"createdAt": "2023-11-15T13:43:41.261Z"
			}
  		"""




	def enviar_audio(self, recebedor, delay, url):
		data={
			"recipient": recebedor,
			"options": {
				"delay": delay
			},
			"audioMessage": {
				"url": url
			}
		}

		request = requests.post(
      		f'{self._url}/instance/{self._instanceId}/send/audio',
			data=json.dumps(data),
        	headers=self._headers
        )
		if not request.ok:
			print(request.text)
			raise Exception('Não foi possível deletar webhook.')
		return request.json()

		"""
			Exemplo de retorno:
			{
				"messageId": "d052f3fd-0e9f-44ba-8a79-b5b9870bb64a",
				"keyId": "BAE58132EBC210FF",
				"keyFromMe": true,
				"keyRemoteJid": "string",
				"keyParticipant": "",
				"pushName": "",
				"contentType": "text",
				"isGroup": false,
				"content": {
					"text": "test",
					"contextInfo": {}
				},
				"source": "api",
				"messageTimestamp": 1700055820,
				"createdAt": "2023-11-15T13:43:41.261Z"
			}
  		"""



	def enviar_arquivo_audio(self, recebedor, delay, anexo):
		data={
			"recipient": recebedor,
			"delay": delay,
			"attachment": anexo
		}

		request = requests.post(
      		f'{self._url}/instance/{self._instanceId}/send/audio-file',
			data=json.dumps(data),
        	headers=self._headers
        )
		if not request.ok:
			print(request.text)
			raise Exception('Não foi possível deletar webhook.')
		return request.json()

		"""
			Exemplo de retorno:
			{
				"messageId": "d052f3fd-0e9f-44ba-8a79-b5b9870bb64a",
				"keyId": "BAE58132EBC210FF",
				"keyFromMe": true,
				"keyRemoteJid": "string",
				"keyParticipant": "",
				"pushName": "",
				"contentType": "text",
				"isGroup": false,
				"content": {
					"text": "test",
					"contextInfo": {}
				},
				"source": "api",
				"messageTimestamp": 1700055820,
				"createdAt": "2023-11-15T13:43:41.261Z"
			}
  		"""



	def enviar_PTV(self, recebedor, delay, url):
		data={
			"recipient": recebedor,
			"options": {
				"delay": delay
			},
			"ptvMessage": {
				"url": url
			}
		}

		request = requests.post(
      		f'{self._url}/instance/{self._instanceId}/send/ptv',
			data=json.dumps(data),
        	headers=self._headers
        )
		if not request.ok:
			print(request.text)
			raise Exception('Não foi possível envia ptv.')
		return request.json()




	def enviar_arquivo_PTV(self, recebedor, delay, anexo):
		data={
			"recipient": recebedor,
			"delay": delay,
			"attachment": anexo
		}

		request = requests.post(
      		f'{self._url}/instance/{self._instanceId}/send/ptv-file',
			data=json.dumps(data),
        	headers=self._headers
        )
		if not request.ok:
			print(request.text)
			raise Exception('Não foi possível envia arquivo ptv.')
		return request.json()






	def enviar_localizacao(self, **kwargs):
		data={
				# "recipient": "string",
				# "options": {
				# 	"delay": 0,
				# 	"presence": "composing | recording | available | unavailable",
				# 	"quoteMessageById": "string",
				# 	"groupMention": {
				# 		"hidden": True,
				# 		"everyone": True
				# 	}
				# },
				# "locationMessage": {
				# 	"latitude": 0,
				# 	"longitude": 0,
				# 	"name": "string",
				# 	"address": "string"
				# }
			}


		for chave, valor in kwargs:
			data[chave] = valor

		request = requests.post(
      		f'{self._url}/instance/{self._instanceId}/send/location',
			data=json.dumps(data),
        	headers=self._headers
        )
		if not request.ok:
			print(request.text)
			raise Exception('Não foi possível envia ptv.')
		return request.json()


	def enviar_reacao_mensagem(self, nome_reacao, id_mensagem):
		data={
			"reactionMessage": {
				"reaction": nome_reacao
			}
		}

		request = requests.patch(
      		f'{self._url}/instance/{self._instanceId}/send/reaction?messageId={id_mensagem}',
			data=json.dumps(data),
        	headers=self._headers
        )
		if not request.ok:
			print(request.text)
			raise Exception('Não foi possível envia ptv.')
		return request.json()

	def editar_mensagem(self, texto, id_mensagem):
		data={
			"editMessage": {
				"text": texto
			}
		}

		request = requests.patch(
      		f'{self._url}/instance/{self._instanceId}/send/edit?messageId={id_mensagem}',
			data=json.dumps(data),
        	headers=self._headers
        )
		if not request.ok:
			print(request.text)
			raise Exception('Não foi possível envia ptv.')
		return request.json()

	def validar_numero(self, numeros=list()):
		data={
			"numbers": numeros
		}

		request = requests.post(
      		f'{self._url}/instance/{self._instanceId}/chat/validate-numbers',
			data=json.dumps(data),
        	headers=self._headers
        )
		if not request.ok:
			print(request.text)
			raise Exception('Não foi possível envia ptv.')
		return request.json()