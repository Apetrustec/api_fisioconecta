# settings.py

# Imports necessários
import os
import json
import firebase_admin
from firebase_admin import credentials
from dotenv import load_dotenv
import boto3 # Adicionado para Secrets Manager
from botocore.exceptions import ClientError # Adicionado para Secrets Manager

# --- Configuração do BASE_DIR ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- Carregar .env (APENAS PARA DESENVOLVIMENTO LOCAL) ---
# O Elastic Beanstalk usará as "Propriedades do Ambiente" para DB e outros,
# e o Secrets Manager para Firebase. A lógica de fallback cobrirá o local.
load_dotenv(os.path.join(BASE_DIR, '.env')) # Garante que carregue o .env da raiz

# --- Configurações Principais ---

# Modo DEBUG (lendo a string 'True' ou 'False' do ambiente)
# No EB, defina GLOBAL_CONFIG_DEBUG = False (OBRIGATÓRIO para produção)
DEBUG = os.getenv('GLOBAL_CONFIG_DEBUG') == 'True'

# Chave secreta lida do ambiente
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY and not DEBUG:
     print("ALERTA DE SEGURANÇA: SECRET_KEY não definida em produção!")
     # Considerar levantar um ImproperlyConfigured aqui em produção estrita


# ALLOWED_HOSTS (Forma segura)
# No EB, defina DJANGO_ALLOWED_HOSTS=api.fisioconecta.com.br,api-fisioconecta-env.us-east-2.elasticbeanstalk.com (ou a URL correta do EB)
allowed_hosts_env = os.getenv('DJANGO_ALLOWED_HOSTS')
ALLOWED_HOSTS = allowed_hosts_env.split(',') if allowed_hosts_env else []
if not ALLOWED_HOSTS and not DEBUG:
     print("ALERTA DE SEGURANÇA: DJANGO_ALLOWED_HOSTS não definida em produção!")
     # Considerar levantar um ImproperlyConfigured

if DEBUG:
    ALLOWED_HOSTS.extend(['localhost', '127.0.0.1'])


# --- Aplicações e Middlewares ---

INSTALLED_APPS = [
    'corsheaders',
    'rest_framework',
    'secured_fields',       # Você tinha, mantive
    'fisio_conecta',        # Seu app principal
    'django_extensions',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # REMOVIDOS: 'pipeline', 'django.contrib.staticfiles', 'whitenoise'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',      # Deve vir antes da maioria
    'django.middleware.gzip.GZipMiddleware',      # Você tinha, mantive
    # 'django_brotli.middleware.BrotliMiddleware',# Mantive comentado, descomente se usar e tiver no requirements.txt
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # REMOVIDO: 'whitenoise.middleware.WhiteNoiseMiddleware'
]

# --- Configuração do WSGI ---
# Esta configuração usa a notação de ponto Python
WSGI_APPLICATION = 'api_fisio_conecta.wsgi.application' # Verifique se 'api_fisio_conecta' é o nome da sua pasta de projeto

# --- Configurações de Segurança e CORS ---
# No EB, defina CORS_ALLOWED_ORIGINS=https://admin.fisioconecta.com.br,http://localhost:8080 (ajuste portas locais)
cors_origins_env = os.getenv('CORS_ALLOWED_ORIGINS')
if cors_origins_env:
    CORS_ALLOWED_ORIGINS = cors_origins_env.split(',')
    CORS_ALLOW_ALL_ORIGINS = False # Garante que apenas a lista seja usada
elif DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True # Permite tudo apenas se DEBUG=True e nenhuma lista foi definida
else:
    CORS_ALLOW_ALL_ORIGINS = False # Bloqueia tudo se não estiver em DEBUG e nenhuma origem for definida
    print("ALERTA DE SEGURANÇA: CORS_ALLOWED_ORIGINS não definida em produção!")

CORS_ALLOW_METHODS = ('DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT',)

# Configurações de segurança para rodar atrás do Load Balancer
if not DEBUG:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    # ESSENCIAL: Diz ao Django para confiar no header 'https' vindo do Load Balancer
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
else:
     # Em DEBUG, não forçamos HTTPS via Django
     CSRF_COOKIE_SECURE = False
     SESSION_COOKIE_SECURE = False
     SECURE_PROXY_SSL_HEADER = None


# --- Outras Configurações Django ---
ROOT_URLCONF = 'api_fisio_conecta.urls' # Verifique se 'api_fisio_conecta' é o nome da sua pasta de projeto
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [], 'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
REST_FRAMEWORK = {
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 5
}
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Recife'
USE_I18N = True
USE_L10N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# --- Conexão com Banco de Dados (RDS) ---
# Usando as variáveis de ambiente configuradas no EB (`DB_NAME`, `DB_USER`, etc.)
# Os valores padrão são para desenvolvimento local
DB_NAME = os.getenv('DB_NAME', 'fisiodb')        # Nome do banco no RDS (ajuste default se local for diferente)
DB_USER = os.getenv('DB_USER', 'fisio_app_user') # Usuário criado para a app (ajuste default se local for diferente)
DB_PASSWORD = os.getenv('DB_PASSWORD')           # Senha vem do ambiente (não coloque default aqui)
DB_HOST = os.getenv('DB_HOST', 'localhost')      # Endpoint do RDS (default localhost para dev)
DB_PORT = os.getenv('DB_PORT', '5432')           # Porta padrão do Postgres

