'use client';

import { useEffect, useState } from 'react';
import { useDataChannel } from '@livekit/components-react';
import { AppConfig } from '@/app-config';
import { SessionView } from '@/components/app/session-view';

interface CommerceData {
  type: string;
  data?: {
    items?: CartItem[];
    count?: number;
    total?: number;
    id?: string;
    status?: string;
    created_at?: string;
    customer?: {
      name?: string;
      address?: string;
    };
  };
}

interface CartItem {
  product_id: string;
  name: string;
  price: number;
  quantity: number;
  subtotal: number;
  size?: string;
}

interface CommerceSessionViewProps {
  appConfig: AppConfig;
}

export function CommerceSessionView({ appConfig }: CommerceSessionViewProps) {
  const [cartItems, setCartItems] = useState<CartItem[]>([]);
  const [cartTotal, setCartTotal] = useState<number>(0);
  const [orderStatus, setOrderStatus] = useState<string>('shopping');
  const [orderId, setOrderId] = useState<string>('');
  const [customerInfo, setCustomerInfo] = useState<{ name?: string; address?: string }>({});

  const { message } = useDataChannel('commerce');

  useEffect(() => {
    if (!message) return;

    try {
      const rawText = new TextDecoder().decode(message.payload).trim();
      const data: CommerceData = JSON.parse(rawText);

      console.log('Received commerce data:', data);

      if (data.type === 'cart_update' && data.data) {
        if (data.data.items) setCartItems(data.data.items);
        if (data.data.total !== undefined) setCartTotal(data.data.total);
      } else if (data.type === 'order_complete' && data.data) {
        if (data.data.id) setOrderId(data.data.id);
        if (data.data.status) setOrderStatus(data.data.status);
        if (data.data.customer) setCustomerInfo(data.data.customer);
        
        // Reset cart after order completion
        setTimeout(() => {
          setCartItems([]);
          setCartTotal(0);
          setCustomerInfo({});
          setOrderStatus('shopping');
          setOrderId('');
        }, 8000); // Show completion for 8 seconds
      }
    } catch (error) {
      console.error('Failed to parse commerce data:', error);
    }
  }, [message]);

  const getStatusColor = () => {
    switch (orderStatus) {
      case 'pending':
        return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'confirmed':
        return 'text-green-600 bg-green-50 border-green-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  return (
    <div className="flex h-full">
      {/* Left Sidebar - Cart & Order Info */}
      <div className="flex w-96 flex-col border-r border-gray-200 bg-white">
        {/* Header */}
        <div className="border-b border-gray-200 p-4">
          <h1 className="text-xl font-bold text-gray-900">{appConfig.companyName}</h1>
          <p className="text-sm text-gray-600">{appConfig.pageTitle}</p>
        </div>

        {/* Order Status */}
        {orderStatus !== 'shopping' && (
          <div className={`border-b border-gray-200 p-4 ${getStatusColor()}`}>
            <div className="flex items-center gap-3">
              <div className="h-3 w-3 rounded-full bg-current"></div>
              <div>
                <h2 className="font-semibold capitalize">{orderStatus} Order</h2>
                {orderId && <p className="text-xs opacity-75">Order ID: {orderId}</p>}
              </div>
            </div>
            {customerInfo.name && (
              <div className="mt-2 rounded bg-white/50 p-2">
                <div className="text-sm font-medium">Customer: {customerInfo.name}</div>
                {customerInfo.address && (
                  <div className="text-xs opacity-75">{customerInfo.address}</div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Cart Items */}
        <div className="flex-1 overflow-y-auto">
          <div className="border-b border-gray-200 p-4">
            <h3 className="mb-3 font-semibold text-gray-900">
              Shopping Cart ({cartItems.length} items)
            </h3>

            {cartItems.length === 0 ? (
              <div className="text-center py-8">
                <div className="text-4xl mb-2">🛍️</div>
                <p className="text-gray-500 text-sm">Your cart is empty</p>
                <p className="text-gray-400 text-xs mt-1">
                  Start by saying "Show me coffee mugs" or "I'm looking for a hoodie"
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {cartItems.map((item, index) => (
                  <div
                    key={`${item.product_id}-${index}`}
                    className="rounded-lg border border-gray-200 p-3 hover:border-gray-300 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900 text-sm">
                          {item.name}
                        </h4>
                        
                        {item.size && (
                          <div className="mt-1 text-xs text-gray-600">
                            Size: {item.size}
                          </div>
                        )}
                      </div>

                      <div className="text-right">
                        <div className="text-sm font-semibold text-gray-900">
                          ₹{item.subtotal}
                        </div>
                        <div className="text-xs text-gray-500">
                          {item.quantity}x ₹{item.price}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Order Summary */}
          {cartItems.length > 0 && (
            <div className="border-b border-gray-200 p-4">
              <h3 className="mb-3 font-semibold text-gray-900">Order Summary</h3>
              
              <div className="space-y-2 text-sm">
                <div className="border-t border-gray-200 pt-2 flex justify-between">
                  <span className="font-semibold text-gray-900">Total</span>
                  <span className="font-bold text-lg text-orange-600">
                    ₹{cartTotal}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Quick Actions */}
          <div className="p-4">
            <h3 className="mb-3 font-semibold text-gray-900">Quick Actions</h3>
            
            <div className="space-y-2 text-sm">
              <div className="rounded bg-orange-50 p-2">
                <div className="font-medium text-orange-900">💬 Try saying:</div>
                <ul className="mt-1 text-orange-700 text-xs space-y-0.5">
                  <li>"Show me all coffee mugs"</li>
                  <li>"Do you have t-shirts under 1000?"</li>
                  <li>"Add the second item to my cart"</li>
                  <li>"What's in my cart?"</li>
                  <li>"Place my order"</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Session View */}
      <div className="flex flex-1 flex-col">
        <SessionView appConfig={appConfig} />
      </div>
    </div>
  );
}
