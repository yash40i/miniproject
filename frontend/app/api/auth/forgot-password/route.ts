import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    console.log('[Forgot Password Proxy] Forwarding to backend:', { email: body.email });
    
    // Forward to backend
    const backendUrl = process.env.BACKEND_URL || 'http://127.0.0.1:8000/auth/forgot-password';
    const response = await fetch(backendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    console.log('[Forgot Password Proxy] Backend response status:', response.status);
    
    let data;
    try {
      data = await response.json();
    } catch (parseError) {
      console.error('[Forgot Password Proxy] Failed to parse JSON:', parseError);
      return NextResponse.json(
        { detail: 'Backend returned invalid JSON' },
        { status: 500 }
      );
    }
    
    if (!response.ok) {
      console.log('[Forgot Password Proxy] Backend error:', data);
      return NextResponse.json(data, { status: response.status });
    }

    console.log('[Forgot Password Proxy] Success');
    return NextResponse.json(data);
  } catch (error) {
    console.error('[Forgot Password Proxy] Error:', error instanceof Error ? error.message : error);
    return NextResponse.json(
      { detail: error instanceof Error ? error.message : 'Internal server error' },
      { status: 500 }
    );
  }
}
