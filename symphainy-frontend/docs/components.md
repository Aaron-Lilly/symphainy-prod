# Component Library Documentation

This document provides comprehensive documentation for all React components used in the Symphainy frontend application, including usage examples, props, and best practices.

## 📋 Table of Contents

- [Overview](#overview)
- [UI Components](#ui-components)
- [Pillar-Specific Components](#pillar-specific-components)
- [Shared Components](#shared-components)
- [Component Patterns](#component-patterns)
- [Accessibility Guidelines](#accessibility-guidelines)
- [Testing Patterns](#testing-patterns)
- [Best Practices](#best-practices)

## 🎯 Overview

The Symphainy frontend uses a comprehensive component library built on:

- **shadcn/ui** - Modern, accessible component primitives
- **Radix UI** - Unstyled, accessible UI primitives
- **Tailwind CSS** - Utility-first styling
- **TypeScript** - Type-safe component development
- **Custom Components** - Pillar-specific and business logic components

## 🧩 UI Components

### Button

A versatile button component with multiple variants and sizes.

```typescript
import { Button } from '@/components/ui/button';

// Basic usage
<Button>Click me</Button>

// Variants
<Button variant="default">Default</Button>
<Button variant="destructive">Delete</Button>
<Button variant="outline">Outline</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="ghost">Ghost</Button>
<Button variant="link">Link</Button>

// Sizes
<Button size="sm">Small</Button>
<Button size="default">Default</Button>
<Button size="lg">Large</Button>
<Button size="icon">🔍</Button>

// With icons
<Button>
  <UploadIcon className="mr-2 h-4 w-4" />
  Upload File
</Button>
```

#### Props

```typescript
interface ButtonProps {
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
  size?: 'default' | 'sm' | 'lg' | 'icon';
  asChild?: boolean;
  disabled?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
  // ... all standard button HTML attributes
}
```

### Card

A flexible card component for displaying content in containers.

```typescript
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';

<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
    <CardDescription>Card description goes here</CardDescription>
  </CardHeader>
  <CardContent>
    <p>Card content goes here</p>
  </CardContent>
  <CardFooter>
    <Button>Action</Button>
  </CardFooter>
</Card>
```

#### Card Components

- `Card` - Main container
- `CardHeader` - Header section with title and description
- `CardTitle` - Card title
- `CardDescription` - Card description
- `CardContent` - Main content area
- `CardFooter` - Footer section with actions

### Input

A styled input component for form inputs.

```typescript
import { Input } from '@/components/ui/input';

<Input 
  type="text" 
  placeholder="Enter your name" 
  value={value} 
  onChange={(e) => setValue(e.target.value)} 
/>
```

### Select

A dropdown select component with search functionality.

```typescript
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

<Select value={value} onValueChange={setValue}>
  <SelectTrigger>
    <SelectValue placeholder="Select an option" />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="option1">Option 1</SelectItem>
    <SelectItem value="option2">Option 2</SelectItem>
    <SelectItem value="option3">Option 3</SelectItem>
  </SelectContent>
</Select>
```

### Tabs

A tabbed interface component.

```typescript
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

<Tabs defaultValue="account" className="w-[400px]">
  <TabsList>
    <TabsTrigger value="account">Account</TabsTrigger>
    <TabsTrigger value="password">Password</TabsTrigger>
  </TabsList>
  <TabsContent value="account">
    Account settings content
  </TabsContent>
  <TabsContent value="password">
    Password settings content
  </TabsContent>
</Tabs>
```

### Table

A data table component with sorting and pagination.

```typescript
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

<Table>
  <TableHeader>
    <TableRow>
      <TableHead>Name</TableHead>
      <TableHead>Email</TableHead>
      <TableHead>Role</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    <TableRow>
      <TableCell>John Doe</TableCell>
      <TableCell>john@example.com</TableCell>
      <TableCell>Admin</TableCell>
    </TableRow>
  </TableBody>
</Table>
```

### Alert

A notification component for displaying messages.

```typescript
import { Alert, AlertDescription } from '@/components/ui/alert';

<Alert>
  <AlertDescription>
    This is an alert message
  </AlertDescription>
</Alert>
```

### Progress

A progress indicator component.

```typescript
import { Progress } from '@/components/ui/progress';

<Progress value={33} />
```

### Badge

A small status indicator component.

```typescript
import { Badge } from '@/components/ui/badge';

<Badge variant="default">Default</Badge>
<Badge variant="secondary">Secondary</Badge>
<Badge variant="destructive">Destructive</Badge>
<Badge variant="outline">Outline</Badge>
```

## 🏛️ Pillar-Specific Components

### Content Pillar Components

#### FileUpload

```typescript
import { FileUpload } from '@/components/content/FileUpload';

<FileUpload
  onFileSelect={(files) => console.log(files)}
  acceptedTypes={['.csv', '.xlsx', '.json']}
  maxSize={10 * 1024 * 1024} // 10MB
  multiple={true}
/>
```

#### DataGrid

```typescript
import { DataGrid } from '@/components/content/DataGrid';

<DataGrid
  data={data}
  columns={columns}
  onRowSelect={(row) => console.log(row)}
  pagination={{
    page: 1,
    pageSize: 10,
    total: 100
  }}
/>
```

### Insights Pillar Components

#### ChartContainer

```typescript
import { ChartContainer } from '@/components/insights/ChartContainer';

<ChartContainer
  data={chartData}
  type="bar"
  title="Sales Analysis"
  height={400}
  onDataPointClick={(point) => console.log(point)}
/>
```

#### InsightCard

```typescript
import { InsightCard } from '@/components/insights/InsightCard';

<InsightCard
  title="Data Quality Score"
  value={85}
  trend="up"
  description="Improved by 5% this month"
  icon={<TrendingUpIcon />}
/>
```

### Operations Pillar Components

#### WorkflowCanvas

```typescript
import { WorkflowCanvas } from '@/components/operations/WorkflowCanvas';

<WorkflowCanvas
  nodes={workflowNodes}
  edges={workflowEdges}
  onNodeAdd={(node) => console.log(node)}
  onEdgeAdd={(edge) => console.log(edge)}
  onWorkflowSave={(workflow) => console.log(workflow)}
/>
```

#### ProcessBlueprint

```typescript
import { ProcessBlueprint } from '@/components/operations/ProcessBlueprint';

<ProcessBlueprint
  blueprint={blueprintData}
  onBlueprintUpdate={(blueprint) => console.log(blueprint)}
  editable={true}
  showValidation={true}
/>
```

### Experience Pillar Components

#### TimelineView

```typescript
import { TimelineView } from '@/components/experience/TimelineView';

<TimelineView
  events={timelineEvents}
  onEventClick={(event) => console.log(event)}
  onEventAdd={(event) => console.log(event)}
  editable={true}
/>
```

#### RoadmapBuilder

```typescript
import { RoadmapBuilder } from '@/components/experience/RoadmapBuilder';

<RoadmapBuilder
  roadmap={roadmapData}
  onRoadmapUpdate={(roadmap) => console.log(roadmap)}
  onMilestoneAdd={(milestone) => console.log(milestone)}
  showTimeline={true}
/>
```

## 🔗 Shared Components

### Chatbot Components

#### PrimaryChatbot

```typescript
import { PrimaryChatbot } from '@/shared/components/chatbot/PrimaryChatbot';

<PrimaryChatbot
  sessionId={sessionId}
  onMessageSend={(message) => console.log(message)}
  onMessageReceive={(message) => console.log(message)}
  placeholder="Ask me anything..."
/>
```

#### SecondaryChatbot

```typescript
import { SecondaryChatbot } from '@/shared/components/chatbot/SecondaryChatbot';

<SecondaryChatbot
  pillar="insights"
  sessionId={sessionId}
  onMessageSend={(message) => console.log(message)}
  onMessageReceive={(message) => console.log(message)}
/>
```

### Layout Components

#### MainLayout

```typescript
import { MainLayout } from '@/shared/components/MainLayout';

<MainLayout>
  <div>Your page content</div>
</MainLayout>
```

#### ErrorBoundary

```typescript
import { ErrorBoundary } from '@/shared/components/ErrorBoundary';

<ErrorBoundary fallback={<ErrorFallback />}>
  <ComponentThatMightError />
</ErrorBoundary>
```

## 🎨 Component Patterns

### Compound Components

```typescript
// Example: Card with compound pattern
<Card>
  <Card.Header>
    <Card.Title>Title</Card.Title>
    <Card.Description>Description</Card.Description>
  </Card.Header>
  <Card.Content>Content</Card.Content>
  <Card.Footer>Footer</Card.Footer>
</Card>
```

### Render Props Pattern

```typescript
// Example: Data provider component
<DataProvider>
  {(data, loading, error) => (
    <div>
      {loading && <Loader />}
      {error && <ErrorMessage error={error} />}
      {data && <DataDisplay data={data} />}
    </div>
  )}
</DataProvider>
```

### Higher-Order Components

```typescript
// Example: withAuthentication HOC
const ProtectedComponent = withAuthentication(MyComponent);

// Usage
<ProtectedComponent requiredRole="admin" />
```

### Custom Hooks Pattern

```typescript
// Example: useData hook
const { data, loading, error, refetch } = useData('/api/data');

// Usage in component
function MyComponent() {
  const { data, loading, error } = useData('/api/users');
  
  if (loading) return <Loader />;
  if (error) return <ErrorMessage error={error} />;
  
  return <UserList users={data} />;
}
```

## ♿ Accessibility Guidelines

### ARIA Attributes

```typescript
// Example: Accessible button
<Button
  aria-label="Close dialog"
  aria-describedby="dialog-description"
  onClick={handleClose}
>
  <XIcon />
</Button>
```

### Keyboard Navigation

```typescript
// Example: Keyboard accessible dropdown
<Select onKeyDown={(e) => {
  if (e.key === 'Escape') {
    e.preventDefault();
    closeDropdown();
  }
}}>
  {/* Select content */}
</Select>
```

### Screen Reader Support

```typescript
// Example: Screen reader friendly table
<Table role="table" aria-label="User data">
  <TableHeader role="rowgroup">
    <TableRow role="row">
      <TableHead role="columnheader" scope="col">Name</TableHead>
      <TableHead role="columnheader" scope="col">Email</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody role="rowgroup">
    <TableRow role="row">
      <TableCell role="cell">John Doe</TableCell>
      <TableCell role="cell">john@example.com</TableCell>
    </TableRow>
  </TableBody>
</Table>
```

### Focus Management

```typescript
// Example: Focus trap for modal
<Modal
  onOpenChange={(open) => {
    if (open) {
      // Focus first interactive element
      firstButtonRef.current?.focus();
    }
  }}
>
  {/* Modal content */}
</Modal>
```

## 🧪 Testing Patterns

### Component Testing

```typescript
// Example: Button component test
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '@/components/ui/button';

describe('Button', () => {
  it('renders with correct text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button', { name: 'Click me' })).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('applies variant styles correctly', () => {
    render(<Button variant="destructive">Delete</Button>);
    const button = screen.getByRole('button');
    expect(button).toHaveClass('bg-destructive');
  });
});
```

### Integration Testing

```typescript
// Example: Form integration test
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { UserForm } from '@/components/UserForm';

describe('UserForm', () => {
  it('submits form data correctly', async () => {
    const onSubmit = jest.fn();
    render(<UserForm onSubmit={onSubmit} />);
    
    fireEvent.change(screen.getByLabelText('Name'), {
      target: { value: 'John Doe' }
    });
    fireEvent.change(screen.getByLabelText('Email'), {
      target: { value: 'john@example.com' }
    });
    fireEvent.click(screen.getByRole('button', { name: 'Submit' }));
    
    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({
        name: 'John Doe',
        email: 'john@example.com'
      });
    });
  });
});
```

### Accessibility Testing

```typescript
// Example: Accessibility test
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { Button } from '@/components/ui/button';

expect.extend(toHaveNoViolations);

describe('Button Accessibility', () => {
  it('should not have accessibility violations', async () => {
    const { container } = render(<Button>Click me</Button>);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
```

## 🎯 Best Practices

### 1. Component Design

- **Single Responsibility**: Each component should have one clear purpose
- **Composition Over Inheritance**: Use composition for code reuse
- **Props Interface**: Define clear TypeScript interfaces for props
- **Default Props**: Provide sensible defaults for optional props

### 2. Performance

- **Memoization**: Use `React.memo` for expensive components
- **Lazy Loading**: Lazy load components when appropriate
- **Bundle Splitting**: Split large components into smaller chunks
- **Virtual Scrolling**: Use virtual scrolling for large lists

### 3. State Management

- **Local State**: Keep component-specific state local
- **Lifted State**: Lift state up when needed by multiple components
- **Context**: Use React Context for global state sparingly
- **Custom Hooks**: Extract state logic into custom hooks

### 4. Error Handling

- **Error Boundaries**: Wrap components in error boundaries
- **Graceful Degradation**: Handle errors gracefully
- **User Feedback**: Provide clear error messages to users
- **Logging**: Log errors for debugging

### 5. Styling

- **Consistent Design**: Follow design system guidelines
- **Responsive Design**: Ensure components work on all screen sizes
- **Dark Mode**: Support both light and dark themes
- **CSS-in-JS**: Use consistent styling approach

### 6. Documentation

- **JSDoc Comments**: Document complex components
- **Storybook**: Create stories for component examples
- **Props Documentation**: Document all props and their types
- **Usage Examples**: Provide clear usage examples

## 🔗 Related Documentation

- [API Documentation](./API.md) - Service layer interfaces
- [State Management Documentation](./state-management.md) - State management patterns
- [Testing Guide](./testing.md) - Testing strategies and patterns
- [Code Quality Guide](./code-quality.md) - Best practices and standards

---

**Last Updated**: [Automated Update]
**Version**: 1.0.0 