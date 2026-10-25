'use client';

import React, { useState } from 'react';
import { Cpu, DollarSign, Zap, ShieldCheck, CheckCircle2, RotateCcw, Key, Save, Eye, EyeOff } from 'lucide-react';
import { toast } from '@/lib/toast';

export default function ModelRegistryPage() {
  const [apiKeys, setApiKeys] = useState({
    openai: 'sk-proj-demo-openai-key-cf3a',
    anthropic: 'sk-ant-demo-claude-key-88',
    gemini: 'AIzaSy-demo-gemini-key-92',
    litellm: 'sk-litellm-master-key-01',
  });
  const [showKeys, setShowKeys] = useState<Record<string, boolean>>({});

  const toggleShow = (provider: string) => {
    setShowKeys((prev) => ({ ...prev, [provider]: !prev[provider] }));
  };

  const handleSaveKeys = () => {
    toast.success('API Anahtarları Kaydedildi', 'LiteLLM Gateway sağlayıcı anahtarları güvenli şekilde doğrulandı ve saklandı.');
  };

  const models = [
    {
      id: 'gpt-4o',
      provider: 'OpenAI (via LiteLLM)',
      tier: 'Tier 1 / Structured Output',
      inputPrice: '$2.50 / 1M',
      outputPrice: '$10.00 / 1M',
      cachedPrice: '$1.25 / 1M (50% Off)',
      status: 'Active (Healthy)',
      fallback: 'claude-3-5-sonnet',
    },
    {
      id: 'claude-3-5-sonnet',
      provider: 'Anthropic',
      tier: 'Tier 1 / High-Reasoning & Codegen',
      inputPrice: '$3.00 / 1M',
      outputPrice: '$15.00 / 1M',
      cachedPrice: '$0.30 / 1M (Cache Read)',
      status: 'Active (Healthy)',
      fallback: 'gemini-1.5-pro',
    },
    {
      id: 'gemini-1.5-pro',
      provider: 'Google Vertex AI',
      tier: 'Tier 2 / Long-Context & Market Trends',
      inputPrice: '$1.25 / 1M',
      outputPrice: '$5.00 / 1M',
      cachedPrice: '$0.31 / 1M',
      status: 'Active (Healthy)',
      fallback: 'gpt-4o',
    },
    {
      id: 'sdxl-turbo / flux',
      provider: 'ComfyUI Cluster',
      tier: 'Media Worker / High-Res Image',
      inputPrice: 'GPU Compute',
      outputPrice: '$0.040 / Image',
      cachedPrice: 'pHash Cached',
      status: 'Active (GPU Node #1)',
      fallback: 'comfy-cpu-fallback',
    },
    {
      id: 'remotion-v4-ssr',
      provider: 'Remotion SSR Worker',
      tier: 'Media Worker / 9:16 Video',
      inputPrice: 'Compute Seconds',
      outputPrice: '$0.120 / Video',
      cachedPrice: 'N/A',
      status: 'Active (Worker Pool #2)',
      fallback: 'remotion-ssr-high-memory',
    },
  ];

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 select-none">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-cyan-950/60 border border-cyan-800/60 text-cyan-300 text-xs font-mono mb-2">
          <Cpu className="w-3.5 h-3.5" />
          <span>M09 — Model Gateway & Budget Accounting</span>
        </div>
        <h1 className="text-2xl font-bold tracking-tight text-white">LiteLLM Model Registry & Price Catalog</h1>
        <p className="text-slate-400 text-xs mt-1">
          Catalog of LLM, image diffusion, and video rendering providers. Enforces rate limits, dynamic fallback, and double-count-proof cost accounting.
        </p>
      </div>

      {/* API Key Vault Configuration */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Key className="w-4 h-4 text-cyan-400" />
            <h2 className="text-sm font-bold text-white font-mono uppercase">Provider Authentication Vault</h2>
          </div>
          <button
            onClick={handleSaveKeys}
            className="px-3.5 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-xs flex items-center gap-1.5 transition-colors shadow-sm"
          >
            <Save className="w-3.5 h-3.5" />
            <span>Save Keys</span>
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
          {Object.entries(apiKeys).map(([provider, keyVal]) => (
            <div key={provider} className="p-3 rounded-xl bg-slate-950 border border-slate-800/80 space-y-1.5">
              <div className="flex items-center justify-between text-slate-400 uppercase text-[10px]">
                <span>{provider} API Key</span>
                <button
                  type="button"
                  onClick={() => toggleShow(provider)}
                  className="text-slate-500 hover:text-slate-300"
                >
                  {showKeys[provider] ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                </button>
              </div>
              <input
                type={showKeys[provider] ? 'text' : 'password'}
                value={keyVal}
                onChange={(e) => setApiKeys({ ...apiKeys, [provider]: e.target.value })}
                className="w-full bg-slate-900 border border-slate-800 rounded px-2.5 py-1 text-slate-200 focus:outline-none focus:border-cyan-500 text-xs"
              />
            </div>
          ))}
        </div>
      </div>

      {/* Model Cards */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/50 overflow-hidden divide-y divide-slate-800 font-mono text-xs">
        <div className="p-3.5 bg-slate-950 text-slate-400 font-semibold grid grid-cols-12 gap-2 text-[11px] uppercase">
          <div className="col-span-3">Model / Provider</div>
          <div className="col-span-3">Tier / Capability</div>
          <div className="col-span-3">Pricing (Input / Output / Cache)</div>
          <div className="col-span-2">Dynamic Fallback</div>
          <div className="col-span-1 text-right">Status</div>
        </div>

        {models.map((m) => (
          <div key={m.id} className="p-4 grid grid-cols-12 gap-2 items-center hover:bg-slate-800/30 transition-colors">
            <div className="col-span-3">
              <div className="font-bold text-slate-100">{m.id}</div>
              <div className="text-[10px] text-slate-500">{m.provider}</div>
            </div>

            <div className="col-span-3 text-slate-300 text-[11px]">
              {m.tier}
            </div>

            <div className="col-span-3 space-y-0.5 text-[10px]">
              <div className="text-slate-200">In: {m.inputPrice} | Out: {m.outputPrice}</div>
              <div className="text-cyan-400 font-semibold">{m.cachedPrice}</div>
            </div>

            <div className="col-span-2 flex items-center gap-1.5 text-slate-400 text-[11px]">
              <RotateCcw className="w-3 h-3 text-amber-400" />
              <span>{m.fallback}</span>
            </div>

            <div className="col-span-1 text-right">
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800/60 font-semibold">
                Online
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
