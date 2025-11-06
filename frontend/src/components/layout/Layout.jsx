import { Link, useLocation } from 'react-router-dom';

function Layout({ children }) {
  const location = useLocation();

  const isActive = (path) => {
    if (path === '/pipelines') {
      return location.pathname === path || location.pathname.startsWith('/pipelines/');
    }
    return location.pathname === path;
  };

  const navLinks = [
    { path: '/pipelines', label: 'Pipelines' },
    { path: '/run', label: 'Run' },
    { path: '/runs', label: 'History' },
    { path: '/applications', label: 'Applications' },
  ];

  return (
    <div className="min-h-screen bg-background">
      <nav className="border-b">
        <div className="container mx-auto px-4">
          <div className="flex h-16 items-center">
            <Link to="/" className="text-xl font-bold mr-8">
              Loan Orchestrator
            </Link>
            <div className="flex gap-6">
              {navLinks.map((link) => (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`text-sm font-medium transition-colors hover:text-primary ${
                    isActive(link.path)
                      ? 'text-foreground'
                      : 'text-muted-foreground'
                  }`}
                >
                  {link.label}
                </Link>
              ))}
            </div>
          </div>
        </div>
      </nav>
      <main className="container mx-auto px-4 py-8">
        {children}
      </main>
    </div>
  );
}

export default Layout;
