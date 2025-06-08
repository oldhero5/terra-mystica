import { NextResponse } from 'next/server'

export async function GET() {
  try {
    // Basic health check for the frontend
    const healthCheck = {
      status: 'healthy',
      service: 'terra-mystica-frontend',
      version: '0.1.0',
      timestamp: new Date().toISOString(),
      checks: {
        frontend: 'healthy',
        backend: 'unknown' // Will be implemented with actual backend calls
      }
    }

    return NextResponse.json(healthCheck)
  } catch (error) {
    return NextResponse.json(
      {
        status: 'unhealthy',
        service: 'terra-mystica-frontend',
        version: '0.1.0',
        timestamp: new Date().toISOString(),
        error: 'Health check failed'
      },
      { status: 500 }
    )
  }
}