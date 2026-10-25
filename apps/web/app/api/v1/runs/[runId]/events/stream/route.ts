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
  
  let startSeq = 0;
  if (sinceSeqParam) {
    // could be "run_88:5" or "5"
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
      // Send initial keep-alive comment
      controller.enqueue(encoder.encode(`: keepalive\n\n`));

      for (const evt of eventsToStream) {
        const payload = `id: ${evt.run_id}:${evt.run_seq}\nevent: ${evt.event_type}\ndata: ${JSON.stringify(evt)}\n\n`;
        controller.enqueue(encoder.encode(payload));
        // Small delay to simulate live streaming if desired, or quick flush
        await new Promise((r) => setTimeout(r, 600));
      }

      // Stream remains open for live heartbeats
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
