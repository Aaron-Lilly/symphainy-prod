#!/usr/bin/env python3
"""
Generate Synthetic Insurance Policy Test Data

Creates realistic insurance policy binary files (EBCDIC encoded) with:
- Header records
- Policy master records
- Claim records
- Beneficiary records
- Trailer records

Usage:
    python generate_insurance_test_data.py
"""

import struct
import codecs
from datetime import datetime, timedelta
import random
from pathlib import Path

# EBCDIC codec (approximate - real EBCDIC would need proper codec)
# For testing, we'll use ASCII and note that real EBCDIC conversion needed
EBCDIC_TO_ASCII = str.maketrans(
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
)


def encode_ebcdic_string(text: str, length: int) -> bytes:
    """
    Encode string to EBCDIC (simplified for testing).
    
    In production, would use proper EBCDIC codec.
    For now, pad with spaces and encode as ASCII (will be converted later).
    """
    # Pad or truncate to exact length
    text = text[:length].ljust(length)
    # Return as bytes (ASCII for now - real EBCDIC conversion needed)
    return text.encode('latin-1')


def encode_ebcdic_number(number: int, length: int) -> bytes:
    """Encode number as EBCDIC string (zero-padded)."""
    num_str = str(number).zfill(length)
    return encode_ebcdic_string(num_str, length)


def encode_ebcdic_decimal(number: float, int_length: int, dec_length: int) -> bytes:
    """Encode decimal number as EBCDIC string."""
    # Format: integer part + decimal part (no decimal point in fixed format)
    int_part = int(number)
    dec_part = int((number - int_part) * (10 ** dec_length))
    num_str = f"{int_part:0{int_length}d}{dec_part:0{dec_length}d}"
    return encode_ebcdic_string(num_str, int_length + dec_length)


def generate_date(offset_days: int = 0) -> str:
    """Generate date string in YYYY-MM-DD format."""
    date = datetime.now() - timedelta(days=offset_days)
    return date.strftime('%Y-%m-%d')


def generate_policy_header(sequence: int, total_records: int, source_system: str = "LEGACY-SYS-01") -> bytes:
    """Generate policy header record (150 bytes)."""
    record = bytearray(150)
    
    # Record type: 'H'
    record[0:1] = b'H'
    
    # Sequence (5 digits)
    record[1:6] = encode_ebcdic_number(sequence, 5)
    
    # File date (YYYY-MM-DD)
    record[6:16] = encode_ebcdic_string(generate_date(), 10)
    
    # File time (HH:MM:SS)
    record[16:24] = encode_ebcdic_string(datetime.now().strftime('%H:%M:%S'), 8)
    
    # Total records (10 digits)
    record[24:34] = encode_ebcdic_number(total_records, 10)
    
    # Source system (20 chars)
    record[34:54] = encode_ebcdic_string(source_system, 20)
    
    # Filler (46 bytes)
    record[54:100] = b' ' * 46
    
    return bytes(record)


