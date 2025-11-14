"""
API Logging Analytics Views
Endpoints to view logs, metrics, and performance analytics
"""
import os
import json
from datetime import datetime, timedelta
from collections import defaultdict
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.core.cache import cache
from django.conf import settings


@api_view(['GET'])
@permission_classes([IsAdminUser])
def api_metrics(request):
    """
    Get real-time API metrics from cache
    
    Returns:
    - Total requests count
    - Requests by status code
    - Error rate
    - Top endpoints
    """
    metrics = {
        'total_requests': cache.get('api_requests_total', 0),
        'total_errors': cache.get('api_requests_errors', 0),
        'by_status': {},
        'error_rate': 0.0,
        'cache_enabled': 'default' in settings.CACHES,
    }
    
    # Get requests by status code
    for status in [200, 201, 204, 400, 401, 403, 404, 500, 502, 503]:
        count = cache.get(f'api_requests_status_{status}', 0)
        if count > 0:
            metrics['by_status'][status] = count
    
    # Calculate error rate
    if metrics['total_requests'] > 0:
        metrics['error_rate'] = round(
            (metrics['total_errors'] / metrics['total_requests']) * 100, 2
        )
    
    return Response(metrics)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def recent_logs(request):
    """
    Get recent API logs from file
    
    Query params:
    - limit: Number of lines to return (default: 50, max: 500)
    - level: Filter by log level (INFO, WARNING, ERROR)
    - search: Search in log messages
    """
    limit = min(int(request.GET.get('limit', 50)), 500)
    level_filter = request.GET.get('level', '').upper()
    search_term = request.GET.get('search', '').lower()
    
    log_file = settings.LOGS_DIR / 'api_requests.log'
    
    if not log_file.exists():
        return Response({
            'logs': [],
            'message': 'No logs file found yet'
        })
    
    try:
        # Read last N lines from log file
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Filter logs
        filtered_logs = []
        for line in reversed(lines):  # Most recent first
            # Apply level filter
            if level_filter and level_filter not in line:
                continue
            
            # Apply search filter
            if search_term and search_term not in line.lower():
                continue
            
            filtered_logs.append(line.strip())
            
            if len(filtered_logs) >= limit:
                break
        
        return Response({
            'logs': filtered_logs,
            'count': len(filtered_logs),
            'total_lines': len(lines)
        })
    
    except Exception as e:
        return Response({
            'error': str(e),
            'logs': []
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def error_logs(request):
    """
    Get recent error logs
    
    Query params:
    - limit: Number of errors to return (default: 20, max: 100)
    """
    limit = min(int(request.GET.get('limit', 20)), 100)
    
    error_file = settings.LOGS_DIR / 'errors.log'
    
    if not error_file.exists():
        return Response({
            'errors': [],
            'message': 'No errors logged yet'
        })
    
    try:
        with open(error_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Get last N lines
        recent_errors = [line.strip() for line in reversed(lines[-limit:])]
        
        return Response({
            'errors': recent_errors,
            'count': len(recent_errors),
            'total_errors': len(lines)
        })
    
    except Exception as e:
        return Response({
            'error': str(e),
            'errors': []
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def slow_requests(request):
    """
    Get recent slow requests (> 1 second)
    
    Query params:
    - limit: Number of requests to return (default: 20, max: 100)
    """
    limit = min(int(request.GET.get('limit', 20)), 100)
    
    slow_file = settings.LOGS_DIR / 'slow_requests.log'
    
    if not slow_file.exists():
        return Response({
            'slow_requests': [],
            'message': 'No slow requests logged yet'
        })
    
    try:
        with open(slow_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Get last N lines
        slow_reqs = [line.strip() for line in reversed(lines[-limit:])]
        
        return Response({
            'slow_requests': slow_reqs,
            'count': len(slow_reqs),
            'total': len(lines)
        })
    
    except Exception as e:
        return Response({
            'error': str(e),
            'slow_requests': []
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def log_analytics(request):
    """
    Analyze JSON logs for patterns and statistics
    
    Returns:
    - Average response time
    - Top endpoints by request count
    - Top endpoints by response time
    - Status code distribution
    - Cache hit rate
    """
    json_log_file = settings.LOGS_DIR / 'api_requests.json'
    
    if not json_log_file.exists():
        return Response({
            'message': 'No JSON logs available yet',
            'analytics': {}
        })
    
    try:
        analytics = {
            'total_requests': 0,
            'avg_response_time_ms': 0,
            'cache_hit_rate': 0,
            'top_endpoints': [],
            'slowest_endpoints': [],
            'status_distribution': defaultdict(int),
            'errors_by_type': defaultdict(int),
        }
        
        endpoint_stats = defaultdict(lambda: {'count': 0, 'total_time': 0})
        cache_hits = 0
        total_cache_tracked = 0
        total_time = 0
        
        # Parse last 1000 lines of JSON logs
        with open(json_log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line in lines[-1000:]:  # Last 1000 requests
            try:
                log_entry = json.loads(line)
                data = log_entry.get('data', {})
                
                analytics['total_requests'] += 1
                
                # Response time
                response_time = data.get('response_time_ms', 0)
                total_time += response_time
                
                # Endpoint stats
                path = data.get('path', 'unknown')
                endpoint_stats[path]['count'] += 1
                endpoint_stats[path]['total_time'] += response_time
                
                # Status distribution
                status = data.get('status_code', 0)
                analytics['status_distribution'][status] += 1
                
                # Cache stats
                cache_status = data.get('cache_status')
                if cache_status in ['HIT', 'MISS']:
                    total_cache_tracked += 1
                    if cache_status == 'HIT':
                        cache_hits += 1
                
                # Error tracking
                if 'exception_type' in data:
                    exc_type = data['exception_type']
                    analytics['errors_by_type'][exc_type] += 1
                
            except json.JSONDecodeError:
                continue
        
        # Calculate averages
        if analytics['total_requests'] > 0:
            analytics['avg_response_time_ms'] = round(
                total_time / analytics['total_requests'], 2
            )
        
        if total_cache_tracked > 0:
            analytics['cache_hit_rate'] = round(
                (cache_hits / total_cache_tracked) * 100, 2
            )
        
        # Top endpoints by count
        top_by_count = sorted(
            endpoint_stats.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:10]
        
        analytics['top_endpoints'] = [
            {
                'endpoint': endpoint,
                'count': stats['count'],
                'avg_time_ms': round(stats['total_time'] / stats['count'], 2)
            }
            for endpoint, stats in top_by_count
        ]
        
        # Slowest endpoints
        slowest = sorted(
            endpoint_stats.items(),
            key=lambda x: x[1]['total_time'] / x[1]['count'],
            reverse=True
        )[:10]
        
        analytics['slowest_endpoints'] = [
            {
                'endpoint': endpoint,
                'avg_time_ms': round(stats['total_time'] / stats['count'], 2),
                'count': stats['count']
            }
            for endpoint, stats in slowest
        ]
        
        # Convert defaultdicts to regular dicts
        analytics['status_distribution'] = dict(analytics['status_distribution'])
        analytics['errors_by_type'] = dict(analytics['errors_by_type'])
        
        return Response(analytics)
    
    except Exception as e:
        return Response({
            'error': str(e),
            'analytics': {}
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def clear_metrics(request):
    """Clear all cached metrics"""
    try:
        # Clear all metric keys
        cache.delete('api_requests_total')
        cache.delete('api_requests_errors')
        
        # Clear status codes
        for status in range(100, 600):
            cache.delete(f'api_requests_status_{status}')
        
        return Response({
            'message': 'Metrics cleared successfully'
        })
    
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500)
