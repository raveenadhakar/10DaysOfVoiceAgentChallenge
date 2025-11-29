'use client';

import { useEffect, useState } from 'react';
import { useDataChannel } from '@livekit/components-react';
import { AppConfig } from '@/app-config';
import { SessionView } from '@/components/app/session-view';

interface StoryData {
  type: string;
  data?: {
    location?: string;
    npcs_met?: Array<{ name: string; description: string }>;
    items_found?: Array<{ name: string; description: string }>;
    key_events?: string[];
    turn_count?: number;
  };
}

interface GMSessionViewProps {
  appConfig: AppConfig;
}

export function GMSessionView({ appConfig }: GMSessionViewProps) {
  const [location, setLocation] = useState<string>('Unknown');
  const [npcsMet, setNpcsMet] = useState<Array<{ name: string; description: string }>>([]);
  const [itemsFound, setItemsFound] = useState<Array<{ name: string; description: string }>>([]);
  const [keyEvents, setKeyEvents] = useState<string[]>([]);
  const [turnCount, setTurnCount] = useState<number>(0);

  const { message } = useDataChannel('gm_session');

  useEffect(() => {
    if (!message) return;

    try {
      const rawText = new TextDecoder().decode(message.payload).trim();
      const data: StoryData = JSON.parse(rawText);

      console.log('Received GM story data:', data);

      if (data.type === 'story_update' && data.data) {
        if (data.data.location) setLocation(data.data.location);
        if (data.data.npcs_met) setNpcsMet(data.data.npcs_met);
        if (data.data.items_found) setItemsFound(data.data.items_found);
        if (data.data.key_events) setKeyEvents(data.data.key_events);
        if (data.data.turn_count !== undefined) setTurnCount(data.data.turn_count);
      }
    } catch (error) {
      console.error('Failed to parse GM story data:', error);
    }
  }, [message]);

  return (
    <div className="flex h-full">
      {/* Left Sidebar - Story State */}
      <div className="flex w-96 flex-col border-r border-gray-200 bg-gradient-to-b from-purple-50 to-white">
        {/* Header */}
        <div className="border-b border-purple-200 bg-gradient-to-r from-purple-600 to-purple-700 p-4 text-white">
          <h1 className="text-xl font-bold">🎲 Fantasy Quest</h1>
          <p className="text-sm text-purple-100">D&D Game Master</p>
        </div>

        {/* Turn Counter */}
        <div className="border-b border-purple-200 bg-purple-100 p-3">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-purple-900">Turn {turnCount}</span>
            <span className="text-xs text-purple-700">Your adventure continues...</span>
          </div>
        </div>

        {/* Current Location */}
        <div className="border-b border-gray-200 p-4">
          <h3 className="mb-2 flex items-center gap-2 font-semibold text-gray-900">
            <span className="text-lg">📍</span>
            Current Location
          </h3>
          <div className="rounded-lg bg-purple-50 p-3 border border-purple-200">
            <p className="font-medium text-purple-900">{location}</p>
          </div>
        </div>

        {/* NPCs Met */}
        <div className="border-b border-gray-200 p-4">
          <h3 className="mb-2 flex items-center gap-2 font-semibold text-gray-900">
            <span className="text-lg">👥</span>
            Characters Met ({npcsMet.length})
          </h3>
          
          {npcsMet.length === 0 ? (
            <p className="text-sm text-gray-500 italic">No characters encountered yet</p>
          ) : (
            <div className="space-y-2">
              {npcsMet.map((npc, index) => (
                <div
                  key={index}
                  className="rounded-lg border border-purple-200 bg-white p-2 hover:border-purple-300 transition-colors"
                >
                  <div className="font-medium text-sm text-gray-900">{npc.name}</div>
                  {npc.description && (
                    <div className="text-xs text-gray-600 mt-0.5">{npc.description}</div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Items Found */}
        <div className="border-b border-gray-200 p-4">
          <h3 className="mb-2 flex items-center gap-2 font-semibold text-gray-900">
            <span className="text-lg">🎒</span>
            Inventory ({itemsFound.length})
          </h3>
          
          {itemsFound.length === 0 ? (
            <p className="text-sm text-gray-500 italic">No items collected yet</p>
          ) : (
            <div className="space-y-2">
              {itemsFound.map((item, index) => (
                <div
                  key={index}
                  className="rounded-lg border border-purple-200 bg-white p-2 hover:border-purple-300 transition-colors"
                >
                  <div className="font-medium text-sm text-gray-900">{item.name}</div>
                  {item.description && (
                    <div className="text-xs text-gray-600 mt-0.5">{item.description}</div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Key Events */}
        <div className="flex-1 overflow-y-auto p-4">
          <h3 className="mb-2 flex items-center gap-2 font-semibold text-gray-900">
            <span className="text-lg">📜</span>
            Story Events
          </h3>
          
          {keyEvents.length === 0 ? (
            <div className="text-center py-8">
              <div className="text-4xl mb-2">⚔️</div>
              <p className="text-gray-500 text-sm">Your adventure awaits!</p>
              <p className="text-gray-400 text-xs mt-1">
                Say "Start adventure" to begin your quest
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {keyEvents.map((event, index) => (
                <div
                  key={index}
                  className="rounded-lg border border-gray-200 bg-white p-2 text-sm"
                >
                  <div className="flex items-start gap-2">
                    <span className="text-purple-600 font-bold text-xs mt-0.5">
                      {index + 1}.
                    </span>
                    <span className="text-gray-700 flex-1">{event}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Quick Tips */}
        <div className="border-t border-gray-200 p-4 bg-purple-50">
          <h3 className="mb-2 font-semibold text-gray-900 text-sm">💡 Quick Tips</h3>
          
          <div className="space-y-1 text-xs text-gray-700">
            <div className="flex items-start gap-1">
              <span className="text-purple-600">•</span>
              <span>The GM will describe scenes and ask "What do you do?"</span>
            </div>
            <div className="flex items-start gap-1">
              <span className="text-purple-600">•</span>
              <span>Your choices shape the story</span>
            </div>
            <div className="flex items-start gap-1">
              <span className="text-purple-600">•</span>
              <span>Be creative! Try anything you can imagine</span>
            </div>
            <div className="flex items-start gap-1">
              <span className="text-purple-600">•</span>
              <span>Say "restart story" to begin a new adventure</span>
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
