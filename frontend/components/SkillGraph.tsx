import React, { useCallback, useEffect, useRef } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useEdgesState,
  useNodesState,
  MarkerType,
  Position,
  getRectOfNodes,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Lock, Unlock, Award } from 'lucide-react';

/**
 * SkillGraph renders the DAG of skills using React Flow.
 * It expects `nodesData` coming from the API:
 *   { nodes: NodeActivation[], summary: { mastered, unlocked, locked } }
 *   NodeActivation { skill: string, state: 'Mastered' | 'Unlocked' | 'Locked', similarity_score: number, prerequisites: string[], unmet_prerequisites?: string[] }
 */
export default function SkillGraph({ nodesData }: { nodesData: any }) {
  const initialNodes = nodesData.nodes.map((node: any, index: number) => {
    const base = {
      id: `${index}`,
      data: { label: node.skill },
      position: { x: Math.random() * 250, y: Math.random() * 250 },
      // will be overwritten by layout if needed
    } as any;

    // Styling based on state
    if (node.state === 'Mastered') {
      base.style = {
        background: '#10b981', // emerald-500
        color: '#fff',
        border: '2px solid #059669',
      };
      base.type = 'mastered';
    } else if (node.state === 'Unlocked') {
      base.style = {
        background: '#f59e0b', // amber-500
        color: '#fff',
        border: '2px solid #d97706',
        boxShadow: '0 0 10px 4px rgba(245,158,11,0.6)', // glowing
      };
      base.type = 'unlocked';
    } else {
      // Locked
      base.style = {
        background: '#374151', // gray-700
        color: '#cbd5e1', // slate-300
        opacity: 0.6,
        border: '2px solid #4b5563',
      };
      base.type = 'locked';
    }
    return base;
  });

  const initialEdges = nodesData.nodes.flatMap((node: any, idx: number) =>
    node.prerequisites.map((pre: string) => {
      // find the index of prerequisite node
      const targetIdx = nodesData.nodes.findIndex((n: any) => n.skill === pre);
      if (targetIdx === -1) return null;
      return {
        id: `e${idx}-${targetIdx}`,
        source: `${targetIdx}`,
        target: `${idx}`,
        type: 'smoothstep',
        markerEnd: { type: MarkerType.Arrow },
        animated: node.state === 'Unlocked',
      };
    }).filter(Boolean)
  );

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const reactFlowInstance = useRef<any>(null);

  // Expose a method to focus a node by skill name (called elsewhere)
  const focusNode = useCallback(
    (skill: string) => {
      const idx = nodesData.nodes.findIndex((n: any) => n.skill === skill);
      if (idx === -1) return;
      const nodeId = `${idx}`;
      const node = nodes.find((n) => n.id === nodeId);
      if (!node) return;
      const { x, y } = node.position;
      reactFlowInstance.current?.setCenter(x, y, { zoom: 1.5, duration: 800 });
    },
    [nodes, nodesData]
  );

  // Simple layout: use reactflow's built‑in dagre layout if needed — omitted for brevity.

  // Provide focusNode on window for demo (click from radar chart can call window.focusSkillNode('JavaScript'))
  useEffect(() => {
    (window as any).focusSkillNode = focusNode;
    return () => {
      delete (window as any).focusSkillNode;
    };
  }, [focusNode]);

  // Custom node components for lock icons
  const nodeTypes = {
    locked: ({ data }: any) => (
      <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
        <Lock size={16} />
        <span>{data.label}</span>
      </div>
    ),
    unlocked: ({ data }: any) => (
      <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
        <Unlock size={16} />
        <span>{data.label}</span>
      </div>
    ),
    mastered: ({ data }: any) => (
      <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
        <Award size={16} />
        <span>{data.label}</span>
      </div>
    ),
  };

  return (
    <div style={{ width: '100%', height: '600px' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
        attributionPosition="top-right"
        ref={reactFlowInstance}
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </div>
  );
}
