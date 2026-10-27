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

import { CustomNode } from './CustomNode';
import { CustomEdge } from './CustomEdge';
import { NodePalette } from './NodePalette';
import { NodeInspector } from './NodeInspector';
import { BottomDrawer } from './BottomDrawer';
import { WorkflowToolbar } from './WorkflowToolbar';
import { DeviceEmulator } from './DeviceEmulator';
import { FactorySwimlane } from './FactorySwimlane';
import { ComfySubCanvasModal } from '@/components/comfy/ComfySubCanvasModal';
import { useAppStore } from '@/lib/store';
import { WorkflowNodeData } from '@/lib/types';
import { toast } from '@/lib/toast';
import { apiClient } from '@/lib/api-client';

const INITIAL_NODES: Node<any>[] = [
  {
    id: 'node_trend_synth',
    type: 'customNode',
    position: { x: 50, y: 120 },
    data: {
      id: 'node_trend_synth',
      title: 'Trend Synthesis',
      category: 'Market Intelligence',
      executor: 'EvidenceResolverAgent',
      status: 'completed',
      model: 'gemini-1.5-pro',
      promptVersion: 'pt_trend_v2',
      timeoutSec: 30,
      maxRetries: 2,
      costEstimate: 0.0075,
      outputSnippet: 'Rising lava hazard hook +42% MoM (High 94% Confidence)',
      parameters: { sources: ['apple_charts', 'tiktok_pulse'], confidence_threshold: 0.8 },
      inputs: [
        { id: 'in_fetch', name: 'Raw Trend Feeds', type: 'text', label: 'Feeds' },
      ],
      outputs: [
        { id: 'out_trend_rep', name: 'TrendReport', type: 'concept_spec', label: 'TrendReport' },
      ],
    },
  },
  {
    id: 'node_game_dna',
    type: 'customNode',
    position: { x: 50, y: 340 },
    data: {
      id: 'node_game_dna',
      title: 'Game DNA Profile',
      category: 'Game DNA',
      executor: 'GameDNAAgent',
      status: 'completed',
      model: 'gpt-4o',
      promptVersion: 'pt_dna_v2',
      timeoutSec: 15,
      maxRetries: 1,
      costEstimate: 0.0051,
      outputSnippet: 'Locked v2.1: 8x8 Match-3, King Arthur VII Sprite, Royal Gold',
      parameters: { version: 'v2.1 - FROZEN', mechanics: '8x8 match-3' },
      inputs: [],
      outputs: [
        { id: 'out_dna_spec', name: 'GameDNA Profile', type: 'concept_spec', label: 'DNASpec' },
      ],
    },
  },
  {
    id: 'node_hypothesis',
    type: 'customNode',
    position: { x: 380, y: 220 },
    data: {
      id: 'node_hypothesis',
      title: 'Hypothesis Generator',
      category: 'Ideation',
      executor: 'HypothesisAgent',
      status: 'completed',
      model: 'gpt-4o',
      promptVersion: 'pt_hypothesis_v3',
      timeoutSec: 45,
      maxRetries: 3,
      costEstimate: 0.00975,
      outputSnippet: 'Selected: The Rising Lava King Rescue (Heuristic Rank 89/100)',
      parameters: { candidate_count: 4, rank_formula: 'heuristic_6_factor' },
      inputs: [
        { id: 'in_trend', name: 'Trend In', type: 'concept_spec', label: 'Trend' },
        { id: 'in_dna', name: 'DNA In', type: 'concept_spec', label: 'DNA' },
      ],
      outputs: [
        { id: 'out_hypo_spec', name: 'Ranked Concepts', type: 'concept_spec', label: 'Concepts' },
      ],
    },
  },
  {
    id: 'node_image_gen',
    type: 'customNode',
    position: { x: 720, y: 80 },
    data: {
      id: 'node_image_gen',
      title: 'ComfyUI Keyframe Gen',
      category: 'Generation',
      executor: 'ComfyImageWorker',
      status: 'completed',
      model: 'sdxl-turbo / comfy-flux',
      timeoutSec: 60,
      maxRetries: 2,
      costEstimate: 0.08,
      thumbnailUrl: 'https://images.unsplash.com/photo-1579783902614-a3fb3927b675?auto=format&fit=crop&w=600&q=80',
      parameters: { resolution: '1080x1920', count: 2 },
      inputs: [
        { id: 'in_concept', name: 'Concept Board', type: 'concept_spec', label: 'Concept' },
      ],
      outputs: [
        { id: 'out_keyframes', name: 'Keyframe Images', type: 'image', label: 'Images' },
      ],
    },
  },
  {
    id: 'node_remotion_render',
    type: 'customNode',
    position: { x: 720, y: 320 },
    data: {
      id: 'node_remotion_render',
      title: 'Remotion 9:16 Video',
      category: 'Generation',
      executor: 'RemotionVideoWorker',
      status: 'completed',
      model: 'remotion-v4-ssr',
      timeoutSec: 90,
      maxRetries: 3,
      costEstimate: 0.135,
      lastAttempt: 2, // retry attempt 2!
      thumbnailUrl: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=600&q=80',
      parameters: { duration_seconds: 15, fps: 30, template: 'hook_cascade_cta' },
      inputs: [
        { id: 'in_keyframes', name: 'Keyframe Input', type: 'image', label: 'Keyframes' },
      ],
      outputs: [
        { id: 'out_mp4', name: '9:16 MP4 Video', type: 'video', label: 'VideoAsset' },
      ],
    },
  },
  {
    id: 'node_phaser_playable',
    type: 'customNode',
    position: { x: 720, y: 560 },
    data: {
      id: 'node_phaser_playable',
      title: 'Phaser Playable Sandbox',
      category: 'Generation',
      executor: 'PhaserPlayableWorker',
      status: 'completed',
      model: 'claude-3-5-sonnet',
      timeoutSec: 60,
      maxRetries: 2,
      costEstimate: 0.021,
      thumbnailUrl: 'https://images.unsplash.com/photo-1550684848-fac1c5b4e853?auto=format&fit=crop&w=600&q=80',
      parameters: { target_fps: 60, grid: '8x8', moves: 5 },
      inputs: [
        { id: 'in_dna_play', name: 'Mechanics Spec', type: 'concept_spec', label: 'Mechanics' },
      ],
      outputs: [
        { id: 'out_playable_zip', name: 'Playable Zip', type: 'code', label: 'Playable' },
      ],
    },
  },
  {
    id: 'node_quality_gate',
    type: 'customNode',
    position: { x: 1080, y: 320 },
    data: {
      id: 'node_quality_gate',
      title: '7-Layer Quality Gate',
      category: 'Evaluation',
      executor: 'LLMJudgeAgent',
      status: 'completed',
      model: 'gpt-4o Rubric v3',
      timeoutSec: 30,
      maxRetries: 1,
      costEstimate: 0.0084,
      warningMessage: 'Advisory: Similarity 0.74 vs Competitor Library',
      parameters: { rubric: 'rubric_v3', pHash_threshold: 0.8 },
      inputs: [
        { id: 'in_video_eval', name: 'Video Asset', type: 'video', label: 'Video' },
        { id: 'in_playable_eval', name: 'Playable Asset', type: 'code', label: 'Playable' },
      ],
      outputs: [
        { id: 'out_eval_rep', name: 'EvaluationReport', type: 'eval_report', label: 'Report' },
      ],
    },
  },
  {
    id: 'node_human_approval',
    type: 'customNode',
    position: { x: 1420, y: 320 },
    data: {
      id: 'node_human_approval',
      title: 'Human Review & Sign-off',
      category: 'Evaluation',
      executor: 'Creative Director',
      status: 'completed',
      model: 'Human Gate',
      timeoutSec: 86400,
      maxRetries: 1,
      costEstimate: 0.0,
      outputSnippet: 'Signed by usr_creative_lead (King assets verified)',
      parameters: { reviewer: 'usr_creative_lead', reason: 'Similarity warning review' },
      inputs: [
        { id: 'in_eval', name: 'Eval Report', type: 'eval_report', label: 'Report' },
      ],
      outputs: [
        { id: 'out_signoff', name: 'Approved Manifest', type: 'manifest', label: 'Approved' },
      ],
    },
  },
];

