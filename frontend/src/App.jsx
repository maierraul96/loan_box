import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from './components/layout/Layout';
import PipelinesListPage from './pages/PipelinesListPage';
import PipelineBuilderPage from './pages/PipelineBuilderPage';
import RunPipelinePage from './pages/RunPipelinePage';
import RunHistoryPage from './pages/RunHistoryPage';
import ApplicationsPage from './pages/ApplicationsPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Navigate to="/pipelines" replace />} />
            <Route path="/pipelines" element={<PipelinesListPage />} />
            <Route path="/pipelines/new" element={<PipelineBuilderPage />} />
            <Route path="/pipelines/:id/edit" element={<PipelineBuilderPage />} />
            <Route path="/run" element={<RunPipelinePage />} />
            <Route path="/runs" element={<RunHistoryPage />} />
            <Route path="/applications" element={<ApplicationsPage />} />
          </Routes>
        </Layout>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
