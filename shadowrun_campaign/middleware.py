"""
Custom middleware for exception handling and logging.
"""
import logging
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib import messages

logger = logging.getLogger(__name__)


class ExceptionLoggingMiddleware:
    """
    Middleware to catch and log all unhandled exceptions.

    This middleware logs exceptions that aren't handled by view-level
    try-except blocks, providing a safety net for error tracking.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        """
        Process any unhandled exceptions.

        Args:
            request: The HTTP request object
            exception: The exception that was raised

        Returns:
            None to let Django's default exception handling take over,
            or an HttpResponse to handle the exception ourselves
        """
        # Log the exception with full context
        logger.error(
            f"Unhandled exception in {request.method} {request.path}",
            exc_info=True,
            extra={
                'user': getattr(request, 'user', None),
                'method': request.method,
                'path': request.path,
                'GET': dict(request.GET),
                'POST': dict(request.POST) if request.method == 'POST' else {},
            }
        )

        # For AJAX requests, return JSON error response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'An unexpected error occurred. Please try again.'
            }, status=500)

        # For regular requests, let Django handle it (will show debug page in DEBUG=True)
        # In production, Django will show the 500 error page
        return None
