 'use client';

import { AnimatePresence, motion } from 'motion/react';
import { FoodSessionView } from '@/components/app/food-session-view';
import { useSession } from '@/components/app/session-provider';
import { WelcomeView } from '@/components/app/welcome-view';

const MotionWelcomeView = motion.create(WelcomeView);
const MotionFoodSessionView = motion.create(FoodSessionView);

const VIEW_MOTION_PROPS = {
  variants: {
    visible: {
      opacity: 1,
    },
    hidden: {
      opacity: 0,
    },
  },
  initial: 'hidden' as const,
  animate: 'visible' as const,
  exit: 'hidden' as const,
  transition: {
    duration: 0.5,
  },
};

export function ViewController() {
  const { appConfig, isSessionActive, startSession } = useSession();

  // Food ordering mode only
  const mode = 'food';

  return (
    <AnimatePresence mode="wait">
      {/* Welcome screen */}
      {!isSessionActive && (
        <MotionWelcomeView
          key="welcome"
          {...VIEW_MOTION_PROPS}
          startButtonText={appConfig.startButtonText}
          onStartCall={startSession}
          mode={mode}
        />
      )}
      {/* Food ordering session view */}
      {isSessionActive && (
        <MotionFoodSessionView
          key="food-session-view"
          {...VIEW_MOTION_PROPS}
          appConfig={appConfig}
        />
      )}
    </AnimatePresence>
  );
}