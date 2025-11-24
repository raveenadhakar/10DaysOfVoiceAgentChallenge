'use client';

import React, { useEffect, useState } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { useWellnessData } from '@/hooks/useWellnessData';
import { cn } from '@/lib/utils';

interface WellnessInsightsProps {
  className?: string;
}

const WELLNESS_TIPS = [
  {
    icon: '🌱',
    title: 'Growth Mindset',
    message: 'Every small step counts toward your wellbeing journey.',
  },
  {
    icon: '💙',
    title: 'Self-Compassion',
    message: 'Be kind to yourself. You deserve the same compassion you give others.',
  },
  {
    icon: '🌟',
    title: 'Present Moment',
    message: 'Take a deep breath and notice something beautiful around you.',
  },
  {
    icon: '🎯',
    title: 'Small Wins',
    message: 'Celebrate your progress, no matter how small it may seem.',
  },
  {
    icon: '🌈',
    title: 'Hope',
    message: 'Tomorrow is a new day with new possibilities.',
  },
  {
    icon: '💪',
    title: 'Resilience',
    message: 'You have overcome challenges before. You can do it again.',
  },
];

const MOOD_SPECIFIC_INSIGHTS = {
  stressed: {
    icon: '🧘',
    title: 'Stress Relief',
    message: 'Try the 4-7-8 breathing technique: inhale for 4, hold for 7, exhale for 8.',
  },
  anxious: {
    icon: '🌊',
    title: 'Calm Waters',
    message: 'Ground yourself by naming 5 things you can see, 4 you can touch, 3 you can hear.',
  },
  tired: {
    icon: '😴',
    title: 'Rest & Recharge',
    message: 'Your body is asking for rest. Listen to it with kindness.',
  },
  sad: {
    icon: '🤗',
    title: 'Gentle Support',
    message: 'It&apos;s okay to feel sad. These feelings are temporary and valid.',
  },
  happy: {
    icon: '✨',
    title: 'Joy Amplifier',
    message: 'Share your happiness! Joy multiplies when shared with others.',
  },
  optimistic: {
    icon: '🌅',
    title: 'Bright Outlook',
    message: 'Your positive energy is contagious. Keep shining!',
  },
};

export function WellnessInsights({ className }: WellnessInsightsProps) {
  const { currentState, moodTrend } = useWellnessData();
  const [currentTip, setCurrentTip] = useState(WELLNESS_TIPS[0]);
  const [showInsight, setShowInsight] = useState(false);

  useEffect(() => {
    // Show mood-specific insight if available
    if (
      currentState.mood &&
      MOOD_SPECIFIC_INSIGHTS[currentState.mood.toLowerCase() as keyof typeof MOOD_SPECIFIC_INSIGHTS]
    ) {
      setCurrentTip(
        MOOD_SPECIFIC_INSIGHTS[
          currentState.mood.toLowerCase() as keyof typeof MOOD_SPECIFIC_INSIGHTS
        ]
      );
      setShowInsight(true);
    } else {
      // Rotate through general tips
      const interval = setInterval(() => {
        setCurrentTip(WELLNESS_TIPS[Math.floor(Math.random() * WELLNESS_TIPS.length)]);
        setShowInsight(true);
      }, 15000);

      return () => clearInterval(interval);
    }
  }, [currentState.mood]);

  // Show initial tip after a delay
  useEffect(() => {
    const timer = setTimeout(() => {
      setShowInsight(true);
    }, 3000);

    return () => clearTimeout(timer);
  }, []);

  const getEncouragement = () => {
    if (currentState.check_in_complete) {
      return {
        icon: '🎉',
        title: 'Check-in Complete!',
        message: 'Great job taking time for your mental health today.',
      };
    }

    if (moodTrend === 'improving') {
      return {
        icon: '📈',
        title: 'Positive Trend',
        message: 'Your mood has been improving. Keep up the great work!',
      };
    }

    if (currentState.daily_objectives.length > 0) {
      return {
        icon: '🎯',
        title: 'Goal Setter',
        message: `You've set ${currentState.daily_objectives.length} goal${currentState.daily_objectives.length > 1 ? 's' : ''} today. That's wonderful!`,
      };
    }

    return currentTip;
  };

  const insight = getEncouragement();

  return (
    <AnimatePresence>
      {showInsight && (
        <motion.div
          initial={{ opacity: 0, y: 20, scale: 0.9 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 20, scale: 0.9 }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
          className={cn(
            'max-w-xs rounded-2xl border border-blue-200 bg-gradient-to-br from-blue-50 to-indigo-100 p-4 shadow-lg',
            className
          )}
        >
          <div className="flex items-start gap-3">
            <motion.div
              animate={{
                scale: [1, 1.1, 1],
                rotate: [0, 5, -5, 0],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: 'easeInOut',
              }}
              className="text-2xl"
            >
              {insight.icon}
            </motion.div>
            <div className="flex-1">
              <h4 className="mb-1 text-sm font-semibold text-blue-800">{insight.title}</h4>
              <p className="text-xs leading-relaxed text-blue-700">{insight.message}</p>
            </div>
          </div>

          {/* Progress indicator for check-in */}
          {!currentState.check_in_complete && (
            <div className="mt-3 border-t border-blue-200 pt-3">
              <div className="flex items-center justify-between text-xs text-blue-600">
                <span>Keep going!</span>
                <span>You&apos;re doing great</span>
              </div>
            </div>
          )}

          {/* Dismiss button */}
          <button
            onClick={() => setShowInsight(false)}
            className="absolute top-2 right-2 text-blue-400 transition-colors hover:text-blue-600"
          >
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
