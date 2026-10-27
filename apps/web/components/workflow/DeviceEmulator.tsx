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
    <div className="fixed top-16 right-5 bottom-12 w-[390px] bg-[#0c101a]/90 backdrop-blur-3xl border border-white/[0.1] rounded-3xl shadow-2xl z-30 flex flex-col overflow-hidden select-none animate-in fade-in slide-in-from-right-4 duration-300">
      {/* Emulator Header */}
      <div className="h-12 border-b border-white/[0.06] px-4 flex items-center justify-between bg-black/20">
        <div className="flex items-center gap-2">
          <Smartphone className="w-4 h-4 text-apple-teal" />
          <span className="text-xs font-semibold tracking-tight text-neutral-100">Live Device Monitor</span>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-apple-blue/10 text-apple-teal border border-apple-blue/20">
            9:16 Mobile
          </span>
        </div>

        <button
          onClick={onClose}
          className="p-1 rounded-md text-neutral-400 hover:text-white hover:bg-white/[0.08] transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Control Strip */}
      <div className="p-2.5 bg-black/10 border-b border-white/[0.05] flex items-center justify-between text-xs font-sans">
        {/* Apple Segmented Platform Overlay */}
        <div className="apple-segmented">
          {(['tiktok', 'reels', 'none'] as const).map((p) => (
            <button
              key={p}
              onClick={() => setPlatformOverlay(p)}
              className={cn(
                'apple-segmented-item capitalize',
                platformOverlay === p && 'apple-segmented-item-active'
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
            'px-2.5 py-1 rounded-lg text-[11px] flex items-center gap-1.5 border transition-all font-medium',
            showSafeZoneGrid
              ? 'bg-apple-amber/15 text-apple-amber border-apple-amber/30'
              : 'bg-white/[0.04] text-neutral-400 border-white/[0.06] hover:text-neutral-200'
          )}
          title="Toggle TikTok / Reels Safe Zone Boundaries"
        >
          <Shield className="w-3 h-3" />
          <span>Safe Zone</span>
        </button>
      </div>

      {/* iPhone Device Frame */}
      <div className="flex-1 p-3 flex items-center justify-center overflow-hidden bg-[#070a11]">
        <div className="relative w-64 h-[490px] rounded-[38px] bg-black border-[5px] border-[#2c3038] shadow-2xl overflow-hidden flex flex-col justify-between ring-1 ring-white/10">
          {/* Dynamic Island Notch */}
          <div className="absolute top-2.5 left-1/2 -translate-x-1/2 w-20 h-4 bg-black rounded-full z-30 flex items-center justify-center border border-white/[0.06]">
            <span className="w-2 h-2 rounded-full bg-neutral-900 mr-2" />
          </div>

          {/* Media Content Canvas / Video / Playable */}
          <div className="relative w-full h-full bg-neutral-950 overflow-hidden">
            {activeMediaType === 'playable' ? (
              // Mini Playable Simulation
              <div className="w-full h-full bg-[#0d1424] flex flex-col items-center justify-between p-3 pt-8 pb-12 text-center">
                <div className="w-full flex items-center justify-between text-[10px] font-mono text-neutral-300">
                  <span className="px-2 py-0.5 rounded-full bg-white/[0.06]">Moves: 5</span>
                  <span className="px-2 py-0.5 rounded-full bg-apple-blue/15 text-apple-teal font-semibold">
                    Score: {playableScore}
                  </span>
                </div>

                <div className="w-48 h-48 grid grid-cols-4 gap-1.5 bg-black/40 p-2.5 rounded-2xl border border-white/[0.06] shadow-inner">
                  {Array.from({ length: 16 }).map((_, i) => {
                    const colors = ['bg-[#ff9f0a]', '#0a84ff', '#ff453a', '#30d158'];
                    const c = ['bg-apple-amber', 'bg-apple-blue', 'bg-apple-red', 'bg-apple-emerald'][i % 4];
                    return (
                      <div
                        key={i}
                        onClick={() => setPlayableScore((prev) => prev + 150)}
                        className={cn('rounded-xl cursor-pointer transition-transform active:scale-90 flex items-center justify-center shadow-sm', c)}
                      >
                        <span className="w-2 h-2 rounded-full bg-white/40" />
                      </div>
                    );
                  })}
                </div>

                <div className="w-full p-2 rounded-xl bg-gradient-to-r from-apple-amber to-orange-500 text-neutral-950 font-bold text-[10px] shadow-md tracking-tight">
                  TAP TO MATCH • PLAY FREE!
                </div>
              </div>
            ) : (
              // 9:16 Video / Keyframe preview
              <img src={previewUrl} alt="Ad Preview" className="w-full h-full object-cover" />
            )}

            {/* Safe Zone Grid Overlay */}
            {showSafeZoneGrid && (
              <div className="absolute inset-0 pointer-events-none z-20 border-2 border-dashed border-apple-amber/40 m-2 rounded-2xl flex flex-col justify-between p-2">
                <div className="text-[9px] font-mono text-apple-amber bg-black/70 px-1.5 py-0.5 rounded-full w-fit">
                  Top Danger Zone
                </div>
                <div className="text-[9px] font-mono text-apple-emerald bg-black/70 px-1.5 py-0.5 rounded-full mx-auto">
                  Safe Central Canvas
                </div>
                <div className="text-[9px] font-mono text-apple-amber bg-black/70 px-1.5 py-0.5 rounded-full w-fit">
                  Bottom Deadzone
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
                <div className="absolute right-2 bottom-14 flex flex-col items-center gap-2.5 text-center">
                  <div className="w-7 h-7 rounded-full border border-white bg-neutral-800 flex items-center justify-center text-[10px] font-bold">
                    CF
                  </div>
                  <div className="flex flex-col items-center">
                    <Heart className="w-5 h-5 fill-white text-white drop-shadow" />
                    <span className="text-[9px] font-semibold mt-0.5">142K</span>
                  </div>
                  <div className="flex flex-col items-center">
                    <MessageCircle className="w-5 h-5 fill-white text-white drop-shadow" />
                    <span className="text-[9px] font-semibold mt-0.5">1.2K</span>
                  </div>
                  <div className="flex flex-col items-center">
                    <Share2 className="w-5 h-5 fill-white text-white drop-shadow" />
                    <span className="text-[9px] font-semibold mt-0.5">Share</span>
                  </div>
                  <div className="w-6 h-6 rounded-full bg-black border border-white/40 flex items-center justify-center animate-spin">
                    <Music className="w-3 h-3 text-apple-teal" />
                  </div>
                </div>

                {/* Bottom Sponsored Caption & CTA */}
                <div className="space-y-1 max-w-[170px] drop-shadow-md">
                  <div className="font-bold text-xs flex items-center gap-1">
                    @royal_match
                    <span className="text-[9px] px-1 py-0.2 bg-white/20 rounded font-normal">Ad</span>
                  </div>
                  <p className="text-[10px] line-clamp-2 leading-tight">
                    {hookText}
                  </p>
                  <div className="pt-1">
                    <span className="px-2 py-0.5 rounded-lg bg-apple-blue text-white font-medium text-[10px] inline-block shadow-md">
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
