from rest_framework import authentication
from firebase_admin import auth, credentials, initialize_app, get_app
# from apetrus.apetrus.models import Firebase


class FirebaseAuthentication (authentication.BaseAuthentication):

	def authenticate(self, request):
		try:

			http_auth = request.META.get('HTTP_AUTHORIZATION', None)
			if http_auth is None:
				return None

			user = None
			app = get_app(name='fisio_conecta')

			if(http_auth is not None and len(http_auth) > 10):
				id_token = http_auth.split(' ').pop()
				user = auth.verify_id_token(id_token, app=app)
				request.user_data = user

			request.app = app
			request.app_name = 'fisio_conecta'
			return (user, None)

		except Exception as e:
			error = "Error FirebaseAuthentication"
			print(error + ": " + str(e))
			return None
