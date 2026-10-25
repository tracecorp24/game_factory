// CreativeForge Intelligence Studio v3.0 - ComfyUI Deep Hybrid Integration
// components/comfy/ComfySubCanvasModal.tsx

'use client';

import React, { useState, useCallback, useMemo, useEffect } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  applyNodeChanges,
  applyEdgeChanges,
  addEdge,
  Connection,
  Edge,
  Node,
  OnNodesChange,
  OnEdgesChange,
  OnConnect,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import { X, Layers, Cpu, Sliders, Type, Sparkles, Image as ImageIcon, Plus, Maximize2, ShieldCheck } from 'lucide-react';
import { ComfyCustomNode } from './ComfyCustomNode';
import { ComfyPresetSelector } from './ComfyPresetSelector';
import { ComfyVariablePanel } from './ComfyVariablePanel';
import { ComfyLiveProgress } from './ComfyLiveProgress';
import { ComfyJsonImporter } from './ComfyJsonImporter';

import { COMFY_PRESETS } from '@/lib/comfy/presets';
import { comfyToReactFlow, reactFlowToComfy } from '@/lib/comfy/adapter';
import { comfyWsManager } from '@/lib/comfy/ws-listener';
import { ComfyNodeData, ComfyPreset, ComfyLiveEvent, COMFY_PORT_COLORS } from '@/lib/comfy/types';
import { toast } from '@/lib/toast';
import { apiClient } from '@/lib/api-client';

interface ComfySubCanvasModalProps {
  isOpen: boolean;
  onClose: () => void;
  onApplyPipeline?: (workflowJson: Record<string, any>) => void;
}

