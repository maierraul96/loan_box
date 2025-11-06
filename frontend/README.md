# Loan Orchestrator - Frontend

React-based frontend for the Loan Orchestrator system. Provides a UI for configuring loan processing pipelines and executing them against loan applications.

## Tech Stack

- **React** - UI library (JavaScript/JSX, not TypeScript)
- **Vite** - Build tool and dev server
- **TailwindCSS** - Utility-first CSS framework
- **shadcn/ui** - Component library built on Radix UI
- **React Query** - Data fetching and caching
- **React Router** - Client-side routing

## Features

### 1. Pipeline Builder

Configure and manage loan processing pipelines:
- Add/remove business rule steps from the available catalog
- Reorder steps via drag-and-drop
- Edit step-specific parameters
- Configure terminal rules that determine final loan status
- Save and update pipeline configurations

### 2. Run Panel

Execute pipelines against loan applications:
- Select from existing loan applications
- Choose a pipeline to run
- Execute the pipeline and view real-time results
- See detailed step-by-step logs
- View final status (APPROVED, REJECTED, or NEEDS_REVIEW)
- Review computed values from each step

### 3. Applications View

Manage loan applications:
- View all submitted applications
- See application details (name, amount, income, debts, country, purpose)
- Track application status
- Create new applications via the backend API

## Quick Start

### Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install
```

### Development

```bash
# Start development server
npm run dev
```

The application will be available at `http://localhost:5173`.

### Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/       # React components
│   │   ├── ui/          # shadcn/ui base components
│   │   └── ...          # Feature components
│   ├── lib/             # Utilities and helpers
│   ├── App.jsx          # Main application component
│   └── main.jsx         # Application entry point
├── public/              # Static assets
├── index.html           # HTML template
├── vite.config.js       # Vite configuration
├── tailwind.config.js   # TailwindCSS configuration
└── package.json         # Dependencies and scripts
```

## Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build production bundle
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint for code quality

## Component Library

This project uses shadcn/ui components, which are:
- Built on Radix UI primitives
- Fully accessible (ARIA compliant)
- Customizable with TailwindCSS
- Copy-paste friendly (not an npm dependency)

To add new shadcn/ui components:

```bash
npx shadcn@latest add [component-name]
```

## API Integration

The frontend communicates with the backend API at `http://localhost:8000`. Key endpoints:

- `GET /api/applications` - List applications
- `POST /api/applications` - Create application
- `GET /api/pipelines` - List pipelines
- `POST /api/pipelines` - Create pipeline
- `PUT /api/pipelines/:id` - Update pipeline
- `GET /api/steps/catalog` - Get available step types
- `POST /api/runs` - Execute pipeline
- `GET /api/runs/:id` - Get run details

## Step Catalog

The frontend displays four business rule types:

1. **DTI Rule** - Debt-to-Income ratio check
2. **Amount Policy** - Country-specific loan limits
3. **Risk Scoring** - Combined risk calculation
4. **Sentiment Check** - AI-powered loan purpose analysis (using OpenAI)

Each step has configurable parameters that can be adjusted in the Pipeline Builder.

## Terminal Rules

Terminal rules determine the final loan status based on step outcomes. The UI allows configuring:

- **Condition**: Logic expression (e.g., "dti_rule.failed", "risk_scoring.risk <= 45", "else")
- **Action**: Final status to set (APPROVED, REJECTED, NEEDS_REVIEW)
- **Order**: Rules are evaluated in sequence; first match wins

Example terminal rules:
```
1. sentiment_check.failed → REJECTED
2. dti_rule.failed OR amount_policy.failed → REJECTED
3. risk_scoring.risk <= 45 → APPROVED
4. else → NEEDS_REVIEW
```

## Styling

The project uses TailwindCSS for styling:
- Utility-first approach for rapid development
- Customized theme in `tailwind.config.js`
- CSS variables for theming support
- Responsive design utilities

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Development Tools

### Vite

Fast development server with:
- Hot Module Replacement (HMR)
- Optimized build with Rollup
- Fast refresh for React

### ESLint

Code quality enforcement with:
- React-specific rules
- React Hooks rules
- Recommended best practices

Configuration in `eslint.config.js`.

## Environment Variables

Create a `.env` file to customize settings:

```env
VITE_API_URL=http://localhost:8000
```

## Known Limitations

- No authentication/authorization implemented
- Pipeline execution is synchronous (no background jobs)
- Limited error handling for network failures
- No pagination for large lists

## Future Enhancements

Potential improvements:
- Real-time pipeline execution updates via WebSockets
- Pipeline versioning and history
- Bulk application import
- Advanced analytics dashboard
- Role-based access control
- Dark mode support

## Contributing

When adding new features:
1. Follow the existing component structure
2. Use JavaScript/JSX (project uses JSX, not TypeScript)
3. Ensure accessibility (use semantic HTML and ARIA)
4. Test across different screen sizes
5. Update this README with new features

## Resources

- [React Documentation](https://react.dev)
- [Vite Documentation](https://vite.dev)
- [TailwindCSS Documentation](https://tailwindcss.com)
- [shadcn/ui Documentation](https://ui.shadcn.com)
- [React Query Documentation](https://tanstack.com/query)

## License

This project was created as part of the Loan Orchestrator take-home exercise.