def generate_policy_record(
    policy_number: str,
    last_name: str,
    first_name: str,
    middle_init: str,
    dob: str,
    ssn: str,
    policy_type: str,
    face_amount: int,
    premium: float,
    premium_freq: str,
    cash_value: float,
    status: str,
    effective_date: str,
    expiration_date: str,
    issue_date: str,
    agent_id: str
) -> bytes:
    """Generate policy master record (150 bytes)."""
    record = bytearray(150)
    offset = 0
    
    # Record type: 'P'
    record[offset:offset+1] = b'P'
    offset += 1
    
    # Policy number (12 chars)
    record[offset:offset+12] = encode_ebcdic_string(policy_number, 12)
    offset += 12
    
    # Insured last name (30 chars)
    record[offset:offset+30] = encode_ebcdic_string(last_name, 30)
    offset += 30
    
    # Insured first name (20 chars)
    record[offset:offset+20] = encode_ebcdic_string(first_name, 20)
    offset += 20
    
    # Middle initial (1 char)
    record[offset:offset+1] = encode_ebcdic_string(middle_init, 1)
    offset += 1
    
    # Date of birth (10 chars)
    record[offset:offset+10] = encode_ebcdic_string(dob, 10)
    offset += 10
    
    # SSN (9 chars, no dashes)
    record[offset:offset+9] = encode_ebcdic_string(ssn.replace('-', ''), 9)
    offset += 9
    
    # Policy type (20 chars)
    record[offset:offset+20] = encode_ebcdic_string(policy_type, 20)
    offset += 20
    
    # Face amount (12 digits)
    record[offset:offset+12] = encode_ebcdic_number(face_amount, 12)
    offset += 12
    
    # Premium amount (8 digits, 2 decimals)
    record[offset:offset+10] = encode_ebcdic_decimal(premium, 8, 2)
    offset += 10
    
    # Premium frequency (1 char)
    record[offset:offset+1] = encode_ebcdic_string(premium_freq, 1)
    offset += 1
    
    # Cash value (12 digits, 2 decimals)
    record[offset:offset+14] = encode_ebcdic_decimal(cash_value, 12, 2)
    offset += 14
    
    # Policy status (10 chars)
    record[offset:offset+10] = encode_ebcdic_string(status, 10)
    offset += 10
    
    # Effective date (10 chars)
    record[offset:offset+10] = encode_ebcdic_string(effective_date, 10)
    offset += 10
    
    # Expiration date (10 chars)
    record[offset:offset+10] = encode_ebcdic_string(expiration_date, 10)
    offset += 10
    
    # Issue date (10 chars)
    record[offset:offset+10] = encode_ebcdic_string(issue_date, 10)
    offset += 10
    
    # Agent ID (10 chars)
    record[offset:offset+10] = encode_ebcdic_string(agent_id, 10)
    offset += 10
    
    # Filler (15 bytes)
    record[offset:offset+15] = b' ' * 15
    
    return bytes(record)


def generate_claim_record(
    policy_number: str,
    claim_number: str,
    claim_date: str,
    claim_type: str,
    claim_amount: float,
    claim_status: str,
    payment_date: str,
    payment_amount: float,
    beneficiary_id: str
) -> bytes:
    """Generate claim record (150 bytes)."""
    record = bytearray(150)
    offset = 0
    
    # Record type: 'C'
    record[offset:offset+1] = b'C'
    offset += 1
    
    # Policy number (12 chars)
    record[offset:offset+12] = encode_ebcdic_string(policy_number, 12)
    offset += 12
    
    # Claim number (15 chars)
    record[offset:offset+15] = encode_ebcdic_string(claim_number, 15)
    offset += 15
    
    # Claim date (10 chars)
    record[offset:offset+10] = encode_ebcdic_string(claim_date, 10)
    offset += 10
    
    # Claim type (20 chars)
    record[offset:offset+20] = encode_ebcdic_string(claim_type, 20)
    offset += 20
    
    # Claim amount (12 digits, 2 decimals)
    record[offset:offset+14] = encode_ebcdic_decimal(claim_amount, 12, 2)
    offset += 14
    
    # Claim status (10 chars)
    record[offset:offset+10] = encode_ebcdic_string(claim_status, 10)
    offset += 10
    
    # Payment date (10 chars)
    record[offset:offset+10] = encode_ebcdic_string(payment_date, 10)
    offset += 10
    
    # Payment amount (12 digits, 2 decimals)
    record[offset:offset+14] = encode_ebcdic_decimal(payment_amount, 12, 2)
    offset += 14
    
    # Beneficiary ID (10 chars)
    record[offset:offset+10] = encode_ebcdic_string(beneficiary_id, 10)
    offset += 10
    
    # Filler (20 bytes)
    record[offset:offset+20] = b' ' * 20
    
    return bytes(record)


