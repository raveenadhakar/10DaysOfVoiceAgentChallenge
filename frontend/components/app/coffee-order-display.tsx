'use client';

import React from 'react';
import { CheckCircle, Coffee, Milk, Plus, User } from 'lucide-react';
import { AnimatePresence, motion } from 'motion/react';
import { useOrderState } from '@/hooks/useOrderState';
import { cn } from '@/lib/utils';
import { CoffeeAnimation } from './coffee-animation';

interface CoffeeOrderDisplayProps {
  className?: string;
}

export function CoffeeOrderDisplay({ className }: CoffeeOrderDisplayProps) {
  const { orderState, isOrderComplete, completedOrder } = useOrderState();

  const isComplete = orderState.drinkType && orderState.size && orderState.milk && orderState.name;

  const hasAnyOrderData = Object.values(orderState).some(
    (value) =>
      value !== undefined && value !== null && (Array.isArray(value) ? value.length > 0 : true)
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn(
        'bg-card mx-auto max-w-md rounded-lg border p-6 shadow-lg backdrop-blur-sm',
        hasAnyOrderData ? 'bg-card/95 border-amber-200 shadow-amber-100/50' : 'bg-card/80',
        className
      )}
    >
      <div className="mb-4 flex items-center gap-2">
        <motion.div animate={{ rotate: hasAnyOrderData ? 360 : 0 }} transition={{ duration: 0.5 }}>
          <Coffee
            className={cn(
              'h-5 w-5 transition-colors',
              hasAnyOrderData ? 'text-amber-600' : 'text-muted-foreground'
            )}
          />
        </motion.div>
        <h3 className="text-lg font-semibold">Brew & Bean Coffee</h3>
        {isComplete && (
          <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} className="ml-auto">
            <CheckCircle className="h-5 w-5 text-green-600" />
          </motion.div>
        )}
      </div>

      <div className="space-y-3">
        <OrderField
          icon={<Coffee className="h-4 w-4" />}
          label="Drink"
          value={orderState.drinkType}
          placeholder="What would you like?"
        />

        <OrderField
          icon={<div className="h-4 w-4 rounded-full border-2 border-current" />}
          label="Size"
          value={orderState.size}
          placeholder="Small, Medium, or Large?"
        />

        <OrderField
          icon={<Milk className="h-4 w-4" />}
          label="Milk"
          value={orderState.milk}
          placeholder="Milk preference?"
        />

        <OrderField
          icon={<Plus className="h-4 w-4" />}
          label="Extras"
          value={orderState.extras?.join(', ')}
          placeholder="Any extras?"
        />

        <OrderField
          icon={<User className="h-4 w-4" />}
          label="Name"
          value={orderState.name}
          placeholder="Name for the order?"
        />
      </div>

      <AnimatePresence>
        {isComplete && !isOrderComplete && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="mt-4 rounded-lg border border-blue-200 bg-blue-50 p-3"
          >
            <p className="text-sm font-medium text-blue-800">Order Ready to Process! 🎯</p>
            <p className="mt-1 text-xs text-blue-600">
              All details collected. Processing your order...
            </p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Coffee Animation Overlay */}
      <AnimatePresence>
        {isOrderComplete && completedOrder && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
            onClick={() => {}} // Prevent closing on click
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              className="mx-4 w-full max-w-md rounded-xl bg-white shadow-2xl"
            >
              <CoffeeAnimation order={completedOrder} />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

interface OrderFieldProps {
  icon: React.ReactNode;
  label: string;
  value?: string;
  placeholder: string;
}

function OrderField({ icon, label, value, placeholder }: OrderFieldProps) {
  return (
    <motion.div
      className={cn(
        'flex items-center gap-3 rounded-md p-2 transition-colors',
        value ? 'border border-amber-100 bg-amber-50/50' : 'bg-transparent'
      )}
      animate={value ? { scale: [1, 1.02, 1] } : {}}
      transition={{ duration: 0.3 }}
    >
      <motion.div
        className={cn(
          'flex-shrink-0 transition-colors',
          value ? 'text-amber-600' : 'text-muted-foreground'
        )}
        animate={value ? { scale: [1, 1.1, 1] } : {}}
        transition={{ duration: 0.2 }}
      >
        {icon}
      </motion.div>
      <div className="min-w-0 flex-1">
        <div className="text-muted-foreground text-sm font-medium">{label}</div>
        <AnimatePresence mode="wait">
          {value ? (
            <motion.div
              key="value"
              initial={{ opacity: 0, x: -10, scale: 0.95 }}
              animate={{ opacity: 1, x: 0, scale: 1 }}
              exit={{ opacity: 0, x: 10, scale: 0.95 }}
              className="text-foreground text-sm font-medium capitalize"
            >
              {value}
            </motion.div>
          ) : (
            <motion.div
              key="placeholder"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="text-muted-foreground text-sm italic"
            >
              {placeholder}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}
