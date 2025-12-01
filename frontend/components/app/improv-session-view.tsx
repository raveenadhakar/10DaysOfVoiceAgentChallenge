'use client';

import { useEffect, useState } from 'react';
import { useDataChannel } from '@livekit/components-react';
import { AppConfig } from '@/app-config';
import { SessionView } from '@/components/app/session-view';

interface ImprovData {
  type: string;
  data?: {
    player_name?: string;
    current_round?: number;
    max_rounds?: number;
    rounds?: Array<{ scenario: string; host_reaction: string }>;
    phase?: 'intro' | 'awaiting_improv' | 'reacting' | 'done';
  };
}

interface ImprovSessionViewProps {
  appConfig: AppConfig;
}

export function ImprovSessionView({ appConfig }: ImprovSessionViewProps) {
  const [playerName, setPlayerName] = useState<string>('Contestant');
  const [currentRound, setCurrentRound] = useState<number>(0);
  const [maxRounds, setMaxRounds] = useState<number>(3);
  const [rounds, setRounds] = useState<Array<{ scenario: string; host_reaction: string }>>([]);
  const [phase, setPhase] = useState<'intro' | 'awaiting_improv' | 'reacting' | 'done'>('intro');

  const { message } = useDataChannel('improv_session');

  useEffect(() => {
    if (!message) return;

    try {
      const rawText = new TextDecoder().decode(message.payload).trim();
      const data: ImprovData = JSON.parse(rawText);

      console.log('Received Improv data:', data);

      if (data.type === 'improv_update' && data.data) {
        if (data.data.player_name) setPlayerName(data.data.player_name);
        if (data.data.current_round !== undefined) setCurrentRound(data.data.current_round);
        if (data.data.max_rounds !== undefined) setMaxRounds(data.data.max_rounds);
        if (data.data.rounds) setRounds(data.data.rounds);
        if (data.data.phase) setPhase(data.data.phase);
      }
    } catch (error) {
      console.error('Failed to parse Improv data:', error);
    }
  }, [message]);

  const getPhaseDisplay = () => {
    switch (phase) {
      case 'intro':
        return { text: 'Getting Ready', color: 'text-pink-600', bg: 'bg-pink-100' };
      case 'awaiting_improv':
        return { text: 'Your Turn!', color: 'text-green-600', bg: 'bg-green-100' };
      case 'reacting':
        return { text: 'Host Feedback', color: 'text-blue-600', bg: 'bg-blue-100' };
      case 'done':
        return { text: 'Show Complete', color: 'text-purple-600', bg: 'bg-purple-100' };
      default:
        return { text: 'Unknown', color: 'text-gray-600', bg: 'bg-gray-100' };
    }
  };

  const phaseDisplay = getPhaseDisplay();

  return (
    <div className="flex h-full">
      {/* Left Sidebar - Game State */}
      <div className="flex w-96 flex-col border-r border-gray-200 bg-gradient-to-b from-pink-50 to-white">
        {/* Header */}
        <div className="border-b border-pink-200 bg-gradient-to-r from-pink-600 to-pink-700 p-4 text-white">
          <h1 className="text-xl font-bold">🎭 Improv Battle</h1>
          <p className="text-sm text-pink-100">Interactive Game Show</p>
        </div>

        {/* Player Info & Status */}
        <div className="border-b border-pink-200 bg-pink-100 p-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-pink-900">Contestant: {playerName}</span>
            <span className={`text-xs px-2 py-1 rounded-full ${phaseDisplay.bg} ${phaseDisplay.color} font-medium`}>
              {phaseDisplay.text}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs text-pink-700">Round {currentRound} of {maxRounds}</span>
            <div className="flex gap-1">
              {Array.from({ length: maxRounds }, (_, i) => (
                <div
                  key={i}
                  className={`w-2 h-2 rounded-full ${
                    i < currentRound ? 'bg-pink-600' : 'bg-pink-300'
                  }`}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Current Scenario */}
        {currentRound > 0 && rounds.length > 0 && (
          <div className="border-b border-gray-200 p-4">
            <h3 className="mb-2 flex items-center gap-2 font-semibold text-gray-900">
              <span className="text-lg">🎬</span>
              Current Scenario
            </h3>
            <div className="rounded-lg bg-pink-50 p-3 border border-pink-200">
              <p className="text-sm text-pink-900 font-medium">
                Round {currentRound}
              </p>
              <p className="text-sm text-gray-700 mt-1">
                {rounds[currentRound - 1]?.scenario}
              </p>
            </div>
          </div>
        )}

        {/* Performance History */}
        <div className="flex-1 overflow-y-auto p-4">
          <h3 className="mb-2 flex items-center gap-2 font-semibold text-gray-900">
            <span className="text-lg">📝</span>
            Performance History
          </h3>
          
          {rounds.length === 0 ? (
            <div className="text-center py-8">
              <div className="text-4xl mb-2">🎭</div>
              <p className="text-gray-500 text-sm">Ready to perform?</p>
              <p className="text-gray-400 text-xs mt-1">
                Say "Start Improv Battle" to begin!
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {rounds.map((round, index) => (
                <div
                  key={index}
                  className={`rounded-lg border p-3 ${
                    index === currentRound - 1 && phase === 'awaiting_improv'
                      ? 'border-pink-400 bg-pink-50'
                      : 'border-gray-200 bg-white'
                  }`}
                >
                  <div className="flex items-start gap-2 mb-2">
                    <span className="text-pink-600 font-bold text-xs mt-0.5">
                      Round {index + 1}
                    </span>
                    <div className="flex-1">
                      <p className="text-xs text-gray-600 mb-1">Scenario:</p>
                      <p className="text-sm text-gray-800">{round.scenario}</p>
                    </div>
                  </div>
                  
                  {round.host_reaction && (
                    <div className="mt-2 pt-2 border-t border-gray-100">
                      <p className="text-xs text-gray-600 mb-1">Host Reaction:</p>
                      <p className="text-sm text-gray-700 italic">"{round.host_reaction}"</p>
                    </div>
                  )}
                  
                  {index === currentRound - 1 && phase === 'awaiting_improv' && (
                    <div className="mt-2 pt-2 border-t border-pink-200">
                      <p className="text-xs text-pink-600 font-medium animate-pulse">
                        🎤 Your turn to perform!
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Quick Tips */}
        <div className="border-t border-gray-200 p-4 bg-pink-50">
          <h3 className="mb-2 font-semibold text-gray-900 text-sm">💡 Performance Tips</h3>
          
          <div className="space-y-1 text-xs text-gray-700">
            <div className="flex items-start gap-1">
              <span className="text-pink-600">•</span>
              <span>Commit fully to your character</span>
            </div>
            <div className="flex items-start gap-1">
              <span className="text-pink-600">•</span>
              <span>Say "End scene" when you're finished</span>
            </div>
            <div className="flex items-start gap-1">
              <span className="text-pink-600">•</span>
              <span>Be creative and have fun!</span>
            </div>
            <div className="flex items-start gap-1">
              <span className="text-pink-600">•</span>
              <span>The host will give you feedback after each scene</span>
            </div>
            <div className="flex items-start gap-1">
              <span className="text-pink-600">•</span>
              <span>Say "stop game" to exit early</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Session View */}
      <div className="flex flex-1 flex-col">
        <SessionView appConfig={appConfig} />
      </div>
    </div>
  );
}