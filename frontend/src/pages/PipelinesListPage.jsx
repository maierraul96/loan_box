import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { pipelines } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

function PipelinesListPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data: pipelinesList, isLoading, error } = useQuery({
    queryKey: ['pipelines'],
    queryFn: pipelines.list,
  });

  const deleteMutation = useMutation({
    mutationFn: pipelines.delete,
    onSuccess: () => {
      queryClient.invalidateQueries(['pipelines']);
    },
  });

  const handleDelete = (id) => {
    if (window.confirm('Are you sure you want to delete this pipeline?')) {
      deleteMutation.mutate(id);
    }
  };

  if (isLoading) {
    return <div>Loading pipelines...</div>;
  }

  if (error) {
    return <div className="text-destructive">Error loading pipelines: {error.message}</div>;
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Pipelines</h1>
        <Button onClick={() => navigate('/pipelines/new')}>
          Create New Pipeline
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Pipelines</CardTitle>
        </CardHeader>
        <CardContent>
          {pipelinesList && pipelinesList.length === 0 ? (
            <p className="text-muted-foreground text-center py-8">
              No pipelines found. Create your first pipeline to get started.
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Description</TableHead>
                  <TableHead>Steps</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {pipelinesList?.map((pipeline) => (
                  <TableRow key={pipeline.id}>
                    <TableCell className="font-medium">{pipeline.name}</TableCell>
                    <TableCell>{pipeline.description || '-'}</TableCell>
                    <TableCell>
                      {pipeline.steps?.length || 0}
                    </TableCell>
                    <TableCell className="text-right space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => navigate(`/pipelines/${pipeline.id}/edit`)}
                      >
                        Edit
                      </Button>
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => handleDelete(pipeline.id)}
                        disabled={deleteMutation.isPending}
                      >
                        Delete
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export default PipelinesListPage;
