from django.test import TestCase, RequestFactory
from unittest.mock import patch, MagicMock
from django.http import HttpResponse
from django_otel.middleware import OpenTelemetryMiddleware


class OpenTelemetryMiddlewareTest(TestCase):
    
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = OpenTelemetryMiddleware()
    
    @patch('django_otel.middleware.trace.get_tracer')
    def test_process_request(self, mock_get_tracer):
        """Test that process_request creates a span."""
        mock_tracer = MagicMock()
        mock_span = MagicMock()
        mock_get_tracer.return_value = mock_tracer
        mock_tracer.start_span.return_value = mock_span
        
        request = self.factory.get('/test/')
        self.middleware.process_request(request)
        
        # Verify span was created
        self.assertTrue(hasattr(request, '_otel_span'))
        self.assertTrue(hasattr(request, '_otel_start_time'))
        mock_tracer.start_span.assert_called_once()
    
    @patch('django_otel.middleware.trace.get_tracer')
    def test_process_response(self, mock_get_tracer):
        """Test that process_response ends the span."""
        mock_tracer = MagicMock()
        mock_span = MagicMock()
        mock_get_tracer.return_value = mock_tracer
        mock_tracer.start_span.return_value = mock_span
        
        request = self.factory.get('/test/')
        response = HttpResponse('test', status=200)
        
        # Setup request with span
        self.middleware.process_request(request)
        self.middleware.process_response(request, response)
        
        # Verify span was ended
        mock_span.set_attributes.assert_called()
        mock_span.set_status.assert_called()
        mock_span.end.assert_called_once()
    
    @patch('django_otel.middleware.trace.get_tracer')
    def test_process_exception(self, mock_get_tracer):
        """Test that exceptions are recorded."""
        mock_tracer = MagicMock()
        mock_span = MagicMock()
        mock_get_tracer.return_value = mock_tracer
        mock_tracer.start_span.return_value = mock_span
        
        request = self.factory.get('/test/')
        exception = ValueError('test error')
        
        # Setup request with span
        self.middleware.process_request(request)
        self.middleware.process_exception(request, exception)
        
        # Verify exception was recorded
        mock_span.record_exception.assert_called_once_with(exception)
        mock_span.set_status.assert_called_once()