"""
HealthSphere AI - Interoperability Views
========================================

Views for healthcare interoperability management and monitoring.
Supports FHIR/HL7 integration monitoring and system administration.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.db import models
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
from datetime import timedelta

from .models import (
    ExternalSystem, FHIRResource, HL7Message,
    DataMapping, IntegrationTransaction, ConsentManagement
)
from .fhir_hl7_services import FHIRClient, HL7MessageProcessor, DataTransformationService


@staff_member_required
def interoperability_dashboard(request):
    """Main dashboard for interoperability monitoring."""
    # System status overview
    systems = ExternalSystem.objects.all()
    connected_systems = systems.filter(connection_status='connected', is_active=True).count()
    total_systems = systems.count()
    
    # Recent activity
    recent_transactions = IntegrationTransaction.objects.select_related(
        'external_system', 'related_patient'
    ).order_by('-started_at')[:10]
    
    # FHIR resource stats
    fhir_stats = FHIRResource.objects.aggregate(
        total_resources=Count('id'),
        valid_resources=Count('id', filter=Q(is_valid=True)),
        patients=Count('related_patient', distinct=True)
    )
    
    # HL7 message stats
    hl7_stats = HL7Message.objects.aggregate(
        total_messages=Count('id'),
        pending_messages=Count('id', filter=Q(status='pending')),
        processed_messages=Count('id', filter=Q(status='processed')),
        error_messages=Count('id', filter=Q(status='error'))
    )
    
    # Recent errors
    recent_errors = IntegrationTransaction.objects.filter(
        status='failed',
        started_at__gte=timezone.now() - timedelta(days=7)
    ).order_by('-started_at')[:5]
    
    # Performance metrics
    avg_response_time = IntegrationTransaction.objects.filter(
        status='completed',
        started_at__gte=timezone.now() - timedelta(days=7)
    ).aggregate(
        avg_duration=models.Avg('duration_ms')
    )['avg_duration'] or 0
    
    context = {
        'total_systems': total_systems,
        'connected_systems': connected_systems,
        'connection_rate': (connected_systems / total_systems * 100) if total_systems > 0 else 0,
        'recent_transactions': recent_transactions,
        'fhir_stats': fhir_stats,
        'hl7_stats': hl7_stats,
        'recent_errors': recent_errors,
        'avg_response_time': round(avg_response_time, 2),
    }
    
    return render(request, 'interoperability/dashboard.html', context)


@staff_member_required
def external_systems_list(request):
    """List and manage external healthcare systems."""
    systems = ExternalSystem.objects.all().order_by('name')
    
    # Filter by status if requested
    status_filter = request.GET.get('status')
    if status_filter:
        systems = systems.filter(connection_status=status_filter)
    
    # Search functionality
    search_query = request.GET.get('q')
    if search_query:
        systems = systems.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(base_url__icontains=search_query)
        )
    
    paginator = Paginator(systems, 20)
    page = request.GET.get('page')
    systems = paginator.get_page(page)
    
    context = {
        'systems': systems,
        'status_filter': status_filter,
        'search_query': search_query,
        'status_choices': [
            ('unknown', 'Unknown'),
            ('connected', 'Connected'),
            ('disconnected', 'Disconnected'),
            ('error', 'Connection Error'),
        ],
        'system_types': ExternalSystem.SYSTEM_TYPES,
    }
    
    return render(request, 'interoperability/external_systems_list.html', context)


@staff_member_required
def external_system_detail(request, system_id):
    """Detailed view of an external healthcare system."""
    system = get_object_or_404(ExternalSystem, pk=system_id)
    
    # Recent transactions for this system
    recent_transactions = IntegrationTransaction.objects.filter(
        external_system=system
    ).order_by('-started_at')[:20]
    
    # Transaction statistics
    transaction_stats = IntegrationTransaction.objects.filter(
        external_system=system,
        started_at__gte=timezone.now() - timedelta(days=30)
    ).aggregate(
        total=Count('id'),
        completed=Count('id', filter=Q(status='completed')),
        failed=Count('id', filter=Q(status='failed')),
        avg_duration=models.Avg('duration_ms')
    )
    
    # FHIR resources from this system
    fhir_resources = FHIRResource.objects.filter(
        source_system=system
    ).order_by('-last_updated')[:10]
    
    context = {
        'system': system,
        'recent_transactions': recent_transactions,
        'transaction_stats': transaction_stats,
        'fhir_resources': fhir_resources,
    }
    
    return render(request, 'interoperability/external_system_detail.html', context)


@require_POST
@staff_member_required
def test_system_connection(request, system_id):
    """Test connection to an external system."""
    system = get_object_or_404(ExternalSystem, pk=system_id)
    
    try:
        success = system.test_connection()
        if success:
            messages.success(request, f"Successfully connected to {system.name}")
        else:
            messages.error(request, f"Failed to connect to {system.name}")
    except Exception as e:
        messages.error(request, f"Error testing connection to {system.name}: {str(e)}")
    
    return redirect('interoperability:external_system_detail', system_id=system_id)


@staff_member_required
def fhir_resources_list(request):
    """List FHIR resources with filtering and search."""
    resources = FHIRResource.objects.select_related(
        'source_system', 'related_patient'
    ).order_by('-last_updated')
    
    # Filter by resource type
    resource_type = request.GET.get('type')
    if resource_type:
        resources = resources.filter(resource_type=resource_type)
    
    # Filter by validation status
    valid_only = request.GET.get('valid_only')
    if valid_only == 'true':
        resources = resources.filter(is_valid=True)
    elif valid_only == 'false':
        resources = resources.filter(is_valid=False)
    
    # Filter by source system
    source_system = request.GET.get('source_system')
    if source_system:
        resources = resources.filter(source_system_id=source_system)
    
    # Search functionality
    search_query = request.GET.get('q')
    if search_query:
        resources = resources.filter(
            Q(resource_id__icontains=search_query) |
            Q(resource_type__icontains=search_query)
        )
    
    paginator = Paginator(resources, 25)
    page = request.GET.get('page')
    resources = paginator.get_page(page)
    
    # Get filter options
    resource_types = FHIRResource.objects.values_list(
        'resource_type', flat=True
    ).distinct().order_by('resource_type')
    
    source_systems = ExternalSystem.objects.filter(is_active=True).order_by('name')
    
    context = {
        'resources': resources,
        'resource_type': resource_type,
        'valid_only': valid_only,
        'source_system': source_system,
        'search_query': search_query,
        'resource_types': resource_types,
        'source_systems': source_systems,
    }
    
    return render(request, 'interoperability/fhir_resources_list.html', context)


@staff_member_required
def fhir_resource_detail(request, resource_id):
    """Detailed view of a FHIR resource."""
    resource = get_object_or_404(FHIRResource, pk=resource_id)
    
    # Format JSON data for display
    formatted_data = json.dumps(resource.resource_data, indent=2)
    
    context = {
        'resource': resource,
        'formatted_data': formatted_data,
    }
    
    return render(request, 'interoperability/fhir_resource_detail.html', context)


@staff_member_required
def hl7_messages_list(request):
    """List HL7 messages with filtering and search."""
    messages_qs = HL7Message.objects.select_related(
        'source_system', 'destination_system', 'related_patient'
    ).order_by('-received_at')
    
    # Filter by message type
    message_type = request.GET.get('type')
    if message_type:
        messages_qs = messages_qs.filter(message_type=message_type)
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        messages_qs = messages_qs.filter(status=status)
    
    # Filter by direction
    direction = request.GET.get('direction')
    if direction:
        messages_qs = messages_qs.filter(direction=direction)
    
    # Search functionality
    search_query = request.GET.get('q')
    if search_query:
        messages_qs = messages_qs.filter(
            Q(control_id__icontains=search_query) |
            Q(message_type__icontains=search_query) |
            Q(trigger_event__icontains=search_query)
        )
    
    paginator = Paginator(messages_qs, 25)
    page = request.GET.get('page')
    messages_qs = paginator.get_page(page)
    
    # Get filter options
    message_types = HL7Message.objects.values_list(
        'message_type', flat=True
    ).distinct().order_by('message_type')
    
    context = {
        'messages': messages_qs,
        'message_type': message_type,
        'status': status,
        'direction': direction,
        'search_query': search_query,
        'message_types': message_types,
        'status_choices': HL7Message.PROCESSING_STATUS,
        'direction_choices': HL7Message.DIRECTIONS,
        'all_message_types': HL7Message.MESSAGE_TYPES,
    }
    
    return render(request, 'interoperability/hl7_messages_list.html', context)


@staff_member_required
def hl7_message_detail(request, message_id):
    """Detailed view of an HL7 message."""
    message = get_object_or_404(HL7Message, pk=message_id)
    
    # Format message data for display
    formatted_raw = message.raw_message.replace('\r', '\n') if message.raw_message else ''
    formatted_parsed = json.dumps(message.parsed_message, indent=2) if message.parsed_message else ''
    
    context = {
        'message': message,
        'formatted_raw': formatted_raw,
        'formatted_parsed': formatted_parsed,
    }
    
    return render(request, 'interoperability/hl7_message_detail.html', context)


@require_POST
@staff_member_required
def reprocess_hl7_message(request, message_id):
    """Reprocess an HL7 message."""
    message = get_object_or_404(HL7Message, pk=message_id)
    
    if message.status != 'error':
        messages.warning(request, "Only messages with error status can be reprocessed.")
        return redirect('interoperability:hl7_message_detail', message_id=message_id)
    
    try:
        processor = HL7MessageProcessor()
        success = processor.process_message(message.raw_message)
        
        if success:
            message.status = 'processed'
            message.processed_at = timezone.now()
            message.save()
            messages.success(request, "Message reprocessed successfully.")
        else:
            messages.error(request, "Failed to reprocess message.")
    
    except Exception as e:
        messages.error(request, f"Error reprocessing message: {str(e)}")
    
    return redirect('interoperability:hl7_message_detail', message_id=message_id)


@staff_member_required
def data_mappings_list(request):
    """List data mappings for transformation rules."""
    mappings = DataMapping.objects.select_related(
        'source_system', 'target_system', 'created_by'
    ).order_by('name')
    
    # Filter by mapping type
    mapping_type = request.GET.get('type')
    if mapping_type:
        mappings = mappings.filter(mapping_type=mapping_type)
    
    # Filter by active status
    active_only = request.GET.get('active_only')
    if active_only == 'true':
        mappings = mappings.filter(is_active=True)
    
    # Search functionality
    search_query = request.GET.get('q')
    if search_query:
        mappings = mappings.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    paginator = Paginator(mappings, 20)
    page = request.GET.get('page')
    mappings = paginator.get_page(page)
    
    context = {
        'mappings': mappings,
        'mapping_type': mapping_type,
        'active_only': active_only,
        'search_query': search_query,
        'mapping_type_choices': DataMapping.MAPPING_TYPES,
    }
    
    return render(request, 'interoperability/data_mappings_list.html', context)


@require_POST
@staff_member_required
def test_data_mapping(request, mapping_id):
    """Test a data mapping with sample data."""
    mapping = get_object_or_404(DataMapping, pk=mapping_id)
    
    # Sample test data
    test_data = {"test": "data", "patient_id": "123", "message_type": "ADT"}
    
    try:
        success, result = mapping.test_mapping(test_data)
        if success:
            messages.success(request, f"Mapping test passed: {result}")
        else:
            messages.error(request, f"Mapping test failed: {result}")
    
    except Exception as e:
        messages.error(request, f"Error testing mapping: {str(e)}")
    
    return redirect('interoperability:data_mappings_list')


@staff_member_required
def integration_transactions_list(request):
    """List integration transactions for monitoring."""
    transactions = IntegrationTransaction.objects.select_related(
        'external_system', 'related_patient', 'initiated_by'
    ).order_by('-started_at')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        transactions = transactions.filter(status=status)
    
    # Filter by transaction type
    transaction_type = request.GET.get('type')
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    
    # Filter by system
    system_id = request.GET.get('system')
    if system_id:
        transactions = transactions.filter(external_system_id=system_id)
    
    # Date range filter
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        transactions = transactions.filter(started_at__gte=date_from)
    if date_to:
        transactions = transactions.filter(started_at__lte=date_to)
    
    paginator = Paginator(transactions, 25)
    page = request.GET.get('page')
    transactions = paginator.get_page(page)
    
    # Get filter options
    systems = ExternalSystem.objects.filter(is_active=True).order_by('name')
    
    context = {
        'transactions': transactions,
        'status': status,
        'transaction_type': transaction_type,
        'system_id': system_id,
        'date_from': date_from,
        'date_to': date_to,
        'systems': systems,
        'status_choices': IntegrationTransaction.TRANSACTION_STATUS,
        'transaction_type_choices': IntegrationTransaction.TRANSACTION_TYPES,
    }
    
    return render(request, 'interoperability/integration_transactions_list.html', context)


@staff_member_required
def consent_management_list(request):
    """List patient consent records."""
    consents = ConsentManagement.objects.select_related(
        'patient', 'created_by'
    ).prefetch_related('authorized_systems').order_by('-created_at')
    
    # Filter by consent type
    consent_type = request.GET.get('type')
    if consent_type:
        consents = consents.filter(consent_type=consent_type)
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        consents = consents.filter(status=status)
    
    # Search by patient name
    search_query = request.GET.get('q')
    if search_query:
        consents = consents.filter(
            Q(patient__first_name__icontains=search_query) |
            Q(patient__last_name__icontains=search_query) |
            Q(purpose__icontains=search_query)
        )
    
    paginator = Paginator(consents, 25)
    page = request.GET.get('page')
    consents = paginator.get_page(page)
    
    context = {
        'consents': consents,
        'consent_type': consent_type,
        'status': status,
        'search_query': search_query,
        'consent_type_choices': ConsentManagement.CONSENT_TYPES,
        'status_choices': ConsentManagement.CONSENT_STATUS,
    }
    
    return render(request, 'interoperability/consent_management_list.html', context)


# API endpoints for AJAX requests

@csrf_exempt
def api_fhir_webhook(request):
    """Webhook endpoint for receiving FHIR notifications."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Process FHIR webhook data
        # This would typically create or update FHIR resources
        
        return JsonResponse({'status': 'success', 'message': 'Webhook processed'})
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def api_hl7_endpoint(request):
    """Endpoint for receiving HL7 messages."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests allowed'}, status=405)
    
    try:
        hl7_message = request.body.decode('utf-8')
        
        processor = HL7MessageProcessor()
        success = processor.process_message(hl7_message)
        
        if success:
            return HttpResponse('MSA|AA|', content_type='text/plain')  # ACK
        else:
            return HttpResponse('MSA|AE|', content_type='text/plain')  # Error
    
    except Exception as e:
        return HttpResponse(f'MSA|AR|Error: {str(e)}', content_type='text/plain')


@staff_member_required
def api_system_status(request):
    """API endpoint for system status updates."""
    systems = ExternalSystem.objects.all()
    
    status_data = []
    for system in systems:
        status_data.append({
            'id': system.id,
            'name': system.name,
            'status': system.connection_status,
            'last_connection': system.last_successful_connection.isoformat() if system.last_successful_connection else None,
            'is_active': system.is_active,
        })
    
    return JsonResponse({'systems': status_data})
