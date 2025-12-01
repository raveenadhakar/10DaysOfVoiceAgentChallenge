 'use client';

import { AnimatePresence, motion } from 'motion/react';
import { FoodSessionView } from '@/components/app/food-session-view';
import { GMSessionView } from '@/components/app/gm-session-view';
import { FraudSessionView } from '@/components/app/fraud-session-view';
import { TutorSessionView } from '@/components/app/tutor-session-view';
import { SDRSessionView } from '@/components/app/sdr-session-view';
import { WellnessSessionView } from '@/components/app/wellness-session-view';
import { CommerceSessionView } from '@/components/app/commerce-session-view';
import { ImprovSessionView } from '@/components/app/improv-session-view';
import { useSession } from '@/components/app/session-provider';
import { WelcomeView } from '@/components/app/welcome-view';

const MotionWelcomeView = motion.create(WelcomeView);
const MotionFoodSessionView = motion.create(FoodSessionView);
const MotionGMSessionView = motion.create(GMSessionView);
const MotionFraudSessionView = motion.create(FraudSessionView);
const MotionTutorSessionView = motion.create(TutorSessionView);
const MotionSDRSessionView = motion.create(SDRSessionView);
const MotionWellnessSessionView = motion.create(WellnessSessionView);
const MotionCommerceSessionView = motion.create(CommerceSessionView);
const MotionImprovSessionView = motion.create(ImprovSessionView);

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

  const agentType = appConfig.agentType || 'food';

  return (
    <AnimatePresence mode="wait">
      {/* Welcome screen */}
      {!isSessionActive && (
        <MotionWelcomeView
          key="welcome"
          {...VIEW_MOTION_PROPS}
          startButtonText={appConfig.startButtonText}
          onStartCall={startSession}
          mode={agentType}
        />
      )}
      {/* Session views based on agent type */}
      {isSessionActive && agentType === 'food' && (
        <MotionFoodSessionView
          key="food-session-view"
          {...VIEW_MOTION_PROPS}
          appConfig={appConfig}
        />
      )}
      {isSessionActive && agentType === 'gm' && (
        <MotionGMSessionView
          key="gm-session-view"
          {...VIEW_MOTION_PROPS}
          appConfig={appConfig}
        />
      )}
      {isSessionActive && agentType === 'fraud' && (
        <MotionFraudSessionView
          key="fraud-session-view"
          {...VIEW_MOTION_PROPS}
          appConfig={appConfig}
        />
      )}
      {isSessionActive && agentType === 'tutor' && (
        <MotionTutorSessionView
          key="tutor-session-view"
          {...VIEW_MOTION_PROPS}
          appConfig={appConfig}
        />
      )}
      {isSessionActive && agentType === 'sdr' && (
        <MotionSDRSessionView
          key="sdr-session-view"
          {...VIEW_MOTION_PROPS}
          appConfig={appConfig}
        />
      )}
      {isSessionActive && agentType === 'wellness' && (
        <MotionWellnessSessionView
          key="wellness-session-view"
          {...VIEW_MOTION_PROPS}
          appConfig={appConfig}
        />
      )}
      {isSessionActive && agentType === 'commerce' && (
        <MotionCommerceSessionView
          key="commerce-session-view"
          {...VIEW_MOTION_PROPS}
          appConfig={appConfig}
        />
      )}
      {isSessionActive && agentType === 'improv' && (
        <MotionImprovSessionView
          key="improv-session-view"
          {...VIEW_MOTION_PROPS}
          appConfig={appConfig}
        />
      )}
    </AnimatePresence>
  );
}