'use client';

import React, { useState } from 'react';
import {
  ScrollText,
  Search,
  Filter,
  Download,
  Copy,
  Check,
  ShieldCheck,
  ExternalLink,
  ChevronRight,
  Terminal,
  Activity,
  X,
  FileSpreadsheet,
  FileCode,
} from 'lucide-react';
import { cn, formatTimestamp } from '@/lib/utils';
import { useAppStore } from '@/lib/store';
import { EventEnvelope } from '@/lib/types';

export default function ExecutionLedgerPage() {
  const { events, projectId } = useAppStore();

  const [search, setSearch] = useState('');
  const [selectedEventType, setSelectedEventType] = useState('ALL');
  const [selectedEvent, setSelectedEvent] = useState<EventEnvelope | null>(events[events.length - 1] || null);
  const [copied, setCopied] = useState(false);

  // Filters
  const filteredEvents = events.filter((e) => {
    const matchesSearch =
      search === '' ||
      e.event_id.toLowerCase().includes(search.toLowerCase()) ||
      e.event_type.toLowerCase().includes(search.toLowerCase()) ||
      (e.agent_id && e.agent_id.toLowerCase().includes(search.toLowerCase())) ||
      JSON.stringify(e.payload_preview).toLowerCase().includes(search.toLowerCase());

    const matchesType = selectedEventType === 'ALL' || e.event_type === selectedEventType;

    return matchesSearch && matchesType;
  });

  const handleCopyJson = (payload: any) => {
    navigator.clipboard.writeText(JSON.stringify(payload, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleExportJsonl = () => {
    const jsonl = events.map((e) => JSON.stringify(e)).join('\n');
    const blob = new Blob([jsonl], { type: 'application/jsonl' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ledger-${projectId}-${Date.now()}.jsonl`;
    a.click();
  };

  const handleExportCsv = () => {
    const headers = ['run_seq', 'event_id', 'event_type', 'occurred_at', 'agent_id', 'integrity_hash'];
    const rows = events.map((e) => [
      e.run_seq,
      e.event_id,
      e.event_type,
      e.occurred_at,
      e.agent_id || e.actor_id || '',
      e.integrity_hash,
    ]);
    const csv = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ledger-${projectId}-${Date.now()}.csv`;
    a.click();
  };

  const uniqueEventTypes = Array.from(new Set(events.map((e) => e.event_type)));

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6 select-none">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-apple-emerald/10 border border-apple-emerald/25 text-apple-emerald text-xs font-medium mb-3">
            <ScrollText className="w-3.5 h-3.5" />
            <span>Cryptographic Execution Ledger & Outbox</span>
          </div>
          <h1 className="text-2xl font-semibold tracking-tight text-neutral-100">Append-Only Event Ledger Explorer</h1>
          <p className="text-neutral-400 text-xs mt-1 leading-relaxed">
            Immutable, audit-ready operational records. Every request, model call, attempt retry, token consumption, and artifact is hashed with SHA-256.
          </p>
        </div>

        {/* Export Buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={handleExportJsonl}
            className="apple-btn-secondary flex items-center gap-1.5"
          >
            <FileCode className="w-4 h-4 text-apple-teal" />
            <span>Export JSONL</span>
          </button>
          <button
            onClick={handleExportCsv}
            className="apple-btn-secondary flex items-center gap-1.5"
          >
            <FileSpreadsheet className="w-4 h-4 text-apple-emerald" />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-3.5 rounded-2xl bg-white/[0.03] border border-white/[0.06] flex flex-col sm:flex-row items-center gap-3 text-xs">
        {/* Search Input */}
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 text-neutral-500 absolute left-3 top-2.5" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by Event ID, Agent, Payload content, Hash..."
            className="w-full bg-black/30 border border-white/[0.08] rounded-xl pl-9 pr-4 py-2 text-xs text-neutral-200 placeholder-neutral-500 focus:outline-none focus:border-apple-blue font-mono"
          />
        </div>

        {/* Event Type Filter */}
        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Filter className="w-4 h-4 text-neutral-500" />
          <select
            value={selectedEventType}
            onChange={(e) => setSelectedEventType(e.target.value)}
            className="bg-black/30 border border-white/[0.08] rounded-xl px-3 py-2 text-xs text-neutral-200 focus:outline-none focus:border-apple-blue font-mono cursor-pointer"
          >
            <option value="ALL" className="bg-[#121724]">All Event Types ({events.length})</option>
            {uniqueEventTypes.map((t) => (
              <option key={t} value={t} className="bg-[#121724]">
                {t}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Main Ledger Split View */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Event Table (7 Cols) */}
        <div className="lg:col-span-7 rounded-3xl border border-white/[0.08] bg-[#121724]/80 backdrop-blur-2xl overflow-hidden shadow-apple-md">
          <div className="p-3.5 bg-black/20 border-b border-white/[0.06] flex items-center justify-between text-xs font-mono text-neutral-400">
            <span>Showing {filteredEvents.length} Recorded Events</span>
            <span className="text-[10px] text-apple-emerald font-semibold">Ledger Status: Healthy</span>
          </div>

          <div className="overflow-x-auto max-h-[620px] overflow-y-auto divide-y divide-white/[0.04] font-mono text-xs">
            {filteredEvents.map((evt) => {
              const isSelected = selectedEvent?.event_id === evt.event_id;
              return (
                <div
                  key={evt.event_id}
                  onClick={() => setSelectedEvent(evt)}
                  className={cn(
                    'p-3.5 flex items-center justify-between cursor-pointer transition-colors hover:bg-white/[0.04]',
                    isSelected ? 'bg-apple-blue/15 border-l-4 border-apple-blue' : ''
                  )}
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <span className="text-neutral-500 text-[10px] w-6">#{evt.run_seq}</span>
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <span
                          className={cn(
                            'font-semibold',
                            evt.event_type.includes('FAILED')
                              ? 'text-apple-red'
                              : evt.event_type.includes('COMPLETED')
                              ? 'text-apple-emerald'
                              : 'text-apple-teal'
                          )}
                        >
                          {evt.event_type}
                        </span>
                        <span className="text-[10px] px-2 py-0.5 rounded-full bg-white/[0.06] text-neutral-400 border border-white/[0.08]">
                          {evt.agent_id || evt.actor_id}
                        </span>
                      </div>
                      <div className="text-[10px] text-neutral-500 truncate max-w-xs mt-0.5 font-sans">
                        {JSON.stringify(evt.payload_preview).slice(0, 55)}...
                      </div>
                    </div>
                  </div>

                  <div className="text-right flex-shrink-0 text-[10px] text-neutral-500 font-mono">
                    <div>{formatTimestamp(evt.occurred_at)}</div>
                    <div className="text-neutral-600">{evt.integrity_hash.slice(0, 10)}...</div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Selected Event Details Inspector (5 Cols) */}
        <div className="lg:col-span-5 rounded-3xl border border-white/[0.08] bg-[#121724]/80 backdrop-blur-2xl p-5 space-y-4 shadow-apple-md">
          {selectedEvent ? (
            <>
              {/* Event Title Header */}
              <div className="flex items-center justify-between border-b border-white/[0.06] pb-3">
                <div>
                  <div className="text-base font-semibold text-neutral-100 flex items-center gap-2">
                    <span className="text-apple-teal font-mono">#{selectedEvent.run_seq}</span>
                    <span>{selectedEvent.event_type}</span>
                  </div>
                  <div className="text-[11px] font-mono text-neutral-500 mt-0.5">
                    Event ID: {selectedEvent.event_id}
                  </div>
                </div>

                <button
                  onClick={() => handleCopyJson(selectedEvent)}
                  className="apple-btn-secondary flex items-center gap-1.5 py-1 px-2.5 text-xs font-mono"
                  title="Copy Full Envelope JSON"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-apple-emerald" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copied ? 'Copied' : 'JSON'}</span>
                </button>
              </div>

              {/* Event Metadata Cards */}
              <div className="grid grid-cols-2 gap-3 text-xs font-mono">
                <div className="p-3 rounded-2xl bg-black/20 border border-white/[0.05]">
                  <div className="text-[10px] text-neutral-500 uppercase">Occurred (UTC)</div>
                  <div className="text-neutral-200 mt-0.5">{selectedEvent.occurred_at}</div>
                </div>

                <div className="p-3 rounded-2xl bg-black/20 border border-white/[0.05]">
                  <div className="text-[10px] text-neutral-500 uppercase">Redaction Level</div>
                  <div className="text-apple-teal mt-0.5">{selectedEvent.redaction_level}</div>
                </div>

                <div className="p-3 rounded-2xl bg-black/20 border border-white/[0.05]">
                  <div className="text-[10px] text-neutral-500 uppercase">Actor</div>
                  <div className="text-neutral-200 mt-0.5">
                    {selectedEvent.agent_id || selectedEvent.actor_id}
                  </div>
                </div>

                <div className="p-3 rounded-2xl bg-black/20 border border-white/[0.05]">
                  <div className="text-[10px] text-neutral-500 uppercase">Run ID</div>
                  <div className="text-neutral-200 mt-0.5">{selectedEvent.run_id}</div>
                </div>
              </div>

              {/* Integrity Hash */}
              <div className="p-3 rounded-2xl bg-black/20 border border-white/[0.05] space-y-1">
                <div className="text-[10px] font-mono uppercase text-neutral-400 flex items-center gap-1.5 font-semibold">
                  <ShieldCheck className="w-3.5 h-3.5 text-apple-emerald" />
                  SHA-256 Cryptographic Hash
                </div>
                <div className="font-mono text-[11px] text-neutral-300 break-all select-all">
                  {selectedEvent.integrity_hash}
                </div>
              </div>

              {/* Payload Preview */}
              <div className="space-y-1.5">
                <div className="text-neutral-400 text-xs font-medium font-sans">
                  Payload Preview (Envelope Body):
                </div>
                <div className="rounded-2xl bg-black/40 border border-white/[0.06] p-3 overflow-x-auto max-h-60 overflow-y-auto">
                  <pre className="text-[11px] font-mono text-apple-teal leading-relaxed">
                    {JSON.stringify(selectedEvent.payload_preview, null, 2)}
                  </pre>
                </div>
              </div>
            </>
          ) : (
            <div className="text-center py-12 text-neutral-500 text-xs">
              Select an event from the ledger table to inspect cryptographic envelope details.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
