import { NextRequest } from 'next/server';
import { DEMO_EVENTS, DEMO_RUN_ID } from '@/lib/fixtures/demo-events';

export const dynamic = 'force-dynamic';

export async function GET(
  req: NextRequest,
  { params }: { params: { runId: string } }
) {
  const { searchParams } = new URL(req.url);
  const sinceSeqParam = searchParams.get('since_seq');
  const lastEventIdHeader = req.headers.get('Last-Event-ID');
  const runId = params.runId;

  // 1. If this is a real run (not the hardcoded fixture DEMO_RUN_ID), proxy to FastAPI backend
  if (runId && runId !== DEMO_RUN_ID) {
    try {
      const backendUrl = new URL(`http://127.0.0.1:8000/api/v1/runs/${encodeURIComponent(runId)}/events/stream`);
      if (sinceSeqParam) backendUrl.searchParams.set('since_seq', sinceSeqParam);

      const headers: Record<string, string> = {
        'Accept': 'text/event-stream',
      };
      if (lastEventIdHeader) {
        headers['Last-Event-ID'] = lastEventIdHeader;
      }

      const backendRes = await fetch(backendUrl.toString(), {
        headers,
        signal: req.signal,
      });

      if (backendRes.ok && backendRes.body) {
        return new Response(backendRes.body, {
          headers: {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache, no-transform',
            Connection: 'keep-alive',
            'X-Accel-Buffering': 'no',
          },
        });
      }
    } catch {
      // Fall through to fallback demo events if backend is not reachable
    }
  }

  // 2. Fallback / Demo fixture event streaming
  let startSeq = 0;
  if (sinceSeqParam) {
    const parts = sinceSeqParam.split(':');
    startSeq = parseInt(parts[parts.length - 1], 10) || 0;
  } else if (lastEventIdHeader) {
    const parts = lastEventIdHeader.split(':');
    startSeq = parseInt(parts[parts.length - 1], 10) || 0;
  }

  const eventsToStream = DEMO_EVENTS.filter((e) => e.run_seq > startSeq);

  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    async start(controller) {
      controller.enqueue(encoder.encode(`: keepalive\n\n`));

      for (const evt of eventsToStream) {
        const payload = `id: ${evt.run_id}:${evt.run_seq}\nevent: ${evt.event_type}\ndata: ${JSON.stringify(evt)}\n\n`;
        controller.enqueue(encoder.encode(payload));
        await new Promise((r) => setTimeout(r, 600));
      }

      const interval = setInterval(() => {
        try {
          controller.enqueue(encoder.encode(`: ping\n\n`));
        } catch {
          clearInterval(interval);
        }
      }, 15000);

      req.signal.addEventListener('abort', () => {
        clearInterval(interval);
        controller.close();
      });
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache, no-transform',
      Connection: 'keep-alive',
      'X-Accel-Buffering': 'no',
    },
  });
}

