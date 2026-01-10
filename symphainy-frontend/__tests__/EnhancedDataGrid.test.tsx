import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { DataGrid } from '../components/content/DataGrid';

describe('Enhanced DataGrid - All Output Types', () => {
  
  describe('PDF Output Types', () => {
    
    test('handles PDF with structured tables', () => {
      // Simulate output from tabula-py table extraction
      const tableData = [
        ['Name', 'Age', 'City', 'Salary'],
        ['John Doe', '30', 'New York', '75000'],
        ['Jane Smith', '28', 'Los Angeles', '70000'],
        ['Bob Johnson', '35', 'Chicago', '80000']
      ];
      
      render(<DataGrid data={tableData} />);
      
      // Verify table headers
      expect(screen.getByText('Name')).toBeInTheDocument();
      expect(screen.getByText('Age')).toBeInTheDocument();
      expect(screen.getByText('City')).toBeInTheDocument();
      expect(screen.getByText('Salary')).toBeInTheDocument();
      
      // Verify table data
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('30')).toBeInTheDocument();
      expect(screen.getByText('New York')).toBeInTheDocument();
      expect(screen.getByText('75000')).toBeInTheDocument();
    });
    
    test('handles PDF with mixed content (text + tables)', () => {
      // Simulate output from mixed content PDF
      const mixedData = [
        ['Content Type', 'Description', 'Data'],
        ['Header', 'Monthly Report Q4 2024', 'Generated on 2024-12-31'],
        ['Table', 'Revenue Data', 'See below'],
        ['Row', 'Q1 Revenue', '$100,000'],
        ['Row', 'Q2 Revenue', '$120,000'],
        ['Footer', 'Total Revenue', '$470,000']
      ];
      
      render(<DataGrid data={mixedData} />);
      
      // Verify mixed content is displayed correctly
      expect(screen.getByText('Content Type')).toBeInTheDocument();
      expect(screen.getByText('Monthly Report Q4 2024')).toBeInTheDocument();
      expect(screen.getByText('$100,000')).toBeInTheDocument();
      expect(screen.getByText('Total Revenue')).toBeInTheDocument();
    });
    
    test('handles PDF with form data', () => {
      // Simulate output from pdfplumber form extraction
      const formData = [
        ['Field Name', 'Value'],
        ['First Name', 'John'],
        ['Last Name', 'Doe'],
        ['Email', 'john.doe@example.com'],
        ['Phone', '(555) 123-4567'],
        ['Address', '123 Main St, Anytown, USA'],
        ['Date of Birth', '1990-01-15'],
        ['SSN', '123-45-6789']
      ];
      
      render(<DataGrid data={formData} />);
      
      // Verify form data is displayed correctly
      expect(screen.getByText('Field Name')).toBeInTheDocument();
      expect(screen.getByText('First Name')).toBeInTheDocument();
      expect(screen.getByText('john.doe@example.com')).toBeInTheDocument();
      expect(screen.getByText('(555) 123-4567')).toBeInTheDocument();
    });
    
    test('handles PDF with free form text', () => {
      // Simulate output from plain text PDF
      const textData = [
        ['Page', 'Content'],
        ['1', 'This is a sample document containing important information about our quarterly performance.'],
        ['2', 'The document outlines key metrics and provides insights into our business operations.'],
        ['3', 'Key findings include increased revenue growth and improved customer satisfaction scores.']
      ];
      
      render(<DataGrid data={textData} />);
      
      // Verify text content is displayed correctly
      expect(screen.getByText('Page')).toBeInTheDocument();
      expect(screen.getByText('Content')).toBeInTheDocument();
      expect(screen.getByText('1')).toBeInTheDocument();
      expect(screen.getByText(/sample document/)).toBeInTheDocument();
    });
  });
  
  describe('Image Output Types', () => {
    
    test('handles image-to-text extraction', () => {
      // Simulate output from pytesseract OCR
      const ocrData = [
        ['Text Content'],
        ['Sample text extracted from image using OCR technology.'],
        ['This text was processed using Tesseract OCR engine.'],
        ['The image was preprocessed to improve text recognition accuracy.']
      ];
      
      render(<DataGrid data={ocrData} />);
      
      // Verify OCR text is displayed correctly
      expect(screen.getByText('Text Content')).toBeInTheDocument();
      expect(screen.getByText(/Sample text extracted/)).toBeInTheDocument();
      expect(screen.getByText(/Tesseract OCR engine/)).toBeInTheDocument();
    });
    
    test('handles image-to-table conversion', () => {
      // Simulate output from image table detection
      const imageTableData = [
        ['Product', 'Sales', 'Revenue'],
        ['Laptop', '50', '$50,000'],
        ['Phone', '75', '$37,500'],
        ['Tablet', '25', '$12,500'],
        ['Total', '150', '$100,000']
      ];
      
      render(<DataGrid data={imageTableData} />);
      
      // Verify image table data is displayed correctly
      expect(screen.getByText('Product')).toBeInTheDocument();
      expect(screen.getByText('Sales')).toBeInTheDocument();
      expect(screen.getByText('Revenue')).toBeInTheDocument();
      expect(screen.getByText('Laptop')).toBeInTheDocument();
      expect(screen.getByText('50')).toBeInTheDocument();
      expect(screen.getByText('$50,000')).toBeInTheDocument();
    });
    
    test('handles mixed content images', () => {
      // Simulate output from mixed content image processing
      const mixedImageData = [
        ['Content Type', 'Description', 'Data'],
        ['Header', 'Financial Report Q4 2024', 'Generated: 2024-12-31'],
        ['Table', 'Revenue', 'Amount'],
        ['Row', 'Q1', '$100K'],
        ['Row', 'Q2', '$120K'],
        ['Row', 'Q3', '$110K'],
        ['Row', 'Q4', '$140K'],
        ['Footer', 'Total Revenue', '$470K'],
        ['Summary', 'Net Growth', '17.5%']
      ];
      
      render(<DataGrid data={mixedImageData} />);
      
      // Verify mixed image content is displayed correctly
      expect(screen.getByText('Financial Report Q4 2024')).toBeInTheDocument();
      expect(screen.getByText('Revenue')).toBeInTheDocument();
      expect(screen.getByText('$100K')).toBeInTheDocument();
      expect(screen.getByText('Total Revenue')).toBeInTheDocument();
      expect(screen.getByText('17.5%')).toBeInTheDocument();
    });
  });
  
  describe('Complex Data Types', () => {
    
    test('handles large datasets with pagination', () => {
      // Simulate large dataset output
      const largeData = Array.from({ length: 150 }, (_, i) => [
        `ID-${i + 1}`,
        `Name-${i + 1}`,
        `Value-${i + 1}`,
        `Category-${(i % 5) + 1}`
      ]);
      
      render(<DataGrid data={largeData} maxRows={50} />);
      
      // Verify pagination info is displayed (check for partial text match)
      expect(screen.getByText(/Showing 50 of/)).toBeInTheDocument();
      
      // Verify first and last visible rows
      expect(screen.getByText('ID-1')).toBeInTheDocument();
      expect(screen.getByText('Name-1')).toBeInTheDocument();
      expect(screen.getByText('ID-50')).toBeInTheDocument();
      expect(screen.getByText('Name-50')).toBeInTheDocument();
      
      // Verify row 51 is not visible (pagination)
      expect(screen.queryByText('ID-51')).not.toBeInTheDocument();
    });
    
    test('handles special characters and formatting', () => {
      // Simulate data with special characters
      const specialCharData = [
        ['Field', 'Value', 'Notes'],
        ['Name', 'José María', 'Accented characters'],
        ['Email', 'test@example.com', 'Email format'],
        ['Phone', '+1 (555) 123-4567', 'Phone format'],
        ['Currency', '$1,234.56', 'Currency format'],
        ['Percentage', '12.5%', 'Percentage format'],
        ['Date', '2024-12-31', 'Date format'],
        ['Special', '© ® ™ € ¥ £', 'Special symbols']
      ];
      
      render(<DataGrid data={specialCharData} />);
      
      // Verify special characters are displayed correctly
      expect(screen.getByText('José María')).toBeInTheDocument();
      expect(screen.getByText('test@example.com')).toBeInTheDocument();
      expect(screen.getByText('+1 (555) 123-4567')).toBeInTheDocument();
      expect(screen.getByText('$1,234.56')).toBeInTheDocument();
      expect(screen.getByText('12.5%')).toBeInTheDocument();
      expect(screen.getByText('© ® ™ € ¥ £')).toBeInTheDocument();
    });
    
    test('handles empty cells and null values', () => {
      // Simulate data with empty cells
      const emptyCellData = [
        ['Name', 'Age', 'City', 'Notes'],
        ['John', '30', 'NYC', ''],
        ['Jane', '', 'LA', 'Age unknown'],
        ['Bob', '35', '', 'City unknown'],
        ['Alice', '', '', 'Minimal info']
      ];
      
      render(<DataGrid data={emptyCellData} />);
      
      // Verify empty cells are handled gracefully
      expect(screen.getByText('John')).toBeInTheDocument();
      expect(screen.getByText('30')).toBeInTheDocument();
      expect(screen.getByText('NYC')).toBeInTheDocument();
      expect(screen.getByText('Jane')).toBeInTheDocument();
      expect(screen.getByText('Age unknown')).toBeInTheDocument();
      expect(screen.getByText('City unknown')).toBeInTheDocument();
    });
  });
  
  describe('Interactive Features', () => {
    
    test('supports sorting for all data types', () => {
      const sortableData = [
        ['Name', 'Age', 'Salary'],
        ['Alice', '25', '50000'],
        ['Bob', '30', '60000'],
        ['Charlie', '28', '55000']
      ];
      
      render(<DataGrid data={sortableData} sortable={true} />);
      
      // Click on Name column header (use getAllByText to handle multiple elements)
      const nameHeaders = screen.getAllByText('Name');
      const nameHeader = nameHeaders.find(el => el.tagName === 'TH') || nameHeaders[0];
      fireEvent.click(nameHeader);
      
      // Verify sorting indicator appears
      expect(screen.getByText('↑')).toBeInTheDocument();
      
      // Click again to reverse sort
      fireEvent.click(nameHeader);
      expect(screen.getByText('↓')).toBeInTheDocument();
    });
    
    test('supports filtering for all data types', () => {
      const filterableData = [
        ['Product', 'Category', 'Price'],
        ['Laptop', 'Electronics', '999'],
        ['Phone', 'Electronics', '599'],
        ['Desk', 'Furniture', '299'],
        ['Chair', 'Furniture', '199']
      ];
      
      render(<DataGrid data={filterableData} filterable={true} />);
      
      // Find and use filter input
      const filterInput = screen.getByPlaceholderText('Filter data...');
      fireEvent.change(filterInput, { target: { value: 'Electronics' } });
      
      // Verify only electronics are shown
      expect(screen.getByText('Laptop')).toBeInTheDocument();
      expect(screen.getByText('Phone')).toBeInTheDocument();
      expect(screen.queryByText('Desk')).not.toBeInTheDocument();
      expect(screen.queryByText('Chair')).not.toBeInTheDocument();
    });
    
    test('supports cell editing for all data types', () => {
      const editableData = [
        ['Name', 'Age', 'City'],
        ['John', '30', 'NYC'],
        ['Jane', '28', 'LA']
      ];
      
      const mockOnEdit = jest.fn();
      render(<DataGrid data={editableData} onEdit={mockOnEdit} />);
      
      // Click on a cell to edit
      const johnCell = screen.getByText('John');
      fireEvent.click(johnCell);
      
      // Verify edit input appears
      const editInput = screen.getByDisplayValue('John');
      expect(editInput).toBeInTheDocument();
      
      // Change the value
      fireEvent.change(editInput, { target: { value: 'Johnny' } });
      fireEvent.blur(editInput);
      
      // Verify edit callback was called
      expect(mockOnEdit).toHaveBeenCalledWith(0, 0, 'Johnny');
    });
  });
  
  describe('Error Handling', () => {
    
    test('handles null data gracefully', () => {
      render(<DataGrid data={null as any} />);
      expect(screen.getByText('No data available')).toBeInTheDocument();
    });
    
    test('handles empty data gracefully', () => {
      render(<DataGrid data={[]} />);
      expect(screen.getByText('No data available')).toBeInTheDocument();
    });
    
    test('handles malformed data gracefully', () => {
      const malformedData = [
        ['Name', 'Age'],
        ['John'], // Missing second column
        ['Jane', '25', 'Extra'] // Extra column
      ];
      
      render(<DataGrid data={malformedData} />);
      
      // Should still render what it can
      expect(screen.getByText('Name')).toBeInTheDocument();
      expect(screen.getByText('Age')).toBeInTheDocument();
      expect(screen.getByText('John')).toBeInTheDocument();
      expect(screen.getByText('Jane')).toBeInTheDocument();
      expect(screen.getByText('25')).toBeInTheDocument();
    });
  });
}); 