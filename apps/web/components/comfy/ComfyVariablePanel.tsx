// CreativeForge Intelligence Studio v3.0 - ComfyUI Deep Hybrid Integration
// components/comfy/ComfyVariablePanel.tsx

'use client';

import React from 'react';
import { Sliders, Dices, Sparkles, Hash, AlignLeft, Info } from 'lucide-react';
import { ComfyVariableSpec } from '@/lib/comfy/types';

interface ComfyVariablePanelProps {
  variables: ComfyVariableSpec[];
  values: Record<string, any>;
  onChange: (name: string, value: any) => void;
  onRandomizeSeed: (name: string) => void;
}

export function ComfyVariablePanel({
  variables,
  values,
  onChange,
  onRandomizeSeed,
}: ComfyVariablePanelProps) {
  return (
    <div className="flex flex-col h-full bg-[#070b14] border-l border-slate-800 p-4 space-y-4 overflow-y-auto select-none">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Sliders className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider font-mono">
            Exposed Pipeline Hooks
          </h3>
        </div>
        <span className="text-[10px] font-mono text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800/60">
          Tier-1 Bindings
        </span>
      </div>

      <p className="text-[11px] text-slate-400 leading-relaxed">
        High-level parameters injected dynamically from Game DNA and Hypothesis agents into this ComfyUI micro-graph.
      </p>

      <div className="space-y-4">
        {variables.map((variable) => {
          const val = values[variable.name] ?? variable.defaultValue;

          if (variable.type === 'string') {
            return (
              <div key={variable.name} className="space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <label className="font-medium text-slate-300 flex items-center gap-1.5">
                    <AlignLeft className="w-3.5 h-3.5 text-blue-400" />
                    <span>{variable.label}</span>
                  </label>
                  <span className="text-[10px] font-mono text-slate-500">{`\${${variable.name}}`}</span>
                </div>
                <textarea
                  rows={3}
                  value={val}
                  onChange={(e) => onChange(variable.name, e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-md p-2.5 text-xs text-slate-100 font-sans focus:outline-none focus:border-cyan-500 leading-relaxed resize-none"
                  placeholder={`Enter ${variable.label.toLowerCase()}...`}
                />
                {variable.description && (
                  <p className="text-[10px] text-slate-500">{variable.description}</p>
                )}
              </div>
            );
          }

          if (variable.type === 'slider') {
            const min = variable.min ?? 1;
            const max = variable.max ?? 50;
            const step = variable.step ?? 1;

            return (
              <div key={variable.name} className="space-y-2 bg-slate-900/40 p-3 rounded-lg border border-slate-800/80">
                <div className="flex items-center justify-between text-xs">
                  <label className="font-medium text-slate-300 flex items-center gap-1.5">
                    <Sliders className="w-3.5 h-3.5 text-cyan-400" />
                    <span>{variable.label}</span>
                  </label>
                  <span className="font-mono text-cyan-300 font-semibold">{val}</span>
                </div>
                <input
                  type="range"
                  min={min}
                  max={max}
                  step={step}
                  value={val}
                  onChange={(e) => onChange(variable.name, parseFloat(e.target.value))}
                  className="w-full accent-cyan-400 cursor-pointer h-1.5 bg-slate-800 rounded"
                />
                <div className="flex justify-between text-[9px] font-mono text-slate-500">
                  <span>{min}</span>
                  <span>{max}</span>
                </div>
              </div>
            );
          }

          if (variable.type === 'number') {
            return (
              <div key={variable.name} className="space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <label className="font-medium text-slate-300 flex items-center gap-1.5">
                    <Hash className="w-3.5 h-3.5 text-purple-400" />
                    <span>{variable.label}</span>
                  </label>
                  {variable.name.includes('seed') && (
                    <button
                      type="button"
                      onClick={() => onRandomizeSeed(variable.name)}
                      className="flex items-center gap-1 text-[10px] font-mono text-purple-300 hover:text-purple-200 bg-purple-950/60 px-1.5 py-0.5 rounded border border-purple-800/60 transition-colors"
                      title="Randomize seed value"
                    >
                      <Dices className="w-3 h-3" />
                      Randomize
                    </button>
                  )}
                </div>
                <input
                  type="number"
                  value={val}
                  onChange={(e) => onChange(variable.name, parseInt(e.target.value, 10) || 0)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-md px-3 py-1.5 text-xs font-mono text-cyan-300 focus:outline-none focus:border-cyan-500"
                />
              </div>
            );
          }

          return null;
        })}
      </div>

      <div className="pt-3 border-t border-slate-800 text-[10px] text-slate-500 flex items-start gap-1.5">
        <Info className="w-3.5 h-3.5 text-slate-400 flex-shrink-0 mt-0.5" />
        <span>
          Variables sync immediately with the visual React Flow nodes and the ComfyUI Daemon execution payload.
        </span>
      </div>
    </div>
  );
}
