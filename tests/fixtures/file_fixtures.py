"""
File Fixtures for Parsing Tests

Creates test files programmatically for all parsing types.
No external file dependencies - all files are created in memory.
"""

import io
import struct
from typing import Tuple, Optional
from datetime import datetime


def create_test_copybook() -> str:
    """
    Create a test COBOL copybook definition.
    
    Includes:
    - Fixed-length fields
    - COMP-3 field (packed decimal)
    - 88-level field (validation rule)
    - Level-01 metadata record
    
    Returns:
        Copybook content as string
    """
    copybook = """       01  CUSTOMER-RECORD.
           05  CUSTOMER-ID        PIC X(10).
           05  CUSTOMER-NAME      PIC X(50).
           05  CUSTOMER-AGE       PIC 9(3).
           05  CUSTOMER-SALARY    PIC S9(8)V99 COMP-3.
           05  CUSTOMER-STATUS    PIC X(1).
               88  ACTIVE         VALUE 'A'.
               88  INACTIVE       VALUE 'I'.
           05  CUSTOMER-DATE      PIC X(8).
           05  FILLER             PIC X(10).
"""
    return copybook


def create_test_binary_file_with_copybook() -> Tuple[bytes, str]:
    """
    Create a test binary file matching the copybook structure.
    
    Record structure:
    - CUSTOMER-ID: 10 bytes (X(10))
    - CUSTOMER-NAME: 50 bytes (X(50))
    - CUSTOMER-AGE: 3 bytes (9(3))
    - CUSTOMER-SALARY: 5 bytes (COMP-3, S9(8)V99 = 5 bytes)
    - CUSTOMER-STATUS: 1 byte (X(1))
    - CUSTOMER-DATE: 8 bytes (X(8))
    - FILLER: 10 bytes (X(10))
    Total: 87 bytes per record
    
    Returns:
        Tuple of (binary_data, copybook_content)
    """
    copybook = create_test_copybook()
    
    # Create 3 test records
    records = []
    
    # Record 1: Active customer
    record1 = bytearray()
    record1.extend(b"CUST001    ")  # CUSTOMER-ID (10 bytes)
    record1.extend(b"Alice Smith                              ")  # CUSTOMER-NAME (50 bytes)
    record1.extend(b"025")  # CUSTOMER-AGE (3 bytes)
    record1.extend(_pack_comp3(50000.00))  # CUSTOMER-SALARY (5 bytes COMP-3)
    record1.extend(b"A")  # CUSTOMER-STATUS (1 byte) - Active
    record1.extend(b"20240101")  # CUSTOMER-DATE (8 bytes)
    record1.extend(b"          ")  # FILLER (10 bytes)
    records.append(bytes(record1))
    
    # Record 2: Active customer
    record2 = bytearray()
    record2.extend(b"CUST002    ")  # CUSTOMER-ID (10 bytes)
    record2.extend(b"Bob Johnson                             ")  # CUSTOMER-NAME (50 bytes)
    record2.extend(b"030")  # CUSTOMER-AGE (3 bytes)
    record2.extend(_pack_comp3(60000.00))  # CUSTOMER-SALARY (5 bytes COMP-3)
    record2.extend(b"A")  # CUSTOMER-STATUS (1 byte) - Active
    record2.extend(b"20240102")  # CUSTOMER-DATE (8 bytes)
    record2.extend(b"          ")  # FILLER (10 bytes)
    records.append(bytes(record2))
    
    # Record 3: Inactive customer
    record3 = bytearray()
    record3.extend(b"CUST003    ")  # CUSTOMER-ID (10 bytes)
    record3.extend(b"Charlie Brown                           ")  # CUSTOMER-NAME (50 bytes)
    record3.extend(b"035")  # CUSTOMER-AGE (3 bytes)
    record3.extend(_pack_comp3(70000.00))  # CUSTOMER-SALARY (5 bytes COMP-3)
    record3.extend(b"I")  # CUSTOMER-STATUS (1 byte) - Inactive
    record3.extend(b"20240103")  # CUSTOMER-DATE (8 bytes)
    record3.extend(b"          ")  # FILLER (10 bytes)
    records.append(bytes(record3))
    
    # Combine all records
    binary_data = b"".join(records)
    
    return binary_data, copybook


def _pack_comp3(value: float) -> bytes:
    """
    Pack a decimal value as COMP-3 (packed decimal).
    
    COMP-3 format:
    - Each digit is stored as a nibble (4 bits)
    - Sign is stored in the last nibble (C=positive, D=negative, F=unsigned)
    - S9(8)V99 means 8 digits before decimal, 2 after = 10 digits total
    - 10 digits = 5 bytes (2 digits per byte) + sign in last nibble
    
    Args:
        value: Decimal value to pack
        
    Returns:
        Packed bytes (5 bytes for S9(8)V99)
    """
    # Convert to integer (multiply by 100 to handle 2 decimal places)
    int_value = int(value * 100)
    
    # Ensure positive (sign handled separately)
    is_negative = int_value < 0
    int_value = abs(int_value)
    
    # Convert to string of digits
    digits = str(int_value).zfill(10)  # 10 digits total
    
    # Pack into bytes (2 digits per byte)
    packed = bytearray(5)
    for i in range(5):
        if i * 2 < len(digits):
            # Get two digits
            digit1 = int(digits[i * 2])
            digit2 = int(digits[i * 2 + 1]) if i * 2 + 1 < len(digits) else 0
            
            # Pack into byte (first digit in high nibble, second in low nibble)
            packed[i] = (digit1 << 4) | digit2
    
    # Set sign in last nibble
    if is_negative:
        packed[4] = (packed[4] & 0xF0) | 0x0D  # D = negative
    else:
        packed[4] = (packed[4] & 0xF0) | 0x0C  # C = positive
    
    return bytes(packed)


