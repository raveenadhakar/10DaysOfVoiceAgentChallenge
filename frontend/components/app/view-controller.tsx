'use client';

import { AnimatePresence, motion } from 'motion/react';
import { useSession } from '@/components/app/session-provider';
import { TutorSessionView } from '@/components/app/tutor-session-view';
import { WelcomeView } from '@/components/app/welcome-view';

const MotionWelcomeView = motion.create(WelcomeView);
const MotionTutorSessionView = motion.create(TutorSessionView);

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

  return (
    <AnimatePresence mode="wait">
      {/* Welcome screen */}
      {!isSessionActive && (
        <MotionWelcomeView
          key="welcome"
          {...VIEW_MOTION_PROPS}
          startButtonText={appConfig.startButtonText}
          onStartCall={startSession}
        />
      )}
      {/* Tutor session view */}
      {isSessionActive && (
        <MotionTutorSessionView
          key="tutor-session-view"
          {...VIEW_MOTION_PROPS}
          appConfig={appConfig}
        />
      )}
    </AnimatePresence>
  );
}
