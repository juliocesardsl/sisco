import csv
from django.http import HttpResponse
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


def exportar_verificacoes_csv(queryset, status='todos'):
    """
    Exporta as verificações de conformidade para um arquivo CSV.

    Args:
        queryset: QuerySet com as verificações a exportar
        status: String indicando qual status foi filtrado

    Returns:
        HttpResponse com arquivo CSV para download
    """
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="verificacoes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Rubrica', 'Empresa', 'Ano', 'Valor Mínimo', 'Valor Máximo', 'Valor Pago', 'Status', 'Data Verificação', 'Observações'])

    for verificacao in queryset:
        writer.writerow([
            verificacao.padrao.rubrica.nome,
            verificacao.padrao.empresa.nome,
            verificacao.padrao.ano,
            f"R$ {verificacao.padrao.valor_minimo:.2f}",
            f"R$ {verificacao.padrao.valor_maximo:.2f}",
            f"R$ {verificacao.valor_pago:.2f}",
            verificacao.get_status_display(),
            verificacao.data_verificacao.strftime('%d/%m/%Y %H:%M'),
            verificacao.observacoes,
        ])

    return response


def exportar_comparacao_excel(comparacao_data, rubrica_codigo, rubrica_nome):
    """
    Exporta a comparação mensal de rubricas para um arquivo Excel.

    Args:
        comparacao_data: Lista de dicts com dados da comparação
        rubrica_codigo: Código da rubrica
        rubrica_nome: Nome da rubrica

    Returns:
        HttpResponse com arquivo Excel para download
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Comparação"

    # Estilos
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=12)
    title_fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
    title_font = Font(bold=True, size=11)
    center_alignment = Alignment(horizontal="center", vertical="center")
    right_alignment = Alignment(horizontal="right", vertical="center")
    left_alignment = Alignment(horizontal="left", vertical="center")
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    # Título
    ws.merge_cells('A1:F1')
    title_cell = ws['A1']
    title_cell.value = f"Comparativo Mensal de Rubricas - {rubrica_codigo} ({rubrica_nome})"
    title_cell.font = Font(bold=True, size=14)
    title_cell.alignment = center_alignment
    ws.row_dimensions[1].height = 25

    # Subtítulo com data
    ws.merge_cells('A2:F2')
    date_cell = ws['A2']
    date_cell.value = f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}"
    date_cell.font = Font(italic=True, size=10, color="666666")
    date_cell.alignment = center_alignment

    # Linha em branco
    ws.append([])

    # Cabeçalhos separando empresa e matrícula
    headers = ['Empresa', 'Matrícula', 'Valor Mês Anterior', 'Valor Mês Atual', 'Variação (Dif.)', 'Variação (%)']
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col_num)
        cell.value = header
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_alignment
        cell.border = thin_border

    # Dados
    row_num = 5
    total_anterior = 0
    total_atual = 0
    
    for item in comparacao_data:
        ws.cell(row=row_num, column=1).value = item.get('empresa', '')
        ws.cell(row=row_num, column=2).value = item.get('matricula', '')
        ws.cell(row=row_num, column=3).value = float(item.get('valor_anterior', 0))
        ws.cell(row=row_num, column=4).value = float(item.get('valor_atual', 0))
        ws.cell(row=row_num, column=5).value = float(item.get('diferenca', 0))
        
        variacao_pct = item.get('variacao_pct')
        if variacao_pct is not None:
            ws.cell(row=row_num, column=6).value = float(variacao_pct)
        
        total_anterior += float(item.get('valor_anterior', 0))
        total_atual += float(item.get('valor_atual', 0))
        
        # Aplicar estilos e cores
        for col in range(1, 7):
            cell = ws.cell(row=row_num, column=col)
            cell.border = thin_border
            
            if col >= 3:  # Colunas numéricas
                cell.alignment = right_alignment
                if col == 5:  # Coluna de diferença
                    diferenca = float(item.get('diferenca', 0))
                    if diferenca > 0:
                        cell.font = Font(bold=True, color="28A745")  # Verde
                    elif diferenca < 0:
                        cell.font = Font(bold=True, color="DC3545")  # Vermelho
                elif col == 6:  # Coluna de percentual
                    variacao_pct = item.get('variacao_pct')
                    if variacao_pct is not None:
                        if float(variacao_pct) > 0:
                            cell.font = Font(bold=True, color="28A745")  # Verde
                        elif float(variacao_pct) < 0:
                            cell.font = Font(bold=True, color="DC3545")  # Vermelho
            else:
                cell.alignment = left_alignment
        
        row_num += 1

    # Linha de totais
    total_row = row_num
    ws.cell(row=total_row, column=1).value = "TOTAL"
    ws.cell(row=total_row, column=1).font = Font(bold=True, size=11)
    ws.cell(row=total_row, column=3).value = total_anterior
    ws.cell(row=total_row, column=4).value = total_atual
    
    if total_anterior > 0:
        total_variacao_pct = ((total_atual - total_anterior) / total_anterior) * 100
        ws.cell(row=total_row, column=6).value = total_variacao_pct
    
    for col in range(1, 7):
        cell = ws.cell(row=total_row, column=col)
        cell.font = Font(bold=True, size=11, color="FFFFFF")
        cell.fill = PatternFill(start_color="404040", end_color="404040", fill_type="solid")
        cell.border = thin_border
        if col >= 3:
            cell.alignment = right_alignment
        else:
            cell.alignment = left_alignment

    # Ajustar largura das colunas
    ws.column_dimensions['A'].width = 20
    ws.column_dimensions['B'].width = 15
    ws.column_dimensions['C'].width = 22
    ws.column_dimensions['D'].width = 22
    ws.column_dimensions['E'].width = 20
    ws.column_dimensions['F'].width = 15

    # Formatar células numéricas como currency
    for row in ws.iter_rows(min_row=5, max_row=total_row, min_col=3, max_col=5):
        for cell in row:
            cell.number_format = 'R$ #,##0.00'
    
    for row in ws.iter_rows(min_row=5, max_row=total_row, min_col=6, max_col=6):
        for cell in row:
            cell.number_format = '0.00"%"'

    # Congelar linha de cabeçalho
    ws.freeze_panes = "A5"
    
    # Aplicar AutoFilter para poder filtrar cada coluna
    ws.auto_filter.ref = f'A4:F{total_row}'

    # Criar resposta HTTP
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="comparacao_rubricas_{rubrica_codigo}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'

    wb.save(response)
    return response
