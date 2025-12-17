from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator


 
class Endereco(models.Model):
	id_endereco = models.AutoField(primary_key=True)
	cep = models.CharField(max_length=10)
	logradouro = models.CharField(max_length=100)
	bairro = models.CharField(max_length=100)
	numero = models.CharField(max_length=20, null=True)
	complemento = models.CharField(max_length=50, null=True, blank=True)
	cidade = models.CharField(max_length=40)
	estado = models.CharField(max_length=40)
	pais = models.CharField(max_length=15, default="Brasil")
 
 
class Pessoa(models.Model):
    id_pessoa = models.AutoField(primary_key=True)
    ativo = models.BooleanField(default=True)
    nome = models.CharField(max_length=50)
    sobrenome = models.CharField(max_length=50, null=True)
    cpf = models.CharField(max_length=14, unique=True) #COLOCAR COMO UNIQUE
    email = models.CharField(max_length=60, unique=True)
    telefone = models.CharField(max_length=15, null=True)#COLOCAR COMO UNIQUE
    data_nascimento = models.DateField(null=True)
    sexo = models.CharField(max_length=1, choices=[('M', 'Masculino'), ('F', 'Feminino'), ('O', 'Outro')], null=True)
    data_cadastro = models.DateField(auto_now_add=True)
    descricao = models.CharField(max_length=300, null=True)
    url_imagem_perfil = models.CharField(max_length=300, null=True)
    endereco = models.ForeignKey(Endereco, models.SET_NULL, null=True, related_name='pessoa')
    tipo_usuario = models.IntegerField(choices=[
        (1, 'Paciente'),
        (2, 'Fisioterapeuta')
    ], null=True)

class Dispositivo (models.Model):
    pessoa = models.ForeignKey(Pessoa, on_delete=models.CASCADE, related_name="dispositivos")
    token = models.CharField(max_length=300, null=True)
    descricao = models.CharField(max_length=100, null=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pessoa.email} - {self.descricao or 'Dispositivo'}"

class Topico (models.Model):
    pessoa = models.ForeignKey(Pessoa, on_delete=models.CASCADE, related_name="topicos")
    nome = models.CharField(max_length=100)
    data_inscricao = models.DateTimeField(auto_now=True)


class Administrador(models.Model):
    id_administrador = models.AutoField(primary_key=True)
    pessoa = models.ForeignKey(Pessoa, models.SET_NULL, null=True)
    # autenticacao = models.BooleanField(default=False)
    
    
class Paciente(models.Model):
    id_paciente = models.AutoField(primary_key=True)
    pessoa = models.OneToOneField(Pessoa, on_delete=models.CASCADE, null=True)
    ativo = models.BooleanField(default=False)
    altura = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    peso = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    uso_remedio_continuo = models.TextField(max_length=300, null=True, blank=True)
    observacoes_medicas = models.TextField(max_length=300, null=True, blank=True)  #podendo ser mudado para laudos. 
    nota_paciente = models.FloatField(default=5) # Media de todas as notas que o paciente recebeu
    resumo_caso = models.CharField(max_length=300, null=True, blank=True)    
    
    
class Fisioterapeuta(models.Model):
    id_fisio = models.AutoField(primary_key=True)
    pessoa = models.OneToOneField(Pessoa, on_delete=models.CASCADE, null=True)
    ativo = models.BooleanField(default=False) # ou coloca para false 
    valor_atendimento = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    # duracao_sessao = models.PositiveIntegerField(default=60) # em minutos
    especialidades = models.ManyToManyField(
        'Especialidade',
        through='Fisio_especialidade',
        related_name='fisioterapeutas'
    )
    crefito = models.CharField(max_length=20, unique=True)
    qtd_atendimentos = models.IntegerField(default=0)
    nota_fisioterapeuta = models.FloatField(default=5) # Media de todas as notas que o fisioterapeuta recebeu 
    
    
class Especialidade(models.Model):
    id_especialidade = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=50, unique=True)
    ativo = models.BooleanField(default=True)
    
    
class Fisio_especialidade(models.Model):
    fisioterapeuta = models.ForeignKey(Fisioterapeuta, on_delete=models.CASCADE)
    especialidade = models.ForeignKey(Especialidade, on_delete=models.CASCADE)
    ativo = models.BooleanField(default=True)

