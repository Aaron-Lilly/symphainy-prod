"""
Public Works Foundation Service

Orchestrates all infrastructure adapters and abstractions.
This is Layer 4 of the 5-layer architecture.

WHAT (Foundation Role): I provide infrastructure capabilities to all platform components
HOW (Foundation Implementation): I use 5-layer architecture with dependency injection

Rules:
- Foundations never call realms
- Foundations never reason
- Foundations are deterministic
"""

from typing import Dict, Any, Optional
from utilities import get_logger

from .adapters.redis_adapter import RedisAdapter
from .adapters.consul_adapter import ConsulAdapter
from .adapters.kreuzberg_adapter import KreuzbergAdapter
from .adapters.mainframe_parsing.unified_adapter import MainframeProcessingAdapter
from .abstractions.state_abstraction import StateManagementAbstraction
from .abstractions.service_discovery_abstraction import ServiceDiscoveryAbstraction
from .abstractions.pdf_processing_abstraction import PdfProcessingAbstraction
from .abstractions.word_processing_abstraction import WordProcessingAbstraction
from .abstractions.excel_processing_abstraction import ExcelProcessingAbstraction
from .abstractions.csv_processing_abstraction import CsvProcessingAbstraction
from .abstractions.json_processing_abstraction import JsonProcessingAbstraction
from .abstractions.text_processing_abstraction import TextProcessingAbstraction
from .abstractions.image_processing_abstraction import ImageProcessingAbstraction
from .abstractions.html_processing_abstraction import HtmlProcessingAbstraction
from .abstractions.kreuzberg_processing_abstraction import KreuzbergProcessingAbstraction
from .abstractions.mainframe_processing_abstraction import MainframeProcessingAbstraction
from .protocols.state_protocol import StateManagementProtocol
from .protocols.service_discovery_protocol import ServiceDiscoveryProtocol
from .protocols.semantic_search_protocol import SemanticSearchProtocol
from .protocols.auth_protocol import AuthenticationProtocol, TenancyProtocol
from .protocols.file_storage_protocol import FileStorageProtocol

# Layer 0: Additional Adapters
from .adapters.meilisearch_adapter import MeilisearchAdapter
from .adapters.supabase_adapter import SupabaseAdapter
from .adapters.gcs_adapter import GCSAdapter
from .adapters.supabase_file_adapter import SupabaseFileAdapter

# Layer 1: Additional Abstractions
from .abstractions.semantic_search_abstraction import SemanticSearchAbstraction
from .abstractions.auth_abstraction import AuthAbstraction
from .abstractions.tenant_abstraction import TenantAbstraction
from .abstractions.file_storage_abstraction import FileStorageAbstraction

