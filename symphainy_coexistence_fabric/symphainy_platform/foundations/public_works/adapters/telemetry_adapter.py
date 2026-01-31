"""
Telemetry Adapter - Raw Technology Client (Layer 0)

OpenTelemetry SDK initialization and configuration.
This is the raw technology layer for telemetry operations.

WHAT (Infrastructure Role): I provide OpenTelemetry SDK initialization
HOW (Infrastructure Implementation): I use real OpenTelemetry SDK with no business logic

Supports both gRPC and HTTP/protobuf OTLP (e.g. Grafana Cloud uses HTTP/protobuf + headers).
"""

from typing import Optional, Dict, Any
import os

try:
    from opentelemetry import trace, metrics, _logs
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
    from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.instrumentation.logging import LoggingInstrumentor
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    TracerProvider = None
    MeterProvider = None
    LoggerProvider = None
    LoggingInstrumentor = None
    FastAPIInstrumentor = None

# gRPC OTLP exporters (default for local/self-hosted)
try:
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter as GrpcOTLPSpanExporter
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter as GrpcOTLPMetricExporter
    from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter as GrpcOTLPLogExporter
    GRPC_OTEL_AVAILABLE = True
except ImportError:
    GrpcOTLPSpanExporter = None
    GrpcOTLPMetricExporter = None
    GrpcOTLPLogExporter = None
    GRPC_OTEL_AVAILABLE = False

# HTTP/protobuf OTLP exporters (Grafana Cloud, etc.)
try:
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter as HttpOTLPSpanExporter
    from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter as HttpOTLPMetricExporter
    from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter as HttpOTLPLogExporter
    HTTP_OTEL_AVAILABLE = True
except ImportError:
    HttpOTLPSpanExporter = None
    HttpOTLPMetricExporter = None
    HttpOTLPLogExporter = None
    HTTP_OTEL_AVAILABLE = False

from utilities import get_logger


def _parse_otel_headers(headers_str: Optional[str]) -> Dict[str, str]:
    """Parse OTEL_EXPORTER_OTLP_HEADERS (key1=value1,key2=value2) into a dict."""
    if not headers_str or not headers_str.strip():
        return {}
    out: Dict[str, str] = {}
    for part in headers_str.split(","):
        part = part.strip()
        if "=" in part:
            k, v = part.split("=", 1)
            out[k.strip()] = v.strip()
    return out


