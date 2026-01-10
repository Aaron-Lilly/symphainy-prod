# Content Pillar Testing Checklist

## ✅ Frontend Server Status
- [x] Frontend development server running on http://localhost:3000
- [x] Content pillar page accessible at http://localhost:3000/pillars/content

## 🧪 Manual Testing Checklist

### 1. File Upload Testing
- [ ] **CSV File Upload**
  - [ ] Select "CSV" file type
  - [ ] Upload a CSV file
  - [ ] Verify file appears in File Dashboard
  - [ ] Verify file is available for parsing

- [ ] **Excel File Upload**
  - [ ] Select "Excel" file type
  - [ ] Upload an Excel file (.xlsx or .xls)
  - [ ] Verify file appears in File Dashboard
  - [ ] Verify file is available for parsing

- [ ] **PDF File Upload**
  - [ ] Select "PDF" file type
  - [ ] Upload a PDF file
  - [ ] Verify file appears in File Dashboard
  - [ ] Verify file is available for parsing

- [ ] **SOP/Workflow File Upload**
  - [ ] Select "SOP/Workflow" file type
  - [ ] Upload a .bpmn, .doc, .docx, or .xml file
  - [ ] Verify file appears in File Dashboard
  - [ ] Verify file shows "Operations" tab (not parsing)

### 2. ParsePreview Component Testing
- [ ] **File Selection**
  - [ ] Select an uploaded file from the dropdown
  - [ ] Verify file details are displayed
  - [ ] Verify parse button is available for non-SOP files

- [ ] **Parsing Functionality**
  - [ ] Click "Parse" button for CSV/Excel/PDF files
  - [ ] Verify parsing state shows loading
  - [ ] Verify parsed data is displayed in tabs

- [ ] **Tab Display Testing**
  - [ ] **Preview Tab**: Verify data grid is displayed for structured data
  - [ ] **Text Tab**: Verify extracted text is displayed for PDF/text files
  - [ ] **Info Tab**: Verify file metadata is displayed
  - [ ] **Issues Tab**: Verify warnings/errors are displayed
  - [ ] **Operations Tab**: Verify SOP/Workflow files show operations info

### 3. Data Grid Testing
- [ ] **Sorting**: Click column headers to sort data
- [ ] **Filtering**: Use search/filter functionality
- [ ] **Export**: Test export to CSV, Excel, JSON, Text formats
- [ ] **Modal Expansion**: Test "View Full Dataset" for large files

### 4. SOP/Workflow Specific Testing
- [ ] **Operations Tab Display**
  - [ ] Verify "Operations Pillar Processing" message
  - [ ] Verify "Go to Operations Pillar" button
  - [ ] Verify file information is displayed

- [ ] **Navigation to Operations**
  - [ ] Click "Go to Operations Pillar" button
  - [ ] Verify navigation to /pillars/operation
  - [ ] Verify file is available in Operations pillar

### 5. Error Handling Testing
- [ ] **Invalid File Types**
  - [ ] Try to upload unsupported file types
  - [ ] Verify appropriate error messages

- [ ] **Large Files**
  - [ ] Upload files > 10MB
  - [ ] Verify performance and error handling

- [ ] **Network Issues**
  - [ ] Simulate network failures during upload/parsing
  - [ ] Verify error messages and retry functionality

### 6. Cross-Pillar Integration Testing
- [ ] **File Sharing**
  - [ ] Upload files in Content pillar
  - [ ] Navigate to other pillars
  - [ ] Verify files are available in "select existing files"

- [ ] **Integration Hints**
  - [ ] Verify integration suggestions are displayed
  - [ ] Verify navigation buttons work correctly

## 🎯 Test Results Summary

### ✅ Passed Tests
- Frontend server accessibility
- Content pillar page loading
- Test files created for manual testing

### 🔄 Tests to Execute
- File upload functionality
- ParsePreview component behavior
- Tab switching and content display
- SOP/Workflow file handling
- Cross-pillar navigation

### 📝 Notes
- Manual testing required due to GlobalSessionProvider dependency
- Focus on end-to-end user workflows
- Verify all file types work as expected
- Test error scenarios and edge cases

## 🧪 Test Files Created
- `test-files/sample.csv` - CSV file with employee data
- `test-files/sample-workflow.bpmn` - BPMN workflow file
- `test-files/sample-text.txt` - Text file with various content

## 🚀 Ready for Manual Testing
The Content pillar is now ready for comprehensive manual testing. You can:

1. **Access the Content pillar** at: http://localhost:3000/pillars/content
2. **Use the test files** in the `test-files/` directory for upload testing
3. **Follow the checklist** above to verify all functionality
4. **Test all file types** and verify the enhanced UI components work correctly

### Key Features to Test:
- ✅ **File Upload**: All file types (CSV, Excel, PDF, SOP/Workflow, Text)
- ✅ **ParsePreview**: Enhanced tabbed interface with new components
- ✅ **SOP/Workflow Handling**: Upload-only, Operations pillar routing
- ✅ **Data Grid**: Sorting, filtering, export functionality
- ✅ **Cross-Pillar Integration**: File sharing between pillars 