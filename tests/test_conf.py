from django.test import TestCase, override_settings
from unittest.mock import patch
from django_otel.conf import configure_opentelemetry, get_otel_setting


class ConfTest(TestCase):
    
    @override_settings(OTEL_EXPORTER_OTLP_ENDPOINT='http://localhost:4317')
    @patch('django_otel.conf.OTLPSpanExporter')
    @patch('django_otel.conf.BatchSpanProcessor')
    @patch('django_otel.conf.trace.set_tracer_provider')
    def test_configure_opentelemetry_with_endpoint(self, mock_set_provider, 
                                                 mock_processor, mock_exporter):
        """Test OpenTelemetry configuration with endpoint."""
        configure_opentelemetry()
        
        # Verify exporter was created with correct endpoint
        mock_exporter.assert_called_once_with(endpoint='http://localhost:4317')
        mock_processor.assert_called_once()
        mock_set_provider.assert_called_once()
    
    @override_settings(OTEL_EXPORTER_OTLP_ENDPOINT=None)
    @patch('django_otel.conf.OTLPSpanExporter')
    def test_configure_opentelemetry_without_endpoint(self, mock_exporter):
        """Test OpenTelemetry configuration without endpoint."""
        configure_opentelemetry()
        
        # Verify exporter was not created
        mock_exporter.assert_not_called()
    
    @override_settings(OTEL_TEST_SETTING='test_value')
    def test_get_otel_setting(self):
        """Test getting OpenTelemetry settings."""
        value = get_otel_setting('TEST_SETTING', 'default')
        self.assertEqual(value, 'test_value')
        
        # Test default value
        value = get_otel_setting('NONEXISTENT', 'default')
        self.assertEqual(value, 'default')