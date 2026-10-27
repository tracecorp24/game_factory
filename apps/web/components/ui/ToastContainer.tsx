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

const STYLES: Record<ToastType, { border: string; bg: string; text: string; iconColor: string; pillBg: string }> = {
  success: {
    border: 'border-apple-emerald/30',
    bg: 'bg-[#121824]/95 shadow-apple-lg',
    text: 'text-neutral-100',
    iconColor: 'text-apple-emerald',
    pillBg: 'bg-apple-emerald/10',
  },
  error: {
    border: 'border-apple-red/30',
    bg: 'bg-[#1a1215]/95 shadow-apple-lg',
    text: 'text-neutral-100',
    iconColor: 'text-apple-red',
    pillBg: 'bg-apple-red/10',
  },
  info: {
    border: 'border-apple-blue/30',
    bg: 'bg-[#121826]/95 shadow-apple-lg',
    text: 'text-neutral-100',
    iconColor: 'text-apple-blue',
    pillBg: 'bg-apple-blue/10',
  },
  warning: {
    border: 'border-apple-amber/30',
    bg: 'bg-[#1a1712]/95 shadow-apple-lg',
    text: 'text-neutral-100',
    iconColor: 'text-apple-amber',
    pillBg: 'bg-apple-amber/10',
  },
};

export function ToastContainer() {
  const { toasts, removeToast } = useToastStore();

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-2.5 max-w-sm w-full pointer-events-none select-none">
      {toasts.map((t) => {
        const Icon = ICONS[t.type];
        const style = STYLES[t.type];

        return (
          <div
            key={t.id}
            className={cn(
              'pointer-events-auto flex items-start gap-3 p-3.5 rounded-2xl border backdrop-blur-2xl transition-all duration-300 animate-in fade-in slide-in-from-bottom-2',
              style.bg,
              style.border
            )}
          >
            <div className={cn('p-1.5 rounded-xl flex-shrink-0 mt-0.5', style.pillBg)}>
              <Icon className={cn('w-4 h-4', style.iconColor)} />
            </div>
            <div className="flex-1 min-w-0 pt-0.5">
              <div className={cn('text-xs font-semibold tracking-tight text-neutral-100')}>
                {t.title}
              </div>
              {t.description && (
                <div className="text-[11px] text-neutral-400 mt-0.5 leading-relaxed font-normal">
                  {t.description}
                </div>
              )}
            </div>
            <button
              onClick={() => removeToast(t.id)}
              className="p-1 rounded-lg text-neutral-400 hover:text-neutral-200 hover:bg-white/[0.08] transition-colors"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        );
      })}
    </div>
  );
}
