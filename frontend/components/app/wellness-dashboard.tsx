'use client';

import React from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { useWellnessData } from '@/hooks/useWellnessData';
import { cn } from '@/lib/utils';

interface WellnessDashboardProps {
  className?: string;
}

export function WellnessDashboard({ className }: WellnessDashboardProps) {
  const { currentState, recentEntries, completionPercentage } = useWellnessData();

  const isVisible =
    currentState.mood ||
    currentState.energy_level ||
    currentState.stress_factors.length > 0 ||
    currentState.daily_objectives.length > 0 ||
    currentState.self_care_intentions.length > 0;

  const getMoodEmoji = (mood?: string) => {
    if (!mood) return '😊';
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

  const getEnergyColor = (energy?: string) => {
    if (!energy) return 'bg-gray-200';
    const energyMap: Record<string, string> = {
      high: 'bg-green-500',
      moderate: 'bg-yellow-500',
      low: 'bg-red-500',
      energized: 'bg-green-400',
      drained: 'bg-red-600',
    };
    return energyMap[energy.toLowerCase()] || 'bg-gray-200';
  };

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 20 }}
          transition={{ duration: 0.3, ease: 'easeOut' }}
          className={cn(
            'max-w-md rounded-2xl border border-gray-200 bg-white/95 p-6 shadow-xl backdrop-blur-sm',
            className
          )}
        >
          {/* Header */}
          <div className="mb-6 flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-800">Wellness Check-in</h2>
            <div className="text-2xl">{getMoodEmoji(currentState.mood)}</div>
          </div>

          {/* Current State */}
          <div className="space-y-4">
            {/* Mood & Energy */}
            <div className="grid grid-cols-2 gap-4">
              <div className="rounded-lg bg-blue-50 p-3">
                <div className="text-sm font-medium text-blue-600">Mood</div>
                <div className="text-lg text-blue-800 capitalize">
                  {currentState.mood || 'Not set'}
                </div>
              </div>
              <div className="rounded-lg bg-green-50 p-3">
                <div className="text-sm font-medium text-green-600">Energy</div>
                <div className="flex items-center gap-2">
                  <div
                    className={cn(
                      'h-3 w-3 rounded-full',
                      getEnergyColor(currentState.energy_level)
                    )}
                  />
                  <div className="text-lg text-green-800 capitalize">
                    {currentState.energy_level || 'Not set'}
                  </div>
                </div>
              </div>
            </div>

            {/* Stress Factors */}
            {currentState.stress_factors.length > 0 && (
              <div className="rounded-lg bg-red-50 p-3">
                <div className="mb-2 text-sm font-medium text-red-600">Stress Factors</div>
                <div className="space-y-1">
                  {currentState.stress_factors.map((factor, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="rounded bg-red-100 px-2 py-1 text-sm text-red-700"
                    >
                      {factor}
                    </motion.div>
                  ))}
                </div>
              </div>
            )}

            {/* Daily Objectives */}
            {currentState.daily_objectives.length > 0 && (
              <div className="rounded-lg bg-purple-50 p-3">
                <div className="mb-2 text-sm font-medium text-purple-600">Today&apos;s Goals</div>
                <div className="space-y-1">
                  {currentState.daily_objectives.map((objective, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="flex items-center gap-2 rounded bg-purple-100 px-2 py-1 text-sm text-purple-700"
                    >
                      <span>🎯</span>
                      {objective}
                    </motion.div>
                  ))}
                </div>
              </div>
            )}

            {/* Self-care Intentions */}
            {currentState.self_care_intentions.length > 0 && (
              <div className="rounded-lg bg-indigo-50 p-3">
                <div className="mb-2 text-sm font-medium text-indigo-600">Self-care Plans</div>
                <div className="space-y-1">
                  {currentState.self_care_intentions.map((intention, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="flex items-center gap-2 rounded bg-indigo-100 px-2 py-1 text-sm text-indigo-700"
                    >
                      <span>💆</span>
                      {intention}
                    </motion.div>
                  ))}
                </div>
              </div>
            )}

            {/* Progress Indicator */}
            <div className="rounded-lg bg-gray-50 p-3">
              <div className="mb-2 flex items-center justify-between">
                <div className="text-sm font-medium text-gray-600">Check-in Progress</div>
                <div className="text-sm text-gray-500">
                  {currentState.check_in_complete ? 'Complete' : 'In Progress'}
                </div>
              </div>
              <div className="h-2 w-full rounded-full bg-gray-200">
                <motion.div
                  className="h-2 rounded-full bg-gradient-to-r from-blue-500 to-purple-500"
                  initial={{ width: 0 }}
                  animate={{
                    width: `${completionPercentage}%`,
                  }}
                  transition={{ duration: 0.5, ease: 'easeOut' }}
                />
              </div>
            </div>
          </div>

          {/* Recent History Preview */}
          {recentEntries.length > 0 && (
            <div className="mt-6 border-t border-gray-200 pt-4">
              <div className="mb-3 text-sm font-medium text-gray-600">Recent Check-ins</div>
              <div className="space-y-2">
                {recentEntries.map((entry, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between rounded bg-gray-50 p-2 text-xs text-gray-500"
                  >
                    <div className="flex items-center gap-2">
                      <span>{getMoodEmoji(entry.mood)}</span>
                      <span className="capitalize">{entry.mood}</span>
                    </div>
                    <div className="text-right">
                      <div>{new Date(entry.date).toLocaleDateString()}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </motion.div>
      )}
    </AnimatePresence>
  );
}
