'use client';

import React from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { useWellnessData } from '@/hooks/useWellnessData';
import { cn } from '@/lib/utils';

interface WellnessVisualizationProps {
  className?: string;
}

export function WellnessVisualization({ className }: WellnessVisualizationProps) {
  const { currentState, completionPercentage } = useWellnessData();

  const isVisible =
    currentState.mood ||
    currentState.energy_level ||
    currentState.stress_factors.length > 0 ||
    currentState.daily_objectives.length > 0 ||
    currentState.self_care_intentions.length > 0;

  const getMoodColor = (mood?: string) => {
    if (!mood) return 'from-gray-300 to-gray-400';
    const moodColors: Record<string, string> = {
      happy: 'from-yellow-300 to-orange-400',
      sad: 'from-blue-400 to-blue-600',
      stressed: 'from-red-400 to-red-600',
      anxious: 'from-orange-400 to-red-500',
      calm: 'from-green-300 to-blue-400',
      energetic: 'from-green-400 to-yellow-400',
      tired: 'from-purple-400 to-gray-500',
      optimistic: 'from-yellow-400 to-pink-400',
      focused: 'from-blue-400 to-purple-500',
      relaxed: 'from-green-300 to-teal-400',
    };
    return moodColors[mood.toLowerCase()] || 'from-gray-300 to-gray-400';
  };

  const getEnergyLevel = (energy?: string) => {
    if (!energy) return 0;
    const energyLevels: Record<string, number> = {
      low: 25,
      drained: 15,
      moderate: 50,
      high: 85,
      energized: 95,
    };
    return energyLevels[energy.toLowerCase()] || 0;
  };

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8, x: -20 }}
          animate={{ opacity: 1, scale: 1, x: 0 }}
          exit={{ opacity: 0, scale: 0.8, x: -20 }}
          transition={{ duration: 0.4, ease: 'easeOut' }}
          className={cn(
            'max-w-xs rounded-2xl border border-white/30 bg-white/90 p-6 shadow-xl backdrop-blur-sm',
            className
          )}
        >
          {/* Header */}
          <div className="mb-6 text-center">
            <h3 className="mb-1 text-lg font-semibold text-gray-800">Wellness Journey</h3>
            <p className="text-sm text-gray-600">Your emotional landscape</p>
          </div>

          {/* Mood Visualization */}
          <div className="mb-6">
            <div className="mb-3 text-sm font-medium text-gray-700">Current Mood</div>
            <div className="relative">
              <motion.div
                className={cn(
                  'mx-auto h-24 w-24 rounded-full bg-gradient-to-br shadow-lg',
                  getMoodColor(currentState.mood)
                )}
                animate={{
                  scale: [1, 1.05, 1],
                  rotate: [0, 2, -2, 0],
                }}
                transition={{
                  duration: 3,
                  repeat: Infinity,
                  ease: 'easeInOut',
                }}
              >
                <div className="absolute inset-0 flex items-center justify-center rounded-full bg-white/20 backdrop-blur-sm">
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
                    className="text-2xl"
                  >
                    {currentState.mood ? (
                      <span className="text-xs font-bold text-white capitalize">
                        {currentState.mood}
                      </span>
                    ) : (
                      '🤔'
                    )}
                  </motion.div>
                </div>
              </motion.div>
            </div>
          </div>

          {/* Energy Level Bar */}
          <div className="mb-6">
            <div className="mb-2 flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">Energy Level</span>
              <span className="text-xs text-gray-500 capitalize">
                {currentState.energy_level || 'Not set'}
              </span>
            </div>
            <div className="h-3 w-full overflow-hidden rounded-full bg-gray-200">
              <motion.div
                className="h-full rounded-full bg-gradient-to-r from-red-400 via-yellow-400 to-green-400"
                initial={{ width: 0 }}
                animate={{ width: `${getEnergyLevel(currentState.energy_level)}%` }}
                transition={{ duration: 1, ease: 'easeOut' }}
              />
            </div>
          </div>

          {/* Progress Rings */}
          <div className="mb-6">
            <div className="mb-3 text-sm font-medium text-gray-700">Check-in Progress</div>
            <div className="flex justify-center">
              <div className="relative h-20 w-20">
                <svg className="h-20 w-20 -rotate-90 transform" viewBox="0 0 36 36">
                  <path
                    className="text-gray-200"
                    stroke="currentColor"
                    strokeWidth="3"
                    fill="transparent"
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  />
                  <motion.path
                    className="text-blue-500"
                    stroke="currentColor"
                    strokeWidth="3"
                    fill="transparent"
                    strokeLinecap="round"
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    initial={{ strokeDasharray: '0 100' }}
                    animate={{ strokeDasharray: `${completionPercentage} 100` }}
                    transition={{ duration: 1.5, ease: 'easeOut' }}
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-sm font-semibold text-gray-700">
                    {Math.round(completionPercentage)}%
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-3 gap-2 text-center">
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="rounded-lg bg-red-50 p-2"
            >
              <div className="text-lg font-bold text-red-600">
                {currentState.stress_factors.length}
              </div>
              <div className="text-xs text-red-500">Stress</div>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="rounded-lg bg-purple-50 p-2"
            >
              <div className="text-lg font-bold text-purple-600">
                {currentState.daily_objectives.length}
              </div>
              <div className="text-xs text-purple-500">Goals</div>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="rounded-lg bg-indigo-50 p-2"
            >
              <div className="text-lg font-bold text-indigo-600">
                {currentState.self_care_intentions.length}
              </div>
              <div className="text-xs text-indigo-500">Self-care</div>
            </motion.div>
          </div>

          {/* Completion Status */}
          {currentState.check_in_complete && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.6, type: 'spring', stiffness: 200 }}
              className="mt-4 rounded-lg border border-green-200 bg-green-50 p-3 text-center"
            >
              <div className="text-sm font-medium text-green-600">✨ Check-in Complete!</div>
              <div className="mt-1 text-xs text-green-500">
                Great job taking care of yourself today
              </div>
            </motion.div>
          )}
        </motion.div>
      )}
    </AnimatePresence>
  );
}
