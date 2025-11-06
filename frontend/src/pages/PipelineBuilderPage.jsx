import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useParams } from 'react-router-dom';
import { pipelines, catalog } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Select } from '@/components/ui/select';

function PipelineBuilderPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const isEditMode = Boolean(id);

  const [pipelineName, setPipelineName] = useState('');
  const [pipelineDescription, setPipelineDescription] = useState('');
  const [steps, setSteps] = useState([]);
  const [terminalRules, setTerminalRules] = useState([]);
  const [stepJsonTexts, setStepJsonTexts] = useState({}); // Track raw JSON text per step
  const [stepJsonErrors, setStepJsonErrors] = useState({}); // Track JSON validation errors

  // Fetch step catalog
  const { data: stepCatalog } = useQuery({
    queryKey: ['stepCatalog'],
    queryFn: catalog.getSteps,
  });

  // Fetch existing pipeline if in edit mode
  const { data: existingPipeline } = useQuery({
    queryKey: ['pipeline', id],
    queryFn: () => pipelines.get(id),
    enabled: isEditMode,
  });

  // Load existing pipeline data
  useEffect(() => {
    if (existingPipeline) {
      setPipelineName(existingPipeline.name);
      setPipelineDescription(existingPipeline.description || '');

      // Backend returns 'steps' with 'step_type', convert to frontend format
      const frontendSteps = (existingPipeline.steps || []).map(step => ({
        type: step.step_type,
        params: step.params || {},
      }));
      setSteps(frontendSteps);

      // Backend returns 'outcome', convert to 'action'
      const frontendRules = (existingPipeline.terminal_rules || []).map(rule => ({
        condition: rule.condition,
        action: rule.outcome,
      }));
      setTerminalRules(frontendRules);
    }
  }, [existingPipeline]);

  // Create/Update mutation
  const saveMutation = useMutation({
    mutationFn: (data) => {
      if (isEditMode) {
        return pipelines.update(id, data);
      }
      return pipelines.create(data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['pipelines']);
      navigate('/pipelines');
    },
  });

  const handleSave = () => {
    // Validate and parse step params from JSON texts
    try {
      const backendSteps = steps.map((step, index) => {
        let params = step.params || {};

        // If user edited the JSON text, parse it
        if (stepJsonTexts[index] !== undefined) {
          params = JSON.parse(stepJsonTexts[index]);
        }

        return {
          step_type: step.type,
          order: index + 1,
          params: params,
        };
      });

      const backendRules = terminalRules.map((rule, index) => ({
        condition: rule.condition,
        outcome: rule.action,
        order: index + 1,
      }));

      const data = {
        name: pipelineName,
        description: pipelineDescription,
        steps: backendSteps,
        terminal_rules: backendRules,
      };
      saveMutation.mutate(data);
    } catch (err) {
      alert(`Invalid JSON in step parameters: ${err.message}`);
    }
  };

  const addStep = () => {
    const firstStepType = stepCatalog?.[0];
    if (firstStepType) {
      setSteps([...steps, {
        type: firstStepType.step_type,
        params: firstStepType.default_params,
      }]);
    }
  };

  const removeStep = (index) => {
    setSteps(steps.filter((_, i) => i !== index));
    // Clean up JSON texts and errors for removed step and reindex remaining ones
    setStepJsonTexts(prev => {
      const updated = {};
      Object.keys(prev).forEach(key => {
        const idx = parseInt(key);
        if (idx < index) {
          updated[idx] = prev[key];
        } else if (idx > index) {
          updated[idx - 1] = prev[key];
        }
        // Skip the removed index
      });
      return updated;
    });
    setStepJsonErrors(prev => {
      const updated = {};
      Object.keys(prev).forEach(key => {
        const idx = parseInt(key);
        if (idx < index) {
          updated[idx] = prev[key];
        } else if (idx > index) {
          updated[idx - 1] = prev[key];
        }
      });
      return updated;
    });
  };

  const moveStep = (index, direction) => {
    const newSteps = [...steps];
    const targetIndex = direction === 'up' ? index - 1 : index + 1;
    if (targetIndex >= 0 && targetIndex < steps.length) {
      [newSteps[index], newSteps[targetIndex]] = [newSteps[targetIndex], newSteps[index]];
      setSteps(newSteps);
      // Also swap the cached JSON texts and errors
      setStepJsonTexts(prev => {
        const updated = { ...prev };
        const temp = updated[index];
        const targetTemp = updated[targetIndex];

        // Delete both keys first
        delete updated[index];
        delete updated[targetIndex];

        // Only set if they exist
        if (targetTemp !== undefined) updated[index] = targetTemp;
        if (temp !== undefined) updated[targetIndex] = temp;

        return updated;
      });
      setStepJsonErrors(prev => {
        const updated = { ...prev };
        const temp = updated[index];
        const targetTemp = updated[targetIndex];

        // Delete both keys first
        delete updated[index];
        delete updated[targetIndex];

        // Only set if they exist
        if (targetTemp !== undefined) updated[index] = targetTemp;
        if (temp !== undefined) updated[targetIndex] = temp;

        return updated;
      });
    }
  };

  const updateStepType = (index, type) => {
    const newSteps = [...steps];
    const stepInfo = stepCatalog?.find(s => s.step_type === type);
    newSteps[index] = {
      type,
      params: stepInfo?.default_params || {},
    };
    setSteps(newSteps);
    // Clear cached JSON text and error since params changed
    setStepJsonTexts(prev => {
      const updated = { ...prev };
      delete updated[index];
      return updated;
    });
    setStepJsonErrors(prev => {
      const updated = { ...prev };
      delete updated[index];
      return updated;
    });
  };

  const updateStepParams = (index, params) => {
    const newSteps = [...steps];
    newSteps[index].params = params;
    setSteps(newSteps);
  };

  const addTerminalRule = () => {
    setTerminalRules([...terminalRules, {
      condition: '',
      action: 'APPROVED',
    }]);
  };

  const removeTerminalRule = (index) => {
    setTerminalRules(terminalRules.filter((_, i) => i !== index));
  };

  const moveTerminalRule = (index, direction) => {
    const newRules = [...terminalRules];
    const targetIndex = direction === 'up' ? index - 1 : index + 1;
    if (targetIndex >= 0 && targetIndex < terminalRules.length) {
      [newRules[index], newRules[targetIndex]] = [newRules[targetIndex], newRules[index]];
      setTerminalRules(newRules);
    }
  };

  const updateTerminalRule = (index, field, value) => {
    const newRules = [...terminalRules];
    newRules[index][field] = value;
    setTerminalRules(newRules);
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">
          {isEditMode ? 'Edit Pipeline' : 'Create Pipeline'}
        </h1>
      </div>

      <div className="space-y-6">
        {/* Pipeline Info */}
        <Card>
          <CardHeader>
            <CardTitle>Pipeline Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Pipeline Name</Label>
              <Input
                id="name"
                value={pipelineName}
                onChange={(e) => setPipelineName(e.target.value)}
                placeholder="Enter pipeline name"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={pipelineDescription}
                onChange={(e) => setPipelineDescription(e.target.value)}
                placeholder="Enter pipeline description"
              />
            </div>
          </CardContent>
        </Card>

        {/* Steps Configuration */}
        <Card>
          <CardHeader>
            <CardTitle>Steps Configuration</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {steps.map((step, index) => (
              <Card key={index} className="border-2">
                <CardContent className="pt-6 space-y-4">
                  <div className="flex justify-between items-start">
                    <div className="flex-1 space-y-4">
                      <div className="space-y-2">
                        <Label>Step Type</Label>
                        <Select
                          value={step.type}
                          onChange={(e) => updateStepType(index, e.target.value)}
                        >
                          {stepCatalog?.map((s) => (
                            <option key={s.step_type} value={s.step_type}>
                              {s.step_type}
                            </option>
                          ))}
                        </Select>
                      </div>

                      {/* Step Parameters */}
                      <div className="space-y-2">
                        <Label>Parameters (JSON)</Label>
                        <Textarea
                          value={stepJsonTexts[index] ?? JSON.stringify(step.params, null, 2)}
                          onChange={(e) => {
                            const newText = e.target.value;
                            // Always update the text so user can type freely
                            setStepJsonTexts(prev => ({ ...prev, [index]: newText }));

                            // Validate JSON and track errors
                            try {
                              JSON.parse(newText);
                              // Valid JSON - clear error
                              setStepJsonErrors(prev => {
                                const updated = { ...prev };
                                delete updated[index];
                                return updated;
                              });
                            } catch (err) {
                              // Invalid JSON - track error
                              setStepJsonErrors(prev => ({ ...prev, [index]: err.message }));
                            }
                          }}
                          rows={4}
                          className={`font-mono text-xs ${stepJsonErrors[index] ? 'border-destructive' : ''}`}
                        />
                        {stepJsonErrors[index] && (
                          <p className="text-sm text-destructive">{stepJsonErrors[index]}</p>
                        )}
                      </div>
                    </div>

                    <div className="flex flex-col gap-2 ml-4">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => moveStep(index, 'up')}
                        disabled={index === 0}
                      >
                        ↑
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => moveStep(index, 'down')}
                        disabled={index === steps.length - 1}
                      >
                        ↓
                      </Button>
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => removeStep(index)}
                      >
                        Remove
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}

            <Button onClick={addStep} disabled={!stepCatalog}>
              Add Step
            </Button>
          </CardContent>
        </Card>

        {/* Terminal Rules */}
        <Card>
          <CardHeader>
            <CardTitle>Terminal Rules</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Rules are evaluated in order. Examples: "dti_rule.failed", "risk_scoring.risk {"<"}= 45", "else"
            </p>

            {terminalRules.map((rule, index) => (
              <Card key={index} className="border-2">
                <CardContent className="pt-6">
                  <div className="flex gap-4 items-start">
                    <div className="flex-1 space-y-4">
                      <div className="space-y-2">
                        <Label>IF (Condition)</Label>
                        <Input
                          value={rule.condition}
                          onChange={(e) => updateTerminalRule(index, 'condition', e.target.value)}
                          placeholder="e.g., dti_rule.failed OR amount_policy.failed"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label>THEN (Action)</Label>
                        <Select
                          value={rule.action}
                          onChange={(e) => updateTerminalRule(index, 'action', e.target.value)}
                        >
                          <option value="APPROVED">APPROVED</option>
                          <option value="REJECTED">REJECTED</option>
                          <option value="NEEDS_REVIEW">NEEDS_REVIEW</option>
                        </Select>
                      </div>
                    </div>

                    <div className="flex flex-col gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => moveTerminalRule(index, 'up')}
                        disabled={index === 0}
                      >
                        ↑
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => moveTerminalRule(index, 'down')}
                        disabled={index === terminalRules.length - 1}
                      >
                        ↓
                      </Button>
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => removeTerminalRule(index)}
                      >
                        Remove
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}

            <Button onClick={addTerminalRule}>
              Add Rule
            </Button>
          </CardContent>
        </Card>

        {/* Save/Cancel Buttons */}
        <div className="flex gap-4">
          <Button
            onClick={handleSave}
            disabled={!pipelineName || saveMutation.isPending || Object.keys(stepJsonErrors).length > 0}
          >
            {saveMutation.isPending ? 'Saving...' : 'Save Pipeline'}
          </Button>
          <Button
            variant="outline"
            onClick={() => navigate('/pipelines')}
          >
            Cancel
          </Button>
        </div>

        {Object.keys(stepJsonErrors).length > 0 && (
          <div className="text-destructive text-sm">
            Please fix JSON errors in step parameters before saving.
          </div>
        )}

        {saveMutation.isError && (
          <div className="text-destructive">
            Error: {saveMutation.error.message}
          </div>
        )}
      </div>
    </div>
  );
}

export default PipelineBuilderPage;
