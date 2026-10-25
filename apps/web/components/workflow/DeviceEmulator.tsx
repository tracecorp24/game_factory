'use client';

import React, { useState } from 'react';
import {
  Smartphone,
  X,
  Play,
  RotateCcw,
  Volume2,
  VolumeX,
  Heart,
  MessageCircle,
  Share2,
  Music,
  Shield,
  Eye,
  Layers,
  Sparkles,
  Gamepad2,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface DeviceEmulatorProps {
  isOpen: boolean;
  onClose: () => void;
  activeMediaType?: 'video' | 'playable' | 'image';
  previewUrl?: string;
  hookText?: string;
}

export function DeviceEmulator({
  isOpen,
  onClose,
  activeMediaType = 'video',
  previewUrl = 'https://images.unsplash.com/photo-1579783902614-a3fb3927b675?auto=format&fit=crop&w=600&q=80',
  hookText = 'Save the King in 5 Seconds! 👑🌋',
}: DeviceEmulatorProps) {
  const [platformOverlay, setPlatformOverlay] = useState<'tiktok' | 'reels' | 'none'>('tiktok');
  const [showSafeZoneGrid, setShowSafeZoneGrid] = useState<boolean>(true);
  const [isPlaying, setIsPlaying] = useState<boolean>(true);
  const [isMuted, setIsMuted] = useState<boolean>(false);
  const [playableScore, setPlayableScore] = useState<number>(450);

  if (!isOpen) return null;

  return (
    <div className="fixed top-16 right-4 bottom-14 w-96 bg-slate-900/95 backdrop-blur-2xl border border-slate-800 rounded-3xl shadow-2xl z-30 flex flex-col overflow-hidden select-none animate-in fade-in slide-in-from-right-4 duration-300">
      {/* Emulator Header */}
      <div className="h-12 border-b border-slate-800 px-4 flex items-center justify-between bg-slate-950/80">
        <div className="flex items-center gap-2">
          <Smartphone className="w-4 h-4 text-cyan-400" />
          <span className="font-mono text-xs font-bold text-slate-100">Live Device Emulator</span>
          <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-cyan-950 text-cyan-300 border border-cyan-800/60">
            9:16
          </span>
        </div>

        <button
          onClick={onClose}
          className="p-1 rounded text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Control Strip */}
      <div className="p-2.5 bg-slate-950/60 border-b border-slate-800 flex items-center justify-between text-xs font-mono">
        {/* Overlay Selector */}
        <div className="flex items-center gap-1 bg-slate-900 p-0.5 rounded-lg border border-slate-800 text-[10px]">
          {(['tiktok', 'reels', 'none'] as const).map((p) => (
            <button
              key={p}
              onClick={() => setPlatformOverlay(p)}
              className={cn(
                'px-2 py-0.5 rounded capitalize transition-colors',
                platformOverlay === p ? 'bg-cyan-500/30 text-cyan-300 font-semibold' : 'text-slate-400 hover:text-slate-200'
              )}
            >
              {p === 'none' ? 'Clean' : p}
            </button>
          ))}
        </div>

        {/* Safe-Zone Toggle */}
        <button
          onClick={() => setShowSafeZoneGrid(!showSafeZoneGrid)}
          className={cn(
            'px-2 py-1 rounded text-[10px] flex items-center gap-1 border transition-colors',
            showSafeZoneGrid
              ? 'bg-amber-950 text-amber-300 border-amber-800/80 font-semibold'
              : 'bg-slate-900 text-slate-400 border-slate-800 hover:text-slate-200'
          )}
          title="Toggle TikTok / Reels Safe Zone Boundaries"
        >
          <Shield className="w-3 h-3" />
          <span>Safe Zone</span>
        </button>
      </div>

      {/* iPhone Device Frame */}
      <div className="flex-1 p-3 flex items-center justify-center overflow-hidden bg-[#050811]">
        <div className="relative w-64 h-[510px] rounded-[36px] bg-slate-950 border-[6px] border-slate-800 shadow-2xl overflow-hidden flex flex-col justify-between">
          {/* Dynamic Island Notch */}
          <div className="absolute top-2 left-1/2 -translate-x-1/2 w-20 h-4 bg-black rounded-full z-30 flex items-center justify-center">
            <span className="w-2 h-2 rounded-full bg-slate-900 mr-2" />
          </div>

          {/* Media Content Canvas / Video / Playable */}
          <div className="relative w-full h-full bg-slate-900 overflow-hidden">
            {activeMediaType === 'playable' ? (
              // Mini Playable Simulation
              <div className="w-full h-full bg-[#0d162a] flex flex-col items-center justify-between p-3 pt-8 pb-14 text-center">
                <div className="w-full flex items-center justify-between text-[10px] font-mono text-slate-300">
                  <span className="px-1.5 py-0.5 rounded bg-slate-800">Moves: 5</span>
                  <span className="px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-300">Score: {playableScore}</span>
                </div>

                <div className="w-48 h-48 grid grid-cols-4 gap-1.5 bg-slate-950/80 p-2 rounded-xl border border-slate-800 shadow-inner">
                  {Array.from({ length: 16 }).map((_, i) => {
                    const colors = ['bg-amber-400', 'bg-blue-500', 'bg-rose-500', 'bg-emerald-400'];
                    const c = colors[i % colors.length];
                    return (
                      <div
                        key={i}
                        onClick={() => setPlayableScore((prev) => prev + 150)}
                        className={cn('rounded-lg cursor-pointer transition-transform active:scale-95 flex items-center justify-center', c)}
                      >
                        <span className="w-1.5 h-1.5 rounded-full bg-white/40" />
                      </div>
                    );
                  })}
                </div>

                <div className="w-full p-2 rounded-lg bg-gradient-to-r from-amber-500 to-orange-600 text-slate-950 font-bold text-[10px]">
                  TAP TO MATCH • PLAY FREE!
                </div>
              </div>
            ) : (
              // 9:16 Video / Keyframe preview
              <img src={previewUrl} alt="Ad Preview" className="w-full h-full object-cover" />
            )}

            {/* Safe Zone Grid Overlay */}
            {showSafeZoneGrid && (
              <div className="absolute inset-0 pointer-events-none z-20 border-2 border-dashed border-amber-500/40 m-2 rounded-2xl flex flex-col justify-between p-2">
                <div className="text-[9px] font-mono text-amber-400 bg-black/60 px-1 py-0.2 rounded w-fit">
                  Top Danger Zone
                </div>
                <div className="text-[9px] font-mono text-emerald-400 bg-black/60 px-1 py-0.2 rounded mx-auto">
                  Safe Central Canvas
                </div>
                <div className="text-[9px] font-mono text-amber-400 bg-black/60 px-1 py-0.2 rounded w-fit">
                  Bottom UI Deadzone
                </div>
              </div>
            )}

            {/* TikTok / Reels Platform UI Overlay */}
            {platformOverlay === 'tiktok' && (
              <div className="absolute inset-0 pointer-events-none z-20 flex flex-col justify-between p-3 pt-8 pb-3 text-white">
                {/* Top Tabs */}
                <div className="flex items-center justify-center gap-3 text-[11px] font-bold drop-shadow-md">
                  <span className="opacity-60">Following</span>
                  <span className="border-b-2 border-white pb-0.5">For You</span>
                </div>

                {/* Right Interactive Sidebar */}
                <div className="absolute right-2 bottom-16 flex flex-col items-center gap-3 text-center">
                  <div className="w-8 h-8 rounded-full border border-white bg-slate-800 flex items-center justify-center text-[10px] font-bold">
                    CF
                  </div>
                  <div className="flex flex-col items-center">
                    <Heart className="w-5 h-5 fill-white text-white drop-shadow" />
                    <span className="text-[9px] font-bold mt-0.5">142K</span>
                  </div>
                  <div className="flex flex-col items-center">
                    <MessageCircle className="w-5 h-5 fill-white text-white drop-shadow" />
                    <span className="text-[9px] font-bold mt-0.5">1,280</span>
                  </div>
                  <div className="flex flex-col items-center">
                    <Share2 className="w-5 h-5 fill-white text-white drop-shadow" />
                    <span className="text-[9px] font-bold mt-0.5">Share</span>
                  </div>
                  <div className="w-7 h-7 rounded-full bg-slate-950 border border-white/40 flex items-center justify-center animate-spin">
                    <Music className="w-3.5 h-3.5 text-cyan-300" />
                  </div>
                </div>

                {/* Bottom Sponsored Caption & CTA */}
                <div className="space-y-1.5 max-w-[170px] drop-shadow-md">
                  <div className="font-bold text-xs flex items-center gap-1">
                    @royal_match_strike
                    <span className="text-[9px] px-1 py-0.2 bg-white/20 rounded font-normal">Ad</span>
                  </div>
                  <p className="text-[10px] line-clamp-2 leading-tight">
                    {hookText}
                  </p>
                  <div className="pt-1">
                    <span className="px-2 py-1 rounded bg-cyan-500 text-slate-950 font-bold text-[10px] inline-block shadow-lg">
                      Install Now ➔
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