class TelemetryAdapter:
    """
    OpenTelemetry SDK adapter - no business logic.
    
    This adapter provides OpenTelemetry SDK initialization and configuration
    without any business logic. It's the raw technology layer.
    """
    
    def __init__(
        self,
        service_name: str = "symphainy-platform",
        otlp_endpoint: Optional[str] = None,
        insecure: bool = True
    ):
        """
        Initialize Telemetry adapter.
        
        Args:
            service_name: Service name for telemetry
            otlp_endpoint: OTLP endpoint URL (defaults to env var)
            insecure: If True, use insecure connection (gRPC only; HTTP uses URL scheme)
        """
        if not OTEL_AVAILABLE:
            raise ImportError(
                "OpenTelemetry SDK not available. Install with: "
                "pip install opentelemetry-api opentelemetry-sdk "
                "opentelemetry-exporter-otlp-proto-grpc opentelemetry-exporter-otlp-proto-http "
                "opentelemetry-instrumentation-logging opentelemetry-instrumentation-fastapi"
            )
        
        self.service_name = service_name
        self.otlp_endpoint = otlp_endpoint or os.getenv(
            "OTEL_EXPORTER_OTLP_ENDPOINT",
            "http://localhost:4317"
        )
        self.insecure = insecure
        self.logger = get_logger(self.__class__.__name__)
        
        # Protocol: http/protobuf (Grafana Cloud) vs grpc (local/self-hosted)
        self._otlp_protocol = (os.getenv("OTEL_EXPORTER_OTLP_PROTOCOL") or "").strip().lower()
        self._otlp_headers = _parse_otel_headers(os.getenv("OTEL_EXPORTER_OTLP_HEADERS"))
        # Use HTTP when protocol is http/protobuf or endpoint is HTTPS (e.g. Grafana Cloud)
        self._use_http = (
            self._otlp_protocol == "http/protobuf"
            or self.otlp_endpoint.strip().lower().startswith("https://")
        )
        
        self._tracer_provider: Optional[TracerProvider] = None
        self._meter_provider: Optional[MeterProvider] = None
        self._logger_provider: Optional[LoggerProvider] = None
        self._initialized = False
    
    def initialize(self) -> bool:
        """
        Initialize OpenTelemetry SDK.
        
        Sets up:
        - TracerProvider (for traces)
        - MeterProvider (for metrics)
        - LoggerProvider (for logs)
        - OTLP exporters (HTTP/protobuf for Grafana Cloud, gRPC for local)
        
        Returns:
            True if initialization successful
        """
        if self._initialized:
            self.logger.warning("OpenTelemetry SDK already initialized")
            return True
        
        try:
            # Create resource
            resource = Resource.create({
                "service.name": self.service_name,
                "service.namespace": "symphainy-platform"
            })
            
            if self._use_http and HTTP_OTEL_AVAILABLE:
                # HTTP/protobuf (Grafana Cloud, etc.) — endpoint + headers from env
                otlp_span_exporter = HttpOTLPSpanExporter(
                    endpoint=self.otlp_endpoint,
                    headers=self._otlp_headers or None
                )
                otlp_metric_exporter = HttpOTLPMetricExporter(
                    endpoint=self.otlp_endpoint,
                    headers=self._otlp_headers or None
                )
                otlp_log_exporter = HttpOTLPLogExporter(
                    endpoint=self.otlp_endpoint,
                    headers=self._otlp_headers or None
                )
                self.logger.info("Using OTLP HTTP/protobuf exporters (e.g. Grafana Cloud)")
            elif GRPC_OTEL_AVAILABLE:
                # gRPC (local/self-hosted)
                otlp_span_exporter = GrpcOTLPSpanExporter(
                    endpoint=self.otlp_endpoint,
                    insecure=self.insecure
                )
                otlp_metric_exporter = GrpcOTLPMetricExporter(
                    endpoint=self.otlp_endpoint,
                    insecure=self.insecure
                )
                otlp_log_exporter = GrpcOTLPLogExporter(
                    endpoint=self.otlp_endpoint,
                    insecure=self.insecure
                )
                self.logger.info("Using OTLP gRPC exporters")
            else:
                self.logger.error(
                    "OTLP protocol is http/protobuf but opentelemetry-exporter-otlp-proto-http "
                    "is not installed; install it for Grafana Cloud support."
                )
                return False
            
            # Initialize TracerProvider
            self._tracer_provider = TracerProvider(resource=resource)
            trace.set_tracer_provider(self._tracer_provider)
            span_processor = BatchSpanProcessor(otlp_span_exporter)
            self._tracer_provider.add_span_processor(span_processor)
            
            # Initialize MeterProvider
            metric_reader = PeriodicExportingMetricReader(
                otlp_metric_exporter,
                export_interval_millis=5000  # Export every 5 seconds
            )
            self._meter_provider = MeterProvider(
                resource=resource,
                metric_readers=[metric_reader]
            )
            metrics.set_meter_provider(self._meter_provider)
            
            # Initialize LoggerProvider
            log_processor = BatchLogRecordProcessor(otlp_log_exporter)
            self._logger_provider = LoggerProvider(
                resource=resource,
                log_record_processors=[log_processor]
            )
            _logs.set_logger_provider(self._logger_provider)
            
            self._initialized = True
            self.logger.info(
                f"OpenTelemetry SDK initialized: service={self.service_name}, "
                f"endpoint={self.otlp_endpoint}"
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenTelemetry SDK: {e}", exc_info=True)
            return False
    
    def instrument_logging(self) -> bool:
        """
        Instrument Python logging for automatic log-to-trace correlation.
        
        Returns:
            True if instrumentation successful
        """
        if not OTEL_AVAILABLE or not LoggingInstrumentor:
            self.logger.warning("LoggingInstrumentor not available")
            return False
        
        try:
            LoggingInstrumentor().instrument()
            self.logger.info("Logging instrumentation enabled")
            return True
        except Exception as e:
            self.logger.error(f"Failed to instrument logging: {e}", exc_info=True)
            return False
    
    def instrument_fastapi(self, app) -> bool:
        """
        Instrument FastAPI application for automatic span creation.
        
        Args:
            app: FastAPI application instance
        
        Returns:
            True if instrumentation successful
        """
        if not OTEL_AVAILABLE or not FastAPIInstrumentor:
            self.logger.warning("FastAPIInstrumentor not available")
            return False
        
        try:
            FastAPIInstrumentor.instrument_app(app)
            self.logger.info("FastAPI instrumentation enabled")
            return True
        except Exception as e:
            self.logger.error(f"Failed to instrument FastAPI: {e}", exc_info=True)
            return False
    
    def get_tracer(self, name: str):
        """Get tracer instance."""
        if not self._tracer_provider:
            return trace.NoOpTracer()
        return trace.get_tracer(name)
    
    def get_meter(self, name: str):
        """Get meter instance."""
        if not self._meter_provider:
            return metrics.NoOpMeter()
        return metrics.get_meter(name)
    
    def is_initialized(self) -> bool:
        """Check if SDK is initialized."""
        return self._initialized
    
    def shutdown(self):
        """Shutdown OpenTelemetry SDK."""
        try:
            if self._tracer_provider:
                self._tracer_provider.shutdown()
            if self._meter_provider:
                self._meter_provider.shutdown()
            if self._logger_provider:
                self._logger_provider.shutdown()
            self._initialized = False
            self.logger.info("OpenTelemetry SDK shut down")
        except Exception as e:
            self.logger.error(f"Failed to shutdown OpenTelemetry SDK: {e}", exc_info=True)