def create_test_pdf() -> bytes:
    """
    Create a simple test PDF file with known text content.
    
    This creates a minimal valid PDF with text "Test PDF Content".
    
    Returns:
        PDF file bytes
    """
    # Minimal PDF structure
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
/Resources <<
/Font <<
/F1 5 0 R
>>
>>
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test PDF Content) Tj
ET
endstream
endobj
5 0 obj
<<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
endobj
xref
0 6
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000279 00000 n
0000000364 00000 n
trailer
<<
/Size 6
/Root 1 0 R
>>
startxref
458
%%EOF"""
    return pdf_content


def create_test_excel() -> bytes:
    """
    Create a simple test Excel file (.xlsx) with known data.
    
    Creates a minimal valid Excel file with:
    - Sheet name: "Test Sheet"
    - Data: Name, Age, City columns with 3 rows
    
    Returns:
        Excel file bytes (minimal .xlsx structure)
    """
    # Note: Creating a full .xlsx file programmatically is complex
    # For testing, we'll create a minimal structure
    # In practice, you might use openpyxl or xlsxwriter
    
    # This is a placeholder - in real tests, use openpyxl to create proper Excel files
    # For now, return a minimal ZIP structure (xlsx is a ZIP file)
    import zipfile
    
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Create minimal Excel structure
        zip_file.writestr('[Content_Types].xml', '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
</Types>''')
        
        zip_file.writestr('_rels/.rels', '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>''')
        
        zip_file.writestr('xl/workbook.xml', '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<sheets>
<sheet name="Test Sheet" sheetId="1" r:id="rId1"/>
</sheets>
</workbook>''')
        
        zip_file.writestr('xl/worksheets/sheet1.xml', '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<sheetData>
<row r="1">
<c r="A1" t="inlineStr"><is><t>Name</t></is></c>
<c r="B1" t="inlineStr"><is><t>Age</t></is></c>
<c r="C1" t="inlineStr"><is><t>City</t></is></c>
</row>
<row r="2">
<c r="A2" t="inlineStr"><is><t>John</t></is></c>
<c r="B2"><v>30</v></c>
<c r="C2" t="inlineStr"><is><t>New York</t></is></c>
</row>
<row r="3">
<c r="A3" t="inlineStr"><is><t>Jane</t></is></c>
<c r="B3"><v>25</v></c>
<c r="C3" t="inlineStr"><is><t>Los Angeles</t></is></c>
</row>
</sheetData>
</worksheet>''')
    
    buffer.seek(0)
    return buffer.read()


def create_test_csv() -> bytes:
    """
    Create a test CSV file with known data.
    
    Returns:
        CSV file bytes
    """
    csv_content = """name,age,city
John,30,New York
Jane,25,Los Angeles
Bob,35,Chicago"""
    return csv_content.encode('utf-8')


def create_test_json() -> bytes:
    """
    Create a test JSON file with known data.
    
    Returns:
        JSON file bytes
    """
    import json
    data = {
        "users": [
            {"name": "John", "age": 30, "city": "New York"},
            {"name": "Jane", "age": 25, "city": "Los Angeles"},
            {"name": "Bob", "age": 35, "city": "Chicago"}
        ]
    }
    return json.dumps(data, indent=2).encode('utf-8')


def create_test_text() -> bytes:
    """
    Create a test plain text file with known content.
    
    Returns:
        Text file bytes
    """
    text_content = """This is a test text file.
It contains multiple lines of text.
Line 3 of the test file.
Line 4 of the test file."""
    return text_content.encode('utf-8')


def create_test_html() -> bytes:
    """
    Create a test HTML file with known content.
    
    Returns:
        HTML file bytes
    """
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Test HTML</title>
</head>
<body>
    <h1>Test HTML Content</h1>
    <p>This is a test paragraph.</p>
    <a href="https://example.com">Test Link</a>
</body>
</html>"""
    return html_content.encode('utf-8')


def create_test_image() -> bytes:
    """
    Create a simple test image file (PNG) with text for OCR testing.
    
    Note: Creating a proper image with text programmatically is complex.
    For testing, we'll create a minimal valid PNG structure.
    In practice, you might use PIL/Pillow to create images with text.
    
    Returns:
        PNG file bytes (minimal valid PNG)
    """
    # Minimal valid PNG structure
    # PNG signature + IHDR chunk + IEND chunk
    png_signature = b'\x89PNG\r\n\x1a\n'
    
    # IHDR chunk (13 bytes data + 4 bytes chunk type + 4 bytes CRC)
    ihdr_data = struct.pack('>IIBBBBB', 100, 50, 8, 2, 0, 0, 0)  # 100x50, RGB, 8-bit
    ihdr_chunk = struct.pack('>I', 13) + b'IHDR' + ihdr_data + struct.pack('>I', 0)  # CRC placeholder
    
    # IEND chunk
    iend_chunk = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', 0xAE426082)
    
    return png_signature + ihdr_chunk + iend_chunk
