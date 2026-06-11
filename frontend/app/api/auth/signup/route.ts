import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    console.log('[Signup Proxy] Forwarding to backend:', { email: body.email });
    
    // Forward to backend - use 127.0.0.1 for localhost resolution
    const backendUrl = process.env.BACKEND_URL || 'http://127.0.0.1:8000/auth/signup';
    const response = await fetch(backendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    console.log('[Signup Proxy] Backend response status:', response.status);
    
    let data;
    try {
      data = await response.json();
    } catch (parseError) {
      console.error('[Signup Proxy] Failed to parse JSON:', parseError);
      return NextResponse.json(
        { detail: 'Backend returned invalid JSON' },
        { status: 500 }
      );
    }
    
    if (!response.ok) {
      console.log('[Signup Proxy] Backend error:', data);
      return NextResponse.json(data, { status: response.status });
    }

    console.log('[Signup Proxy] Success, returning token');
    return NextResponse.json(data);
  } catch (error) {
    console.error('[Signup Proxy] Error:', error instanceof Error ? error.message : error);
    return NextResponse.json(
      { detail: error instanceof Error ? error.message : 'Internal server error' },
      { status: 500 }
    );
  }
}
