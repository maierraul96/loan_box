import { useQuery } from '@tanstack/react-query';
import { applications } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';

function ApplicationsPage() {
  const { data: applicationsList, isLoading, error } = useQuery({
    queryKey: ['applications'],
    queryFn: applications.list,
  });

  const getStatusBadge = (status) => {
    if (!status) return <Badge variant="outline">PENDING</Badge>;
    const variants = {
      APPROVED: 'success',
      REJECTED: 'destructive',
      NEEDS_REVIEW: 'warning',
      PENDING: 'outline',
    };
    return <Badge variant={variants[status] || 'default'}>{status}</Badge>;
  };

  if (isLoading) {
    return <div>Loading applications...</div>;
  }

  if (error) {
    return <div className="text-destructive">Error loading applications: {error.message}</div>;
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Applications</h1>

      <Card>
        <CardHeader>
          <CardTitle>All Loan Applications</CardTitle>
        </CardHeader>
        <CardContent>
          {applicationsList && applicationsList.length === 0 ? (
            <p className="text-muted-foreground text-center py-8">
              No applications found. Applications are created via API.
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Applicant Name</TableHead>
                  <TableHead>Amount</TableHead>
                  <TableHead>Income</TableHead>
                  <TableHead>Debts</TableHead>
                  <TableHead>Country</TableHead>
                  <TableHead>Purpose</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {applicationsList?.map((app) => (
                  <TableRow key={app.id}>
                    <TableCell className="font-medium">{app.applicant_name}</TableCell>
                    <TableCell>{app.amount.toLocaleString()}</TableCell>
                    <TableCell>{app.monthly_income.toLocaleString()}</TableCell>
                    <TableCell>{app.declared_debts.toLocaleString()}</TableCell>
                    <TableCell>{app.country}</TableCell>
                    <TableCell>{app.loan_purpose || '-'}</TableCell>
                    <TableCell>{getStatusBadge(app.status)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <div className="mt-4 text-sm text-muted-foreground">
        <p>Note: Applications are created via the API. Use the Run page to execute pipelines on these applications.</p>
      </div>
    </div>
  );
}

export default ApplicationsPage;
