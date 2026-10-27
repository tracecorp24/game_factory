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
      <div className="rounded-2xl bg-[#0c101a]/85 backdrop-blur-3xl border border-white/[0.08] p-2.5 shadow-2xl flex flex-col sm:flex-row items-center justify-between gap-3 text-xs select-none">
        {/* Left: Playback Controls */}
        <div className="flex items-center gap-1.5">
          {/* Step Back */}
          <button
            onClick={stepReplayPrev}
            disabled={replayStep <= 0}
            className="p-1.5 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] text-neutral-300 disabled:opacity-30 transition-colors"
            title="Step Previous Event"
          >
            <SkipBack className="w-3.5 h-3.5" />
          </button>

          {/* Play / Pause Toggle */}
          <button
            onClick={() => setIsReplaying(!isReplaying)}
            className="apple-btn-primary flex items-center gap-1.5 py-1 px-3 shadow-sm"
            title={isReplaying ? 'Pause Replay' : 'Play Historical Replay'}
          >
            {isReplaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5 fill-current" />}
            <span className="text-[11px]">{isReplaying ? 'Pause' : 'Replay'}</span>
          </button>

          {/* Step Next */}
          <button
            onClick={stepReplayNext}
            disabled={replayStep >= events.length - 1}
            className="p-1.5 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] text-neutral-300 disabled:opacity-30 transition-colors"
            title="Step Next Event"
          >
            <SkipForward className="w-3.5 h-3.5" />
          </button>

          {/* Reset to Latest */}
          <button
            onClick={resetToLatest}
            className="p-1.5 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] text-neutral-300 transition-colors ml-0.5"
            title="Jump to Live / Latest Event"
          >
            <RotateCcw className="w-3 h-3" />
          </button>

          {/* Replay Speed in Apple Segmented Control */}
          <div className="apple-segmented ml-1">
            {[0.5, 1, 2, 5].map((spd) => (
              <button
                key={spd}
                onClick={() => setReplaySpeed(spd)}
                className={cn(
                  'apple-segmented-item !px-1.5 !py-0.5 !text-[10px] font-mono',
                  replaySpeed === spd && 'apple-segmented-item-active'
                )}
              >
                {spd}x
              </button>
            ))}
          </div>
        </div>

        {/* Center: Interactive Scrubber Slider */}
        <div className="flex-1 w-full flex items-center gap-2.5 px-2">
          <span className="text-[10px] font-mono text-neutral-400 whitespace-nowrap">
            Step {replayStep + 1} / {events.length}
          </span>
          <input
            type="range"
            min={0}
            max={events.length - 1}
            value={replayStep}
            onChange={(e) => setReplayStep(parseInt(e.target.value, 10))}
            className="w-full h-1 bg-white/[0.1] rounded-lg appearance-none cursor-pointer accent-apple-blue"
          />
        </div>

        {/* Right: Current Event Badge */}
        {currentEvent && (
          <div className="flex items-center gap-2 font-mono text-[11px] whitespace-nowrap">
            <span className="px-2 py-0.5 rounded-full bg-apple-blue/15 text-apple-teal border border-apple-blue/25 text-[10px] font-semibold">
              {currentEvent.event_type}
            </span>
            <span className="text-neutral-400 text-[10px]">
              {formatTimestamp(currentEvent.occurred_at)}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
