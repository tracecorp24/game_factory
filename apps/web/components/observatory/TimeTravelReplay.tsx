'use client';

import React, { useEffect, useRef } from 'react';
import {
  Play,
  Pause,
  SkipBack,
  SkipForward,
  RotateCcw,
  Clock,
  Sparkles,
  Zap,
} from 'lucide-react';
import { cn, formatTimestamp } from '@/lib/utils';
import { useAppStore } from '@/lib/store';

export function TimeTravelReplay() {
  const {
    events,
    replayStep,
    isReplaying,
    replaySpeed,
    setReplayStep,
    setIsReplaying,
    setReplaySpeed,
    stepReplayNext,
    stepReplayPrev,
    resetToLatest,
  } = useAppStore();

  const timerRef = useRef<any>(null);

  // Auto-play interval
  useEffect(() => {
    if (isReplaying) {
      const intervalMs = Math.max(300, 1500 / replaySpeed);
      timerRef.current = setInterval(() => {
        const current = useAppStore.getState().replayStep;
        const total = useAppStore.getState().events.length;
        if (current < total - 1) {
          stepReplayNext();
        } else {
          setIsReplaying(false);
        }
      }, intervalMs);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isReplaying, replaySpeed, stepReplayNext, setIsReplaying]);

  const currentEvent = events[replayStep] || events[events.length - 1];

  return (
    <div className="absolute top-4 left-6 right-6 lg:left-8 lg:right-96 z-10 pointer-events-auto">
      <div className="rounded-xl bg-slate-900/90 backdrop-blur-md border border-slate-800/80 p-3 shadow-2xl flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
        {/* Left: Playback Controls */}
        <div className="flex items-center gap-2">
          {/* Step Back */}
          <button
            onClick={stepReplayPrev}
            disabled={replayStep <= 0}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 disabled:opacity-40 transition-colors"
            title="Step Previous Event"
          >
            <SkipBack className="w-4 h-4" />
          </button>

          {/* Play / Pause Toggle */}
          <button
            onClick={() => setIsReplaying(!isReplaying)}
            className="px-3 py-1.5 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:shadow-cyan-500/20 text-white font-medium flex items-center gap-1.5 transition-all"
            title={isReplaying ? 'Pause Replay' : 'Play Historical Replay'}
          >
            {isReplaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4 fill-current" />}
            <span className="text-xs font-mono">{isReplaying ? 'Pause' : 'Replay'}</span>
          </button>

          {/* Step Next */}
          <button
            onClick={stepReplayNext}
            disabled={replayStep >= events.length - 1}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 disabled:opacity-40 transition-colors"
            title="Step Next Event"
          >
            <SkipForward className="w-4 h-4" />
          </button>

          {/* Reset to Latest */}
          <button
            onClick={resetToLatest}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
            title="Jump to Live / Latest Event"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>

          {/* Replay Speed */}
          <div className="flex items-center rounded-lg bg-slate-950 p-0.5 border border-slate-800 text-[10px] font-mono">
            {[0.5, 1, 2, 5].map((spd) => (
              <button
                key={spd}
                onClick={() => setReplaySpeed(spd)}
                className={cn(
                  'px-1.5 py-0.5 rounded transition-colors',
                  replaySpeed === spd ? 'bg-cyan-500/30 text-cyan-300 font-semibold' : 'text-slate-400 hover:text-slate-200'
                )}
              >
                {spd}x
              </button>
            ))}
          </div>
        </div>

        {/* Center: Interactive Scrubber Slider */}
        <div className="flex-1 w-full flex items-center gap-3 px-2">
          <span className="text-[10px] font-mono text-slate-400 whitespace-nowrap">
            Step {replayStep + 1} / {events.length}
          </span>
          <input
            type="range"
            min={0}
            max={events.length - 1}
            value={replayStep}
            onChange={(e) => setReplayStep(parseInt(e.target.value, 10))}
            className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
          />
        </div>

        {/* Right: Current Event Badge */}
        {currentEvent && (
          <div className="flex items-center gap-2 font-mono text-[11px] whitespace-nowrap">
            <span className="px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800/60 font-semibold">
              {currentEvent.event_type}
            </span>
            <span className="text-slate-400 text-[10px]">
              {formatTimestamp(currentEvent.occurred_at)}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
