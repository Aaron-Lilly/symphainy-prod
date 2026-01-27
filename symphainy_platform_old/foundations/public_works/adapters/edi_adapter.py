"""
EDI Adapter - Infrastructure Implementation (Layer 0)

Handles EDI protocol ingestion (AS2, SFTP, etc.).
Processes EDI data and stores via FileStorageAbstraction.

WHAT (Infrastructure Role): I provide EDI protocol ingestion
HOW (Infrastructure Implementation): I process EDI data and use FileStorageAbstraction
"""

import uuid
from typing import Dict, Any, Optional
from utilities import get_logger, get_clock

from ..protocols.ingestion_protocol import (
    IngestionRequest,
    IngestionResult,
    IngestionType
)
from .as2_decryption import AS2Decryptor, AS2DecryptionError


class EDIAdapter:
    """
    EDI adapter - handles EDI protocol ingestion.
    
    Supports:
    - AS2 (Applicability Statement 2)
    - SFTP (Secure File Transfer Protocol)
    - Email attachments (future)
    """
    
    def __init__(
        self,
        file_storage_abstraction: Any,
        edi_config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize EDI adapter.
        
        Args:
            file_storage_abstraction: FileStorageAbstraction instance
            edi_config: Optional EDI configuration containing:
                - partners: Dict[str, Dict] - Partner configurations keyed by partner_id
                  Each partner config should contain:
                    - as2_name: Partner's AS2 identifier
                    - decrypt_key: Private key bytes (PEM format) for decryption
                    - decrypt_key_pass: Password for private key (optional)
                    - verify_cert: Partner's certificate bytes (PEM format) for signature verification
                - organization: Dict - Organization configuration (for pyas2lib)
                  Should contain:
                    - as2_name: Organization's AS2 identifier
                    - decrypt_key: Organization's private key (if different from partner)
                    - decrypt_key_pass: Password for organization key (optional)
        """
        self.file_storage = file_storage_abstraction
        self.config = edi_config or {}
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        
        # Cache AS2 decryptors per partner
        self._as2_decryptors: Dict[str, AS2Decryptor] = {}
        
        # Pre-initialize decryptors for configured partners
        partners = self.config.get("partners", {})
        for partner_id, partner_config in partners.items():
            try:
                self._as2_decryptors[partner_id] = AS2Decryptor(partner_config)
                self.logger.info(f"AS2 decryptor initialized for partner: {partner_id}")
            except Exception as e:
                self.logger.warning(f"Failed to initialize AS2 decryptor for partner {partner_id}: {e}")
    
    async def ingest(self, request: IngestionRequest) -> IngestionResult:
        """
        Ingest via EDI protocol.
        
        Args:
            request: Ingestion request with EDI type
        
        Returns:
            IngestionResult with file_id, file_reference, storage_location, and metadata
        """
        if request.ingestion_type != IngestionType.EDI:
            return IngestionResult(
                success=False,
                file_id="",
                file_reference="",
                storage_location="",
                ingestion_metadata={},
                error=f"EDI adapter only handles EDI, got {request.ingestion_type}"
            )
        
        if not request.data:
            return IngestionResult(
                success=False,
                file_id="",
                file_reference="",
                storage_location="",
                ingestion_metadata={},
                error="EDI adapter requires file data"
            )
        
        # Extract EDI-specific metadata
        edi_protocol = request.source_metadata.get("protocol", "as2")  # as2, sftp, email
        partner_id = request.source_metadata.get("partner_id")
        transaction_type = request.source_metadata.get("transaction_type")
        
        # Process EDI data (decrypt, validate, etc.)
        try:
            processed_data, processing_metadata = await self._process_edi_data(
                request.data,
                edi_protocol,
                partner_id
            )
        except AS2DecryptionError as e:
            return IngestionResult(
                success=False,
                file_id="",
                file_reference="",
                storage_location="",
                ingestion_metadata={},
                error=f"AS2 decryption failed: {str(e)}"
            )
        
        # Generate file ID and reference
        file_id = str(uuid.uuid4())
        filename = request.source_metadata.get(
            "filename",
            f"edi_{transaction_type or 'file'}_{self.clock.now_iso().replace(':', '-')}"
        )
        
        # Storage path in GCS (tenant/session/file_id format)
        storage_path = f"{request.tenant_id}/{request.session_id}/{file_id}/{filename}"
        file_reference = f"file:{request.tenant_id}:{request.session_id}:{file_id}"
        
        # Prepare metadata
        edi_metadata = {
            **request.source_metadata,
            "ingestion_type": "edi",
            "edi_protocol": edi_protocol,
            "partner_id": partner_id,
            "transaction_type": transaction_type,
            "ingestion_timestamp": self.clock.now_iso(),
            "tenant_id": request.tenant_id,
            "session_id": request.session_id,
            "file_id": file_id
        }
        
        # Store as file (same as upload)
        success = await self.file_storage.upload_file(
            file_path=storage_path,
            file_data=processed_data,
            metadata=edi_metadata
        )
        
        if success:
            self.logger.info(f"EDI file ingested successfully: {storage_path} ({len(processed_data)} bytes)")
            return IngestionResult(
                success=True,
                file_id=file_id,
                file_reference=file_reference,
                storage_location=storage_path,
                ingestion_metadata={
                    "ingestion_type": "edi",
                    "edi_protocol": edi_protocol,
                    "partner_id": partner_id,
                    "transaction_type": transaction_type,
                    "original_filename": filename,
                    "file_size": len(processed_data),
                    "storage_path": storage_path,
                    **processing_metadata  # Include AS2 metadata (verified, sender, message_id, etc.)
                }
            )
        else:
            return IngestionResult(
                success=False,
                file_id="",
                file_reference="",
                storage_location="",
                ingestion_metadata={},
                error="EDI ingestion failed - FileStorageAbstraction.upload_file() returned False"
            )
    
    async def _process_edi_data(
        self,
        data: bytes,
        protocol: str,
        partner_id: Optional[str]
    ) -> tuple[bytes, Dict[str, Any]]:
        """
        Process EDI data (decrypt, validate, etc.).
        
        Args:
            data: Raw EDI data
            protocol: EDI protocol (as2, sftp, email)
            partner_id: Partner identifier (for AS2 decryption)
        
        Returns:
            Tuple of (processed_data, metadata)
            metadata contains protocol-specific information (e.g., AS2 verification status)
        """
        # Protocol-specific processing
        if protocol == "as2":
            # AS2 decryption/validation (returns both data and metadata)
            return await self._process_as2(data, partner_id)
        elif protocol == "sftp":
            # SFTP file processing (already decrypted)
            return data, {}
        else:
            # Default: return as-is
            self.logger.warning(f"Unknown EDI protocol: {protocol}, returning data as-is")
            return data, {}
    
    async def _process_as2(self, data: bytes, partner_id: Optional[str]) -> tuple[bytes, Dict[str, Any]]:
        """
        Process AS2 protocol data (decrypt and verify signature).
        
        Args:
            data: AS2 encrypted/signed message (HTTP request body)
            partner_id: Partner identifier for decryption configuration
        
        Returns:
            Decrypted EDI data
        
        Raises:
            AS2DecryptionError: If decryption or verification fails
        """
        if not partner_id:
            self.logger.warning("AS2 processing: partner_id not provided, attempting to process without partner config")
            # Try to process without partner-specific config (may work if message is not encrypted)
            try:
                # Get default partner config if available
                partners = self.config.get("partners", {})
                if partners:
                    # Use first partner as default
                    partner_id = list(partners.keys())[0]
                    self.logger.info(f"Using default partner for AS2 processing: {partner_id}")
                else:
                    raise AS2DecryptionError("partner_id required for AS2 decryption")
            except Exception as e:
                raise AS2DecryptionError(f"AS2 processing failed: partner_id required. {str(e)}")
        
        # Get or create decryptor for this partner
        decryptor = self._get_decryptor(partner_id)
        
        # Get organization config (optional, for pyas2lib)
        organization_config = self.config.get("organization")
        
        try:
            # Decrypt and verify message
            decrypted_payload, metadata = await decryptor.decrypt_and_verify(
                data,
                organization_config
            )
            
            # Log processing results
            self.logger.info(
                f"AS2 message processed successfully: "
                f"partner_id={partner_id}, "
                f"verified={metadata.get('verified')}, "
                f"sender={metadata.get('sender')}, "
                f"message_id={metadata.get('message_id')}, "
                f"payload_size={len(decrypted_payload)}"
            )
            
            # Warn if signature not verified
            if not metadata.get("verified"):
                self.logger.warning(
                    f"AS2 message signature not verified for partner {partner_id}. "
                    f"Message may be from untrusted source."
                )
            
            # Store metadata for later use (e.g., MDN generation)
            # Metadata is stored in ingestion_metadata in the ingest() method
            
            return decrypted_payload, metadata
            
        except AS2DecryptionError:
            raise
        except Exception as e:
            self.logger.error(f"AS2 processing failed for partner {partner_id}: {e}", exc_info=True)
            raise AS2DecryptionError(f"AS2 processing failed: {str(e)}")
    
    def _get_decryptor(self, partner_id: str) -> AS2Decryptor:
        """
        Get or create AS2 decryptor for partner.
        
        Args:
            partner_id: Partner identifier
        
        Returns:
            AS2Decryptor instance
        
        Raises:
            AS2DecryptionError: If partner config not found
        """
        # Check cache first
        if partner_id in self._as2_decryptors:
            return self._as2_decryptors[partner_id]
        
        # Get partner config
        partners = self.config.get("partners", {})
        if partner_id not in partners:
            raise AS2DecryptionError(
                f"Partner configuration not found for partner_id: {partner_id}. "
                f"Available partners: {list(partners.keys())}"
            )
        
        partner_config = partners[partner_id]
        
        # Create decryptor
        try:
            decryptor = AS2Decryptor(partner_config)
            self._as2_decryptors[partner_id] = decryptor
            self.logger.info(f"AS2 decryptor created for partner: {partner_id}")
            return decryptor
        except Exception as e:
            raise AS2DecryptionError(f"Failed to create AS2 decryptor for partner {partner_id}: {str(e)}")
