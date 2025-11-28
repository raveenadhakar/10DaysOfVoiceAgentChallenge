'use client';

import { RoomAudioRenderer, StartAudio } from '@livekit/components-react';
import type { AppConfig } from '@/app-config';
import { SessionProvider } from '@/components/app/session-provider';
import { ViewController } from '@/components/app/view-controller';
import { Toaster } from '@/components/livekit/toaster';

interface AppProps {
  appConfig: AppConfig;
}

export function App({ appConfig }: AppProps) {
  return (
    <SessionProvider appConfig={appConfig}>
      <main className="h-svh">
        <ViewController />
      </main>

      {/* Required for LiveKit audio */}
      <StartAudio label="Start Audio" />
      <RoomAudioRenderer />

      {/* Toast notifications */}
      <Toaster />
    </SessionProvider>
  );
}
