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
        self.arango_adapter: Optional[Any] = None  # ArangoAdapter
        self.arango_graph_adapter: Optional[Any] = None  # ArangoGraphAdapter
        self.meilisearch_adapter: Optional[MeilisearchAdapter] = None
        self.supabase_adapter: Optional[SupabaseAdapter] = None
        self.gcs_adapter: Optional[GCSAdapter] = None
        self.supabase_file_adapter: Optional[SupabaseFileAdapter] = None
        
        # Layer 0: Parsing Adapters
        self.kreuzberg_adapter: Optional[KreuzbergAdapter] = None
        self.mainframe_adapter: Optional[MainframeProcessingAdapter] = None
        # Other parsing adapters (PDF, Word, Excel, etc.) will be added when available
        
        # Layer 0: Ingestion Adapters
        self.upload_adapter: Optional[Any] = None
        self.edi_adapter: Optional[Any] = None
        self.api_adapter: Optional[Any] = None
        
        # Layer 1: Infrastructure Abstractions
        self.state_abstraction: Optional[StateManagementAbstraction] = None
        self.service_discovery_abstraction: Optional[ServiceDiscoveryAbstraction] = None
        self.semantic_search_abstraction: Optional[SemanticSearchAbstraction] = None
        self.knowledge_discovery_abstraction: Optional[Any] = None  # KnowledgeDiscoveryAbstraction
        self.auth_abstraction: Optional[AuthAbstraction] = None
        self.tenant_abstraction: Optional[TenantAbstraction] = None
        self.file_storage_abstraction: Optional[FileStorageAbstraction] = None
        
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
        
        # Layer 1: Ingestion Abstractions
        self.ingestion_abstraction: Optional[Any] = None  # Will import IngestionAbstraction when needed
        
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
        from config.env_contract import get_env_contract
        env = get_env_contract()

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
        

        # Meilisearch adapter
        meilisearch_host = self.config.get("meilisearch_host") or "meilisearch"
        meilisearch_port = self.config.get("meilisearch_port") or 7700
        meilisearch_key = self.config.get("meilisearch_key") or (getattr(env, "MEILI_MASTER_KEY", None) if hasattr(env, "MEILI_MASTER_KEY") else None)
        self.meilisearch_adapter = MeilisearchAdapter(
            host=meilisearch_host,
            port=meilisearch_port,
            api_key=meilisearch_key
        )
        if self.meilisearch_adapter.connect():
            self.logger.info("Meilisearch adapter created")
        else:
            self.logger.warning("Meilisearch adapter connection failed")
        
        # Supabase adapter (with fallback pattern matching original ConfigAdapter)
        from config.config_helper import (
            get_supabase_url,
            get_supabase_anon_key,
            get_supabase_service_key
        )
        from config.env_contract import get_env_contract
        env = get_env_contract()
        
        # Use helper functions that support fallback patterns and .env.secrets
        supabase_url = (
            self.config.get("supabase_url") or
            get_supabase_url() or
            (getattr(env, "SUPABASE_URL", None) if hasattr(env, "SUPABASE_URL") else None)
        )
        supabase_anon_key = (
            self.config.get("supabase_anon_key") or
            get_supabase_anon_key() or
            (getattr(env, "SUPABASE_ANON_KEY", None) if hasattr(env, "SUPABASE_ANON_KEY") else None)
        )
        supabase_service_key = (
            self.config.get("supabase_service_key") or
            get_supabase_service_key() or
            (getattr(env, "SUPABASE_SERVICE_KEY", None) if hasattr(env, "SUPABASE_SERVICE_KEY") else None)
        )
        supabase_jwks_url = self.config.get("supabase_jwks_url") or (getattr(env, "SUPABASE_JWKS_URL", None) if hasattr(env, "SUPABASE_JWKS_URL") else None)
        supabase_jwt_issuer = self.config.get("supabase_jwt_issuer") or (getattr(env, "SUPABASE_JWT_ISSUER", None) if hasattr(env, "SUPABASE_JWT_ISSUER") else None)
        if supabase_url and supabase_anon_key:
            self.supabase_adapter = SupabaseAdapter(
                url=supabase_url,
                anon_key=supabase_anon_key,
                service_key=supabase_service_key,
                jwks_url=supabase_jwks_url,
                jwt_issuer=supabase_jwt_issuer
            )
            self.logger.info("Supabase adapter created")
        else:
            self.logger.warning("Supabase configuration not provided, Supabase adapter not created")
        
        # GCS adapter (with fallback pattern matching original ConfigAdapter)
        from config.config_helper import (
            get_gcs_project_id,
            get_gcs_bucket_name,
            get_gcs_credentials_json
        )
        
        gcs_project_id = (
            self.config.get("gcs_project_id") or
            get_gcs_project_id() or
            (getattr(env, "GCS_PROJECT_ID", None) if hasattr(env, "GCS_PROJECT_ID") else None)
        )
        gcs_bucket_name = (
            self.config.get("gcs_bucket_name") or
            get_gcs_bucket_name() or
            (getattr(env, "GCS_BUCKET_NAME", None) if hasattr(env, "GCS_BUCKET_NAME") else None)
        )
        gcs_credentials_json = (
            self.config.get("gcs_credentials_json") or
            get_gcs_credentials_json() or
            (getattr(env, "GCS_CREDENTIALS_JSON", None) if hasattr(env, "GCS_CREDENTIALS_JSON") else None)
        )
        if gcs_project_id and gcs_bucket_name:
            try:
                self.gcs_adapter = GCSAdapter(
                    project_id=gcs_project_id,
                    bucket_name=gcs_bucket_name,
                    credentials_json=gcs_credentials_json
                )
                self.logger.info("GCS adapter created")
            except ImportError as e:
                self.logger.warning(f"GCS adapter not created (missing dependencies): {e}")
                self.gcs_adapter = None
            except Exception as e:
                self.logger.warning(f"GCS adapter creation failed: {e}")
                self.gcs_adapter = None
        else:
            self.logger.warning("GCS configuration not provided, GCS adapter not created")
        
        # Supabase File adapter
        if supabase_url and supabase_service_key:
            self.supabase_file_adapter = SupabaseFileAdapter(
                url=supabase_url,
                service_key=supabase_service_key
            )
            await self.supabase_file_adapter.connect()
            self.logger.info("Supabase File adapter created")
        else:
            self.logger.warning("Supabase File adapter not created (missing URL or service key)")
        
        # Mainframe adapter (will be created in _create_abstractions after State Surface is available)
        
        # ArangoDB adapter
        from config.env_contract import get_env_contract
        env = get_env_contract()
        
        arango_url = (
            self.config.get("arango_url") or
            (getattr(env, "ARANGO_URL", None) if hasattr(env, "ARANGO_URL") else None) or
            "http://localhost:8529"
        )
        arango_username = (
            self.config.get("arango_username") or
            (getattr(env, "ARANGO_USERNAME", None) if hasattr(env, "ARANGO_USERNAME") else None) or
            "root"
        )
        arango_password = (
            self.config.get("arango_password") or
            (getattr(env, "ARANGO_ROOT_PASSWORD", None) if hasattr(env, "ARANGO_ROOT_PASSWORD") else None) or
            ""
        )
        arango_database = (
            self.config.get("arango_database") or
            (getattr(env, "ARANGO_DATABASE", None) if hasattr(env, "ARANGO_DATABASE") else None) or
            "symphainy_platform"
        )
        
        if arango_url:
            from .adapters.arango_adapter import ArangoAdapter
            from .adapters.arango_graph_adapter import ArangoGraphAdapter
            
            self.arango_adapter = ArangoAdapter(
                url=arango_url,
                username=arango_username,
                password=arango_password,
                database=arango_database
            )
            if await self.arango_adapter.connect():
                self.logger.info("ArangoDB adapter created")
                
                # Create ArangoDB Graph adapter
                self.arango_graph_adapter = ArangoGraphAdapter(self.arango_adapter)
                self.logger.info("ArangoDB Graph adapter created")
            else:
                self.logger.warning("ArangoDB adapter connection failed")
        else:
            self.logger.warning("ArangoDB configuration not provided, ArangoDB adapter not created")
    
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
        
        # Knowledge discovery abstraction
        if self.meilisearch_adapter:
            from .abstractions.knowledge_discovery_abstraction import KnowledgeDiscoveryAbstraction
            self.knowledge_discovery_abstraction = KnowledgeDiscoveryAbstraction(
                meilisearch_adapter=self.meilisearch_adapter,
                arango_graph_adapter=self.arango_graph_adapter,
                arango_adapter=self.arango_adapter
            )
            self.logger.info("Knowledge discovery abstraction created")
        else:
            self.logger.warning("Knowledge discovery abstraction not created (Meilisearch adapter missing)")
        
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
        from config.config_helper import get_gcs_bucket_name
        from config.env_contract import get_env_contract
        env = get_env_contract()
        
        gcs_bucket_name = (
            self.config.get("gcs_bucket_name") or
            get_gcs_bucket_name() or
            (getattr(env, "GCS_BUCKET_NAME", None) if hasattr(env, "GCS_BUCKET_NAME") else None)
        )
        if self.gcs_adapter and self.supabase_file_adapter and gcs_bucket_name:
            self.file_storage_abstraction = FileStorageAbstraction(
                gcs_adapter=self.gcs_adapter,
                supabase_file_adapter=self.supabase_file_adapter,
                bucket_name=gcs_bucket_name
            )
            self.logger.info("File storage abstraction created")
        else:
            self.logger.warning("File storage abstraction not created (missing adapters or bucket name)")
        
        # Ingestion adapters (created after file_storage_abstraction is available)
        from .adapters.upload_adapter import UploadAdapter
        from .adapters.edi_adapter import EDIAdapter
        from .adapters.api_adapter import APIAdapter
        
        if self.file_storage_abstraction:
            # Upload adapter
            self.upload_adapter = UploadAdapter(
                file_storage_abstraction=self.file_storage_abstraction
            )
            self.logger.info("Upload adapter created")
            
            # EDI adapter (Phase 2)
            edi_config = self.config.get("edi", {})
            self.edi_adapter = EDIAdapter(
                file_storage_abstraction=self.file_storage_abstraction,
                edi_config=edi_config if edi_config else None
            )
            self.logger.info("EDI adapter created")
            
            # API adapter (Phase 3)
            self.api_adapter = APIAdapter(
                file_storage_abstraction=self.file_storage_abstraction
            )
            self.logger.info("API adapter created")
        else:
            self.logger.warning("Ingestion adapters not created (file storage abstraction missing)")
        
        # Ingestion abstraction (created after adapters are available)
        from .abstractions.ingestion_abstraction import IngestionAbstraction
        self.ingestion_abstraction = IngestionAbstraction(
            upload_adapter=self.upload_adapter,
            edi_adapter=self.edi_adapter,
            api_adapter=self.api_adapter
        )
        self.logger.info("Ingestion abstraction created")
        
        
        # Create State Surface for parsing abstractions (they need it for file retrieval)
        # Note: This creates a temporary State Surface - the actual one is created in Runtime
        # For tests: if no state_abstraction, use in-memory mode
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
    
    def set_state_surface(self, state_surface: Any):
        """
        Set State Surface for all parsing abstractions.
        
        This is called after Runtime creates State Surface to ensure all abstractions
        use the same State Surface instance (the one from Runtime).
        
        Args:
            state_surface: State Surface instance from Runtime
        """
        # Update all abstractions with State Surface
        if self.kreuzberg_processing_abstraction:
            self.kreuzberg_processing_abstraction.state_surface = state_surface
        
        if self.mainframe_adapter:
            self.mainframe_adapter.state_surface = state_surface
        if self.mainframe_processing_abstraction:
            self.mainframe_processing_abstraction.state_surface = state_surface
        
        if self.pdf_processing_abstraction:
            self.pdf_processing_abstraction.state_surface = state_surface
        if self.word_processing_abstraction:
            self.word_processing_abstraction.state_surface = state_surface
        if self.excel_processing_abstraction:
            self.excel_processing_abstraction.state_surface = state_surface
        if self.csv_processing_abstraction:
            self.csv_processing_abstraction.state_surface = state_surface
        if self.json_processing_abstraction:
            self.json_processing_abstraction.state_surface = state_surface
        if self.text_processing_abstraction:
            self.text_processing_abstraction.state_surface = state_surface
        if self.image_processing_abstraction:
            self.image_processing_abstraction.state_surface = state_surface
        if self.html_processing_abstraction:
            self.html_processing_abstraction.state_surface = state_surface
        
        self.logger.info("✅ State Surface set for all parsing abstractions")
    
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
    
    def get_ingestion_abstraction(self) -> Optional[Any]:
        """
        Get ingestion abstraction (for Content Realm Ingestion Service).
        
        Returns:
            Optional[IngestionAbstraction]: Ingestion abstraction or None
        """
        return self.ingestion_abstraction


    def get_supabase_file_adapter(self) -> Optional[SupabaseFileAdapter]:
        """
        Get Supabase file adapter (for File Metadata Service).
        """
        return self.supabase_file_adapter