# Esse modelo vai ser resposavel pelo cadastro da agenda do fisioterapeuta.
# opções : retornar a proposta para tdos os fisioteraupeuta que tem disponibilidade naquele horario 
# class Disponibilidade(models.Model):
#     fisioterapeuta = models.ForeignKey(Fisioterapeuta, on_delete=models.CASCADE, related_name="disponibilidades")
#     dia_semana = models.IntegerField(choices=[
#         (0, "Segunda"),
#         (1, "Terça"),
#         (2, "Quarta"),
#         (3, "Quinta"),
#         (4, "Sexta"),
#         (5, "Sábado"),
#         (6, "Domingo"),
#     ])
#     hora_inicio = models.TimeField()
#     hora_fim = models.TimeField()

#     def __str__(self):
#         return f"{self.get_dia_semana_display()} - {self.hora_inicio} às {self.hora_fim}"
    

class Atendimento(models.Model):
    id_atendimento = models.AutoField(primary_key=True)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    fisioterapeuta = models.ForeignKey(Fisioterapeuta, on_delete=models.CASCADE, null=True)
    # ativo = models.BooleanField(default=True)
    especialidade = models.ForeignKey(Especialidade, on_delete=models.CASCADE, null=True)
    data_hora = models.DateTimeField()
    # data_hora_fim = models.DateTimeField(null=True, blank=True) # hora que termina a sessão do fisioterapeuta 
    endereco = models.ForeignKey(Endereco, on_delete=models.CASCADE, null=True)
    status = models.IntegerField(choices=[
        (1, 'Nao realizado'),
        (2, 'Realizado'),
        (3, 'Cancelado'),
        (4, 'Aguardando Aprovacao'),
        (5, 'Agendado'),
        (6, 'Reagendado'),
        (7, 'Aprovado'),
        (8, 'Negado'),
    ], default=4)
    valor_maximo_proposta = models.FloatField(null=True)
    isProposta = models.BooleanField(default=False)
    local_atendimento = models.CharField(max_length=100, null=True)
    motivo_cancelamento = models.CharField(max_length=200, null=True)
    fez_checkin = models.BooleanField(default=False)
    fez_checkout = models.BooleanField(default=False)
    is_retorno = models.BooleanField(default=False) # se o atendimento é de retorno ou não
    
# Esse modelo é a resposta do fisioterapeuta para determinado atendimento modelo uber em caso de recusa recusa apenas para ele.
class RespostaFisioterapeuta(models.Model):
    id_resposta = models.AutoField(primary_key=True)
    atendimento = models.ForeignKey(Atendimento, on_delete=models.CASCADE, related_name="respostas")
    fisioterapeuta = models.ForeignKey(Fisioterapeuta, on_delete=models.CASCADE)
    status = models.IntegerField(choices=[
        (1, 'Pendente'),
        (2, 'Aceito'),
        (3, 'Recusado'),
    ], default=1)
    data_resposta = models.DateTimeField(auto_now_add=True)
    motivo_cancelamento = models.CharField(max_length=200, null=True, blank=True)

class Avaliacao(models.Model):
    id_avaliacao = models.AutoField(primary_key=True)
    atendimento = models.ForeignKey(Atendimento, on_delete=models.CASCADE)
    autor = models.ForeignKey(Pessoa, on_delete=models.CASCADE, related_name="avaliacoes_enviadas")# Pessoa que fez a avaliação 
    destinatario = models.ForeignKey(Pessoa, on_delete=models.CASCADE, related_name="avaliacoes_recebidas") # pessoa que recebeu a avaliação 
    nota_gent = models.IntegerField(default=5) # 1 a 5
    nota_educ = models.IntegerField(default=5) # 1 a 5
    nota_pont = models.IntegerField(default=5) # 1 a 5
    comentario = models.TextField(max_length=200, blank=True)
    data = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)


class CodigoVerificacao(models.Model):
    codigo = models.CharField(max_length=6, unique=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    expira_em = models.DateTimeField()
    usado = models.BooleanField(default=False)
    usuario_utilizador = models.ForeignKey(Pessoa, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"Código: {self.codigo}, Usado: {self.usado}"

class CheckInOut(models.Model):
    CHECK_TYPE_CHOICES = (
        ('in', 'check_in'),
        ('out', 'check_out'),
    )

    id = models.AutoField(primary_key=True)
    atendimento = models.ForeignKey('Atendimento', on_delete=models.CASCADE, related_name='checkins')
    tipo = models.CharField(max_length=3, choices=CHECK_TYPE_CHOICES)

    pergunta_dor = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    pergunta_mudanca = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    pergunta_bem_estar = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    pergunta_confianca = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "CheckIn/CheckOut"
        verbose_name_plural = "CheckIns/CheckOuts"
        unique_together = ('atendimento', 'tipo')
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.pessoa_id} - {self.atendimento_id} - {self.tipo}"