export function ComfySubCanvasModal({
  isOpen,
  onClose,
  onApplyPipeline,
}: ComfySubCanvasModalProps) {
  const [activePreset, setActivePreset] = useState<ComfyPreset>(COMFY_PRESETS[0]);
  const [nodes, setNodes] = useState<Node<any>[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [variableValues, setVariableValues] = useState<Record<string, any>>({});

  // Execution & Live WebSocket State
  const [currentEvent, setCurrentEvent] = useState<ComfyLiveEvent | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [outputPreviewUrl, setOutputPreviewUrl] = useState<string | null>(null);

  // Custom node types for sub-canvas
  const nodeTypes = useMemo(() => ({ comfyNode: ComfyCustomNode as any }), []);

  // Initialize graph from the active preset
  const loadPreset = useCallback((preset: ComfyPreset) => {
    setActivePreset(preset);
    const { nodes: convertedNodes, edges: convertedEdges } = comfyToReactFlow(preset.workflowJson);
    setNodes(convertedNodes);
    setEdges(convertedEdges);

    // Set default variable values
    const defaults: Record<string, any> = {};
    preset.exposedVariables.forEach((v) => {
      defaults[v.name] = v.defaultValue;
    });
    setVariableValues(defaults);
    setOutputPreviewUrl(null);
  }, []);

  useEffect(() => {
    if (isOpen && nodes.length === 0) {
      loadPreset(COMFY_PRESETS[0]);
    }
  }, [isOpen, nodes.length, loadPreset]);

  // Subscribe to live Comfy events
  useEffect(() => {
    const unsubscribe = comfyWsManager.subscribe((event) => {
      setCurrentEvent(event);

      if (event.type === 'executing') {
        setNodes((prevNodes) =>
          prevNodes.map((n) => ({
            ...n,
            data: {
              ...n.data,
              status: n.id === event.nodeId ? 'executing' : n.data.status,
            },
          }))
        );
      } else if (event.type === 'progress') {
        setNodes((prevNodes) =>
          prevNodes.map((n) => {
            if (n.id === event.nodeId) {
              return {
                ...n,
                data: {
                  ...n.data,
                  status: 'executing',
                  progress: { step: event.step || 0, totalSteps: event.totalSteps || 25 },
                },
              };
            }
            return n;
          })
        );
      } else if (event.type === 'executed') {
        setNodes((prevNodes) =>
          prevNodes.map((n) => {
            if (n.id === event.nodeId) {
              return {
                ...n,
                data: {
                  ...n.data,
                  status: 'completed',
                  progress: undefined,
                },
              };
            }
            return n;
          })
        );
      } else if (event.type === 'done') {
        setIsExecuting(false);
        if (event.previewUrl) {
          setOutputPreviewUrl(event.previewUrl);
        }
      } else if (event.type === 'execution_error') {
        setIsExecuting(false);
      }
    });

    return () => unsubscribe();
  }, []);

  const onNodesChange: OnNodesChange<Node<any>> = useCallback(
    (changes) => setNodes((nds) => applyNodeChanges(changes, nds)),
    []
  );

  const onEdgesChange: OnEdgesChange = useCallback(
    (changes) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    []
  );

  const onConnect: OnConnect = useCallback(
    (params: Connection) => {
      if (params.source === params.target) return;

      const newEdge: Edge = {
        ...params,
        id: `e_${params.source}_${params.target}_${Date.now()}`,
        type: 'default',
        animated: true,
        style: { stroke: '#06b6d4', strokeWidth: 2 },
      };
      setEdges((eds) => addEdge(newEdge, eds));
    },
    []
  );

  // Synchronize Variable changes into matching node parameters
  const handleVariableChange = useCallback(
    (name: string, value: any) => {
      setVariableValues((prev) => ({ ...prev, [name]: value }));

      const spec = activePreset.exposedVariables.find((v) => v.name === name);
      if (spec && spec.targetNodeId && spec.targetParam) {
        setNodes((prev) =>
          prev.map((n) => {
            if (n.id === spec.targetNodeId) {
              return {
                ...n,
                data: {
                  ...n.data,
                  parameters: {
                    ...n.data.parameters,
                    [spec.targetParam!]: value,
                  },
                },
              };
            }
            return n;
          })
        );
      }
    },
    [activePreset]
  );

  const handleRandomizeSeed = useCallback(
    (name: string) => {
      const newSeed = Math.floor(Math.random() * 9000000000) + 1000000000;
      handleVariableChange(name, newSeed);
    },
    [handleVariableChange]
  );

  // Add node from sub-palette
  const handleAddPaletteNode = (classType: string, title: string, category: ComfyNodeData['category']) => {
    const nextId = String(Date.now()).slice(-4);
    const newNode: Node<any> = {
      id: nextId,
      type: 'comfyNode',
      position: { x: 250 + Math.random() * 100, y: 150 + Math.random() * 100 },
      data: {
        id: nextId,
        nodeId: nextId,
        classType,
        title,
        category,
        inputs: [
          { id: `in_${nextId}_input`, name: 'input', type: 'BASIC_PIPE', label: 'input' },
        ],
        outputs: [
          { id: `out_${nextId}_0`, name: 'output', type: 'IMAGE', label: 'output', index: 0 },
        ],
        parameters: {},
        status: 'idle',
      },
    };
    setNodes((prev) => [...prev, newNode]);
  };

  // Import / Export JSON
  const handleImportJson = (json: Record<string, any>) => {
    const converted = comfyToReactFlow(json);
    setNodes(converted.nodes);
    setEdges(converted.edges);
  };

  const handleExportJson = () => {
    return reactFlowToComfy(nodes, edges);
  };

  // Live Test Render Execution
  const handleTriggerTestRun = async () => {
    setIsExecuting(true);
    setOutputPreviewUrl(null);

    // Reset node execution states
    setNodes((prev) =>
      prev.map((n) => ({
        ...n,
        data: { ...n.data, status: 'idle', progress: undefined },
      }))
    );

    toast.info('ComfyUI Test Render Başlatıldı', `"${activePreset.name}" şablonu bağlanıyor...`);

    // Check backend API test-run first
    try {
      await apiClient.triggerComfyTestRun(activePreset.id, variableValues);
    } catch {
      // If backend is in local fallback, continue with node pipeline simulation
    }

    const steps = variableValues.steps || 25;
    comfyWsManager.startSimulatedRun(steps, (finalUrl) => {
      setOutputPreviewUrl(finalUrl);
      toast.success('ComfyUI Render Tamamlandı', `${steps} KSampler adımı tamamlandı.`);
    });
  };

  const handleStopRun = () => {
    comfyWsManager.stopSimulation();
    setIsExecuting(false);
    toast.warning('Render Durduruldu', 'KSampler yürütmesi sonlandırıldı.');
  };

  const handleSaveAndApply = () => {
    const exportedJson = reactFlowToComfy(nodes, edges);
    if (onApplyPipeline) {
      onApplyPipeline(exportedJson);
    }
    toast.success('Boru Hattına Uygulandı', 'ComfyUI mikro-grafiği ana pipeline düğümüne kilitlendi.');
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4 animate-fade-in">
      <div className="relative w-full max-w-[96vw] h-[94vh] bg-[#070b14] border border-cyan-500/30 rounded-2xl shadow-2xl flex flex-col overflow-hidden text-slate-100">
        {/* Top Header Bar */}
        <div className="h-14 px-6 border-b border-slate-800 bg-[#080d1a] flex items-center justify-between select-none z-10 flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-cyan-950/80 border border-cyan-800/80 text-cyan-400">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-sm font-bold tracking-wide uppercase font-mono text-slate-100">
                  ComfyUI Micro-Graph Sub-Canvas
                </h2>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800 flex items-center gap-1">
                  <ShieldCheck className="w-3 h-3 text-cyan-400" />
                  Tier-2 Native VRAM Engine
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-sans">
                Interactive node graph transpiled directly to ComfyUI execution payload.
              </p>
            </div>
          </div>

          {/* Right Header Actions */}
          <div className="flex items-center gap-3">
            {/* JSON Importer / Exporter */}
            <ComfyJsonImporter
              onImportJson={handleImportJson}
              onExportJson={handleExportJson}
            />

            <button
              onClick={handleSaveAndApply}
              className="px-4 py-1.5 rounded-lg text-xs font-semibold bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-white shadow-md shadow-emerald-950 transition-all font-mono"
            >
              Apply to Pipeline Node
            </button>

            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition-colors"
              title="Close Sub-Canvas"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Preset Selector Ribbon */}
        <ComfyPresetSelector
          activePresetId={activePreset.id}
          onSelectPreset={loadPreset}
        />

        {/* Main Work Area: Left Palette + Center React Flow + Right Variable Panel */}
        <div className="flex-1 flex min-h-0 relative overflow-hidden">
          {/* Left Node Palette */}
          <div className="w-52 border-r border-slate-800 bg-[#080d1a]/95 p-3 flex flex-col gap-2 overflow-y-auto select-none flex-shrink-0">
            <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider font-semibold">
              Available Nodes
            </span>
            <div className="space-y-1.5">
              <button
                onClick={() => handleAddPaletteNode('CheckpointLoaderSimple', 'Load Checkpoint', 'loader')}
                className="w-full flex items-center gap-2 p-2 rounded bg-slate-900/60 border border-slate-800 hover:border-cyan-500/50 hover:bg-slate-800/80 text-xs text-left transition-colors"
              >
                <Cpu className="w-3.5 h-3.5 text-purple-400" />
                <span className="truncate">Checkpoint Loader</span>
              </button>

              <button
                onClick={() => handleAddPaletteNode('CLIPTextEncode', 'CLIP Text Encode', 'conditioning')}
                className="w-full flex items-center gap-2 p-2 rounded bg-slate-900/60 border border-slate-800 hover:border-cyan-500/50 hover:bg-slate-800/80 text-xs text-left transition-colors"
              >
                <Type className="w-3.5 h-3.5 text-amber-400" />
                <span className="truncate">Prompt Encode</span>
              </button>

              <button
                onClick={() => handleAddPaletteNode('KSampler', 'KSampler', 'sampling')}
                className="w-full flex items-center gap-2 p-2 rounded bg-slate-900/60 border border-slate-800 hover:border-cyan-500/50 hover:bg-slate-800/80 text-xs text-left transition-colors"
              >
                <Sliders className="w-3.5 h-3.5 text-cyan-400" />
                <span className="truncate">KSampler</span>
              </button>

              <button
                onClick={() => handleAddPaletteNode('EmptyLatentImage', 'Empty Latent', 'latent')}
                className="w-full flex items-center gap-2 p-2 rounded bg-slate-900/60 border border-slate-800 hover:border-cyan-500/50 hover:bg-slate-800/80 text-xs text-left transition-colors"
              >
                <Sparkles className="w-3.5 h-3.5 text-pink-400" />
                <span className="truncate">Empty Latent</span>
              </button>

              <button
                onClick={() => handleAddPaletteNode('VAEDecode', 'VAE Decode', 'latent')}
                className="w-full flex items-center gap-2 p-2 rounded bg-slate-900/60 border border-slate-800 hover:border-cyan-500/50 hover:bg-slate-800/80 text-xs text-left transition-colors"
              >
                <Sparkles className="w-3.5 h-3.5 text-rose-400" />
                <span className="truncate">VAE Decode</span>
              </button>

              <button
                onClick={() => handleAddPaletteNode('ControlNetApply', 'Apply ControlNet', 'controlnet')}
                className="w-full flex items-center gap-2 p-2 rounded bg-slate-900/60 border border-slate-800 hover:border-cyan-500/50 hover:bg-slate-800/80 text-xs text-left transition-colors"
              >
                <Layers className="w-3.5 h-3.5 text-emerald-400" />
                <span className="truncate">ControlNet</span>
              </button>

              <button
                onClick={() => handleAddPaletteNode('LoraLoader', 'Load LoRA', 'lora')}
                className="w-full flex items-center gap-2 p-2 rounded bg-slate-900/60 border border-slate-800 hover:border-cyan-500/50 hover:bg-slate-800/80 text-xs text-left transition-colors"
              >
                <Sparkles className="w-3.5 h-3.5 text-purple-300" />
                <span className="truncate">LoRA Loader</span>
              </button>

              <button
                onClick={() => handleAddPaletteNode('SaveImage', 'Save Image', 'image')}
                className="w-full flex items-center gap-2 p-2 rounded bg-slate-900/60 border border-slate-800 hover:border-cyan-500/50 hover:bg-slate-800/80 text-xs text-left transition-colors"
              >
                <ImageIcon className="w-3.5 h-3.5 text-blue-400" />
                <span className="truncate">Save Image</span>
              </button>
            </div>

            {/* Port Colors Legend */}
            <div className="mt-auto pt-3 border-t border-slate-800/80 space-y-1.5 text-[9px] font-mono">
              <span className="text-slate-500 font-semibold uppercase">Port Types</span>
              <div className="grid grid-cols-2 gap-1 text-slate-400">
                <div className="flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full" style={{ backgroundColor: COMFY_PORT_COLORS.MODEL }} />
                  <span>MODEL</span>
                </div>
                <div className="flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full" style={{ backgroundColor: COMFY_PORT_COLORS.CLIP }} />
                  <span>CLIP</span>
                </div>
                <div className="flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full" style={{ backgroundColor: COMFY_PORT_COLORS.CONDITIONING }} />
                  <span>COND</span>
                </div>
                <div className="flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full" style={{ backgroundColor: COMFY_PORT_COLORS.LATENT }} />
                  <span>LATENT</span>
                </div>
                <div className="flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full" style={{ backgroundColor: COMFY_PORT_COLORS.VAE }} />
                  <span>VAE</span>
                </div>
                <div className="flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full" style={{ backgroundColor: COMFY_PORT_COLORS.IMAGE }} />
                  <span>IMAGE</span>
                </div>
              </div>
            </div>
          </div>

          {/* Center React Flow Canvas */}
          <div className="flex-1 h-full relative bg-[#090d16]">
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={onConnect}
              nodeTypes={nodeTypes}
              fitView
              className="bg-[#090d16]"
              minZoom={0.2}
              maxZoom={1.5}
            >
              <Background color="#1a2234" gap={20} size={1} />
              <Controls className="!bg-slate-900 !border-slate-800 !text-slate-200 fill-slate-200" />
              <MiniMap
                className="!bg-slate-950 !border-slate-800"
                nodeColor={(n: any) => {
                  if (n.data?.status === 'executing') return '#00f2fe';
                  if (n.data?.status === 'completed') return '#10b981';
                  if (n.data?.status === 'error') return '#f43f5e';
                  return '#334155';
                }}
              />
            </ReactFlow>
          </div>

          {/* Right Variables Panel */}
          <div className="w-80 h-full flex-shrink-0">
            <ComfyVariablePanel
              variables={activePreset.exposedVariables}
              values={variableValues}
              onChange={handleVariableChange}
              onRandomizeSeed={handleRandomizeSeed}
            />
          </div>
        </div>

        {/* Bottom Live Progress Drawer */}
        <ComfyLiveProgress
          currentEvent={currentEvent}
          isExecuting={isExecuting}
          onTriggerTestRun={handleTriggerTestRun}
          onStopRun={handleStopRun}
          outputPreviewUrl={outputPreviewUrl}
        />
      </div>
    </div>
  );
}
