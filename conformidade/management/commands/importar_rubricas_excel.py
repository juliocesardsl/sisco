from pathlib import Path

import openpyxl
from django.core.management.base import BaseCommand, CommandError

from conformidade.models import Rubrica


class Command(BaseCommand):
    help = 'Importa rubricas de uma planilha Excel para o banco de dados.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            default=str(Path('Arquivos') / '1. Banco de Rubricas_legislação_condição de cálculo_072021 até 052026.xlsx'),
            help='Caminho para a planilha de rubricas.',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Importa todas as linhas da planilha, sem filtrar pelo vencimento.',
        )
        parser.add_argument(
            '--filter-vencimento',
            default='rubrica ligada ao vencimento?',
            help='Valor da coluna "filtro vencimento" que deve ser importado por padrão.',
        )

    def handle(self, *args, **options):
        file_path = Path(options['file'])
        if not file_path.exists():
            raise CommandError(f'Arquivo não encontrado: {file_path}')

        workbook = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
        sheet = workbook.active
        rows = list(sheet.iter_rows(min_row=2, values_only=True))

        filter_value = (options['filter_vencimento'] or '').strip().casefold()
        use_filter = not options['all'] and bool(filter_value)

        created = 0
        updated = 0
        skipped = 0

        for row in rows:
            codigo = self._clean_text(row[3])
            if not codigo:
                skipped += 1
                continue

            filtro_vencimento = self._clean_text(row[1])
            if use_filter and (filtro_vencimento or '').casefold() != filter_value:
                skipped += 1
                continue

            defaults = {
                'nome': self._clean_text(row[4]) or codigo,
                'filtro_vencimento': filtro_vencimento,
                'filtro_valor_fixo': self._clean_text(row[2]),
                'dc_rubrica': self._clean_text(row[4]),
                'tipo_orgao_por_rubrica': self._clean_text(row[5]),
                'tipo_rubrica_analise': self._clean_text(row[6]),
                'descricao_rubrica_sigrh': self._clean_text(row[7]),
                'descricao': self._clean_text(row[8]),
                'tipo_de_rubrica': self._clean_text(row[9]),
                'criterio_calculo_rubrica': self._clean_text(row[10]),
                'valor': self._clean_text(row[11]),
                'legislacao_vigente': self._clean_text(row[12]),
                'link_para_consulta': self._clean_text(row[13]),
                'ativa': True,
                'valor_padrao': None,
            }

            _, was_created = Rubrica.objects.update_or_create(codigo=codigo, defaults=defaults)
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f'Importação concluída: {created} criadas, {updated} atualizadas, {skipped} ignoradas.'
        ))

    @staticmethod
    def _clean_text(value):
        if value is None:
            return ''
        text = str(value).strip()
        return text