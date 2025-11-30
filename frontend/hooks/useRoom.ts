import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Room, RoomEvent, TokenSource } from 'livekit-client';
import { AppConfig } from '@/app-config';
import { toastAlert } from '@/components/livekit/alert-toast';

export function useRoom(appConfig: AppConfig) {
  const aborted = useRef(false);
  const room = useMemo(() => new Room(), []);
  const [isSessionActive, setIsSessionActive] = useState(false);

  useEffect(() => {
    function onDisconnected() {
      setIsSessionActive(false);
    }

    function onMediaDevicesError(error: Error) {
      toastAlert({
        title: 'Encountered an error with your media devices',
        description: `${error.name}: ${error.message}`,
      });
    }

    room.on(RoomEvent.Disconnected, onDisconnected);
    room.on(RoomEvent.MediaDevicesError, onMediaDevicesError);

    return () => {
      room.off(RoomEvent.Disconnected, onDisconnected);
      room.off(RoomEvent.MediaDevicesError, onMediaDevicesError);
    };
  }, [room]);

  useEffect(() => {
    return () => {
      aborted.current = true;
      room.disconnect();
    };
  }, [room]);

  const tokenSource = useMemo(
    () =>
      TokenSource.custom(async () => {
        const url = new URL(
          process.env.NEXT_PUBLIC_CONN_DETAILS_ENDPOINT ?? '/api/connection-details',
          window.location.origin
        );

        const requestBody = {
          agent_type: appConfig.agentType || 'food',
          room_config: appConfig.agentName
            ? {
                agents: [{ agent_name: appConfig.agentName }],
              }
            : undefined,
        };

        console.log('🎯 Sending connection request with:', requestBody);

        try {
          const res = await fetch(url.toString(), {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-Sandbox-Id': appConfig.sandboxId ?? '',
            },
            body: JSON.stringify(requestBody),
          });
          const data = await res.json();
          console.log('✅ Received connection details:', data);
          return data;
        } catch (error) {
          console.error('❌ Error fetching connection details:', error);
          throw new Error('Error fetching connection details!');
        }
      }),
    [appConfig]
  );

  const startSession = useCallback(() => {
    console.log('🚀 Starting session with config:', {
      agentType: appConfig.agentType,
      agentName: appConfig.agentName,
      roomState: room.state
    });
    
    setIsSessionActive(true);

    if (room.state === 'disconnected') {
      const { isPreConnectBufferEnabled } = appConfig;
      
      // Show a connecting toast
      toastAlert({
        title: 'Connecting to agent...',
        description: 'Please allow microphone access when prompted',
      });
      
      Promise.all([
        room.localParticipant.setMicrophoneEnabled(true, undefined, {
          preConnectBuffer: isPreConnectBufferEnabled,
        }).catch((micError) => {
          console.error('❌ Microphone error:', micError);
          throw new Error(`Microphone access denied or unavailable: ${micError.message}`);
        }),
        tokenSource
          .fetch({ agentName: appConfig.agentName })
          .then((connectionDetails) => {
            console.log('✅ Connection details received:', connectionDetails);
            if (!connectionDetails.serverUrl || !connectionDetails.participantToken) {
              throw new Error('Invalid connection details received from server');
            }
            return room.connect(connectionDetails.serverUrl, connectionDetails.participantToken);
          }),
      ])
      .then(() => {
        console.log('✅ Successfully connected to room');
        toastAlert({
          title: 'Connected!',
          description: 'You can now speak to the agent',
        });
      })
      .catch((error) => {
        if (aborted.current) {
          // Once the effect has cleaned up after itself, drop any errors
          //
          // These errors are likely caused by this effect rerunning rapidly,
          // resulting in a previous run `disconnect` running in parallel with
          // a current run `connect`
          return;
        }

        console.error('❌ Error connecting to agent:', error);
        setIsSessionActive(false); // Reset session state on error
        
        // Provide more specific error messages
        let errorTitle = 'Connection Error';
        let errorDescription = error.message;
        
        if (error.message.includes('Microphone')) {
          errorTitle = 'Microphone Access Required';
          errorDescription = 'Please allow microphone access in your browser settings and try again.';
        } else if (error.message.includes('connection details')) {
          errorTitle = 'Server Connection Failed';
          errorDescription = 'Could not connect to the voice agent server. Please check if the backend is running.';
        }
        
        toastAlert({
          title: errorTitle,
          description: errorDescription,
        });
      });
    } else {
      console.log('⚠️ Room is not in disconnected state:', room.state);
    }
  }, [room, appConfig, tokenSource]);

  const endSession = useCallback(() => {
    setIsSessionActive(false);
  }, []);

  return { room, isSessionActive, startSession, endSession };
}
