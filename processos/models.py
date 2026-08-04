from django.db import models
from django.contrib.auth.models import User


class TipoProcesso(models.Model):
    """Tipos de processos"""
    nome = models.CharField(max_length=255, unique=True)
    descricao = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Tipo de Processo'
        verbose_name_plural = 'Tipos de Processo'

    def __str__(self):
        return self.nome


class Processo(models.Model):
    """Modelo para Processos"""
    STATUS_CHOICES = [
        ('aberto', 'Aberto'),
        ('em_andamento', 'Em Andamento'),
        ('finalizado', 'Finalizado'),
        ('arquivado', 'Arquivado'),
    ]

    numero = models.CharField(max_length=100, unique=True)
    tipo = models.ForeignKey(TipoProcesso, on_delete=models.SET_NULL, null=True, blank=True)
    titulo = models.CharField(max_length=255)
    descricao = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberto')
    responsavel = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processos')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    data_conclusao = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-data_criacao']
        verbose_name = 'Processo'
        verbose_name_plural = 'Processos'

    def __str__(self):
        return f"{self.numero} - {self.titulo}"


class DocumentoProcesso(models.Model):
    """Modelo para Documentos associados a Processos"""
    processo = models.ForeignKey(Processo, on_delete=models.CASCADE, related_name='documentos')
    titulo = models.CharField(max_length=255)
    arquivo = models.FileField(upload_to='processos/%Y/%m/%d/')
    data_upload = models.DateTimeField(auto_now_add=True)
    tamanho = models.IntegerField()  # Tamanho em bytes

    class Meta:
        ordering = ['-data_upload']
        verbose_name = 'Documento de Processo'
        verbose_name_plural = 'Documentos de Processo'

    def __str__(self):
        return f"{self.titulo} - {self.processo}"


class ComentarioProcesso(models.Model):
    """Modelo para Comentários em Processos"""
    processo = models.ForeignKey(Processo, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    texto = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['data_criacao']
        verbose_name = 'Comentário de Processo'
        verbose_name_plural = 'Comentários de Processo'

    def __str__(self):
        return f"Comentário em {self.processo} por {self.autor}"
