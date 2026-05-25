from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import JSONField

class Rubrica(models.Model):
    """Modelo para Rubricas de pagamento"""
    nome = models.CharField(max_length=255, unique=True)
    codigo = models.CharField(max_length=50, unique=True)
    descricao = models.TextField(blank=True)
    valor_padrao = models.DecimalField(max_digits=12, decimal_places=2)
    ativa = models.BooleanField(default=True)
    
    # Detalhes de Cálculo
    formula_calculo = models.TextField(blank=True, help_text="Fórmula ou expressão para cálculo da rubrica")
    tipo_calculo = models.CharField(
        max_length=255,
        blank=True,
        default='fixo',
        help_text="Descreva o tipo de cálculo ou fórmula usada"
    )
    base_calculo = models.CharField(max_length=255, blank=True, help_text="Base de cálculo (ex: salário base, horas trabalhadas)")
    base_legal = models.CharField(max_length=255, blank=True, help_text="Texto explicando a base legal desta rubrica")
    incidencia = models.CharField(max_length=255, blank=True, help_text="Incidência sobre encargos e benefícios")
    caracteristicas = models.TextField(blank=True, help_text="Características específicas da rubrica")

    # Regras de Verificação
    regras_verificacao = JSONField(default=dict, blank=True, help_text="Regras para validação desta rubrica")
    tolerancia = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Tolerância percentual na verificação")
    tipo_validacao = models.CharField(
        max_length=255,
        blank=True,
        default='exato',
        help_text="Descreva o tipo de validação desta rubrica"
    )
    
    # Padrões de Conformidade
    valor_minimo_padrao = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    valor_maximo_padrao = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    carga_horaria_padrao = models.IntegerField(null=True, blank=True, help_text="Carga horária padrão (horas semanais)")
    
    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['codigo']
        verbose_name = 'Rubrica'
        verbose_name_plural = 'Rubricas'

    def __str__(self):
        return f"{self.codigo} - {self.nome}"


class Empresa(models.Model):
    """Modelo para Empresas"""
    nome = models.CharField(max_length=255)
    codigo = models.CharField(max_length=50, unique=True)
    cnpj = models.CharField(max_length=18, unique=True)
    razao_social = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    telefone = models.CharField(max_length=255, blank=True)
    ativa = models.BooleanField(default=True)
    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'

    def __str__(self):
        return self.nome


class PadraoConformidade(models.Model):
    """Modelo para Padrões de Conformidade por rubrica, empresa e ano"""
    rubrica = models.ForeignKey(Rubrica, on_delete=models.CASCADE, related_name='padroes')
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='padroes')
    ano = models.IntegerField(validators=[MinValueValidator(2000), MaxValueValidator(2100)])
    valor_minimo = models.DecimalField(max_digits=12, decimal_places=2)
    valor_maximo = models.DecimalField(max_digits=12, decimal_places=2)
    carga_horaria = models.IntegerField()  # horas semanais
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('rubrica', 'empresa', 'ano')
        ordering = ['-ano', 'empresa', 'rubrica']
        verbose_name = 'Padrão de Conformidade'
        verbose_name_plural = 'Padrões de Conformidade'

    def __str__(self):
        return f"{self.rubrica} - {self.empresa} ({self.ano})"


class VerificacaoConformidade(models.Model):
    """Modelo para Verificações de Conformidade"""
    STATUS_CHOICES = [
        ('correto', 'Correto'),
        ('verificar', 'Verificar'),
        ('incorreto', 'Incorreto'),
    ]

    padrao = models.ForeignKey(PadraoConformidade, on_delete=models.CASCADE, related_name='verificacoes', null=True, blank=True)
    rubrica = models.CharField(max_length=255, blank=True)
    ano_referencia = models.IntegerField(null=True, blank=True)
    carga_horaria = models.IntegerField(null=True, blank=True)
    valor_pago = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    arquivo_vencimento = models.FileField(upload_to='verificacoes/vencimento/', blank=True, null=True)
    arquivo_extrator = models.FileField(upload_to='verificacoes/extrator/', blank=True, null=True)
    data_verificacao = models.DateTimeField(auto_now_add=True)
    verificado_por = models.CharField(max_length=255, blank=True)
    
    # Campos para armazenar resumo dos resultados
    total_registros = models.IntegerField(default=0)
    corretos = models.IntegerField(default=0)
    verificar = models.IntegerField(default=0)
    incorretos = models.IntegerField(default=0)
    resultados_json = JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-data_verificacao']
        verbose_name = 'Verificação de Conformidade'
        verbose_name_plural = 'Verificações de Conformidade'

    def __str__(self):
        rubrica_str = self.rubrica or (self.padrao.rubrica.nome if self.padrao else 'Sem rubrica')
        return f"{rubrica_str} - {self.status}"

    def verificar_conformidade(self):
        """Verifica se o valor pago está em conformidade com o padrão"""
        if self.padrao:
            if self.valor_pago < self.padrao.valor_minimo or self.valor_pago > self.padrao.valor_maximo:
                self.status = 'incorreto'
            else:
                self.status = 'correto'
        return self.status
