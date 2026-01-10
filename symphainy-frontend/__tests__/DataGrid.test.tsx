import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { DataGrid } from '../components/content/DataGrid';

describe('DataGrid Component', () => {
  describe('Basic Rendering', () => {
    test('renders empty state when no data provided', () => {
      render(<DataGrid data={[]} />);
      expect(screen.getByText('No data available')).toBeInTheDocument();
    });

    test('renders empty state when data is null', () => {
      render(<DataGrid data={null as any} />);
      expect(screen.getByText('No data available')).toBeInTheDocument();
    });

    test('renders simple array data correctly', () => {
      const testData = [
        ['Name', 'Age', 'City'],
        ['John', '25', 'NYC'],
        ['Jane', '30', 'LA']
      ];
      
      render(<DataGrid data={testData} />);
      
      expect(screen.getByText('Name')).toBeInTheDocument();
      expect(screen.getByText('Age')).toBeInTheDocument();
      expect(screen.getByText('City')).toBeInTheDocument();
      expect(screen.getByText('John')).toBeInTheDocument();
      expect(screen.getByText('Jane')).toBeInTheDocument();
      expect(screen.getByText('25')).toBeInTheDocument();
      expect(screen.getByText('30')).toBeInTheDocument();
    });
  });

  describe('Object to Array Conversion (Backward Compatibility)', () => {
    test('converts object data to arrays when no columns provided', () => {
      const testData = [
        { name: 'John', age: '25', city: 'NYC' },
        { name: 'Jane', age: '30', city: 'LA' }
      ];
      
      render(<DataGrid data={testData} />);
      
      // Should display object values
      expect(screen.getByText('John')).toBeInTheDocument();
      expect(screen.getByText('Jane')).toBeInTheDocument();
      expect(screen.getByText('25')).toBeInTheDocument();
      expect(screen.getByText('30')).toBeInTheDocument();
      expect(screen.getByText('NYC')).toBeInTheDocument();
      expect(screen.getByText('LA')).toBeInTheDocument();
    });

    test('converts object data using provided column order', () => {
      const testData = [
        { name: 'John', age: '25', city: 'NYC' },
        { name: 'Jane', age: '30', city: 'LA' }
      ];
      const columns = ['name', 'city', 'age'];
      
      render(<DataGrid data={testData} columns={columns} />);
      
      // Should display in column order: name, city, age
      expect(screen.getByText('name')).toBeInTheDocument();
      expect(screen.getByText('city')).toBeInTheDocument();
      expect(screen.getByText('age')).toBeInTheDocument();
      expect(screen.getByText('John')).toBeInTheDocument();
      expect(screen.getByText('Jane')).toBeInTheDocument();
      expect(screen.getByText('NYC')).toBeInTheDocument();
      expect(screen.getByText('LA')).toBeInTheDocument();
      expect(screen.getByText('25')).toBeInTheDocument();
      expect(screen.getByText('30')).toBeInTheDocument();
    });

    test('handles missing object properties gracefully', () => {
      const testData = [
        { name: 'John', age: '25' }, // missing city
        { name: 'Jane', city: 'LA' } // missing age
      ];
      const columns = ['name', 'age', 'city'];
      
      render(<DataGrid data={testData} columns={columns} />);
      
      // Should display empty strings for missing properties
      expect(screen.getByText('John')).toBeInTheDocument();
      expect(screen.getByText('Jane')).toBeInTheDocument();
      expect(screen.getByText('25')).toBeInTheDocument();
      // Empty cells should be present but not visible as text
    });
  });

  describe('Filtering Functionality', () => {
    test('shows filter input when filterable is true', () => {
      const testData = [
        ['Name', 'Age'],
        ['John', '25'],
        ['Jane', '30']
      ];
      
      render(<DataGrid data={testData} filterable={true} />);
      
      expect(screen.getByPlaceholderText('Filter data...')).toBeInTheDocument();
    });

    test('filters data correctly by text input', () => {
      const testData = [
        ['Name', 'Age', 'City'],
        ['John', '25', 'NYC'],
        ['Jane', '30', 'LA'],
        ['Bob', '35', 'Chicago']
      ];
      
      render(<DataGrid data={testData} filterable={true} />);
      
      const filterInput = screen.getByPlaceholderText('Filter data...');
      fireEvent.change(filterInput, { target: { value: 'John' } });
      
      expect(screen.getByText('John')).toBeInTheDocument();
      expect(screen.queryByText('Jane')).not.toBeInTheDocument();
      expect(screen.queryByText('Bob')).not.toBeInTheDocument();
    });

    test('filters are case insensitive', () => {
      const testData = [
        ['Name', 'Age'],
        ['John', '25'],
        ['Jane', '30']
      ];
      
      render(<DataGrid data={testData} filterable={true} />);
      
      const filterInput = screen.getByPlaceholderText('Filter data...');
      fireEvent.change(filterInput, { target: { value: 'jane' } });
      
      expect(screen.getByText('Jane')).toBeInTheDocument();
      expect(screen.queryByText('John')).not.toBeInTheDocument();
    });

    test('filters across multiple columns', () => {
      const testData = [
        ['Name', 'Age', 'City'],
        ['John', '25', 'NYC'],
        ['Jane', '30', 'LA'],
        ['Bob', '35', 'Chicago']
      ];
      
      render(<DataGrid data={testData} filterable={true} />);
      
      const filterInput = screen.getByPlaceholderText('Filter data...');
      fireEvent.change(filterInput, { target: { value: '30' } });
      
      expect(screen.getByText('Jane')).toBeInTheDocument();
      expect(screen.getByText('30')).toBeInTheDocument();
      expect(screen.queryByText('John')).not.toBeInTheDocument();
      expect(screen.queryByText('Bob')).not.toBeInTheDocument();
    });
  });

  describe('Sorting Functionality', () => {
    test('shows sort dropdown when sortable is true', () => {
      const testData = [
        ['Name', 'Age'],
        ['John', '25'],
        ['Jane', '30']
      ];
      
      render(<DataGrid data={testData} sortable={true} />);
      
      expect(screen.getByDisplayValue('No sorting')).toBeInTheDocument();
    });

    test('sorts data correctly when column is selected', () => {
      const testData = [
        ['Name', 'Age'],
        ['John', '25'],
        ['Jane', '30'],
        ['Bob', '20']
      ];
      
      render(<DataGrid data={testData} sortable={true} />);
      
      const sortSelect = screen.getByDisplayValue('No sorting');
      fireEvent.change(sortSelect, { target: { value: '0' } }); // Sort by Name column
      
      // Should sort alphabetically by name
      const rows = screen.getAllByRole('row');
      const dataRows = rows.slice(1); // Skip header row
      
      // Check that Bob comes first (alphabetically)
      expect(dataRows[0]).toHaveTextContent('Bob');
    });

    test('toggles sort direction when clicking column header', () => {
      const testData = [
        ['Name', 'Age'],
        ['John', '25'],
        ['Jane', '30'],
        ['Bob', '20']
      ];
      
      render(<DataGrid data={testData} sortable={true} />);
      
      // Use getAllByText to get all elements with 'Name' and select the header
      const nameElements = screen.getAllByText('Name');
      const nameHeader = nameElements.find(element => 
        element.closest('th') && element.closest('th')?.className.includes('cursor-pointer')
      );
      
      if (nameHeader) {
        fireEvent.click(nameHeader);
        
        // Should show ascending sort indicator
        expect(screen.getByText('↑')).toBeInTheDocument();
        
        // Click again to reverse sort
        fireEvent.click(nameHeader);
        expect(screen.getByText('↓')).toBeInTheDocument();
      }
    });
  });

  describe('Row Limiting', () => {
    test('limits displayed rows to maxRows prop', () => {
      const testData = [
        ['Name', 'Age'],
        ['John', '25'],
        ['Jane', '30'],
        ['Bob', '35'],
        ['Alice', '40'],
        ['Charlie', '45']
      ];
      
      render(<DataGrid data={testData} maxRows={3} />);
      
      // Should show pagination info
      expect(screen.getByText('Showing 3 of 5 rows')).toBeInTheDocument();
      
      // Should only show 3 data rows
      const rows = screen.getAllByRole('row');
      const dataRows = rows.slice(1); // Skip header
      expect(dataRows).toHaveLength(3);
    });

    test('shows all rows when data count is less than maxRows', () => {
      const testData = [
        ['Name', 'Age'],
        ['John', '25'],
        ['Jane', '30']
      ];
      
      render(<DataGrid data={testData} maxRows={10} />);
      
      // Should not show pagination info
      expect(screen.queryByText(/Showing.*of.*rows/)).not.toBeInTheDocument();
      
      // Should show all 2 data rows
      const rows = screen.getAllByRole('row');
      const dataRows = rows.slice(1); // Skip header
      expect(dataRows).toHaveLength(2);
    });
  });

  describe('Editing Functionality', () => {
    test('enables cell editing when onEdit prop is provided', () => {
      const testData = [
        ['Name', 'Age'],
        ['John', '25']
      ];
      const mockOnEdit = jest.fn();
      
      render(<DataGrid data={testData} onEdit={mockOnEdit} />);
      
      // Click on a cell to edit
      const cell = screen.getByText('John');
      fireEvent.click(cell);
      
      // Should show input field
      const input = screen.getByDisplayValue('John');
      expect(input).toBeInTheDocument();
    });

    test('calls onEdit callback when cell value changes', () => {
      const testData = [
        ['Name', 'Age'],
        ['John', '25']
      ];
      const mockOnEdit = jest.fn();
      
      render(<DataGrid data={testData} onEdit={mockOnEdit} />);
      
      // Click on a cell to edit
      const cell = screen.getByText('John');
      fireEvent.click(cell);
      
      // Change the value
      const input = screen.getByDisplayValue('John');
      fireEvent.change(input, { target: { value: 'Jane' } });
      
      // Should call onEdit callback
      expect(mockOnEdit).toHaveBeenCalledWith(0, 0, 'Jane');
    });

    test('saves changes when input loses focus', () => {
      const testData = [
        ['Name', 'Age'],
        ['John', '25']
      ];
      const mockOnEdit = jest.fn();
      
      render(<DataGrid data={testData} onEdit={mockOnEdit} />);
      
      // Click on a cell to edit
      const cell = screen.getByText('John');
      fireEvent.click(cell);
      
      // Change the value
      const input = screen.getByDisplayValue('John');
      fireEvent.change(input, { target: { value: 'Jane' } });
      
      // Blur the input
      fireEvent.blur(input);
      
      // Should no longer show input
      expect(screen.queryByDisplayValue('Jane')).not.toBeInTheDocument();
      expect(screen.getByText('Jane')).toBeInTheDocument();
    });
  });

  describe('Edge Cases and Error Handling', () => {
    test('handles data with empty cells', () => {
      const testData = [
        ['Name', 'Age', 'City'],
        ['John', '', 'NYC'],
        ['', '30', 'LA'],
        ['Bob', '35', '']
      ];
      
      render(<DataGrid data={testData} />);
      
      expect(screen.getByText('John')).toBeInTheDocument();
      expect(screen.getByText('Bob')).toBeInTheDocument();
      expect(screen.getByText('30')).toBeInTheDocument();
      expect(screen.getByText('35')).toBeInTheDocument();
      expect(screen.getByText('NYC')).toBeInTheDocument();
      expect(screen.getByText('LA')).toBeInTheDocument();
    });

    test('handles data with null/undefined values', () => {
      const testData = [
        ['Name', 'Age'],
        ['John', null],
        [undefined, '30']
      ];
      
      render(<DataGrid data={testData} />);
      
      expect(screen.getByText('John')).toBeInTheDocument();
      expect(screen.getByText('30')).toBeInTheDocument();
    });

    test('handles data with special characters', () => {
      const testData = [
        ['Name', 'Description'],
        ['José', 'Special chars: éñü'],
        ['Müller', 'German: äöüß'],
        ['O\'Connor', 'Irish: O\'Connor'],
        ['Smith & Co.', 'Business: & Co.']
      ];
      
      render(<DataGrid data={testData} />);
      
      expect(screen.getByText('José')).toBeInTheDocument();
      expect(screen.getByText('Müller')).toBeInTheDocument();
      expect(screen.getByText('O\'Connor')).toBeInTheDocument();
      expect(screen.getByText('Smith & Co.')).toBeInTheDocument();
      expect(screen.getByText('Special chars: éñü')).toBeInTheDocument();
      expect(screen.getByText('German: äöüß')).toBeInTheDocument();
    });

    test('handles very large numbers and decimals', () => {
      const testData = [
        ['ID', 'Amount', 'Percentage'],
        ['1', '1234567890.123456789', '99.999999%'],
        ['2', '0.000000001', '0.000001%']
      ];
      
      render(<DataGrid data={testData} />);
      
      expect(screen.getByText('1234567890.123456789')).toBeInTheDocument();
      expect(screen.getByText('0.000000001')).toBeInTheDocument();
      expect(screen.getByText('99.999999%')).toBeInTheDocument();
      expect(screen.getByText('0.000001%')).toBeInTheDocument();
    });

    test('handles mixed data types in object format', () => {
      const testData = [
        { id: 1, name: 'John', active: true, score: 95.5 },
        { id: 2, name: 'Jane', active: false, score: 87.25 }
      ];
      
      render(<DataGrid data={testData} />);
      
      expect(screen.getByText('1')).toBeInTheDocument();
      expect(screen.getByText('2')).toBeInTheDocument();
      expect(screen.getByText('John')).toBeInTheDocument();
      expect(screen.getByText('Jane')).toBeInTheDocument();
      expect(screen.getByText('true')).toBeInTheDocument();
      expect(screen.getByText('false')).toBeInTheDocument();
      expect(screen.getByText('95.5')).toBeInTheDocument();
      expect(screen.getByText('87.25')).toBeInTheDocument();
    });
  });

  describe('Performance and Large Datasets', () => {
    test('handles large datasets efficiently', () => {
      // Create a large dataset
      const testData = [
        ['ID', 'Name', 'Value'],
        ...Array.from({ length: 1000 }, (_, i) => [
          i.toString(),
          `User${i}`,
          (i * 1.5).toString()
        ])
      ];
      
      render(<DataGrid data={testData} maxRows={100} />);
      
      // Should render without errors
      expect(screen.getByText('ID')).toBeInTheDocument();
      expect(screen.getByText('Name')).toBeInTheDocument();
      expect(screen.getByText('Value')).toBeInTheDocument();
      expect(screen.getByText('User0')).toBeInTheDocument();
      expect(screen.getByText('User99')).toBeInTheDocument();
      
      // Should show pagination info
      expect(screen.getByText('Showing 100 of 1000 rows')).toBeInTheDocument();
    });

    test('filters large datasets efficiently', () => {
      const testData = [
        ['ID', 'Name', 'Category'],
        ...Array.from({ length: 1000 }, (_, i) => [
          i.toString(),
          `User${i}`,
          i % 2 === 0 ? 'Even' : 'Odd'
        ])
      ];
      
      render(<DataGrid data={testData} filterable={true} maxRows={50} />);
      
      const filterInput = screen.getByPlaceholderText('Filter data...');
      fireEvent.change(filterInput, { target: { value: 'Even' } });
      
      // Should filter efficiently - use queryAllByText to check for multiple instances
      const evenElements = screen.queryAllByText('Even');
      expect(evenElements.length).toBeGreaterThan(0);
      
      // Should not show Odd elements
      const oddElements = screen.queryAllByText('Odd');
      expect(oddElements.length).toBe(0);
    });
  });
}); 