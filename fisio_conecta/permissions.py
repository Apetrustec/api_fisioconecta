from rest_framework.permissions import BasePermission
from rest_framework.exceptions import APIException
from rest_framework import status
from django.contrib.auth.models import AnonymousUser
from firebase_admin import auth, get_app
from packaging import version
from django.db.models import Q
from fisio_conecta import models


class IsLogged(BasePermission):
	"""this class checks if the client is logged in.

	Arguments:
			BasePermission {rest_framework.permissions} -- is the rest frame work method that helps in checking
	"""

	def has_permission(self, request, view):

		try:

			id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()


			if not id_token:
				return False

			app = get_app(name='fisio_conecta')
			decoded_token = auth.verify_id_token(id_token, app=app)
			request.user_data = decoded_token

			request.app = app
			request.app_name = 'fisio_conecta'

			return True

		except:

			return False



class ValidVersionForbidden(APIException):
	"""This class checks and warns that the version of the client App is out of
	date.

	Arguments:
			APIException {rest_framework.permissions} -- is the rest frame work method that helps in checking
	"""

	def __init__(self, versao, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.versao = versao

		self.status_code = status.HTTP_403_FORBIDDEN

		self.detail = 'Parece que seu App está desatualizado, por favor vá até sua loja de apps e atualize-o para versão {}.'.format(self.versao)

class IsPaciente (BasePermission):
	"""This class checks is a client.

	Arguments:
			BasePermission {rest_framework.permissions} -- is the rest frame work method that helps in checking
	"""
	def has_permission(self, request, view):

			user = request.user or request.user_data
			if type(user) is AnonymousUser:
				return False

			request.paciente = models.Paciente.objects.filter(pessoa__email = user.get('email')).last()

			if request.paciente:
				return True

			return False

class IsFisioterapeuta (BasePermission):
	"""This class checks is a client.

	Arguments:
			BasePermission {rest_framework.permissions} -- is the rest frame work method that helps in checking
	"""
	def has_permission(self, request, view):

		user = request.user or request.user_data
		if type(user) is AnonymousUser:
			return False
		
		request.fisioterapeuta = models.Fisioterapeuta.objects.filter(pessoa__email = user.get('email')).last()

		if request.fisioterapeuta:
			return True
		
		return False

class IsAdmin (BasePermission):
	"""This class checks if it is admin with past email.

	Arguments:
			BasePermission {rest_framework.permissions} -- is the rest frame work method that helps in checking
	"""
	def has_permission(self, request, view):

		user = request.user or request.user_data
		if type(user) is AnonymousUser:
				return False

		admin = models.Administrador.objects.filter(
			pessoa__email= user.get('email')
    	)
		return admin.exists()