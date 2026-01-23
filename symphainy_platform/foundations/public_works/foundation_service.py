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
from .abstractions.artifact_storage_abstraction import ArtifactStorageAbstraction
from .abstractions.visual_generation_abstraction import VisualGenerationAbstraction

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
        self.csv_adapter: Optional[Any] = None  # CsvProcessingAdapter
        self.excel_adapter: Optional[Any] = None  # ExcelProcessingAdapter
        self.pdf_adapter: Optional[Any] = None  # PdfProcessingAdapter
        self.word_adapter: Optional[Any] = None  # WordProcessingAdapter
        self.html_adapter: Optional[Any] = None  # HtmlProcessingAdapter
        self.image_adapter: Optional[Any] = None  # ImageProcessingAdapter
        self.json_adapter: Optional[Any] = None  # JsonProcessingAdapter
        
        # Layer 0: Ingestion Adapters
        self.upload_adapter: Optional[Any] = None
        self.edi_adapter: Optional[Any] = None
        self.api_adapter: Optional[Any] = None
        
        # Layer 0: Visual Generation Adapter
        self.visual_generation_adapter: Optional[Any] = None  # VisualGenerationAdapter
        
        # Layer 0: LLM Adapters
        self.openai_adapter: Optional[Any] = None  # OpenAIAdapter
        self.huggingface_adapter: Optional[Any] = None  # HuggingFaceAdapter
        
        # Layer 0: DuckDB Adapter
        self.duckdb_adapter: Optional[Any] = None  # DuckDBAdapter
        
        # Layer 1: Infrastructure Abstractions
        self.state_abstraction: Optional[StateManagementAbstraction] = None
        self.service_discovery_abstraction: Optional[ServiceDiscoveryAbstraction] = None
        self.semantic_search_abstraction: Optional[SemanticSearchAbstraction] = None
        self.knowledge_discovery_abstraction: Optional[Any] = None  # KnowledgeDiscoveryAbstraction
        self.semantic_data_abstraction: Optional[Any] = None  # SemanticDataAbstraction
        self.deterministic_compute_abstraction: Optional[Any] = None  # DeterministicComputeAbstraction
        self.registry_abstraction: Optional[Any] = None  # RegistryAbstraction
        self.auth_abstraction: Optional[AuthAbstraction] = None
        self.tenant_abstraction: Optional[TenantAbstraction] = None
        self.file_storage_abstraction: Optional[FileStorageAbstraction] = None
        self.artifact_storage_abstraction: Optional[ArtifactStorageAbstraction] = None
        self.event_publisher_abstraction: Optional[Any] = None  # EventPublisherAbstraction
        
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
        from symphainy_platform.config.env_contract import get_env_contract
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
        
        # Create parsing adapters (CSV, Excel, PDF, Word, HTML, Image, JSON)
        from .adapters.csv_adapter import CsvProcessingAdapter
        from .adapters.excel_adapter import ExcelProcessingAdapter
        from .adapters.pdf_adapter import PdfProcessingAdapter
        from .adapters.word_adapter import WordProcessingAdapter
        from .adapters.html_adapter import HtmlProcessingAdapter
        from .adapters.image_adapter import ImageProcessingAdapter
        from .adapters.json_adapter import JsonProcessingAdapter
        
        self.csv_adapter = CsvProcessingAdapter()
        self.logger.info("CSV adapter created")
        
        self.excel_adapter = ExcelProcessingAdapter()
        self.logger.info("Excel adapter created")
        
        self.pdf_adapter = PdfProcessingAdapter()
        self.logger.info("PDF adapter created")
        
        self.word_adapter = WordProcessingAdapter()
        self.logger.info("Word adapter created")
        
        self.html_adapter = HtmlProcessingAdapter()
        self.logger.info("HTML adapter created")
        
        self.image_adapter = ImageProcessingAdapter()
        self.logger.info("Image/OCR adapter created")
        
        self.json_adapter = JsonProcessingAdapter()
        self.logger.info("JSON adapter created")
        

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
        from symphainy_platform.config.config_helper import (
            get_supabase_url,
            get_supabase_anon_key,
            get_supabase_service_key
        )
        from symphainy_platform.config.env_contract import get_env_contract
        env = get_env_contract()
        
        # Use helper functions that support fallback patterns and .env.secrets
        supabase_url = (
            self.config.get("supabase_url") or
            get_supabase_url() or
            (getattr(env, "SUPABASE_URL", None) if hasattr(env, "SUPABASE_URL") else None)
        )
        supabase_anon_key = (
            self.config.get("supabase_anon_key") or
            get_supabase_anon_key()
        )
        supabase_service_key = (
            self.config.get("supabase_service_key") or
            get_supabase_service_key()
        )
        supabase_jwks_url = self.config.get("supabase_jwks_url") or (getattr(env, "SUPABASE_JWKS_URL", None) if hasattr(env, "SUPABASE_JWKS_URL") else None)
        supabase_jwt_issuer = self.config.get("supabase_jwt_issuer") or (getattr(env, "SUPABASE_JWT_ISSUER", None) if hasattr(env, "SUPABASE_JWT_ISSUER") else None)
        
        # Debug logging for Supabase credential access
        self.logger.info(f"🔍 Supabase Configuration Check:")
        self.logger.info(f"   SUPABASE_URL: {'✅ Set' if supabase_url else '❌ Missing'}")
        self.logger.info(f"   SUPABASE_ANON_KEY: {'✅ Set' if supabase_anon_key else '❌ Missing'}")
        self.logger.info(f"   SUPABASE_SERVICE_KEY: {'✅ Set' if supabase_service_key else '❌ Missing'}")
        if supabase_service_key:
            # Log first 30 chars to verify it's being read (without exposing full key)
            key_preview = supabase_service_key[:30] + "..." if len(supabase_service_key) > 30 else supabase_service_key
            self.logger.info(f"   Service key preview: {key_preview}")
        
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
        from symphainy_platform.config.config_helper import (
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
        
        # Debug logging for credential access
        self.logger.info(f"🔍 GCS Configuration Check:")
        self.logger.info(f"   GCS_PROJECT_ID: {'✅ Set' if gcs_project_id else '❌ Missing'}")
        self.logger.info(f"   GCS_BUCKET_NAME: {'✅ Set' if gcs_bucket_name else '❌ Missing'}")
        self.logger.info(f"   GCS_CREDENTIALS_JSON: {'✅ Set' if gcs_credentials_json else '❌ Missing'}")
        if gcs_credentials_json:
            # Log first 50 chars to verify it's being read (without exposing full key)
            creds_preview = gcs_credentials_json[:50] + "..." if len(gcs_credentials_json) > 50 else gcs_credentials_json
            self.logger.info(f"   Credentials preview: {creds_preview}")
        
        # GCS adapter is REQUIRED for platform operation
        if not gcs_project_id or not gcs_bucket_name:
            raise RuntimeError(
                "GCS configuration is required for platform operation. "
                "Please provide GCS_PROJECT_ID and GCS_BUCKET_NAME environment variables."
            )
        
        try:
            self.gcs_adapter = GCSAdapter(
                project_id=gcs_project_id,
                bucket_name=gcs_bucket_name,
                credentials_json=gcs_credentials_json
            )
            self.logger.info("GCS adapter created")
        except ImportError as e:
            raise RuntimeError(
                f"GCS adapter dependencies not available: {e}. "
                "Please install: pip install google-cloud-storage google-auth"
            )
        except Exception as e:
            raise RuntimeError(
                f"GCS adapter creation failed: {e}. "
                "Please verify GCS credentials and configuration."
            )
        
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
        
        # Visual Generation adapter
        from .adapters.visual_generation_adapter import VisualGenerationAdapter
        self.visual_generation_adapter = VisualGenerationAdapter()
        self.logger.info("Visual Generation adapter created")
        
        # LLM Adapters (OpenAI and HuggingFace)
        from symphainy_platform.config.config_helper import (
            get_openai_api_key,
            get_huggingface_endpoint_url,
            get_huggingface_api_key
        )
        from symphainy_platform.config.env_contract import get_env_contract
        env = get_env_contract()
        
        # OpenAI adapter
        openai_api_key = (
            self.config.get("openai_api_key") or
            get_openai_api_key() or
            (getattr(env, "LLM_OPENAI_API_KEY", None) if hasattr(env, "LLM_OPENAI_API_KEY") else None) or
            (getattr(env, "OPENAI_API_KEY", None) if hasattr(env, "OPENAI_API_KEY") else None)
        )
        openai_base_url = (
            self.config.get("openai_base_url") or
            (getattr(env, "OPENAI_BASE_URL", None) if hasattr(env, "OPENAI_BASE_URL") else None)
        )
        
        if openai_api_key:
            from .adapters.openai_adapter import OpenAIAdapter
            try:
                # Create a simple config dict for the adapter
                openai_config = {
                    "LLM_OPENAI_API_KEY": openai_api_key,
                    "OPENAI_API_KEY": openai_api_key
                }
                self.openai_adapter = OpenAIAdapter(
                    api_key=openai_api_key,
                    base_url=openai_base_url,
                    config_adapter=openai_config
                )
                self.logger.info("✅ OpenAI adapter created")
            except Exception as e:
                self.logger.warning(f"OpenAI adapter creation failed: {e}")
        else:
            self.logger.warning("OpenAI API key not found, OpenAI adapter not created")
        
        # HuggingFace adapter
        hf_endpoint_url = (
            self.config.get("huggingface_endpoint_url") or
            get_huggingface_endpoint_url() or
            (getattr(env, "HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL", None) if hasattr(env, "HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL") else None)
        )
        hf_api_key = (
            self.config.get("huggingface_api_key") or
            get_huggingface_api_key() or
            (getattr(env, "HUGGINGFACE_EMBEDDINGS_API_KEY", None) if hasattr(env, "HUGGINGFACE_EMBEDDINGS_API_KEY") else None) or
            (getattr(env, "HUGGINGFACE_API_KEY", None) if hasattr(env, "HUGGINGFACE_API_KEY") else None)
        )
        
        if hf_endpoint_url and hf_api_key:
            from .adapters.huggingface_adapter import HuggingFaceAdapter
            try:
                # Create a simple config dict for the adapter
                hf_config = {
                    "HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL": hf_endpoint_url,
                    "HUGGINGFACE_EMBEDDINGS_API_KEY": hf_api_key,
                    "HUGGINGFACE_API_KEY": hf_api_key
                }
                self.huggingface_adapter = HuggingFaceAdapter(
                    endpoint_url=hf_endpoint_url,
                    api_key=hf_api_key,
                    config_adapter=hf_config
                )
                self.logger.info("✅ HuggingFace adapter created")
            except Exception as e:
                self.logger.warning(f"HuggingFace adapter creation failed: {e}")
        else:
            self.logger.warning("HuggingFace configuration not found, HuggingFace adapter not created")
        
        # Mainframe adapter (will be created in _create_abstractions after State Surface is available)
        
        # ArangoDB adapter
        from symphainy_platform.config.env_contract import get_env_contract
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
        
        # DuckDB adapter (for deterministic compute)
        await self._initialize_duckdb()
    
    async def _initialize_duckdb(self):
        """Initialize DuckDB adapter and abstraction."""
        from .adapters.duckdb_adapter import DuckDBAdapter
        from .abstractions.deterministic_compute_abstraction import DeterministicComputeAbstraction
        
        duckdb_config = self.config.get("duckdb", {})
        if duckdb_config:
            database_path = duckdb_config.get(
                "database_path",
                "/app/data/duckdb/main.duckdb"  # Default path
            )
            
            self.duckdb_adapter = DuckDBAdapter(
                database_path=database_path,
                read_only=duckdb_config.get("read_only", False)
            )
            
            # Connect
            if await self.duckdb_adapter.connect():
                self.logger.info(f"DuckDB adapter connected: {database_path}")
                
                # Create abstraction (file_storage_abstraction will be set later in _create_abstractions)
                self.deterministic_compute_abstraction = DeterministicComputeAbstraction(
                    duckdb_adapter=self.duckdb_adapter,
                    file_storage_abstraction=None  # Will be set later in _create_abstractions
                )
                
                # Initialize schema (create tables if needed)
                await self.deterministic_compute_abstraction.initialize_schema()
                
                self.logger.info("Deterministic Compute Abstraction created")
            else:
                self.logger.warning("DuckDB adapter connection failed")
                self.duckdb_adapter = None
                self.deterministic_compute_abstraction = None
        else:
            self.logger.info("DuckDB configuration not provided, DuckDB adapter not created")
            self.duckdb_adapter = None
            self.deterministic_compute_abstraction = None
    
    async def _create_abstractions(self):
        """Create all infrastructure abstractions (Layer 1)."""
        self.logger.info("Creating infrastructure abstractions...")
        
        # State management abstraction
        self.state_abstraction = StateManagementAbstraction(
            redis_adapter=self.redis_adapter,
            arango_adapter=self.arango_adapter  # ArangoDB adapter for durable state
        )
        self.logger.info("State management abstraction created")
        
        # Ensure required ArangoDB collections exist for state management
        if self.arango_adapter:
            await self._ensure_state_collections()
        
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
        
        # Knowledge discovery abstraction (REQUIRED for platform operation)
        # Make it optional for testing scenarios
        if not self.arango_adapter:
            self.logger.warning("ArangoDB adapter missing - knowledge discovery abstraction not created")
        elif not self.arango_graph_adapter:
            self.logger.warning("ArangoDB Graph adapter missing - knowledge discovery abstraction not created")
        else:
            from .abstractions.knowledge_discovery_abstraction import KnowledgeDiscoveryAbstraction
            self.knowledge_discovery_abstraction = KnowledgeDiscoveryAbstraction(
                meilisearch_adapter=self.meilisearch_adapter,  # Optional - can be None
                arango_graph_adapter=self.arango_graph_adapter,
                arango_adapter=self.arango_adapter
            )
            self.logger.info("Knowledge discovery abstraction created")
        
        # Semantic data abstraction (REQUIRED for platform operation)
        if not self.arango_adapter:
            raise RuntimeError("ArangoDB adapter is required for semantic data abstraction")
        
        from .abstractions.semantic_data_abstraction import SemanticDataAbstraction
        self.semantic_data_abstraction = SemanticDataAbstraction(
            arango_adapter=self.arango_adapter
        )
        self.logger.info("Semantic data abstraction created")
        
        # Deterministic compute abstraction (created after DuckDB adapter)
        # Note: DuckDB adapter is initialized in _create_adapters, but abstraction
        # needs file_storage_abstraction which is created here. So we update it here.
        if self.duckdb_adapter and self.deterministic_compute_abstraction:
            # Update abstraction with file_storage_abstraction (was None during initialization)
            self.deterministic_compute_abstraction.file_storage = self.file_storage_abstraction
            self.logger.info("Deterministic compute abstraction updated with file storage")
        elif not self.duckdb_adapter:
            self.logger.warning("Deterministic compute abstraction not created (DuckDB adapter missing)")
        
        # Auth abstraction
        if self.supabase_adapter:
            self.auth_abstraction = AuthAbstraction(
                supabase_adapter=self.supabase_adapter
            )
            self.logger.info("Auth abstraction created")
        else:
            self.logger.warning("Auth abstraction not created (Supabase adapter missing)")
        
        # Registry abstraction (for lineage, metadata, registry operations)
        if self.supabase_adapter:
            from .abstractions.registry_abstraction import RegistryAbstraction
            self.registry_abstraction = RegistryAbstraction(
                supabase_adapter=self.supabase_adapter
            )
            self.logger.info("Registry abstraction created")
        else:
            self.logger.warning("Registry abstraction not created (Supabase adapter missing)")
        
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
        from symphainy_platform.config.config_helper import get_gcs_bucket_name
        from symphainy_platform.config.env_contract import get_env_contract
        env = get_env_contract()
        
        gcs_bucket_name = (
            self.config.get("gcs_bucket_name") or
            get_gcs_bucket_name() or
            (getattr(env, "GCS_BUCKET_NAME", None) if hasattr(env, "GCS_BUCKET_NAME") else None)
        )
        
        # File storage abstraction is REQUIRED for platform operation
        if not self.gcs_adapter:
            raise RuntimeError("GCS adapter is required for file storage abstraction")
        if not self.supabase_file_adapter:
            raise RuntimeError("Supabase file adapter is required for file storage abstraction")
        if not gcs_bucket_name:
            raise RuntimeError("GCS bucket name is required for file storage abstraction")
        
        self.file_storage_abstraction = FileStorageAbstraction(
            gcs_adapter=self.gcs_adapter,
            supabase_file_adapter=self.supabase_file_adapter,
            bucket_name=gcs_bucket_name
        )
        self.logger.info("File storage abstraction created")
        
        # Artifact storage abstraction (REQUIRED for platform operation)
        if not self.gcs_adapter:
            raise RuntimeError("GCS adapter is required for artifact storage abstraction")
        if not self.supabase_file_adapter:
            raise RuntimeError("Supabase file adapter is required for artifact storage abstraction")
        if not gcs_bucket_name:
            raise RuntimeError("GCS bucket name is required for artifact storage abstraction")
        
        self.artifact_storage_abstraction = ArtifactStorageAbstraction(
            gcs_adapter=self.gcs_adapter,
            supabase_file_adapter=self.supabase_file_adapter,
            bucket_name=gcs_bucket_name
        )
        self.logger.info("Artifact storage abstraction created")
        
        # Visual Generation abstraction
        from .abstractions.visual_generation_abstraction import VisualGenerationAbstraction
        self.visual_generation_abstraction = VisualGenerationAbstraction(
            visual_generation_adapter=self.visual_generation_adapter,
            file_storage_abstraction=self.file_storage_abstraction
        )
        self.logger.info("Visual Generation abstraction created")
        
        # Event publisher abstraction (optional - may not be available)
        if self.redis_adapter:
            try:
                from .adapters.redis_streams_publisher import RedisStreamsPublisher
                from .abstractions.event_publisher_abstraction import EventPublisherAbstraction
                
                redis_streams_publisher = RedisStreamsPublisher(self.redis_adapter)
                self.event_publisher_abstraction = EventPublisherAbstraction(
                    primary_publisher=redis_streams_publisher
                )
                if await self.event_publisher_abstraction.initialize():
                    self.logger.info("Event publisher abstraction created")
                else:
                    self.logger.warning("Event publisher abstraction initialization failed")
            except ImportError:
                self.logger.warning("Event publisher abstraction not available (redis_streams_publisher module not found)")
                self.event_publisher_abstraction = None
        else:
            self.logger.warning("Event publisher abstraction not created (Redis adapter missing)")
            self.event_publisher_abstraction = None
        
        # Ingestion adapters (created after file_storage_abstraction is available)
        from .adapters.upload_adapter import UploadAdapter
        from .adapters.edi_adapter import EDIAdapter
        from .adapters.api_adapter import APIAdapter
        
        # Ingestion adapters require file storage abstraction
        if not self.file_storage_abstraction:
            raise RuntimeError("File storage abstraction is required for ingestion adapters")
        
        # Upload adapter (REQUIRED)
        self.upload_adapter = UploadAdapter(
            file_storage_abstraction=self.file_storage_abstraction
        )
        self.logger.info("Upload adapter created")
        
        # EDI adapter (optional - only if EDI config provided)
        edi_config = self.config.get("edi", {})
        if edi_config:
            self.edi_adapter = EDIAdapter(
                file_storage_abstraction=self.file_storage_abstraction,
                edi_config=edi_config
            )
            self.logger.info("EDI adapter created")
        else:
            self.logger.info("EDI adapter not created (no EDI configuration provided)")
        
        # API adapter (REQUIRED)
        self.api_adapter = APIAdapter(
            file_storage_abstraction=self.file_storage_abstraction
        )
        self.logger.info("API adapter created")
        
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
        
        # Other parsing abstractions (with adapters connected)
        self.pdf_processing_abstraction = PdfProcessingAbstraction(
            pdf_adapter=self.pdf_adapter,
            state_surface=temp_state_surface
        )
        
        self.word_processing_abstraction = WordProcessingAbstraction(
            word_adapter=self.word_adapter,
            state_surface=temp_state_surface
        )
        
        self.excel_processing_abstraction = ExcelProcessingAbstraction(
            excel_adapter=self.excel_adapter,
            state_surface=temp_state_surface
        )
        
        self.csv_processing_abstraction = CsvProcessingAbstraction(
            csv_adapter=self.csv_adapter,
            state_surface=temp_state_surface
        )
        
        self.json_processing_abstraction = JsonProcessingAbstraction(
            json_adapter=self.json_adapter,
            state_surface=temp_state_surface
        )
        
        self.text_processing_abstraction = TextProcessingAbstraction(
            text_adapter=None,  # Text adapter uses built-in text processing (no adapter needed)
            state_surface=temp_state_surface
        )
        
        self.image_processing_abstraction = ImageProcessingAbstraction(
            ocr_adapter=self.image_adapter,
            state_surface=temp_state_surface
        )
        
        self.html_processing_abstraction = HtmlProcessingAbstraction(
            html_adapter=self.html_adapter,
            state_surface=temp_state_surface
        )
        
        self.logger.info("Parsing abstractions created with adapters connected")
    
    async def _ensure_state_collections(self):
        """
        Ensure required ArangoDB collections exist for state management.
        
        This ensures infrastructure is ready before use, following the pattern
        established for Supabase and other foundational databases.
        
        Raises:
            RuntimeError: If collection creation fails (fail fast at startup)
        """
        if not self.arango_adapter:
            return
        
        required_collections = ["state_data"]
        
        for collection_name in required_collections:
            try:
                if not await self.arango_adapter.collection_exists(collection_name):
                    success = await self.arango_adapter.create_collection(collection_name)
                    if success:
                        self.logger.info(f"✅ Created ArangoDB collection: {collection_name}")
                    else:
                        raise RuntimeError(f"Failed to create ArangoDB collection: {collection_name}")
                else:
                    self.logger.debug(f"ArangoDB collection already exists: {collection_name}")
            except Exception as e:
                self.logger.error(f"Failed to ensure ArangoDB collection {collection_name}: {e}")
                raise RuntimeError(f"Infrastructure initialization failed: could not create collection {collection_name}") from e
    
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
            # Also update strategies' state_surface
            if hasattr(self.mainframe_adapter, 'custom_strategy') and self.mainframe_adapter.custom_strategy:
                self.mainframe_adapter.custom_strategy.state_surface = state_surface
            if hasattr(self.mainframe_adapter, 'cobrix_strategy') and self.mainframe_adapter.cobrix_strategy:
                self.mainframe_adapter.cobrix_strategy.state_surface = state_surface
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
    
    def get_visual_generation_abstraction(self) -> Optional[VisualGenerationAbstraction]:
        """Get Visual Generation abstraction."""
        return self.visual_generation_abstraction
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
    
    def get_semantic_data_abstraction(self) -> Optional[Any]:
        """
        Get semantic data abstraction (for Content Realm and Insights Realm).
        
        Returns:
            Optional[SemanticDataAbstraction]: Semantic data abstraction or None
        """
        return self.semantic_data_abstraction


    def get_supabase_file_adapter(self) -> Optional[SupabaseFileAdapter]:
        """
        Get Supabase file adapter (for File Metadata Service).
        """
        return self.supabase_file_adapter
    
    def get_event_publisher_abstraction(self) -> Optional[Any]:
        """
        Get event publisher abstraction (for Transactional Outbox).
        
        Returns:
            Optional[EventPublisherAbstraction]: Event publisher abstraction or None
        """
        return self.event_publisher_abstraction
    
    def get_arango_adapter(self) -> Optional[Any]:
        """
        Get ArangoDB adapter (for lineage tracking and embeddings).
        
        Returns:
            Optional[ArangoAdapter]: ArangoDB adapter or None
        """
        return self.arango_adapter
    
    def get_supabase_adapter(self) -> Optional[SupabaseAdapter]:
        """
        Get Supabase adapter (for lineage tracking).
        
        Returns:
            Optional[SupabaseAdapter]: Supabase adapter or None
        """
        return self.supabase_adapter
    
    def get_artifact_storage_abstraction(self) -> Optional[ArtifactStorageAbstraction]:
        """
        Get Artifact Storage abstraction.
        
        Returns:
            Optional[ArtifactStorageAbstraction]: Artifact Storage abstraction or None
        """
        return self.artifact_storage_abstraction
    
    def get_state_surface(self) -> Optional[Any]:
        """
        Get State Surface (for file retrieval).
        
        Returns:
            Optional[StateSurface]: State Surface or None
        """
        # State Surface is part of Runtime, not Foundation
        # This method is a placeholder - State Surface should be passed via context
        return None
    
    def get_llm_adapter(self) -> Optional[Any]:
        """
        Get LLM adapter (OpenAI) for governed LLM access.
        
        Returns:
            Optional[OpenAIAdapter]: OpenAI adapter or None
        """
        return self.openai_adapter
    
    def get_huggingface_adapter(self) -> Optional[Any]:
        """
        Get HuggingFace adapter for embedding generation.
        
        Returns:
            Optional[HuggingFaceAdapter]: HuggingFace adapter or None
        """
        return self.huggingface_adapter