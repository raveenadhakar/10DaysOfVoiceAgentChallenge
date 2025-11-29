import { NextResponse } from 'next/server';
import { AccessToken, type AccessTokenOptions, type VideoGrant } from 'livekit-server-sdk';
import { RoomConfiguration } from '@livekit/protocol';

type ConnectionDetails = {
  serverUrl: string;
  roomName: string;
  participantName: string;
  participantToken: string;
};

// NOTE: you are expected to define the following environment variables in `.env.local`:
const API_KEY = process.env.LIVEKIT_API_KEY;
const API_SECRET = process.env.LIVEKIT_API_SECRET;
const LIVEKIT_URL = process.env.LIVEKIT_URL;

// don't cache the results
export const revalidate = 0;

export async function POST(req: Request) {
  console.log('📥 POST /api/connection-details - Request received');
  
  try {
    if (LIVEKIT_URL === undefined) {
      console.error('❌ LIVEKIT_URL is not defined');
      throw new Error('LIVEKIT_URL is not defined');
    }
    if (API_KEY === undefined) {
      console.error('❌ LIVEKIT_API_KEY is not defined');
      throw new Error('LIVEKIT_API_KEY is not defined');
    }
    if (API_SECRET === undefined) {
      console.error('❌ LIVEKIT_API_SECRET is not defined');
      throw new Error('LIVEKIT_API_SECRET is not defined');
    }

    // Parse agent configuration from request body
    const body = await req.json();
    const agentName: string = body?.room_config?.agents?.[0]?.agent_name;
    const agentType: string = body?.agent_type || 'food'; // Default to food agent

    console.log('🎯 Connection request received:', {
      agentType,
      agentName,
      body: JSON.stringify(body, null, 2)
    });

    // Generate participant token
    const participantName = 'user';
    const participantIdentity = `voice_assistant_user_${Math.floor(Math.random() * 10_000)}`;
    const roomName = `voice_assistant_room_${Math.floor(Math.random() * 10_000)}`;

    const participantToken = await createParticipantToken(
      { identity: participantIdentity, name: participantName },
      roomName,
      agentName,
      agentType
    );

    // Return connection details
    const data: ConnectionDetails = {
      serverUrl: LIVEKIT_URL,
      roomName,
      participantToken: participantToken,
      participantName,
    };
    
    console.log('✅ Connection details created:', {
      roomName,
      agentType,
      serverUrl: LIVEKIT_URL
    });
    
    const headers = new Headers({
      'Cache-Control': 'no-store',
    });
    return NextResponse.json(data, { headers });
  } catch (error) {
    if (error instanceof Error) {
      console.error('❌ Error creating connection:', error);
      return new NextResponse(error.message, { status: 500 });
    }
  }
}

function createParticipantToken(
  userInfo: AccessTokenOptions,
  roomName: string,
  agentName?: string,
  agentType?: string
): Promise<string> {
  const at = new AccessToken(API_KEY, API_SECRET, {
    ...userInfo,
    ttl: '15m',
  });
  const grant: VideoGrant = {
    room: roomName,
    roomJoin: true,
    canPublish: true,
    canPublishData: true,
    canSubscribe: true,
  };
  at.addGrant(grant);

  if (agentName || agentType) {
    at.roomConfig = new RoomConfiguration({
      agents: agentName ? [{ agentName }] : [],
    });
    
    // Set room metadata to specify agent type
    if (agentType) {
      at.roomConfig.metadata = agentType;
    }
  }

  return at.toJwt();
}
