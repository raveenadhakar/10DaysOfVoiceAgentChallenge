'use client';

import React from 'react';
import { CheckCircle, ShoppingCart, Package, User, CreditCard } from 'lucide-react';
import { AnimatePresence, motion } from 'motion/react';
import { useFoodOrderState } from '@/hooks/useFoodOrderState';
import { cn } from '@/lib/utils';

interface FoodOrderDisplayProps {
  className?: string;
}

export function FoodOrderDisplay({ className }: FoodOrderDisplayProps) {
  const { orderState, isOrderComplete, completedOrder } = useFoodOrderState();

  const hasItems = orderState.cartItems && orderState.cartItems.length > 0;
  const hasCustomerInfo = orderState.customerName || orderState.customerAddress;

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn(
        'bg-card mx-auto max-w-md rounded-lg border p-6 shadow-lg backdrop-blur-sm',
        hasItems ? 'bg-card/95 border-green-200 shadow-green-100/50' : 'bg-card/80',
        className
      )}
    >
      <div className="mb-4 flex items-center gap-2">
        <motion.div animate={{ rotate: hasItems ? 360 : 0 }} transition={{ duration: 0.5 }}>
          <ShoppingCart
            className={cn(
              'h-5 w-5 transition-colors',
              hasItems ? 'text-green-600' : 'text-muted-foreground'
            )}
          />
        </motion.div>
        <h3 className="text-lg font-semibold">FreshMart Order</h3>
        {isOrderComplete && (
          <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} className="ml-auto">
            <CheckCircle className="h-5 w-5 text-green-600" />
          </motion.div>
        )}
      </div>

      <div className="space-y-3">
        <OrderField
          icon={<Package className="h-4 w-4" />}
          label="Items"
          value={hasItems ? `${orderState.cartItems?.length} items in cart` : undefined}
          placeholder="No items yet"
        />

        <OrderField
          icon={<CreditCard className="h-4 w-4" />}
          label="Total"
          value={orderState.total ? `$${orderState.total.toFixed(2)}` : undefined}
          placeholder="$0.00"
        />

        <OrderField
          icon={<User className="h-4 w-4" />}
          label="Customer"
          value={orderState.customerName}
          placeholder="Name for the order?"
        />

        <OrderField
          icon={<Package className="h-4 w-4" />}
          label="Delivery"
          value={orderState.customerAddress || (hasCustomerInfo ? 'Pickup' : undefined)}
          placeholder="Pickup or delivery?"
        />
      </div>

      <AnimatePresence>
        {hasItems && hasCustomerInfo && !isOrderComplete && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="mt-4 rounded-lg border border-green-200 bg-green-50 p-3"
          >
            <p className="text-sm font-medium text-green-800">Ready to Order! 🛒</p>
            <p className="mt-1 text-xs text-green-600">
              Say "Place my order" or "I'm done" to complete your order.
            </p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Order Completion Overlay */}
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
              className="mx-4 w-full max-w-md rounded-xl bg-white shadow-2xl p-6"
            >
              <div className="text-center">
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.2 }}
                  className="mx-auto mb-4 h-16 w-16 rounded-full bg-green-100 flex items-center justify-center"
                >
                  <CheckCircle className="h-8 w-8 text-green-600" />
                </motion.div>
                
                <h2 className="text-xl font-bold text-gray-900 mb-2">Order Confirmed!</h2>
                
                {completedOrder.orderId && (
                  <p className="text-sm text-gray-600 mb-4">
                    Order ID: <span className="font-mono">{completedOrder.orderId}</span>
                  </p>
                )}
                
                <div className="bg-gray-50 rounded-lg p-4 mb-4">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm text-gray-600">Items:</span>
                    <span className="font-medium">{completedOrder.cartItems?.length || 0}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Total:</span>
                    <span className="font-bold text-green-600">
                      ${completedOrder.total?.toFixed(2) || '0.00'}
                    </span>
                  </div>
                </div>
                
                <p className="text-sm text-gray-600">
                  {completedOrder.customerName && `Thank you, ${completedOrder.customerName}! `}
                  Your order has been placed and will be ready for pickup soon.
                </p>
              </div>
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
        value ? 'border border-green-100 bg-green-50/50' : 'bg-transparent'
      )}
      animate={value ? { scale: [1, 1.02, 1] } : {}}
      transition={{ duration: 0.3 }}
    >
      <motion.div
        className={cn(
          'flex-shrink-0 transition-colors',
          value ? 'text-green-600' : 'text-muted-foreground'
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
              className="text-foreground text-sm font-medium"
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