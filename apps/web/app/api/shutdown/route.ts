import { NextResponse } from 'next/server';

export async function POST() {
  setTimeout(() => {
    process.exit(0);
  }, 400);

  return NextResponse.json({
    success: true,
    message: 'CreativeForge server is shutting down cleanly.',
  });
}
