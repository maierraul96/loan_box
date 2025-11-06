import { useState, Fragment } from 'react';
import { useQuery } from '@tanstack/react-query';
import { runs } from '@/lib/api';
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
import { Button } from '@/components/ui/button';

function RunHistoryPage() {
  const [expandedRun, setExpandedRun] = useState(null);

  const { data: runsList, isLoading, error } = useQuery({
    queryKey: ['runs'],
    queryFn: runs.list,
  });

  const getStatusBadge = (status) => {
    const variants = {
      APPROVED: 'success',
      REJECTED: 'destructive',
      NEEDS_REVIEW: 'warning',
    };
    return <Badge variant={variants[status] || 'default'}>{status}</Badge>;
  };

  const toggleExpand = (runId) => {
    setExpandedRun(expandedRun === runId ? null : runId);
  };

  if (isLoading) {
    return <div>Loading run history...</div>;
  }

  if (error) {
    return <div className="text-destructive">Error loading runs: {error.message}</div>;
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Run History</h1>

      <Card>
        <CardHeader>
          <CardTitle>All Pipeline Runs</CardTitle>
        </CardHeader>
        <CardContent>
          {runsList && runsList.length === 0 ? (
            <p className="text-muted-foreground text-center py-8">
              No runs found. Execute a pipeline to see results here.
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Application</TableHead>
                  <TableHead>Pipeline</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Executed At</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {runsList?.map((run) => (
                  <Fragment key={run.id}>
                    <TableRow>
                      <TableCell className="font-medium">
                        {run.application?.applicant_name || `App #${run.application_id}`}
                      </TableCell>
                      <TableCell>
                        {run.pipeline?.name || `Pipeline #${run.pipeline_id}`}
                      </TableCell>
                      <TableCell>{getStatusBadge(run.final_status)}</TableCell>
                      <TableCell>
                        {new Date(run.executed_at).toLocaleString()}
                      </TableCell>
                      <TableCell className="text-right">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => toggleExpand(run.id)}
                        >
                          {expandedRun === run.id ? 'Hide' : 'View'} Details
                        </Button>
                      </TableCell>
                    </TableRow>
                    {expandedRun === run.id && (
                      <TableRow>
                        <TableCell colSpan={5}>
                          <div className="space-y-4 mt-2">
                            {/* Step Logs */}
                            <Card>
                              <CardHeader>
                                <CardTitle className="text-base">Step Logs</CardTitle>
                              </CardHeader>
                              <CardContent className="space-y-3">
                                {run.step_logs && run.step_logs.map((log, index) => (
                                  <div key={index} className="border-l-4 pl-4 py-2" style={{
                                    borderLeftColor: log.passed ? '#22c55e' : '#ef4444'
                                  }}>
                                    <div className="flex items-center gap-2 mb-1">
                                      <span className={log.passed ? 'text-green-600' : 'text-red-600'}>
                                        {log.passed ? '✓' : '✗'}
                                      </span>
                                      <span className="font-medium">{log.step_type}</span>
                                      <Badge variant={log.passed ? 'success' : 'destructive'} className="ml-2">
                                        {log.passed ? 'Passed' : 'Failed'}
                                      </Badge>
                                    </div>
                                    <div className="text-xs space-y-2 mt-2">
                                      {log.message && (
                                        <div className="text-muted-foreground">
                                          {log.message}
                                        </div>
                                      )}
                                      {log.computed_values && Object.keys(log.computed_values).length > 0 && (
                                        <div>
                                          <span className="font-medium">Computed Values:</span>
                                          <pre className="bg-muted p-2 rounded overflow-auto mt-1">
                                            {JSON.stringify(log.computed_values, null, 2)}
                                          </pre>
                                        </div>
                                      )}
                                    </div>
                                  </div>
                                ))}
                              </CardContent>
                            </Card>

                            {/* Terminal Rule Logs */}
                            <Card>
                              <CardHeader>
                                <CardTitle className="text-base">Terminal Rules Evaluation</CardTitle>
                              </CardHeader>
                              <CardContent className="space-y-3">
                                {run.terminal_rule_logs && run.terminal_rule_logs.map((log, index) => (
                                  <div key={index} className="border-l-4 pl-4 py-2" style={{
                                    borderLeftColor: log.matched ? '#3b82f6' : '#d1d5db'
                                  }}>
                                    <div className="flex items-center gap-2 mb-1">
                                      <span className={log.matched ? 'text-blue-600' : 'text-gray-400'}>
                                        {log.matched ? '→' : '○'}
                                      </span>
                                      <span className="font-medium">Rule {log.order}</span>
                                      {log.matched && (
                                        <Badge variant="default" className="ml-2">MATCHED</Badge>
                                      )}
                                      {log.evaluated && !log.matched && (
                                        <Badge variant="outline" className="ml-2">Evaluated</Badge>
                                      )}
                                      {!log.evaluated && (
                                        <Badge variant="secondary" className="ml-2">Not Evaluated</Badge>
                                      )}
                                    </div>
                                    <div className="text-xs space-y-1 mt-2">
                                      <div>
                                        <span className="font-medium">Condition:</span>{' '}
                                        <code className="bg-muted px-1 py-0.5 rounded">{log.condition}</code>
                                      </div>
                                      <div>
                                        <span className="font-medium">Outcome:</span>{' '}
                                        {getStatusBadge(log.outcome)}
                                      </div>
                                      <div>
                                        <span className="font-medium">Reason:</span>{' '}
                                        <span className="text-muted-foreground">{log.reason}</span>
                                      </div>
                                    </div>
                                  </div>
                                ))}
                              </CardContent>
                            </Card>
                          </div>
                        </TableCell>
                      </TableRow>
                    )}
                  </Fragment>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export default RunHistoryPage;
