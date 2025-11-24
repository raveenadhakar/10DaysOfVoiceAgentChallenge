'use client';

import React from 'react';
import { motion } from 'motion/react';
import { cn } from '@/lib/utils';

interface WellnessWelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
  className?: string;
}

export function WellnessWelcomeView({
  startButtonText,
  onStartCall,
  className,
}: WellnessWelcomeViewProps) {
  return (
    <div className={cn('flex min-h-screen flex-col items-center justify-center p-8', className)}>
      {/* Background Elements */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.1, 0.2, 0.1],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          className="absolute -top-1/2 -right-1/2 h-full w-full rounded-full bg-gradient-to-br from-blue-200/30 to-purple-200/30 blur-3xl"
        />
        <motion.div
          animate={{
            scale: [1.2, 1, 1.2],
            opacity: [0.1, 0.15, 0.1],
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: 'easeInOut',
            delay: 2,
          }}
          className="absolute -bottom-1/2 -left-1/2 h-full w-full rounded-full bg-gradient-to-tr from-indigo-200/30 to-pink-200/30 blur-3xl"
        />
      </div>

      {/* Main Content */}
      <div className="relative z-10 mx-auto max-w-2xl text-center">
        {/* Logo/Icon */}
        <motion.div
          initial={{ scale: 0, rotate: -180 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          className="mb-8"
        >
          <div className="mx-auto flex h-24 w-24 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-purple-600 shadow-2xl">
            <span className="text-4xl">🌱</span>
          </div>
        </motion.div>

        {/* Title */}
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.6 }}
          className="mb-4 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-4xl font-bold text-transparent md:text-5xl"
        >
          Wellness Companion
        </motion.h1>

        {/* Subtitle */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.6 }}
          className="mb-8 text-xl leading-relaxed text-gray-600"
        >
          Your supportive AI companion for daily wellness check-ins
        </motion.p>

        {/* Features */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7, duration: 0.6 }}
          className="mb-12 grid grid-cols-1 gap-6 md:grid-cols-3"
        >
          <div className="rounded-2xl border border-white/30 bg-white/80 p-6 shadow-lg backdrop-blur-sm">
            <div className="mb-3 text-3xl">💭</div>
            <h3 className="mb-2 font-semibold text-gray-800">Mood Check-ins</h3>
            <p className="text-sm text-gray-600">
              Share how you&apos;re feeling in a safe, supportive environment
            </p>
          </div>
          <div className="rounded-2xl border border-white/30 bg-white/80 p-6 shadow-lg backdrop-blur-sm">
            <div className="mb-3 text-3xl">🎯</div>
            <h3 className="mb-2 font-semibold text-gray-800">Goal Setting</h3>
            <p className="text-sm text-gray-600">
              Set and track daily objectives for personal growth
            </p>
          </div>
          <div className="rounded-2xl border border-white/30 bg-white/80 p-6 shadow-lg backdrop-blur-sm">
            <div className="mb-3 text-3xl">🌿</div>
            <h3 className="mb-2 font-semibold text-gray-800">Self-care</h3>
            <p className="text-sm text-gray-600">
              Plan meaningful self-care activities for your wellbeing
            </p>
          </div>
        </motion.div>

        {/* Start Button */}
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.9, duration: 0.6, type: 'spring', stiffness: 200 }}
        >
          <button
            onClick={onStartCall}
            className="group relative transform rounded-2xl bg-gradient-to-r from-blue-500 to-purple-600 px-8 py-4 font-semibold text-white shadow-xl transition-all duration-300 hover:scale-105 hover:shadow-2xl"
          >
            <span className="relative z-10">{startButtonText}</span>
            <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-blue-600 to-purple-700 opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
          </button>
        </motion.div>

        {/* Instructions */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2, duration: 0.6 }}
          className="mt-8 text-sm text-gray-500"
        >
          <p>Click the button above to start your wellness check-in with Alex</p>
          <p className="mt-2">
            💡 <strong>Tip:</strong> Find a quiet space where you can speak comfortably
          </p>
        </motion.div>
      </div>

      {/* Floating Elements */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        {[...Array(6)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute h-2 w-2 rounded-full bg-gradient-to-r from-blue-400 to-purple-400 opacity-20"
            animate={{
              x: [0, 100, 0],
              y: [0, -100, 0],
              scale: [1, 1.5, 1],
            }}
            transition={{
              duration: 8 + i * 2,
              repeat: Infinity,
              ease: 'easeInOut',
              delay: i * 1.5,
            }}
            style={{
              left: `${10 + i * 15}%`,
              top: `${20 + i * 10}%`,
            }}
          />
        ))}
      </div>
    </div>
  );
}