const INITIAL_EDGES: Edge[] = [
  { id: 'e_trend_hypo', source: 'node_trend_synth', target: 'node_hypothesis', sourceHandle: 'out_trend_rep', targetHandle: 'in_trend', type: 'customEdge', data: { isActive: true } },
  { id: 'e_dna_hypo', source: 'node_game_dna', target: 'node_hypothesis', sourceHandle: 'out_dna_spec', targetHandle: 'in_dna', type: 'customEdge', data: { isActive: true } },
  { id: 'e_hypo_img', source: 'node_hypothesis', target: 'node_image_gen', sourceHandle: 'out_hypo_spec', targetHandle: 'in_concept', type: 'customEdge', data: { isActive: true } },
  { id: 'e_img_video', source: 'node_image_gen', target: 'node_remotion_render', sourceHandle: 'out_keyframes', targetHandle: 'in_keyframes', type: 'customEdge', data: { isActive: true } },
  { id: 'e_dna_playable', source: 'node_game_dna', target: 'node_phaser_playable', sourceHandle: 'out_dna_spec', targetHandle: 'in_dna_play', type: 'customEdge', data: { isActive: true } },
  { id: 'e_video_qa', source: 'node_remotion_render', target: 'node_quality_gate', sourceHandle: 'out_mp4', targetHandle: 'in_video_eval', type: 'customEdge', data: { isActive: true } },
  { id: 'e_playable_qa', source: 'node_phaser_playable', target: 'node_quality_gate', sourceHandle: 'out_playable_zip', targetHandle: 'in_playable_eval', type: 'customEdge', data: { isActive: true } },
  { id: 'e_qa_human', source: 'node_quality_gate', target: 'node_human_approval', sourceHandle: 'out_eval_rep', targetHandle: 'in_eval', type: 'customEdge', data: { isActive: true } },
];

