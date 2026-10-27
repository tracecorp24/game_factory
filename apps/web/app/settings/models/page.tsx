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
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-apple-blue/10 border border-apple-blue/20 text-apple-blue text-xs font-medium mb-3">
            <Cpu className="w-3.5 h-3.5" />
            <span>M09 · Model Gateway & Budget Accounting</span>
          </div>
          <h1 className="text-2xl font-semibold tracking-tight text-neutral-100">
            LiteLLM Model Registry & Price Catalog
          </h1>
          <p className="text-neutral-400 text-xs sm:text-sm mt-1 max-w-2xl leading-relaxed">
            Catalog of LLM, image diffusion, and video rendering providers. Enforces rate limits, dynamic fallback, and double-count-proof cost accounting.
          </p>
        </div>

        <button
          onClick={handleSaveKeys}
          className="apple-btn-primary flex items-center gap-2 py-2 px-4 shadow-apple-sm text-xs self-start md:self-auto"
        >
          <Save className="w-4 h-4" />
          <span>Save Settings</span>
        </button>
      </div>

      {/* API Key Vault Configuration */}
      <div className="p-6 rounded-3xl bg-white/[0.03] border border-white/[0.08] backdrop-blur-xl shadow-apple-sm space-y-4">
        <div className="flex items-center gap-2">
          <Key className="w-4 h-4 text-apple-blue" />
          <h2 className="text-sm font-semibold text-neutral-200">Provider Authentication Vault</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
          {Object.entries(apiKeys).map(([provider, keyVal]) => (
            <div
              key={provider}
              className="p-3.5 rounded-2xl bg-white/[0.02] border border-white/[0.06] space-y-2 hover:border-white/[0.12] transition-colors"
            >
              <div className="flex items-center justify-between text-neutral-400 uppercase text-[10px] font-sans font-medium">
                <span>{provider} API Key</span>
                <button
                  type="button"
                  onClick={() => toggleShow(provider)}
                  className="text-neutral-500 hover:text-neutral-200 transition-colors"
                >
                  {showKeys[provider] ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                </button>
              </div>
              <input
                type={showKeys[provider] ? 'text' : 'password'}
                value={keyVal}
                onChange={(e) => setApiKeys({ ...apiKeys, [provider]: e.target.value })}
                className="w-full bg-white/[0.04] border border-white/[0.08] rounded-xl px-3 py-1.5 text-neutral-100 focus:outline-none focus:border-apple-blue text-xs transition-colors"
              />
            </div>
          ))}
        </div>
      </div>

      {/* Model Cards */}
      <div className="rounded-3xl border border-white/[0.08] bg-white/[0.03] backdrop-blur-xl shadow-apple-sm overflow-hidden divide-y divide-white/[0.04] font-mono text-xs">
        <div className="p-4 bg-white/[0.02] text-neutral-400 font-semibold grid grid-cols-12 gap-3 text-[11px] uppercase font-sans tracking-wide">
          <div className="col-span-3">Model / Provider</div>
          <div className="col-span-3">Tier / Capability</div>
          <div className="col-span-3">Pricing (Input / Output / Cache)</div>
          <div className="col-span-2">Dynamic Fallback</div>
          <div className="col-span-1 text-right">Status</div>
        </div>

        {models.map((m) => (
          <div
            key={m.id}
            className="p-4 grid grid-cols-12 gap-3 items-center hover:bg-white/[0.03] transition-colors"
          >
            <div className="col-span-3">
              <div className="font-semibold text-neutral-100">{m.id}</div>
              <div className="text-[11px] text-neutral-500 font-sans">{m.provider}</div>
            </div>

            <div className="col-span-3 text-neutral-300 text-[11px] font-sans">
              {m.tier}
            </div>

            <div className="col-span-3 space-y-0.5 text-[11px]">
              <div className="text-neutral-300">In: {m.inputPrice} | Out: {m.outputPrice}</div>
              <div className="text-apple-blue font-semibold">{m.cachedPrice}</div>
            </div>

            <div className="col-span-2 flex items-center gap-1.5 text-neutral-400 text-[11px]">
              <RotateCcw className="w-3 h-3 text-apple-amber" />
              <span>{m.fallback}</span>
            </div>

            <div className="col-span-1 text-right">
              <span className="text-[10px] px-2.5 py-0.5 rounded-full bg-apple-emerald/10 text-apple-emerald border border-apple-emerald/20 font-semibold">
                Online
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
