'use client';

import React from 'react';
import { useToastStore, ToastType } from '@/lib/toast';
import { CheckCircle2, AlertCircle, Info, AlertTriangle, X } from 'lucide-react';
import { cn } from '@/lib/utils';

const ICONS: Record<ToastType, React.ElementType> = {
  success: CheckCircle2,
  error: AlertCircle,
  info: Info,
  warning: AlertTriangle,
};

const STYLES: Record<ToastType, { border: string; bg: string; text: string; iconColor: string }> = {
  success: {
    border: 'border-emerald-500/40',
    bg: 'bg-emerald-950/90 shadow-emerald-950/50',
    text: 'text-emerald-200',
    iconColor: 'text-emerald-400',
  },
  error: {
    border: 'border-rose-500/40',
    bg: 'bg-rose-950/90 shadow-rose-950/50',
    text: 'text-rose-200',
    iconColor: 'text-rose-400',
  },
  info: {
    border: 'border-cyan-500/40',
    bg: 'bg-cyan-950/90 shadow-cyan-950/50',
    text: 'text-cyan-200',
    iconColor: 'text-cyan-400',
  },
  warning: {
    border: 'border-amber-500/40',
    bg: 'bg-amber-950/90 shadow-amber-950/50',
    text: 'text-amber-200',
    iconColor: 'text-amber-400',
  },
};

export function ToastContainer() {
  const { toasts, removeToast } = useToastStore();

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-2.5 max-w-md w-full pointer-events-none select-none">
      {toasts.map((t) => {
        const Icon = ICONS[t.type];
        const style = STYLES[t.type];

        return (
          <div
            key={t.id}
            className={cn(
              'pointer-events-auto flex items-start gap-3 p-3.5 rounded-xl border backdrop-blur-xl shadow-xl transition-all duration-300 animate-in fade-in slide-in-from-bottom-2',
              style.bg,
              style.border
            )}
          >
            <Icon className={cn('w-5 h-5 flex-shrink-0 mt-0.5', style.iconColor)} />
            <div className="flex-1 min-w-0">
              <div className={cn('text-xs font-bold font-mono tracking-wide', style.text)}>
                {t.title}
              </div>
              {t.description && (
                <div className="text-[11px] text-slate-300/90 mt-0.5 leading-relaxed font-sans">
                  {t.description}
                </div>
              )}
            </div>
            <button
              onClick={() => removeToast(t.id)}
              className="p-1 rounded text-slate-400 hover:text-slate-200 hover:bg-black/20 transition-colors"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        );
      })}
    </div>
  );
}
