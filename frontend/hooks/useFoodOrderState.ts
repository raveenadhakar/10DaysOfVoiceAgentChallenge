'use client';

import { useEffect, useState } from 'react';
import { DataPacket_Kind, RemoteParticipant } from 'livekit-client';
import { useRoomContext } from '@livekit/components-react';

export interface CartItem {
  id: string;
  name: string;
  category: string;
  price: number;
  brand?: string;
  size?: string;
  units?: string;
  tags?: string[];
  quantity: number;
  notes?: string;
  subtotal: number;
}

export interface FoodOrderState {
  cartItems?: CartItem[];
  subtotal?: number;
  tax?: number;
  total?: number;
  customerName?: string;
  customerAddress?: string;
  orderId?: string;
  status?: string;
}

export interface FoodOrderUpdate {
  type: 'cart_update' | 'order_complete';
  data: FoodOrderState;
}

export function useFoodOrderState() {
  const [orderState, setOrderState] = useState<FoodOrderState>({});
  const [isOrderComplete, setIsOrderComplete] = useState(false);
  const [completedOrder, setCompletedOrder] = useState<FoodOrderState | null>(null);
  const room = useRoomContext();

  useEffect(() => {
    if (!room) return;

    const handleDataReceived = (
      payload: Uint8Array,
      participant?: RemoteParticipant,
      kind?: DataPacket_Kind,
      topic?: string
    ) => {
      if (topic !== 'food_order') return;

      try {
        const decoder = new TextDecoder();
        const message = decoder.decode(payload);
        const update: FoodOrderUpdate = JSON.parse(message);

        console.log('Food order update received:', update);

        if (update.type === 'cart_update') {
          setOrderState(update.data);
          setIsOrderComplete(false);
        } else if (update.type === 'order_complete') {
          setCompletedOrder(update.data);
          setIsOrderComplete(true);
          // Reset order state after showing completion
          setTimeout(() => {
            setOrderState({});
            setIsOrderComplete(false);
            setCompletedOrder(null);
          }, 8000); // Show completion for 8 seconds
        }
      } catch (error) {
        console.error('Failed to parse food order update:', error);
      }
    };

    room.on('dataReceived', handleDataReceived);

    return () => {
      room.off('dataReceived', handleDataReceived);
    };
  }, [room]);

  return {
    orderState,
    isOrderComplete,
    completedOrder,
  };
}