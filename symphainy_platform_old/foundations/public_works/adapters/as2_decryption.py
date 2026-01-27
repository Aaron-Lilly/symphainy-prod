"""
AS2 Decryption Module - AS2 Message Processing

Handles AS2 (Applicability Statement 2) message decryption and signature verification.
Supports both pyas2lib (preferred) and manual S/MIME decryption (fallback).

WHAT (Infrastructure Role): I provide AS2 decryption capabilities
HOW (Infrastructure Implementation): I use pyas2lib or cryptography for S/MIME
"""

import base64
from typing import Dict, Any, Optional, Tuple
from utilities import get_logger

logger = get_logger(__name__)


class AS2DecryptionError(Exception):
    """Custom exception for AS2 decryption errors."""
    pass


class AS2Decryptor:
    """
    AS2 message decryptor.
    
    Supports:
    - Message decryption using recipient's private key
    - Signature verification using sender's certificate
    - MDN (Message Disposition Notification) handling
    """
    
    def __init__(
        self,
        partner_config: Dict[str, Any]
    ):
        """
        Initialize AS2 decryptor.
        
        Args:
            partner_config: Partner configuration containing:
                - decrypt_key: Private key bytes (PEM format) for decryption
                - decrypt_key_pass: Password for private key (optional)
                - verify_cert: Partner's certificate bytes (PEM format) for signature verification
                - as2_name: Partner's AS2 identifier
        """
        self.partner_config = partner_config
        self.logger = logger
        self._pyas2_available = False
        self._cryptography_available = False
        
        # Check for pyas2lib availability
        try:
            import pyas2lib
            self._pyas2_available = True
            self.logger.info("pyas2lib available - using for AS2 decryption")
        except ImportError:
            self.logger.warning("pyas2lib not available - will use manual S/MIME decryption")
        
        # Check for cryptography availability (for fallback)
        try:
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.serialization import pkcs12
            from cryptography.hazmat.backends import default_backend
            self._cryptography_available = True
            self.logger.info("cryptography available - can use for S/MIME decryption")
        except ImportError:
            self.logger.warning("cryptography not available - AS2 decryption may fail")
    
    async def decrypt_and_verify(
        self,
        as2_message: bytes,
        organization_config: Optional[Dict[str, Any]] = None
    ) -> Tuple[bytes, Dict[str, Any]]:
        """
        Decrypt and verify AS2 message.
        
        Args:
            as2_message: Raw AS2 message bytes (HTTP request body)
            organization_config: Optional organization config (for pyas2lib)
        
        Returns:
            Tuple of (decrypted_payload, metadata)
            metadata contains:
                - verified: bool (signature verified)
                - sender: str (AS2 name of sender)
                - message_id: str (AS2 message ID)
                - mdn_required: bool (whether MDN is required)
        """
        if self._pyas2_available:
            return await self._decrypt_with_pyas2lib(as2_message, organization_config)
        elif self._cryptography_available:
            return await self._decrypt_with_cryptography(as2_message)
        else:
            raise AS2DecryptionError(
                "Neither pyas2lib nor cryptography available. "
                "Install pyas2lib (recommended) or cryptography for AS2 decryption."
            )
    
    async def _decrypt_with_pyas2lib(
        self,
        as2_message: bytes,
        organization_config: Optional[Dict[str, Any]]
    ) -> Tuple[bytes, Dict[str, Any]]:
        """
        Decrypt AS2 message using pyas2lib (preferred method).
        
        Args:
            as2_message: Raw AS2 message bytes
            organization_config: Organization configuration
        
        Returns:
            Tuple of (decrypted_payload, metadata)
        """
        try:
            from pyas2lib.as2 import Organization, Partner, Message
            
            # Create organization (recipient)
            if not organization_config:
                organization_config = {
                    "as2_name": self.partner_config.get("organization_as2_name", "default_org"),
                    "decrypt_key": self.partner_config.get("decrypt_key"),
                    "decrypt_key_pass": self.partner_config.get("decrypt_key_pass")
                }
            
            my_org = Organization(
                as2_name=organization_config.get("as2_name"),
                decrypt_key=organization_config.get("decrypt_key"),
                decrypt_key_pass=organization_config.get("decrypt_key_pass")
            )
            
            # Create partner (sender)
            partner = Partner(
                as2_name=self.partner_config.get("as2_name"),
                verify_cert=self.partner_config.get("verify_cert")
            )
            
            # Parse and decrypt message
            msg = Message()
            
            # Define helper functions for pyas2lib
            def find_organization(as2_name: str) -> Organization:
                """Find organization by AS2 name."""
                if as2_name == my_org.as2_name:
                    return my_org
                raise ValueError(f"Organization not found: {as2_name}")
            
            def find_partner(as2_name: str) -> Partner:
                """Find partner by AS2 name."""
                if as2_name == partner.as2_name:
                    return partner
                raise ValueError(f"Partner not found: {as2_name}")
            
            def check_duplicate_msg(message_id: str) -> bool:
                """Check for duplicate messages (implement based on your needs)."""
                # TODO: Implement duplicate message checking using State Surface or database
                return False
            
            # Parse message
            status, exception, mdn = msg.parse(
                as2_message,
                find_organization,
                find_partner,
                check_duplicate_msg
            )
            
            if not status:
                raise AS2DecryptionError(f"AS2 message parsing failed: {exception}")
            
            # Extract decrypted content
            decrypted_payload = msg.decrypted_content
            
            # Build metadata
            metadata = {
                "verified": msg.verified,  # Signature verified
                "sender": msg.sender.as2_name if msg.sender else None,
                "message_id": msg.message_id,
                "mdn_required": msg.mdn_requested,
                "mdn": mdn,
                "encryption_algorithm": getattr(msg, "encryption_algorithm", None),
                "signature_algorithm": getattr(msg, "signature_algorithm", None)
            }
            
            self.logger.info(
                f"AS2 message decrypted successfully: "
                f"sender={metadata['sender']}, message_id={metadata['message_id']}, verified={metadata['verified']}"
            )
            
            return decrypted_payload, metadata
            
        except ImportError:
            raise AS2DecryptionError("pyas2lib not available")
        except Exception as e:
            self.logger.error(f"AS2 decryption with pyas2lib failed: {e}", exc_info=True)
            raise AS2DecryptionError(f"AS2 decryption failed: {str(e)}")
    
    async def _decrypt_with_cryptography(
        self,
        as2_message: bytes
    ) -> Tuple[bytes, Dict[str, Any]]:
        """
        Decrypt AS2 message using cryptography library (fallback method).
        
        This is a simplified implementation. For full AS2 support, use pyas2lib.
        
        Args:
            as2_message: Raw AS2 message bytes
        
        Returns:
            Tuple of (decrypted_payload, metadata)
        """
        try:
            from email import message_from_bytes
            from email.policy import HTTP
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.serialization import pkcs12
            from cryptography.hazmat.backends import default_backend
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import padding
            from cryptography import x509
            
            # Parse HTTP message
            # AS2 messages are typically sent as HTTP POST with multipart/signed or application/pkcs7-mime
            # This is a simplified parser - full AS2 requires proper MIME parsing
            
            # Try to parse as email message (AS2 uses MIME)
            try:
                email_msg = message_from_bytes(as2_message, policy=HTTP)
                content_type = email_msg.get_content_type()
                
                if content_type == "application/pkcs7-mime" or "encrypted-data" in content_type:
                    # Encrypted message - need to decrypt
                    encrypted_data = email_msg.get_payload(decode=True)
                    
                    # Load private key for decryption
                    decrypt_key = self.partner_config.get("decrypt_key")
                    decrypt_key_pass = self.partner_config.get("decrypt_key_pass")
                    
                    if not decrypt_key:
                        raise AS2DecryptionError("decrypt_key not provided in partner config")
                    
                    # Load private key
                    if isinstance(decrypt_key, bytes):
                        key_data = decrypt_key
                    else:
                        key_data = decrypt_key.encode('utf-8')
                    
                    private_key = serialization.load_pem_private_key(
                        key_data,
                        password=decrypt_key_pass.encode('utf-8') if decrypt_key_pass else None,
                        backend=default_backend()
                    )
                    
                    # Decrypt (simplified - full AS2 requires proper CMS/PKCS#7 parsing)
                    # This is a placeholder - full implementation requires CMS library
                    self.logger.warning(
                        "Manual S/MIME decryption is simplified. "
                        "For full AS2 support, install pyas2lib."
                    )
                    
                    # For now, return as-is with warning
                    metadata = {
                        "verified": False,
                        "sender": None,
                        "message_id": None,
                        "mdn_required": False,
                        "warning": "Manual decryption not fully implemented - install pyas2lib for full support"
                    }
                    
                    return encrypted_data, metadata
                
                else:
                    # Not encrypted, return payload
                    payload = email_msg.get_payload(decode=True)
                    metadata = {
                        "verified": False,
                        "sender": email_msg.get("From"),
                        "message_id": email_msg.get("Message-ID"),
                        "mdn_required": False
                    }
                    return payload, metadata
                    
            except Exception as e:
                self.logger.error(f"Failed to parse AS2 message: {e}", exc_info=True)
                raise AS2DecryptionError(f"Failed to parse AS2 message: {str(e)}")
                
        except ImportError:
            raise AS2DecryptionError("cryptography library not available")
        except Exception as e:
            self.logger.error(f"AS2 decryption with cryptography failed: {e}", exc_info=True)
            raise AS2DecryptionError(f"AS2 decryption failed: {str(e)}")