def generate_beneficiary_record(
    policy_number: str,
    beneficiary_id: str,
    last_name: str,
    first_name: str,
    relation: str,
    percent: float,
    date_added: str,
    date_removed: str
) -> bytes:
    """Generate beneficiary record (150 bytes)."""
    record = bytearray(150)
    offset = 0
    
    # Record type: 'B'
    record[offset:offset+1] = b'B'
    offset += 1
    
    # Policy number (12 chars)
    record[offset:offset+12] = encode_ebcdic_string(policy_number, 12)
    offset += 12
    
    # Beneficiary ID (10 chars)
    record[offset:offset+10] = encode_ebcdic_string(beneficiary_id, 10)
    offset += 10
    
    # Last name (30 chars)
    record[offset:offset+30] = encode_ebcdic_string(last_name, 30)
    offset += 30
    
    # First name (20 chars)
    record[offset:offset+20] = encode_ebcdic_string(first_name, 20)
    offset += 20
    
    # Relation (20 chars)
    record[offset:offset+20] = encode_ebcdic_string(relation, 20)
    offset += 20
    
    # Beneficiary percent (3 digits, 2 decimals)
    record[offset:offset+5] = encode_ebcdic_decimal(percent, 3, 2)
    offset += 5
    
    # Date added (10 chars)
    record[offset:offset+10] = encode_ebcdic_string(date_added, 10)
    offset += 10
    
    # Date removed (10 chars)
    record[offset:offset+10] = encode_ebcdic_string(date_removed, 10)
    offset += 10
    
    # Filler (25 bytes)
    record[offset:offset+25] = b' ' * 25
    
    return bytes(record)


def generate_trailer_record(
    sequence: int,
    total_policies: int,
    total_claims: int,
    total_beneficiaries: int,
    checksum: int
) -> bytes:
    """Generate trailer record (150 bytes)."""
    record = bytearray(150)
    offset = 0
    
    # Record type: 'T'
    record[offset:offset+1] = b'T'
    offset += 1
    
    # Sequence (5 digits)
    record[offset:offset+5] = encode_ebcdic_number(sequence, 5)
    offset += 5
    
    # Total policies (10 digits)
    record[offset:offset+10] = encode_ebcdic_number(total_policies, 10)
    offset += 10
    
    # Total claims (10 digits)
    record[offset:offset+10] = encode_ebcdic_number(total_claims, 10)
    offset += 10
    
    # Total beneficiaries (10 digits)
    record[offset:offset+10] = encode_ebcdic_number(total_beneficiaries, 10)
    offset += 10
    
    # Checksum (15 digits)
    record[offset:offset+15] = encode_ebcdic_number(checksum, 15)
    offset += 15
    
    # Filler (39 bytes)
    record[offset:offset+39] = b' ' * 39
    
    return bytes(record)


