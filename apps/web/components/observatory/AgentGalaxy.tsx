'use client';

import React, { useEffect, useRef, useMemo } from 'react';
import { AgentCard } from './AgentCard';
import { OrchestrationCore } from './OrchestrationCore';
import { AgentInspector } from './AgentInspector';
import { TimeTravelReplay } from './TimeTravelReplay';
import { LiveTimelineDrawer } from './LiveTimelineDrawer';
import { useAppStore } from '@/lib/store';
import { SSEStreamManager } from '@/lib/sse-client';
import { cn } from '@/lib/utils';

export function AgentGalaxy() {
  const {
    agents,
    selectedAgentId,
    setSelectedAgentId,
    activeRunId,
    observatoryTheme,
    reducedMotion,
    activeSignalPackets,
    events,
    replayStep,
  } = useAppStore();

  const containerRef = useRef<HTMLDivElement>(null);

  // Connect to SSE stream
  useEffect(() => {
    const sse = new SSEStreamManager(activeRunId);
    sse.connect();
    return () => sse.disconnect();
  }, [activeRunId]);

  // Center point
  const centerX = 540;
  const centerY = 450;

  // Compute (x, y) coordinates for each agent
  const agentPositions = useMemo(() => {
    const pos: Record<string, { x: number; y: number }> = {};
    Object.values(agents).forEach((agent) => {
      const rad = (agent.angle * Math.PI) / 180;
      pos[agent.id] = {
        x: centerX + Math.cos(rad) * agent.radius * 1.35,
        y: centerY + Math.sin(rad) * agent.radius * 0.95,
      };
    });
    return pos;
  }, [agents, centerX, centerY]);

  // Inter-agent communication links
  const links = [
    { from: 'TrendScoutAgent', to: 'HypothesisAgent' },
    { from: 'EvidenceResolverAgent', to: 'HypothesisAgent' },
    { from: 'GameDNAAgent', to: 'HypothesisAgent' },
    { from: 'GameDNAAgent', to: 'PhaserPlayableWorker' },
    { from: 'HypothesisAgent', to: 'ComfyImageWorker' },
    { from: 'ComfyImageWorker', to: 'RemotionVideoWorker' },
    { from: 'RemotionVideoWorker', to: 'LLMJudgeAgent' },
    { from: 'PhaserPlayableWorker', to: 'PlaywrightQAAgent' },
    { from: 'PlaywrightQAAgent', to: 'LLMJudgeAgent' },
    { from: 'LLMJudgeAgent', to: 'HumanReviewAgent' },
  ];

  const isNeon = observatoryTheme === 'neon';

  return (
    <div className="flex-1 flex h-full overflow-hidden relative select-none bg-[#090d16]">
      {/* Time-Travel Replay Scrubber (Top Bar) */}
      <TimeTravelReplay />

      {/* Main Galaxy Interactive Canvas */}
      <div
        ref={containerRef}
        className={cn(
          'flex-1 h-full relative overflow-auto',
          isNeon ? 'cyber-grid-neon' : 'cyber-grid-bg'
        )}
      >
        <div style={{ width: '1150px', height: '900px', position: 'relative' }}>
          {/* SVG Connection Lines & Animated Signal Particles */}
          <svg
            className="absolute inset-0 pointer-events-none"
            width="1150"
            height="900"
          >
            <defs>
              <linearGradient id="coreLineGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#00f2fe" stopOpacity="0.6" />
                <stop offset="100%" stopColor="#a855f7" stopOpacity="0.2" />
              </linearGradient>
              <linearGradient id="agentLineGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#38bdf8" stopOpacity="0.4" />
                <stop offset="100%" stopColor="#818cf8" stopOpacity="0.4" />
              </linearGradient>
            </defs>

            {/* Orbital Concentric Rings */}
            <ellipse
              cx={centerX}
              cy={centerY}
              rx={260}
              ry={200}
              fill="none"
              stroke="#1e293b"
              strokeDasharray="4 6"
              strokeWidth="1"
            />
            <ellipse
              cx={centerX}
              cy={centerY}
              rx={380}
              ry={290}
              fill="none"
              stroke="#1e293b"
              strokeDasharray="6 8"
              strokeWidth="1"
            />

            {/* Lines from Core to each Agent */}
            {Object.entries(agentPositions).map(([id, pos]) => (
              <line
                key={`core-line-${id}`}
                x1={centerX}
                y1={centerY}
                x2={pos.x}
                y2={pos.y}
                stroke="url(#coreLineGradient)"
                strokeWidth={isNeon ? '1.5' : '1'}
                strokeDasharray={isNeon ? '3 5' : '2 4'}
                opacity={0.4}
              />
            ))}

            {/* Inter-Agent Pipeline Arcs */}
            {links.map((link, idx) => {
              const p1 = agentPositions[link.from];
              const p2 = agentPositions[link.to];
              if (!p1 || !p2) return null;

              const midX = (p1.x + p2.x) / 2;
              const midY = (p1.y + p2.y) / 2;
              const pathD = `M ${p1.x} ${p1.y} Q ${midX} ${midY - 20} ${p2.x} ${p2.y}`;

              return (
                <g key={`link-${idx}`}>
                  <path
                    d={pathD}
                    fill="none"
                    stroke={isNeon ? '#00f2fe' : '#475569'}
                    strokeWidth={isNeon ? '1.8' : '1.2'}
                    opacity={isNeon ? 0.35 : 0.25}
                    strokeDasharray={isNeon ? '6 4' : undefined}
                  />
                </g>
              );
            })}

            {/* Dynamic Signal Packets (Traveling between agents strictly on real events) */}
            {activeSignalPackets.map((pkt) => {
              const p1 = pkt.from === 'Core' ? { x: centerX, y: centerY } : agentPositions[pkt.from] || { x: centerX, y: centerY };
              const p2 = agentPositions[pkt.to] || { x: centerX, y: centerY };
              const pathD = `M ${p1.x} ${p1.y} L ${p2.x} ${p2.y}`;

              return (
                <circle key={pkt.id} r="5" fill="#00f2fe" filter="drop-shadow(0 0 8px #00f2fe)">
                  <animateMotion dur="1.2s" repeatCount="1" path={pathD} />
                </circle>
              );
            })}
          </svg>

          {/* Central Orchestration Core */}
          <OrchestrationCore x={centerX} y={centerY} />

          {/* Surrounding Agent Cards */}
          {Object.values(agents).map((agent) => {
            const pos = agentPositions[agent.id] || { x: centerX, y: centerY };
            return (
              <AgentCard
                key={agent.id}
                agent={agent}
                isSelected={selectedAgentId === agent.id}
                onSelect={() => setSelectedAgentId(agent.id)}
                x={pos.x}
                y={pos.y}
              />
            );
          })}
        </div>
      </div>

      {/* Right Slide-out Agent Inspector */}
      <AgentInspector />

      {/* Bottom Live Timeline Drawer */}
      <LiveTimelineDrawer />
    </div>
  );
}
