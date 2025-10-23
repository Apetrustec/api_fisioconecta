


from datetime import date, datetime, timezone
import random
import string

from fisio_conecta.models import CodigoVerificacao


def formatarTelefone (telefone, ddi=True):
	"""
		Formata número de telefone

		Formato DDI DD + 9 + número

		Exemplo: +5584988762526
	"""
	if not telefone: raise Exception ('Você não enviou o telefone')

	if str(type(telefone)) != "<class 'str'>":
		raise Exception ('O tipo do dado enviado precisa ser string')

	if len(telefone) == 8:
		return f'{"55" if ddi else ""}849{telefone}'

	elif len(telefone) == 9:
		return f'{"55" if ddi else ""}84{telefone}'

	elif len(telefone) == 11:
		return f'{"55" if ddi else ""}{telefone}'

	elif len(telefone) == 13:
		return telefone[2:] if not ddi else f'{telefone}'

	elif len(telefone) == 14: return telefone if ddi else telefone[3:]

	else:
		raise Exception ('Formato incompatível')
	
def gerar_codigo_verificacao(validade_minutos=7, tamanho=6, usuario_utilizador=None):
    """
    Gera um código de verificação com números e letras, salva no banco e retorna o objeto.

    Args:
        validade_minutos (int): Tempo de validade do código em minutos. Padrão é 7 minutos.
        tamanho (int): Quantidade de caracteres do código. Padrão é 6.
        usuario_utilizador (Pessoa): Usuário relacionado ao código.

        CodigoVerificacao: O objeto criado com os detalhes do código.
        esse codigo é para verificação e tem expiração de 7 minutos.
    """
    caracteres = string.ascii_uppercase + string.digits
    codigo = ''.join(random.choices(caracteres, k=tamanho))

    agora = timezone.now()
    expira_em = agora + datetime.timedelta(minutes=validade_minutos)

    codigo_verificacao = CodigoVerificacao.objects.create(
        codigo=codigo,
        expira_em=expira_em,
        usuario_utilizador=usuario_utilizador
    )

    return codigo_verificacao

def formatar_data_hora(data):
    if isinstance(data, datetime):
        return data.strftime("%d-%m-%Y às %H:%M")
    elif isinstance(data, date):  # se usar date também precisa importar date
        return data.strftime("%d-%m-%Y")
    else:
        try:
            dt = datetime.fromisoformat(data)
            return dt.strftime("%d-%m-%Y às %H:%M")
        except:
            return str(data)
        
def gerar_codigo_seguranca(tamanho=6):
    """
    Gera um código de segurança  com números e letras, 
    """
    caracteres = string.ascii_uppercase + string.digits
    codigo = ''.join(random.choices(caracteres, k=tamanho))

    return codigo