if not DB_PASSWORD and not DEBUG:
     print("ALERTA DE SEGURANÇA: DB_PASSWORD não definida em produção!")
     # Considerar levantar um ImproperlyConfigured

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
    }
}


# --- Inicialização do Firebase (Usando AWS Secrets Manager com Fallback Local) ---

# --- !! CONFIRME ESTE NOME !! ---
SECRET_NAME = "FIREBASE_CREDS_JSON" # O nome EXATO que você deu ao segredo no Secrets Manager
# --- !! CONFIRME A REGIÃO !! ---
REGION_NAME = "us-east-2" # A região onde o segredo e o EB estão

cred = None
firebase_creds_dict = None

print(f"INFO: Tentando buscar segredo '{SECRET_NAME}' do AWS Secrets Manager na região '{REGION_NAME}'...")
try:
    # Tenta criar cliente boto3. Falhará localmente se credenciais AWS não estiverem configuradas.
    # No EB, ele usará a Role da instância automaticamente.
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=REGION_NAME)
    get_secret_value_response = client.get_secret_value(SecretId=SECRET_NAME)

    if 'SecretString' in get_secret_value_response:
        secret = get_secret_value_response['SecretString']
        firebase_creds_dict = json.loads(secret)
        # Garante que as quebras de linha na chave privada estão corretas
        if 'private_key' in firebase_creds_dict:
            firebase_creds_dict['private_key'] = firebase_creds_dict['private_key'].replace('\\n', '\n')
        cred = credentials.Certificate(firebase_creds_dict)
        print("INFO: Credenciais do Firebase carregadas do Secrets Manager com sucesso.")
    else:
        print(f"AVISO: Segredo '{SECRET_NAME}' encontrado, mas não contém SecretString.")

except ClientError as e:
    error_code = e.response.get("Error", {}).get("Code")
    if error_code == "ResourceNotFoundException":
         print(f"AVISO: Segredo '{SECRET_NAME}' não encontrado no Secrets Manager.")
    elif error_code == "AccessDeniedException":
         print(f"ERRO CRÍTICO: Acesso negado ao buscar o segredo '{SECRET_NAME}'. Verifique as permissões IAM da role EC2.")
         # Considerar 'raise e' aqui se o Firebase for essencial
    else:
         print(f"ERRO BOTO3 inesperado ao buscar o segredo '{SECRET_NAME}': {e}")
         # Considerar 'raise e'
except ImportError:
    print("AVISO: Biblioteca 'boto3' não encontrada. Não foi possível buscar segredo do Secrets Manager.")
except Exception as e: # Pega outros erros (JSONDecode, ValueError, boto3 não configurado localmente, etc.)
    print(f"ERRO durante busca/processamento do segredo '{SECRET_NAME}': {e}")
    # Considerar 'raise e'

# Fallback para o modo local SOMENTE se 'cred' não foi definido com sucesso acima
if not cred:
    print("INFO: Falha ao buscar/processar segredo do Secrets Manager. Tentando carregar credenciais locais do Firebase...")
    # --- !! CONFIRME O NOME/CAMINHO DO ARQUIVO LOCAL !! ---
    local_creds_path = os.path.join(BASE_DIR, 'fisio-conecta-producao.json')
    if os.path.exists(local_creds_path):
        try:
            cred = credentials.Certificate(local_creds_path)
            print(f"INFO: Credenciais locais do Firebase carregadas com sucesso de '{local_creds_path}'.")
        except Exception as local_e:
            print(f"ERRO: Falha ao carregar credenciais locais de '{local_creds_path}': {local_e}")
    else:
        print(f"AVISO CRÍTICO: Credenciais do Firebase não encontradas (nem Secrets Manager, nem local em '{local_creds_path}'). Firebase NÃO será inicializado.")

# Inicializa o app Firebase apenas se as credenciais foram carregadas com sucesso
# E apenas se ainda não foi inicializado (importante para Gunicorn evitar re-inicialização)
if cred and not firebase_admin._apps:
    try:
        firebase_admin.initialize_app(
            cred,
            name='fisio_conecta',
            options={'auth_token_validity_leeway': 300}
        )
        print("INFO: Firebase Admin SDK inicializado com sucesso.")
    except Exception as init_e:
        print(f"ERRO CRÍTICO: Falha ao inicializar Firebase Admin SDK mesmo após carregar credenciais: {init_e}")
        # Considerar 'raise init_e' se o Firebase for absolutamente essencial para a app iniciar

elif not cred:
    print("ERRO FINAL: Não foi possível obter/carregar credenciais válidas do Firebase. A funcionalidade dependente do Firebase pode falhar.")

# --- Fim da Seção de Inicialização do Firebase ---
