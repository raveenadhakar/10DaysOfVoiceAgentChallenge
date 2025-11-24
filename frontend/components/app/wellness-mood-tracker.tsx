'use client';

import React from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { useWellnessData } from '@/hooks/useWellnessData';
import { cn } from '@/lib/utils';

interface WellnessMoodTrackerProps {
  className?: string;
}

export function WellnessMoodTracker({ className }: WellnessMoodTrackerProps) {
  const { recentEntries, moodTrend, isLoading } = useWellnessData();

  if (isLoading || recentEntries.length === 0) {
    return null;
  }

  const getMoodEmoji = (mood: string) => {
    const moodMap: Record<string, string> = {
      happy: '😊',
      sad: '😢',
      stressed: '😰',
      anxious: '😟',
      calm: '😌',
      energetic: '⚡',
      tired: '😴',
      optimistic: '🌟',
      focused: '🎯',
      relaxed: '😌',
    };
    return moodMap[mood.toLowerCase()] || '😊';
  };

  const getTrendIcon = () => {
    switch (moodTrend) {
      case 'improving':
        return '📈';
      case 'declining':
        return '📉';
      default:
        return '➡️';
    }
  };

  const getTrendColor = () => {
    switch (moodTrend) {
      case 'improving':
        return 'text-green-600 bg-green-50';
      case 'declining':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-blue-600 bg-blue-50';
    }
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, scale: 0.9, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.9, y: 20 }}
        transition={{ duration: 0.3, ease: 'easeOut' }}
        className={cn(
          'max-w-xs rounded-2xl border border-white/30 bg-white/90 p-4 shadow-lg backdrop-blur-sm',
          className
        )}
      >
        {/* Header */}
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-gray-800">Mood History</h3>
          <div className={cn('rounded-full px-2 py-1 text-xs font-medium', getTrendColor())}>
            {getTrendIcon()} {moodTrend}
          </div>
        </div>

        {/* Recent Moods Timeline */}
        <div className="space-y-3">
          {recentEntries
            .slice(-4)
            .reverse()
            .map((entry, index) => (
              <motion.div
                key={entry.timestamp}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-center justify-between"
              >
                <div className="flex items-center gap-3">
                  <div className="text-lg">{getMoodEmoji(entry.mood)}</div>
                  <div>
                    <div className="text-sm font-medium text-gray-800 capitalize">{entry.mood}</div>
                    <div className="text-xs text-gray-500">
                      {new Date(entry.date).toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric',
                      })}
                    </div>
                  </div>
                </div>
                <div className="text-xs text-gray-400">
                  {entry.time.split(':').slice(0, 2).join(':')}
                </div>
              </motion.div>
            ))}
        </div>

        {/* Weekly Summary */}
        {recentEntries.length >= 3 && (
          <div className="mt-4 border-t border-gray-200 pt-3">
            <div className="mb-2 text-xs font-medium text-gray-600">This Week</div>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="rounded bg-blue-50 p-2 text-center">
                <div className="font-semibold text-blue-600">{recentEntries.length}</div>
                <div className="text-blue-500">Check-ins</div>
              </div>
              <div className="rounded bg-purple-50 p-2 text-center">
                <div className="font-semibold text-purple-600">
                  {Math.round(
                    recentEntries.reduce((acc, entry) => acc + entry.daily_objectives.length, 0) /
                      recentEntries.length
                  )}
                </div>
                <div className="text-purple-500">Avg Goals</div>
              </div>
            </div>
          </div>
        )}
      </motion.div>
    </AnimatePresence>
  );
}
