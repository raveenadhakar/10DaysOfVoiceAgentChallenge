'use client';

import { useEffect, useState } from 'react';
import { useDataChannel } from '@livekit/components-react';
import { AppConfig } from '@/app-config';
import { SessionView } from '@/components/app/session-view';

interface FraudCaseData {
  userName?: string;
  cardEnding?: string;
  transactionAmount?: string;
  transactionName?: string;
  transactionTime?: string;
  transactionCategory?: string;
  transactionSource?: string;
  transactionLocation?: string;
  status?: string;
  outcome?: string;
}

interface FraudData {
  type: string;
  data?: FraudCaseData;
}

interface FraudSessionViewProps {
  appConfig: AppConfig;
}

export function FraudSessionView({ appConfig }: FraudSessionViewProps) {
  const [fraudCase, setFraudCase] = useState<FraudCaseData>({});
  const [lastUpdate, setLastUpdate] = useState<string>('');

  const { message } = useDataChannel('fraud_alert');

  useEffect(() => {
    if (!message) return;

    try {
      const rawText = new TextDecoder().decode(message.payload).trim();
      const data: FraudData = JSON.parse(rawText);

      console.log('Received fraud data:', data);

      if (data.type === 'fraud_update' && data.data) {
        setFraudCase((prev) => ({ ...prev, ...data.data }));
        setLastUpdate(new Date().toLocaleTimeString());
      }
    } catch (error) {
      console.error('Failed to parse fraud data:', error);
    }
  }, [message]);

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'pending_review':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'verification_failed':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'confirmed_safe':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'confirmed_fraud':
        return 'bg-red-100 text-red-800 border-red-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getStatusText = (status?: string) => {
    switch (status) {
      case 'pending_review':
        return 'Pending Review';
      case 'verification_failed':
        return 'Verification Failed';
      case 'confirmed_safe':
        return 'Confirmed Safe';
      case 'confirmed_fraud':
        return 'Confirmed Fraud';
      default:
        return 'Unknown';
    }
  };

  const getStatusIcon = (status?: string) => {
    switch (status) {
      case 'pending_review':
        return '⏳';
      case 'verification_failed':
        return '❌';
      case 'confirmed_safe':
        return '✅';
      case 'confirmed_fraud':
        return '🚨';
      default:
        return '❓';
    }
  };

  return (
    <div className="flex h-full">
      {/* Left Sidebar */}
      <div className="flex w-96 flex-col border-r border-gray-200 bg-white">
        {/* Header */}
        <div className="border-b border-gray-200 bg-gradient-to-r from-red-600 to-red-700 p-4 text-white">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🏦</span>
            <div>
              <h1 className="text-xl font-bold">SecureBank</h1>
              <p className="text-sm text-red-100">Fraud Detection Department</p>
            </div>
          </div>
        </div>

        {/* Case Status */}
        {fraudCase.status && (
          <div className="border-b border-gray-200 p-4">
            <h3 className="mb-2 text-sm font-semibold text-gray-700">Case Status</h3>
            <div
              className={`flex items-center gap-2 rounded-lg border-2 p-3 ${getStatusColor(
                fraudCase.status
              )}`}
            >
              <span className="text-2xl">{getStatusIcon(fraudCase.status)}</span>
              <span className="font-semibold">{getStatusText(fraudCase.status)}</span>
            </div>
          </div>
        )}

        {/* Customer Information */}
        {fraudCase.userName && (
          <div className="border-b border-gray-200 bg-blue-50 p-4">
            <h3 className="mb-3 text-sm font-semibold text-gray-700">Customer Information</h3>
            <div className="space-y-2">
              <div className="rounded-lg bg-white p-3 shadow-sm">
                <div className="mb-1 text-xs font-medium text-gray-500">CUSTOMER NAME</div>
                <div className="text-sm font-semibold text-gray-900">{fraudCase.userName}</div>
              </div>
              {fraudCase.cardEnding && (
                <div className="rounded-lg bg-white p-3 shadow-sm">
                  <div className="mb-1 text-xs font-medium text-gray-500">CARD ENDING</div>
                  <div className="font-mono text-sm font-semibold text-gray-900">
                    •••• {fraudCase.cardEnding}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Transaction Details */}
        {fraudCase.transactionAmount && (
          <div className="flex-1 overflow-y-auto p-4">
            <h3 className="mb-3 text-sm font-semibold text-gray-700">Suspicious Transaction</h3>

            <div className="space-y-3">
              {/* Amount - Highlighted */}
              <div className="rounded-lg border-2 border-red-300 bg-red-50 p-3">
                <div className="mb-1 text-xs font-medium text-red-700">AMOUNT</div>
                <div className="text-2xl font-bold text-red-700">{fraudCase.transactionAmount}</div>
              </div>

              {/* Merchant */}
              {fraudCase.transactionName && (
                <div className="rounded-lg border border-gray-200 bg-white p-3 shadow-sm">
                  <div className="mb-1 text-xs font-medium text-gray-500">MERCHANT</div>
                  <div className="text-sm font-semibold text-gray-900">
                    {fraudCase.transactionName}
                  </div>
                </div>
              )}

              {/* Time */}
              {fraudCase.transactionTime && (
                <div className="rounded-lg border border-gray-200 bg-white p-3 shadow-sm">
                  <div className="mb-1 text-xs font-medium text-gray-500">DATE & TIME</div>
                  <div className="text-sm font-medium text-gray-900">
                    {fraudCase.transactionTime}
                  </div>
                </div>
              )}

              {/* Location */}
              {fraudCase.transactionLocation && (
                <div className="rounded-lg border border-gray-200 bg-white p-3 shadow-sm">
                  <div className="mb-1 flex items-center gap-1 text-xs font-medium text-gray-500">
                    <span>📍</span>
                    <span>LOCATION</span>
                  </div>
                  <div className="text-sm font-medium text-gray-900">
                    {fraudCase.transactionLocation}
                  </div>
                </div>
              )}

              {/* Source */}
              {fraudCase.transactionSource && (
                <div className="rounded-lg border border-gray-200 bg-white p-3 shadow-sm">
                  <div className="mb-1 text-xs font-medium text-gray-500">SOURCE</div>
                  <div className="text-sm font-medium text-gray-900">
                    {fraudCase.transactionSource}
                  </div>
                </div>
              )}

              {/* Category */}
              {fraudCase.transactionCategory && (
                <div className="rounded-lg border border-gray-200 bg-white p-3 shadow-sm">
                  <div className="mb-1 text-xs font-medium text-gray-500">CATEGORY</div>
                  <div className="text-sm font-medium text-gray-900">
                    <span className="inline-block rounded bg-gray-100 px-2 py-1 text-xs font-semibold text-gray-700 uppercase">
                      {fraudCase.transactionCategory}
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Outcome */}
        {fraudCase.outcome && (
          <div className="border-t border-gray-200 bg-gray-50 p-4">
            <h4 className="mb-2 text-sm font-semibold text-gray-700">Resolution</h4>
            <p className="text-sm text-gray-600">{fraudCase.outcome}</p>
          </div>
        )}

        {/* Last Update */}
        {lastUpdate && (
          <div className="border-t border-gray-200 p-4">
            <div className="text-xs text-gray-500">Last update: {lastUpdate}</div>
          </div>
        )}

        {/* Security Notice */}
        <div className="border-t border-gray-200 bg-yellow-50 p-4">
          <div className="flex items-start gap-2">
            <span className="text-lg">🔒</span>
            <div>
              <h4 className="mb-1 text-sm font-semibold text-yellow-800">Security Notice</h4>
              <p className="text-xs text-yellow-700">
                We will never ask for your full card number, PIN, or password. Only answer security
                questions to verify your identity.
              </p>
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