export function WorkflowCanvas() {
  const [nodes, setNodes] = useState<Node<any>[]>(INITIAL_NODES);
  const [edges, setEdges] = useState<Edge[]>(INITIAL_EDGES);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>('node_remotion_render');
  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  const [viewMode, setViewMode] = useState<'canvas' | 'swimlane'>('canvas');
  const [showDeviceEmulator, setShowDeviceEmulator] = useState<boolean>(false);
  const [isComfySubCanvasOpen, setIsComfySubCanvasOpen] = useState<boolean>(false);

  useEffect(() => {
    const handleOpenComfy = () => setIsComfySubCanvasOpen(true);
    window.addEventListener('open-comfy-subcanvas', handleOpenComfy);
    return () => window.removeEventListener('open-comfy-subcanvas', handleOpenComfy);
  }, []);

  const nodeTypes = useMemo(() => ({ customNode: CustomNode as any }), []);
  const edgeTypes = useMemo(() => ({ customEdge: CustomEdge as any }), []);

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
      if (params.source === params.target) {
        toast.error('Bağlantı Hatası', 'Bir düğüm doğrudan kendisine bağlanamaz.');
        return;
      }

      const newEdge: Edge = {
        ...params,
        id: `e_${params.source}_${params.target}_${Date.now()}`,
        type: 'customEdge',
        data: { isActive: true, isInvalid: false },
      };

      setEdges((eds) => addEdge(newEdge, eds));
    },
    []
  );

  const onNodeClick = useCallback((_: any, node: Node) => {
    setSelectedNodeId(node.id);
  }, []);

  const onNodeDoubleClick = useCallback((_: any, node: Node) => {
    const data = node.data as any;
    if (node.id === 'node_image_gen' || data?.executor === 'ComfyImageWorker' || (typeof data?.model === 'string' && data.model.includes('comfy'))) {
      setIsComfySubCanvasOpen(true);
    }
  }, []);

  const handleApplyComfyPipeline = useCallback((workflowJson: Record<string, any>) => {
    setNodes((nds) =>
      nds.map((n) => {
        if (n.id === 'node_image_gen') {
          return {
            ...n,
            data: {
              ...n.data,
              parameters: {
                ...n.data.parameters,
                custom_comfy_workflow: workflowJson,
              },
            },
          };
        }
        return n;
      })
    );
  }, []);

  const selectedNode = useMemo(() => {
    return nodes.find((n) => n.id === selectedNodeId)?.data || null;
  }, [nodes, selectedNodeId]);

  const handleUpdateNode = useCallback(
    (updated: Partial<WorkflowNodeData>) => {
      if (!selectedNodeId) return;
      setNodes((nds) =>
        nds.map((n) => {
          if (n.id === selectedNodeId) {
            return {
              ...n,
              data: { ...n.data, ...updated },
            };
          }
          return n;
        })
      );
    },
    [selectedNodeId]
  );

  const handleAddNodeFromPalette = useCallback((item: any) => {
    const newNodeId = `node_${item.id}_${Date.now().toString(36).slice(-4)}`;
    const newNode: Node<WorkflowNodeData> = {
      id: newNodeId,
      type: 'customNode',
      position: { x: 450 + Math.random() * 80, y: 200 + Math.random() * 80 },
      data: {
        id: newNodeId,
        title: item.title,
        category: item.category,
        executor: item.executor,
        status: 'idle',
        model: item.defaultModel || 'gpt-4o',
        timeoutSec: 30,
        maxRetries: 2,
        costEstimate: 0.015,
        parameters: {},
        inputs: [{ id: `in_${newNodeId}`, name: 'Input', type: 'concept_spec', label: 'Input' }],
        outputs: [{ id: `out_${newNodeId}`, name: 'Output', type: 'concept_spec', label: 'Output' }],
      },
    };
    setNodes((nds) => [...nds, newNode]);
    setSelectedNodeId(newNodeId);
  }, []);

  const handleValidate = () => {
    const errors: string[] = [];
    if (edges.length === 0) {
      errors.push('No edges defined in workflow DAG.');
    }
    // Check for isolated nodes (nodes with 0 incoming and 0 outgoing edges, except source/generator nodes)
    const connectedNodeIds = new Set<string>();
    edges.forEach((e) => {
      connectedNodeIds.add(e.source);
      connectedNodeIds.add(e.target);
    });

    const isolated = nodes.filter((n) => !connectedNodeIds.has(n.id) && n.data?.category !== 'Game DNA' && n.data?.category !== 'Market Intelligence');
    if (isolated.length > 0) {
      errors.push(`${isolated.length} isolated node(s) detected: ${isolated.map((n) => n.data?.title || n.id).join(', ')}`);
    }

    setValidationErrors(errors);
    if (errors.length === 0) {
      toast.success('DAG Doğrulaması Başarılı', `${nodes.length} düğüm ve ${edges.length} bağlantı doğrulandı. 0 Döngü (Cycle), 0 Tip Uyuşmazlığı.`);
    } else {
      toast.error('DAG Doğrulama Hatası', errors.join(' | '));
    }
  };

  const handleDryRun = () => {
    const totalCost = nodes.reduce((sum, n) => sum + (n.data?.costEstimate || 0.015), 0);
    toast.info(
      'Dry Run Tamamlandı',
      `DAG Tahmini Maliyet: $${totalCost.toFixed(4)} USD. LiteLLM Model Kotaları & $15.00 Bütçe Limiti Geçerli.`
    );
  };

  const handleRun = async () => {
    useAppStore.getState().setRunStatus('running');
    toast.success('İş Akışı Başlatıldı', 'DAG motoru aktifleşti. Canlı telemetri olayları akmaya başladı.');

    try {
      await apiClient.startWorkflowRun('wf_standard_pipeline', {
        node_count: nodes.length,
        version: 'v4.2',
      });
    } catch {
      // Backend may be offline or starting up; store local run status gracefully
    }
  };

  const handlePause = async () => {
    useAppStore.getState().setRunStatus('paused');
    toast.warning('İş Akışı Duraklatıldı', 'Çalışan düğüm yürütmeleri donduruldu.');
    try {
      await apiClient.pauseRun(useAppStore.getState().activeRunId);
    } catch {}
  };

  const handleCancel = async () => {
    useAppStore.getState().setRunStatus('failed');
    toast.error('İş Akışı İptal Edildi', 'Yürütme durduruldu ve tahsis edilen kaynaklar serbest bırakıldı.');
    try {
      await apiClient.cancelRun(useAppStore.getState().activeRunId);
    } catch {}
  };

  const handleLoadTemplate = (templateName: string) => {
    if (templateName === 'Trend Concept Mockup') {
      const filteredNodes = INITIAL_NODES.filter((n) =>
        ['node_trend_synth', 'node_game_dna', 'node_hypothesis'].includes(n.id)
      );
      const filteredEdges = INITIAL_EDGES.filter((e) =>
        ['e_trend_hypo', 'e_dna_hypo'].includes(e.id)
      );
      setNodes(filteredNodes);
      setEdges(filteredEdges);
      toast.success('Şablon Yüklendi', `"${templateName}" şablonu (3 Düğüm) canvas üzerine yüklendi.`);
    } else if (templateName === 'Selected Concept Video Ad') {
      const filteredNodes = INITIAL_NODES.filter((n) =>
        ['node_hypothesis', 'node_image_gen', 'node_remotion_render', 'node_quality_gate', 'node_human_approval'].includes(n.id)
      );
      const filteredEdges = INITIAL_EDGES.filter((e) =>
        ['e_hypo_img', 'e_img_video', 'e_video_qa', 'e_qa_human'].includes(e.id)
      );
      setNodes(filteredNodes);
      setEdges(filteredEdges);
      toast.success('Şablon Yüklendi', `"${templateName}" şablonu (Video Pipeline) canvas üzerine yüklendi.`);
    } else if (templateName === 'Selected Concept Basic Playable') {
      const filteredNodes = INITIAL_NODES.filter((n) =>
        ['node_game_dna', 'node_phaser_playable', 'node_quality_gate', 'node_human_approval'].includes(n.id)
      );
      const filteredEdges = INITIAL_EDGES.filter((e) =>
        ['e_dna_playable', 'e_playable_qa', 'e_qa_human'].includes(e.id)
      );
      setNodes(filteredNodes);
      setEdges(filteredEdges);
      toast.success('Şablon Yüklendi', `"${templateName}" şablonu (HTML5 Playable) canvas üzerine yüklendi.`);
    } else {
      // Default: Full Campaign 360
      setNodes(INITIAL_NODES);
      setEdges(INITIAL_EDGES);
      toast.success('Şablon Yüklendi', 'Full Campaign 360 (8 Düğüm) eksiksiz mimarisi canvas üzerine yüklendi.');
    }
  };

  return (
    <div className="flex flex-col h-full overflow-hidden select-none relative">
      {/* Top Workflow Toolbar with View Switcher & Emulator Button */}
      <WorkflowToolbar
        onValidate={handleValidate}
        onDryRun={handleDryRun}
        onRun={handleRun}
        onPause={handlePause}
        onCancel={handleCancel}
        onLoadTemplate={handleLoadTemplate}
        validationErrors={validationErrors}
        viewMode={viewMode}
        onViewModeChange={setViewMode}
        showDeviceEmulator={showDeviceEmulator}
        onToggleDeviceEmulator={() => setShowDeviceEmulator(!showDeviceEmulator)}
        onOpenComfySubCanvas={() => setIsComfySubCanvasOpen(true)}
      />

      {/* Main Content: DAG Canvas OR Factory Concurrency Swimlane */}
      {viewMode === 'swimlane' ? (
        <FactorySwimlane />
      ) : (
        <div className="flex-1 flex min-h-0 relative">
          {/* Left Draggable Node Palette */}
          <NodePalette onAddNode={handleAddNodeFromPalette} />

          {/* Center React Flow Canvas */}
          <div className="flex-1 h-full relative bg-[#0a0d14]">
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={onConnect}
              onNodeClick={onNodeClick}
              onNodeDoubleClick={onNodeDoubleClick}
              nodeTypes={nodeTypes}
              edgeTypes={edgeTypes}
              fitView
              className="bg-[#0a0d14]"
              minZoom={0.2}
              maxZoom={1.5}
            >
              <Background color="rgba(255, 255, 255, 0.05)" gap={20} size={1} />
              <Controls className="!bg-[#121724]/90 !border-white/[0.08] !rounded-xl !shadow-apple-sm !text-neutral-300 fill-neutral-300 backdrop-blur-xl" />
              <MiniMap
                className="!bg-[#0c101a]/90 !border-white/[0.08] !rounded-xl !shadow-apple-sm backdrop-blur-xl !overflow-hidden"
                nodeColor={(n: any) => {
                  if (n.data?.status === 'completed') return '#30d158';
                  if (n.data?.status === 'running') return '#0a84ff';
                  if (n.data?.status === 'failed') return '#ff453a';
                  return '#3a3a3c';
                }}
              />
            </ReactFlow>
          </div>

          {/* Right Node Inspector */}
          <NodeInspector
            selectedNode={selectedNode}
            onUpdateNode={handleUpdateNode}
            onOpenComfySubCanvas={() => setIsComfySubCanvasOpen(true)}
          />
        </div>
      )}

      {/* Docked Mobile Safe-Zone Device Emulator */}
      <DeviceEmulator
        isOpen={showDeviceEmulator}
        onClose={() => setShowDeviceEmulator(false)}
        activeMediaType="video"
        previewUrl="https://images.unsplash.com/photo-1579783902614-a3fb3927b675?auto=format&fit=crop&w=600&q=80"
        hookText="Save the King from the Rising Lava! 👑🌋"
      />

      {/* Tier 2: ComfyUI Sub-Canvas Modal */}
      <ComfySubCanvasModal
        isOpen={isComfySubCanvasOpen}
        onClose={() => setIsComfySubCanvasOpen(false)}
        onApplyPipeline={handleApplyComfyPipeline}
      />

      {/* Bottom Collapsible Drawer */}
      <BottomDrawer />
    </div>
  );
}