class PublicWorksFoundationService:
    """
    Public Works Foundation Service - 5-Layer Architecture
    
    This service implements the 5-layer architecture pattern,
    providing infrastructure capabilities to all platform components.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Public Works Foundation Service.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.logger = get_logger(self.__class__.__name__)
        
        # Layer 0: Infrastructure Adapters
        self.redis_adapter: Optional[RedisAdapter] = None
        self.consul_adapter: Optional[ConsulAdapter] = None
        # ArangoDB adapter will be added when needed
        
        # Layer 0: Parsing Adapters
        self.kreuzberg_adapter: Optional[KreuzbergAdapter] = None
        self.mainframe_adapter: Optional[MainframeProcessingAdapter] = None
        # Other parsing adapters (PDF, Word, Excel, etc.) will be added when available
        
        # Layer 1: Infrastructure Abstractions
        self.state_abstraction: Optional[StateManagementAbstraction] = None
        self.service_discovery_abstraction: Optional[ServiceDiscoveryAbstraction] = None
        
        # Layer 1: Parsing Abstractions
        self.pdf_processing_abstraction: Optional[PdfProcessingAbstraction] = None
        self.word_processing_abstraction: Optional[WordProcessingAbstraction] = None
        self.excel_processing_abstraction: Optional[ExcelProcessingAbstraction] = None
        self.csv_processing_abstraction: Optional[CsvProcessingAbstraction] = None
        self.json_processing_abstraction: Optional[JsonProcessingAbstraction] = None
        self.text_processing_abstraction: Optional[TextProcessingAbstraction] = None
        self.image_processing_abstraction: Optional[ImageProcessingAbstraction] = None
        self.html_processing_abstraction: Optional[HtmlProcessingAbstraction] = None
        self.kreuzberg_processing_abstraction: Optional[KreuzbergProcessingAbstraction] = None
        self.mainframe_processing_abstraction: Optional[MainframeProcessingAbstraction] = None
        
        # Initialization flag
        self._initialized = False
    
    async def initialize(self) -> bool:
        """
        Initialize all infrastructure components.
        
        Returns:
            bool: True if initialization successful
        """
        if self._initialized:
            self.logger.warning("Public Works Foundation already initialized")
            return True
        
        try:
            self.logger.info("Initializing Public Works Foundation...")
            
            # Layer 0: Create adapters
            await self._create_adapters()
            
            # Layer 1: Create abstractions
            await self._create_abstractions()
            
            self._initialized = True
            self.logger.info("Public Works Foundation initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Public Works Foundation: {e}", exc_info=True)
            return False
    
    async def _create_adapters(self):
        """Create all infrastructure adapters (Layer 0)."""
        self.logger.info("Creating infrastructure adapters...")
        
        # Redis adapter
        redis_config = self.config.get("redis", {})
        if redis_config:
            self.redis_adapter = RedisAdapter(
                host=redis_config.get("host", "localhost"),
                port=redis_config.get("port", 6379),
                db=redis_config.get("db", 0),
                password=redis_config.get("password")
            )
            await self.redis_adapter.connect()
            self.logger.info("Redis adapter created")
        else:
            self.logger.warning("Redis configuration not provided, Redis adapter not created")
        
        # Consul adapter
        consul_config = self.config.get("consul", {})
        if consul_config:
            self.consul_adapter = ConsulAdapter(
                host=consul_config.get("host", "localhost"),
                port=consul_config.get("port", 8500),
                token=consul_config.get("token")
            )
            if self.consul_adapter.connect():
                self.logger.info("Consul adapter created")
            else:
                self.logger.warning("Consul adapter connection failed")
        else:
            self.logger.warning("Consul configuration not provided, Consul adapter not created")
        
        # Parsing adapters
        kreuzberg_config = self.config.get("kreuzberg", {})
        if kreuzberg_config:
            self.kreuzberg_adapter = KreuzbergAdapter(
                api_key=kreuzberg_config.get("api_key"),
                base_url=kreuzberg_config.get("base_url", "http://localhost:8080")
            )
            self.logger.info("Kreuzberg adapter created")
        else:
            self.logger.info("Kreuzberg configuration not provided, Kreuzberg adapter not created")
        
        # Mainframe adapter (will be created in _create_abstractions after State Surface is available)
        
        # ArangoDB adapter will be added when needed
    
    async def _create_abstractions(self):
        """Create all infrastructure abstractions (Layer 1)."""
        self.logger.info("Creating infrastructure abstractions...")
        
        # State management abstraction
        self.state_abstraction = StateManagementAbstraction(
            redis_adapter=self.redis_adapter,
            arango_adapter=None  # Will be added when ArangoDB adapter is ready
        )
        self.logger.info("State management abstraction created")
        
        # Service discovery abstraction
        self.service_discovery_abstraction = ServiceDiscoveryAbstraction(
            consul_adapter=self.consul_adapter
        )
        self.logger.info("Service discovery abstraction created")

        
        # Semantic search abstraction
        if self.meilisearch_adapter:
            self.semantic_search_abstraction = SemanticSearchAbstraction(
                meilisearch_adapter=self.meilisearch_adapter
            )
            self.logger.info("Semantic search abstraction created")
        else:
            self.logger.warning("Semantic search abstraction not created (Meilisearch adapter missing)")
        
        # Auth abstraction
        if self.supabase_adapter:
            self.auth_abstraction = AuthAbstraction(
                supabase_adapter=self.supabase_adapter
            )
            self.logger.info("Auth abstraction created")
        else:
            self.logger.warning("Auth abstraction not created (Supabase adapter missing)")
        
        # Tenant abstraction
        if self.supabase_adapter:
            self.tenant_abstraction = TenantAbstraction(
                supabase_adapter=self.supabase_adapter,
                redis_adapter=self.redis_adapter  # For caching
            )
            self.logger.info("Tenant abstraction created")
        else:
            self.logger.warning("Tenant abstraction not created (Supabase adapter missing)")
        
        # File storage abstraction
        gcs_bucket_name = self.config.get("gcs_bucket_name") or (self.env.GCS_BUCKET_NAME if hasattr(self, "env") else None)
        if self.gcs_adapter and self.supabase_file_adapter and gcs_bucket_name:
            self.file_storage_abstraction = FileStorageAbstraction(
                gcs_adapter=self.gcs_adapter,
                supabase_file_adapter=self.supabase_file_adapter,
                bucket_name=gcs_bucket_name
            )
            self.logger.info("File storage abstraction created")
        else:
            self.logger.warning("File storage abstraction not created (missing adapters or bucket name)")
        
        
        # Create State Surface for parsing abstractions (they need it for file retrieval)
        # Note: This creates a temporary State Surface - the actual one is created in Runtime
        from symphainy_platform.runtime.state_surface import StateSurface
        temp_state_surface = StateSurface(
            state_abstraction=self.state_abstraction,
            use_memory=(self.state_abstraction is None)
        )
        
        # Parsing abstractions
        self.logger.info("Creating parsing abstractions...")
        
        # Kreuzberg abstraction
        if self.kreuzberg_adapter:
            self.kreuzberg_processing_abstraction = KreuzbergProcessingAbstraction(
                kreuzberg_adapter=self.kreuzberg_adapter,
                state_surface=temp_state_surface
            )
            self.logger.info("Kreuzberg processing abstraction created")
        
        # Mainframe adapter and abstraction
        cobrix_config = self.config.get("cobrix", {})
        cobrix_service_url = cobrix_config.get("service_url") if cobrix_config else None
        
        self.mainframe_adapter = MainframeProcessingAdapter(
            state_surface=temp_state_surface,
            cobrix_service_url=cobrix_service_url,
            prefer_cobrix=cobrix_config.get("prefer_cobrix", False) if cobrix_config else False
        )
        
        self.mainframe_processing_abstraction = MainframeProcessingAbstraction(
            mainframe_adapter=self.mainframe_adapter,
            state_surface=temp_state_surface
        )
        self.logger.info("Mainframe processing abstraction created")
        
        # Other parsing abstractions (ready for adapters when available)
        self.pdf_processing_abstraction = PdfProcessingAbstraction(
            pdf_adapter=None,  # Will be set when adapter is available
            state_surface=temp_state_surface
        )
        
        self.word_processing_abstraction = WordProcessingAbstraction(
            word_adapter=None,  # Will be set when adapter is available
            state_surface=temp_state_surface
        )
        
        self.excel_processing_abstraction = ExcelProcessingAbstraction(
            excel_adapter=None,  # Will be set when adapter is available
            state_surface=temp_state_surface
        )
        
        self.csv_processing_abstraction = CsvProcessingAbstraction(
            csv_adapter=None,  # Will be set when adapter is available
            state_surface=temp_state_surface
        )
        
        self.json_processing_abstraction = JsonProcessingAbstraction(
            json_adapter=None,  # Will be set when adapter is available
            state_surface=temp_state_surface
        )
        
        self.text_processing_abstraction = TextProcessingAbstraction(
            text_adapter=None,  # Can work without adapter
            state_surface=temp_state_surface
        )
        
        self.image_processing_abstraction = ImageProcessingAbstraction(
            ocr_adapter=None,  # Will be set when adapter is available
            state_surface=temp_state_surface
        )
        
        self.html_processing_abstraction = HtmlProcessingAbstraction(
            html_adapter=None,  # Will be set when adapter is available
            state_surface=temp_state_surface
        )
        
        self.logger.info("Parsing abstractions created (adapters to be connected when available)")
    
    async def shutdown(self):
        """Shutdown all infrastructure components."""
        self.logger.info("Shutting down Public Works Foundation...")
        
        if self.redis_adapter:
            await self.redis_adapter.disconnect()
        
        if self.consul_adapter:
            self.consul_adapter.disconnect()
        
        self._initialized = False
        self.logger.info("Public Works Foundation shut down")
    
    # ============================================================================
    # Abstraction Access Methods
    # ============================================================================
    
    def get_state_abstraction(self) -> Optional[StateManagementProtocol]:
        """
        Get state management abstraction.
        
        Returns:
            Optional[StateManagementProtocol]: State management abstraction or None
        """
        return self.state_abstraction
    
    def get_service_discovery_abstraction(self) -> Optional[ServiceDiscoveryProtocol]:
        """
        Get service discovery abstraction.
        
        Returns:
            Optional[ServiceDiscoveryProtocol]: Service discovery abstraction or None
        """
        return self.service_discovery_abstraction
    
    def is_initialized(self) -> bool:
        """Check if foundation is initialized."""
        return self._initialized
    
    # ============================================================================
    # Parsing Abstraction Access Methods
    # ============================================================================
    
    def get_pdf_processing_abstraction(self) -> Optional[PdfProcessingAbstraction]:
        """Get PDF processing abstraction."""
        return self.pdf_processing_abstraction
    
    def get_word_processing_abstraction(self) -> Optional[WordProcessingAbstraction]:
        """Get Word processing abstraction."""
        return self.word_processing_abstraction
    
    def get_excel_processing_abstraction(self) -> Optional[ExcelProcessingAbstraction]:
        """Get Excel processing abstraction."""
        return self.excel_processing_abstraction
    
    def get_csv_processing_abstraction(self) -> Optional[CsvProcessingAbstraction]:
        """Get CSV processing abstraction."""
        return self.csv_processing_abstraction
    
    def get_json_processing_abstraction(self) -> Optional[JsonProcessingAbstraction]:
        """Get JSON processing abstraction."""
        return self.json_processing_abstraction
    
    def get_text_processing_abstraction(self) -> Optional[TextProcessingAbstraction]:
        """Get Text processing abstraction."""
        return self.text_processing_abstraction
    
    def get_image_processing_abstraction(self) -> Optional[ImageProcessingAbstraction]:
        """Get Image processing abstraction."""
        return self.image_processing_abstraction
    
    def get_html_processing_abstraction(self) -> Optional[HtmlProcessingAbstraction]:
        """Get HTML processing abstraction."""
        return self.html_processing_abstraction
    
    def get_kreuzberg_processing_abstraction(self) -> Optional[KreuzbergProcessingAbstraction]:
        """Get Kreuzberg processing abstraction."""
        return self.kreuzberg_processing_abstraction
    
    def get_mainframe_processing_abstraction(self) -> Optional[MainframeProcessingAbstraction]:
        """Get Mainframe processing abstraction."""
        return self.mainframe_processing_abstraction
    # ============================================================================
    # Smart City Abstraction Access Methods
    # ============================================================================
    
    def get_semantic_search_abstraction(self) -> Optional[SemanticSearchProtocol]:
        """
        Get semantic search abstraction (for Librarian service).
        
        Returns:
            Optional[SemanticSearchProtocol]: Semantic search abstraction or None
        """
        return self.semantic_search_abstraction
    
    def get_auth_abstraction(self) -> Optional[AuthenticationProtocol]:
        """
        Get authentication abstraction (for Security Guard service).
        
        Returns:
            Optional[AuthenticationProtocol]: Authentication abstraction or None
        """
        return self.auth_abstraction
    
    def get_tenant_abstraction(self) -> Optional[TenancyProtocol]:
        """
        Get tenant abstraction (for Security Guard service).
        
        Returns:
            Optional[TenancyProtocol]: Tenant abstraction or None
        """
        return self.tenant_abstraction
    
    def get_file_storage_abstraction(self) -> Optional[FileStorageProtocol]:
        """
        Get file storage abstraction (for Data Steward service).
        
        Returns:
            Optional[FileStorageProtocol]: File storage abstraction or None
        """
        return self.file_storage_abstraction

