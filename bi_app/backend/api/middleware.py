"""
API Request Logging Middleware
Logs all API requests with timing, status, and error details
"""
import time
import json
import logging
import traceback
from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve
from django.core.cache import cache

# Configure logger
logger = logging.getLogger('api.requests')
error_logger = logging.getLogger('api.errors')


class APIRequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all API requests with:
    - Request method, path, query params
    - Response status code and time
    - User information
    - Cache hit/miss status
    - Error details with stack traces
    """
    
    def process_request(self, request):
        """Called before view processing"""
        # Store request start time
        request._start_time = time.time()
        
        # Extract request info
        request._log_data = {
            'method': request.method,
            'path': request.path,
            'query_params': dict(request.GET),
            'user': str(request.user) if request.user.is_authenticated else 'anonymous',
            'user_id': request.user.id if request.user.is_authenticated else None,
            'ip_address': self.get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:200],
        }
        
        # Log body for POST/PUT/PATCH (limit size)
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                body = request.body.decode('utf-8')[:1000]  # First 1000 chars
                request._log_data['body_preview'] = body
            except:
                request._log_data['body_preview'] = '<binary or invalid UTF-8>'
        
        return None
    
    def process_response(self, request, response):
        """Called after view processing"""
        # Only log API endpoints
        if not request.path.startswith('/api/'):
            return response
        
        # Calculate response time
        if hasattr(request, '_start_time'):
            response_time_ms = (time.time() - request._start_time) * 1000
        else:
            response_time_ms = 0
        
        # Get log data
        log_data = getattr(request, '_log_data', {})
        log_data['status_code'] = response.status_code
        log_data['response_time_ms'] = round(response_time_ms, 2)
        
        # Check cache status
        cache_status = response.get('X-Cache', 'N/A')
        log_data['cache_status'] = cache_status
        
        # Determine log level based on status code
        if response.status_code >= 500:
            log_level = logging.ERROR
            log_data['level'] = 'ERROR'
        elif response.status_code >= 400:
            log_level = logging.WARNING
            log_data['level'] = 'WARNING'
        else:
            log_level = logging.INFO
            log_data['level'] = 'INFO'
        
        # Try to get response size
        try:
            if hasattr(response, 'content'):
                log_data['response_size_bytes'] = len(response.content)
        except:
            pass
        
        # Format log message
        log_message = self.format_log_message(log_data)
        
        # Log the request
        logger.log(log_level, log_message, extra={'data': log_data})
        
        # Track slow requests (> 1 second)
        if response_time_ms > 1000:
            logger.warning(
                f"SLOW REQUEST: {log_data['method']} {log_data['path']} took {response_time_ms:.2f}ms",
                extra={'data': log_data}
            )
        
        # Increment request counter in cache
        self.update_metrics(log_data)
        
        return response
    
    def process_exception(self, request, exception):
        """Called when view raises an exception"""
        # Only log API endpoints
        if not request.path.startswith('/api/'):
            return None
        
        # Calculate response time
        if hasattr(request, '_start_time'):
            response_time_ms = (time.time() - request._start_time) * 1000
        else:
            response_time_ms = 0
        
        # Get log data
        log_data = getattr(request, '_log_data', {})
        log_data['status_code'] = 500
        log_data['response_time_ms'] = round(response_time_ms, 2)
        log_data['level'] = 'ERROR'
        log_data['exception_type'] = type(exception).__name__
        log_data['exception_message'] = str(exception)
        log_data['traceback'] = traceback.format_exc()
        
        # Log the error
        error_message = (
            f"EXCEPTION: {log_data['method']} {log_data['path']} - "
            f"{log_data['exception_type']}: {log_data['exception_message']}"
        )
        error_logger.error(error_message, extra={'data': log_data}, exc_info=True)
        
        # Update metrics
        self.update_metrics(log_data, error=True)
        
        return None  # Let Django handle the exception
    
    def format_log_message(self, log_data):
        """Format a readable log message"""
        return (
            f"{log_data.get('level', 'INFO')} - "
            f"{log_data['method']} {log_data['path']} - "
            f"Status: {log_data['status_code']} - "
            f"Time: {log_data['response_time_ms']}ms - "
            f"User: {log_data['user']} - "
            f"Cache: {log_data.get('cache_status', 'N/A')}"
        )
    
    def get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def update_metrics(self, log_data, error=False):
        """Update request metrics in cache"""
        try:
            # Increment total requests counter
            cache.incr('api_requests_total', delta=1)
            
            # Increment status code counter
            status_code = log_data.get('status_code', 0)
            cache.incr(f'api_requests_status_{status_code}', delta=1)
            
            # Increment error counter if error
            if error or status_code >= 400:
                cache.incr('api_requests_errors', delta=1)
            
            # Track endpoint-specific metrics
            endpoint = log_data['path']
            cache.incr(f'api_endpoint_{endpoint}', delta=1)
            
        except Exception as e:
            # Don't let metrics tracking break the request
            logger.debug(f"Failed to update metrics: {e}")
