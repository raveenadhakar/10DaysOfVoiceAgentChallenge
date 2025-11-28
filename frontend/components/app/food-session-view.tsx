'use client';

import { useEffect, useState } from 'react';
import { useDataChannel } from '@livekit/components-react';
import { AppConfig } from '@/app-config';
import { SessionView } from '@/components/app/session-view';

interface FoodOrderData {
  type: string;
  data?: {
    cart?: CartItem[];
    total?: number;
    subtotal?: number;
    tax?: number;
    customer?: {
      name?: string;
      address?: string;
    };
    order_id?: string;
    status?: string;
  };
}

interface CartItem {
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

interface FoodSessionViewProps {
  appConfig: AppConfig;
}

export function FoodSessionView({ appConfig }: FoodSessionViewProps) {
  const [cartItems, setCartItems] = useState<CartItem[]>([]);
  const [orderTotal, setOrderTotal] = useState<number>(0);
  const [orderSubtotal, setOrderSubtotal] = useState<number>(0);
  const [orderTax, setOrderTax] = useState<number>(0);
  const [customerInfo, setCustomerInfo] = useState<{ name?: string; address?: string }>({});
  const [orderStatus, setOrderStatus] = useState<string>('shopping');
  const [orderId, setOrderId] = useState<string>('');

  const { message } = useDataChannel('food_order');

  useEffect(() => {
    if (!message) return;

    try {
      const rawText = new TextDecoder().decode(message.payload).trim();
      const data: FoodOrderData = JSON.parse(rawText);

      console.log('Received food order data:', data);

      if (data.type === 'cart_update' && data.data) {
        if (data.data.cart) setCartItems(data.data.cart);
        if (data.data.subtotal !== undefined) setOrderSubtotal(data.data.subtotal);
        if (data.data.tax !== undefined) setOrderTax(data.data.tax);
        if (data.data.total !== undefined) setOrderTotal(data.data.total);
      } else if (data.type === 'order_complete' && data.data) {
        if (data.data.order_id) setOrderId(data.data.order_id);
        if (data.data.status) setOrderStatus(data.data.status);
        if (data.data.customer) setCustomerInfo(data.data.customer);
        
        // Reset cart after order completion
        setTimeout(() => {
          setCartItems([]);
          setOrderTotal(0);
          setOrderSubtotal(0);
          setOrderTax(0);
          setCustomerInfo({});
          setOrderStatus('shopping');
          setOrderId('');
        }, 8000); // Show completion for 8 seconds
      }
    } catch (error) {
      console.error('Failed to parse food order data:', error);
    }
  }, [message]);

  const getCategoryIcon = (category: string) => {
    switch (category.toLowerCase()) {
      case 'groceries':
        return '🛒';
      case 'snacks':
        return '🍿';
      case 'prepared_food':
        return '🍕';
      default:
        return '🍽️';
    }
  };

  const getStatusColor = () => {
    switch (orderStatus) {
      case 'confirmed':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'processing':
        return 'text-blue-600 bg-blue-50 border-blue-200';
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
          <h1 className="text-xl font-bold text-gray-900">FreshMart</h1>
          <p className="text-sm text-gray-600">Food & Grocery Ordering</p>
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
                <div className="text-4xl mb-2">🛒</div>
                <p className="text-gray-500 text-sm">Your cart is empty</p>
                <p className="text-gray-400 text-xs mt-1">
                  Start by saying "I need some bread" or "Add pasta to my cart"
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {cartItems.map((item, index) => (
                  <div
                    key={`${item.id}-${index}`}
                    className="rounded-lg border border-gray-200 p-3 hover:border-gray-300 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className="text-lg">
                            {getCategoryIcon(item.category)}
                          </span>
                          <div>
                            <h4 className="font-medium text-gray-900 text-sm">
                              {item.name}
                            </h4>
                            {item.brand && (
                              <p className="text-xs text-gray-500">by {item.brand}</p>
                            )}
                          </div>
                        </div>
                        
                        <div className="mt-1 flex items-center gap-2 text-xs text-gray-600">
                          <span>{item.size}</span>
                          {item.notes && (
                            <>
                              <span>•</span>
                              <span className="italic">{item.notes}</span>
                            </>
                          )}
                        </div>

                        {item.tags && item.tags.length > 0 && (
                          <div className="mt-1 flex flex-wrap gap-1">
                            {item.tags.slice(0, 2).map((tag) => (
                              <span
                                key={tag}
                                className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600"
                              >
                                {tag}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>

                      <div className="text-right">
                        <div className="text-sm font-semibold text-gray-900">
                          ${item.subtotal.toFixed(2)}
                        </div>
                        <div className="text-xs text-gray-500">
                          {item.quantity}x ${item.price.toFixed(2)}
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
                <div className="flex justify-between">
                  <span className="text-gray-600">Subtotal</span>
                  <span className="font-medium">${orderSubtotal.toFixed(2)}</span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-gray-600">Tax</span>
                  <span className="font-medium">${orderTax.toFixed(2)}</span>
                </div>
                
                <div className="border-t border-gray-200 pt-2 flex justify-between">
                  <span className="font-semibold text-gray-900">Total</span>
                  <span className="font-bold text-lg text-green-600">
                    ${orderTotal.toFixed(2)}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Quick Actions */}
          <div className="p-4">
            <h3 className="mb-3 font-semibold text-gray-900">Quick Actions</h3>
            
            <div className="space-y-2 text-sm">
              <div className="rounded bg-blue-50 p-2">
                <div className="font-medium text-blue-900">💬 Try saying:</div>
                <ul className="mt-1 text-blue-700 text-xs space-y-0.5">
                  <li>"Add bread to my cart"</li>
                  <li>"I need ingredients for pasta"</li>
                  <li>"What's in my cart?"</li>
                  <li>"Remove the milk"</li>
                  <li>"I'm done, place my order"</li>
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