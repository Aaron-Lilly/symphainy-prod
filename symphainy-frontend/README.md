# Symphainy Frontend

A modern, AI-powered business intelligence and process automation platform built with Next.js 14 and TypeScript. Symphainy provides a comprehensive suite of tools for data analysis, insights generation, process optimization, and AI-driven experience design.

## 🚀 Features

### Four Core Pillars

- **📊 Content Pillar** - Upload, parse, and manage your data files with intelligent preprocessing
- **🔍 Insights Pillar** - Generate powerful visualizations, business analysis, and AI-driven insights
- **⚙️ Operations Pillar** - Optimize workflows and processes with interactive blueprint design
- **🎯 Business Outcomes Pillar** - Build AI-powered futures with roadmap planning and timeline visualization

### Key Capabilities

- **File Management** - Upload and parse various data formats (CSV, Parquet, etc.)
- **Data Visualization** - Interactive charts, heatmaps, and advanced analytics
- **AI Assistant** - Integrated chat assistant for data analysis and insights
- **Process Design** - Visual workflow and blueprint creation
- **Real-time Updates** - WebSocket integration for live data streaming
- **Responsive Design** - Modern, mobile-first UI with dark/light theme support

## 🏗️ **Current Architecture Status**

### **Production Ready Features**
- ✅ **Modern React Architecture**: Next.js 14 with App Router and TypeScript
- ✅ **Component Library**: Shadcn/UI with Radix UI primitives for accessibility
- ✅ **State Management**: Jotai for atomic state management
- ✅ **Real-Time Integration**: WebSocket support for live updates
- ✅ **Responsive Design**: Mobile-first design with dark/light theme support
- ✅ **Testing Framework**: Jest and Playwright for comprehensive testing
- ✅ **Performance Optimized**: Code splitting, lazy loading, and optimization

### **Integration Status**
- ✅ **Backend Integration**: Connected to Symphainy Platform APIs
- ✅ **Service Layer**: Clean separation between UI and business logic
- ✅ **Authentication**: Integrated with platform authentication system
- ✅ **Multi-Tenant Support**: Frontend supports tenant isolation

## 🛠️ Tech Stack

### Core Framework

- **Next.js 14** - React framework with App Router
- **React 18** - Frontend library
- **TypeScript** - Type-safe development

### UI & Styling

- **Tailwind CSS** - Utility-first CSS framework
- **Shadcn/UI** - Modern component library
- **Radix UI** - Accessible primitives
- **Framer Motion** - Animation library
- **Lucide React** - Icon library

### Data & Visualization

- **Nivo** - Data visualization library (Bar, Line, Heatmap, Scatter)
- **Recharts** - Composable charting library
- **React Flow** - Interactive node-based diagrams

### Backend Integration

- **Supabase** - Backend-as-a-Service
- **Axios** - HTTP client
- **WebSocket** - Real-time communication

### Development & Testing

- **Jest** - Unit testing framework
- **Playwright** - End-to-end testing
- **ESLint** - Code linting
- **Babel** - JavaScript compilation

## 📦 Installation

### Prerequisites

- Node.js 18+
- npm or yarn package manager

### Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd symphainy-frontend
   ```

2. **Install dependencies**

   ```bash
   npm install
   ```

3. **Environment Configuration**
   Create a `.env.local` file in the root directory:

   ```env
   NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
   # Add other environment variables as needed
   ```

4. **Start the development server**

   ```bash
   npm run dev
   ```

5. **Open your browser**
   Navigate to [http://localhost:3000](http://localhost:3000)

## 🎯 Usage

### Getting Started

1. **Welcome Journey** - New users are guided through an onboarding experience
2. **Pillar Navigation** - Choose from four main functional areas
3. **File Upload** - Start by uploading your data files in the Content pillar
4. **Analysis** - Move to Insights pillar for data visualization and AI analysis
5. **Process Design** - Use Operations pillar for workflow optimization
6. **Future Planning** - Leverage Business Outcomes pillar for strategic roadmapping

### Pillar Descriptions

#### 📊 Content Pillar (`/pillars/content`)

- File upload and management
- Data parsing and preview
- File dashboard with metadata

#### 🔍 Insights Pillar (`/pillars/insight`)

- AI-powered data analysis
- Interactive visualizations
- Business intelligence reports
- Chat assistant for data queries

#### ⚙️ Operations Pillar (`/pillars/operation`)

- Process blueprint design
- Workflow visualization
- Interactive node-based diagrams
- Journey optimization

#### 🎯 Business Outcomes Pillar (`/pillars/business-outcomes`)

- AI future planning
- Roadmap creation
- Timeline visualization
- Strategic blueprint development

## 🧪 Development

### Available Scripts

```bash
# Development
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint

# Testing
npm run test         # Run unit tests
npm run test:unit    # Run unit tests (alias)
npm run test:e2e     # Run end-to-end tests
```

### Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[API Documentation](./docs/API.md)** - Service layer interfaces and patterns
- **[Component Library](./docs/components.md)** - Component catalog and usage
- **[State Management](./docs/state-management.md)** - Jotai patterns and session management
- **[Service Layer](./docs/services.md)** - Service architecture and patterns
- **[Configuration Guide](./docs/configuration.md)** - Environment and build configuration
- **[Installation Guide](./docs/installation.md)** - Setup and development environment
- **[Deployment Guide](./docs/deployment.md)** - Production deployment and optimization
- **[Performance Guide](./docs/performance.md)** - Optimization techniques and monitoring
- **[Troubleshooting Guide](./docs/troubleshooting.md)** - Common issues and solutions
- **[Testing Guide](./docs/testing.md)** - Testing strategies and patterns
- **[Code Quality Guide](./docs/code-quality.md)** - Best practices and standards

### Project Structure

```
symphainy-frontend/
├── app/                    # Next.js App Router pages
│   ├── pillars/           # Four main application pillars
│   │   ├── content/       # Content management
│   │   ├── business-outcomes/ # Business outcomes & strategic planning
│   │   ├── insight/       # Data analysis & visualization
│   │   ├── insights/      # Alternative insights route
│   │   └── operation/     # Process optimization
│   └── layout.tsx         # Root layout
├── components/            # React components
│   ├── content/          # Content pillar components
│   ├── insights/         # Insights pillar components
│   ├── operations/       # Operations pillar components
│   ├── business-outcomes/ # Business outcomes components
│   └── ui/              # Reusable UI components
├── lib/                  # Utilities and API clients
│   ├── api/             # API integration layer
│   ├── config.ts        # Configuration
│   └── utils.ts         # Utility functions
├── shared/              # Shared resources
│   ├── agui/           # App UI providers
│   ├── components/     # Global components
│   ├── data/          # Static data
│   └── types/         # TypeScript definitions
└── tests/              # Test files
    └── e2e/           # End-to-end tests
```

### Testing

- **Unit Tests** - Jest with React Testing Library
- **E2E Tests** - Playwright for comprehensive browser testing
- **Test Coverage** - Automated testing for all pillars and core functionality

### Code Style

- **TypeScript** - Strict type checking enabled
- **ESLint** - Configured with Next.js recommended rules
- **Prettier** - Code formatting (configure as needed)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`npm run test && npm run test:e2e`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Development Guidelines

- Follow TypeScript best practices
- Write tests for new features
- Use semantic commit messages
- Maintain responsive design principles
- Ensure accessibility standards

## 📄 License

This project is private and proprietary.

## 🆘 Support

For issues and questions:

1. Check existing issues in the repository
2. Create a new issue with detailed description
3. Include steps to reproduce for bugs
4. Provide environment details

---

**Built with ❤️ using Next.js, TypeScript, and modern web technologies**