def generate_synthetic_insurance_data(
    num_policies: int = 100,
    output_path: Path = None
) -> bytes:
    """
    Generate synthetic insurance policy binary file.
    
    Args:
        num_policies: Number of policy records to generate
        output_path: Optional path to save file
    
    Returns:
        bytes: Binary file content
    """
    if output_path is None:
        output_path = Path(__file__).parent / "files" / "insurance_policy_comprehensive_ebcdic.bin"
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_data = bytearray()
    
    # Sample data pools
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
    first_names = ["John", "Jane", "Robert", "Mary", "Michael", "Patricia", "David", "Jennifer"]
    policy_types = ["LIFE", "TERM", "WHOLE", "UNIVERSAL"]
    statuses = ["ACTIVE", "LAPSED", "SURRENDERED", "MATURED"]
    claim_types = ["DEATH", "DISABILITY", "ACCIDENTAL", "SURRENDER"]
    claim_statuses = ["PENDING", "APPROVED", "DENIED", "PAID"]
    relations = ["SPOUSE", "CHILD", "PARENT", "OTHER"]
    premium_freqs = ["M", "Q", "A"]
    
    # Generate header
    total_records = 1 + num_policies + (num_policies * 2) + (num_policies * 2) + 1  # H + P + C + B + T
    header = generate_policy_header(1, total_records)
    file_data.extend(header)
    
    total_claims = 0
    total_beneficiaries = 0
    checksum = 0
    
    # Generate policies, claims, and beneficiaries
    for i in range(num_policies):
        policy_num = f"POL{1000000 + i:06d}"
        
        # Policy record
        dob = generate_date(random.randint(7300, 25550))  # 20-70 years ago
        ssn = f"{random.randint(100, 999)}{random.randint(10, 99)}{random.randint(1000, 9999)}"
        face_amount = random.randint(50000, 1000000)
        premium = face_amount * random.uniform(0.001, 0.01)
        cash_value = face_amount * random.uniform(0.1, 0.8)
        effective_date = generate_date(random.randint(0, 3650))  # 0-10 years ago
        expiration_date = generate_date(-random.randint(0, 3650))  # Future date
        issue_date = effective_date
        
        policy = generate_policy_record(
            policy_number=policy_num,
            last_name=random.choice(last_names),
            first_name=random.choice(first_names),
            middle_init=random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
            dob=dob,
            ssn=ssn,
            policy_type=random.choice(policy_types),
            face_amount=face_amount,
            premium=premium,
            premium_freq=random.choice(premium_freqs),
            cash_value=cash_value,
            status=random.choice(statuses),
            effective_date=effective_date,
            expiration_date=expiration_date,
            issue_date=issue_date,
            agent_id=f"AGT{random.randint(1000, 9999):04d}"
        )
        file_data.extend(policy)
        checksum += sum(policy)
        
        # Generate 1-2 claims per policy
        num_claims = random.randint(1, 2)
        for j in range(num_claims):
            claim_num = f"CLM{policy_num}{j:02d}"
            claim_date = generate_date(random.randint(0, 1095))  # 0-3 years ago
            claim_amount = face_amount * random.uniform(0.1, 1.0)
            payment_date = claim_date if random.random() > 0.3 else ""
            payment_amount = claim_amount if payment_date else 0.0
            
            claim = generate_claim_record(
                policy_number=policy_num,
                claim_number=claim_num,
                claim_date=claim_date,
                claim_type=random.choice(claim_types),
                claim_amount=claim_amount,
                claim_status=random.choice(claim_statuses),
                payment_date=payment_date,
                payment_amount=payment_amount,
                beneficiary_id=f"BEN{policy_num}001"
            )
            file_data.extend(claim)
            total_claims += 1
            checksum += sum(claim)
        
        # Generate 1-2 beneficiaries per policy
        num_beneficiaries = random.randint(1, 2)
        beneficiary_percent = 100.0 / num_beneficiaries
        for j in range(num_beneficiaries):
            ben_id = f"BEN{policy_num}{j+1:03d}"
            date_added = effective_date
            date_removed = "" if random.random() > 0.1 else generate_date(random.randint(0, 1095))
            
            beneficiary = generate_beneficiary_record(
                policy_number=policy_num,
                beneficiary_id=ben_id,
                last_name=random.choice(last_names),
                first_name=random.choice(first_names),
                relation=random.choice(relations),
                percent=beneficiary_percent,
                date_added=date_added,
                date_removed=date_removed
            )
            file_data.extend(beneficiary)
            total_beneficiaries += 1
            checksum += sum(beneficiary)
    
    # Generate trailer
    trailer = generate_trailer_record(
        sequence=total_records,
        total_policies=num_policies,
        total_claims=total_claims,
        total_beneficiaries=total_beneficiaries,
        checksum=checksum
    )
    file_data.extend(trailer)
    
    # Write to file
    with open(output_path, 'wb') as f:
        f.write(bytes(file_data))
    
    print(f"✅ Generated {num_policies} policies, {total_claims} claims, {total_beneficiaries} beneficiaries")
    print(f"✅ Total file size: {len(file_data)} bytes ({len(file_data) / 150:.0f} records)")
    print(f"✅ Saved to: {output_path}")
    
    return bytes(file_data)


if __name__ == "__main__":
    # Generate test data
    data = generate_synthetic_insurance_data(num_policies=100)
    print("\n✅ Test data generation complete!")
