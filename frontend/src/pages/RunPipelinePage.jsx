import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { applications, pipelines, runs } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Select } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';

function RunPipelinePage() {
  const [selectedApplicationId, setSelectedApplicationId] = useState('');
  const [selectedPipelineId, setSelectedPipelineId] = useState('');
  const [runResult, setRunResult] = useState(null);

  // Fetch applications and pipelines
  const { data: applicationsList } = useQuery({
    queryKey: ['applications'],
    queryFn: applications.list,
  });

  const { data: pipelinesList } = useQuery({
    queryKey: ['pipelines'],
    queryFn: pipelines.list,
  });

  // Execute pipeline mutation
  const executeMutation = useMutation({
    mutationFn: runs.execute,
    onSuccess: (data) => {
      setRunResult(data);
    },
  });

  const handleExecute = () => {
    if (selectedApplicationId && selectedPipelineId) {
      executeMutation.mutate({
        application_id: parseInt(selectedApplicationId),
        pipeline_id: parseInt(selectedPipelineId),
      });
    }
  };

  const getStatusBadge = (status) => {
    const variants = {
      APPROVED: 'success',
      REJECTED: 'destructive',
      NEEDS_REVIEW: 'warning',
    };
    return <Badge variant={variants[status] || 'default'}>{status}</Badge>;
  };

  const getStepStatusIcon = (passed) => {
    return passed ? '✓' : '✗';
  };

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Run Pipeline</h1>

      <div className="space-y-6">
        {/* Execution Form */}
        <Card>
          <CardHeader>
            <CardTitle>Execute Pipeline</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="application">Application</Label>
              <Select
                id="application"
                value={selectedApplicationId}
                onChange={(e) => setSelectedApplicationId(e.target.value)}
              >
                <option value="">Select an application...</option>
                {applicationsList?.map((app) => (
                  <option key={app.id} value={app.id}>
                    {app.applicant_name} ({app.amount}, {app.country})
                  </option>
                ))}
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="pipeline">Pipeline</Label>
              <Select
                id="pipeline"
                value={selectedPipelineId}
                onChange={(e) => setSelectedPipelineId(e.target.value)}
              >
                <option value="">Select a pipeline...</option>
                {pipelinesList?.map((pipeline) => (
                  <option key={pipeline.id} value={pipeline.id}>
                    {pipeline.name}
                  </option>
                ))}
              </Select>
            </div>

            <Button
              onClick={handleExecute}
              disabled={!selectedApplicationId || !selectedPipelineId || executeMutation.isPending}
            >
              {executeMutation.isPending ? 'Executing...' : 'Execute Pipeline'}
            </Button>

            {executeMutation.isError && (
              <div className="text-destructive">
                Error: {executeMutation.error.message}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Results */}
        {runResult && (
          <Card>
            <CardHeader>
              <CardTitle>Execution Results</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Summary Information */}
              <div className="grid grid-cols-2 gap-4 p-4 bg-muted rounded-lg">
                <div>
                  <span className="text-sm text-muted-foreground">Applicant:</span>
                  <div className="font-medium">
                    {runResult.application?.applicant_name || `Application #${runResult.application_id}`}
                  </div>
                </div>
                <div>
                  <span className="text-sm text-muted-foreground">Pipeline:</span>
                  <div className="font-medium">
                    {runResult.pipeline?.name || `Pipeline #${runResult.pipeline_id}`}
                  </div>
                </div>
                <div>
                  <span className="text-sm text-muted-foreground">Final Status:</span>
                  <div className="mt-1">
                    {getStatusBadge(runResult.final_status)}
                  </div>
                </div>
                <div>
                  <span className="text-sm text-muted-foreground">Executed At:</span>
                  <div className="text-sm">
                    {new Date(runResult.executed_at).toLocaleString()}
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                <h3 className="font-semibold">Step Execution Logs:</h3>
                {runResult.step_logs && runResult.step_logs.map((log, index) => (
                  <Card key={index} className="border-2">
                    <CardContent className="pt-4">
                      <div className="flex items-start gap-3">
                        <span className={`text-2xl ${log.passed ? 'text-green-600' : 'text-red-600'}`}>
                          {getStepStatusIcon(log.passed)}
                        </span>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <h4 className="font-medium">Step {index + 1}: {log.step_type}</h4>
                            <Badge variant={log.passed ? 'success' : 'destructive'}>
                              {log.passed ? 'Passed' : 'Failed'}
                            </Badge>
                          </div>
                          <div className="text-sm space-y-2">
                            {log.message && (
                              <div className="text-muted-foreground">
                                {log.message}
                              </div>
                            )}
                            {log.computed_values && Object.keys(log.computed_values).length > 0 && (
                              <div>
                                <span className="font-medium text-xs">Computed Values:</span>
                                <pre className="bg-muted p-2 rounded text-xs overflow-auto mt-1">
                                  {JSON.stringify(log.computed_values, null, 2)}
                                </pre>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              {/* Terminal Rule Logs */}
              <div className="space-y-3 mt-6">
                <h3 className="font-semibold">Terminal Rules Evaluation:</h3>
                {runResult.terminal_rule_logs && runResult.terminal_rule_logs.map((log, index) => {
                  // Determine background color based on match and outcome
                  let cardClassName = "border-2";
                  let bgColor = "";

                  if (log.matched) {
                    // Matched rule gets a light background based on outcome
                    if (log.outcome === 'APPROVED') {
                      bgColor = "bg-green-50";
                      cardClassName = "border-2 border-green-300";
                    } else if (log.outcome === 'REJECTED') {
                      bgColor = "bg-red-50";
                      cardClassName = "border-2 border-red-300";
                    } else if (log.outcome === 'NEEDS_REVIEW') {
                      bgColor = "bg-yellow-50";
                      cardClassName = "border-2 border-yellow-300";
                    }
                  } else if (!log.evaluated) {
                    // Not evaluated rules are more grayed out
                    bgColor = "bg-gray-50 opacity-80";
                    cardClassName = "border-2 border-gray-200";
                  }

                  return (
                    <Card key={index} className={`${cardClassName} ${bgColor}`}>
                      <CardContent className="pt-4">
                        <div className="flex items-start gap-3">
                          <span className={`text-2xl ${log.matched ? 'text-blue-600' : !log.evaluated ? 'text-gray-300' : 'text-gray-400'}`}>
                            {log.matched ? '→' : '○'}
                          </span>
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <h4 className={`font-medium ${!log.evaluated ? 'text-gray-400' : ''}`}>Rule {log.order}</h4>
                              {log.matched && (
                                <Badge variant="default">MATCHED</Badge>
                              )}
                              {log.evaluated && !log.matched && (
                                <Badge variant="outline">Evaluated</Badge>
                              )}
                              {!log.evaluated && (
                                <Badge variant="secondary" className="opacity-80">Not Evaluated</Badge>
                              )}
                            </div>
                            <div className={`text-sm space-y-2 ${!log.evaluated ? 'text-gray-400' : ''}`}>
                              <div>
                                <span className="font-medium">Condition:</span>{' '}
                                <code className="bg-muted px-1 py-0.5 rounded text-xs">{log.condition}</code>
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
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}

export default RunPipelinePage;
