from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.db.models import Sum
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO

from billing.models import BillingTransaction, UserBalance
from orders.models import Order
from django.utils import timezone


@login_required
def transaction_history(request):
    """View user's transaction history"""
    if request.user.user_type != 'subscriber':
        return redirect('dashboard_home')
    
    # Get filter parameters
    transaction_type = request.GET.get('type', 'all')
    days = request.GET.get('days', '365')
    
    try:
        days = int(days)
    except ValueError:
        days = 365
    
    # Get transactions
    start_date = timezone.now() - timedelta(days=days)
    transactions = BillingTransaction.objects.filter(
        user=request.user,
        created_at__gte=start_date
    ).select_related('order')
    
    if transaction_type in ['credit', 'debit']:
        transactions = transactions.filter(type=transaction_type)
    
    # Get balance
    balance = UserBalance.objects.get(user=request.user)
    
    # Calculate summary
    credits = transactions.filter(type='credit').aggregate(sum=Sum('amount'))['sum'] or 0
    debits = transactions.filter(type='debit').aggregate(sum=Sum('amount'))['sum'] or 0
    
    context = {
        'transactions': transactions.order_by('-created_at'),
        'current_balance': balance.balance,
        'total_credits': credits,
        'total_debits': debits,
        'filter_type': transaction_type,
        'filter_days': days,
    }
    
    return render(request, 'billing/transaction_history.html', context)


@login_required
def generate_receipt(request, transaction_id):
    """Generate PDF receipt for a transaction"""
    if request.user.user_type != 'subscriber':
        return redirect('dashboard_home')
    
    transaction = get_object_or_404(
        BillingTransaction,
        id=transaction_id,
        user=request.user
    )
    
    # Create PDF in memory
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=30,
        alignment=1  # Center
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#764ba2'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Title
    elements.append(Paragraph('ORDER IN', title_style))
    elements.append(Paragraph('Transaction Receipt', styles['Heading2']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Receipt header
    header_data = [
        ['Receipt Number', f'TXN-{transaction.id}'],
        ['Date', transaction.created_at.strftime('%Y-%m-%d %H:%M:%S')],
        ['Account', request.user.username],
    ]
    
    header_table = Table(header_data, colWidths=[2*inch, 4*inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Transaction details
    elements.append(Paragraph('Transaction Details', heading_style))
    
    detail_data = [
        ['Type', transaction.get_type_display()],
        ['Amount', f'R {transaction.amount:.2f}'],
        ['Description', transaction.description],
        ['Balance After', f'R {transaction.balance_after:.2f}'],
    ]
    
    if transaction.order:
        detail_data.append(['Order ID', f'#{transaction.order.id}'])
    
    detail_table = Table(detail_data, colWidths=[2*inch, 4*inch])
    detail_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(detail_table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Footer
    footer_text = 'This is an automated receipt from Order In. Please keep for your records.'
    elements.append(Paragraph(footer_text, styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    response = FileResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt-txn-{transaction.id}.pdf"'
    
    return response


@login_required
def order_receipt(request, order_id):
    """Generate detailed receipt for an order"""
    if request.user.user_type != 'subscriber':
        return redirect('dashboard_home')
    
    order = get_object_or_404(Order, id=order_id, subscriber=request.user)
    
    # Create PDF in memory
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=30,
        alignment=1  # Center
    )
    
    # Title
    elements.append(Paragraph('ORDER IN', title_style))
    elements.append(Paragraph('Order Receipt', styles['Heading2']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Order header
    header_data = [
        ['Order Number', f'ORD-{order.id}'],
        ['Date', order.created_at.strftime('%Y-%m-%d %H:%M:%S')],
        ['Status', order.get_status_display()],
        ['Customer', request.user.get_full_name() or request.user.username],
    ]
    
    header_table = Table(header_data, colWidths=[2*inch, 4*inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Order items
    elements.append(Paragraph('Order Items', styles['Heading2']))
    
    items_data = [['Product', 'Qty', 'Unit Price', 'Total']]
    for item in order.items.all():
        items_data.append([
            item.product.name,
            str(item.quantity),
            f'R {item.unit_price:.2f}',
            f'R {item.total_price:.2f}'
        ])
    
    items_table = Table(items_data, colWidths=[2.5*inch, 0.75*inch, 1.5*inch, 1.25*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Totals
    totals_data = [
        ['Products Total', f'R {order.total_price:.2f}'],
        ['Service Fee', f'R {order.service_fee:.2f}'],
        ['ORDER TOTAL', f'R {order.total_amount:.2f}'],
    ]
    
    totals_table = Table(totals_data, colWidths=[4.25*inch, 1.75*inch])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 14),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, -1), (-1, -1), 10),
        ('GRID', (0, -1), (-1, -1), 1, colors.black),
    ]))
    elements.append(totals_table)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    response = FileResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="order-{order.id}-receipt.pdf"'
    
    return response
