'use client';

import { useEffect, useState } from 'react';
import { useDataChannel } from '@livekit/components-react';
import { AppConfig } from '@/app-config';
import { SessionView } from '@/components/app/session-view';

interface LeadData {
  name?: string;
  email?: string;
  company?: string;
  role?: string;
  use_case?: string;
  team_size?: string;
  timeline?: string;
}

interface SDRData {
  type: string;
  lead?: LeadData;
  call_complete?: boolean;
  questions_asked?: number;
  timestamp?: string;
}

interface SDRSessionViewProps {
  appConfig: AppConfig;
}

export function SDRSessionView({ appConfig }: SDRSessionViewProps) {
  const [leadData, setLeadData] = useState<LeadData>({});
  const [callComplete, setCallComplete] = useState(false);
  const [questionsAsked, setQuestionsAsked] = useState(0);
  const [lastUpdate, setLastUpdate] = useState<string>('');

  const { message } = useDataChannel('sdr_session');

  useEffect(() => {
    if (!message) return;

    try {
      const rawText = new TextDecoder().decode(message.payload).trim();
      const data: SDRData = JSON.parse(rawText);

      console.log('Received SDR data:', data);

      if (data.type === 'lead_update' && data.lead) {
        setLeadData((prev) => ({ ...prev, ...data.lead }));
        setLastUpdate(new Date().toLocaleTimeString());
      }

      if (data.type === 'call_complete') {
        setCallComplete(true);
        if (data.lead) {
          setLeadData((prev) => ({ ...prev, ...data.lead }));
        }
      }

      if (data.questions_asked !== undefined) {
        setQuestionsAsked(data.questions_asked);
      }
    } catch (error) {
      console.error('Failed to parse SDR data:', error);
    }
  }, [message]);

  const getCompletionPercentage = () => {
    const fields = ['name', 'email', 'use_case'];
    const filledFields = fields.filter((field) => leadData[field as keyof LeadData]);
    return Math.round((filledFields.length / fields.length) * 100);
  };

  const getMissingFields = () => {
    const requiredFields = [
      { key: 'name', label: 'Name' },
      { key: 'email', label: 'Email' },
      { key: 'use_case', label: 'Use Case' },
    ];
    return requiredFields.filter((field) => !leadData[field.key as keyof LeadData]);
  };

  return (
    <div className="flex h-full">
      {/* Left Sidebar */}
      <div className="flex w-80 flex-col border-r border-gray-200 bg-white">
        {/* Header */}
        <div className="border-b border-gray-200 bg-gradient-to-r from-blue-600 to-indigo-600 p-4 text-white">
          <h1 className="text-xl font-bold">Razorpay SDR</h1>
          <p className="text-sm text-blue-100">Sales Development Representative</p>
        </div>

        {/* Lead Progress */}
        <div className="border-b border-gray-200 bg-blue-50 p-4">
          <h3 className="mb-2 font-semibold text-gray-900">Lead Capture Progress</h3>

          <div className="mb-2 flex justify-between text-sm">
            <span className="text-gray-600">Completion</span>
            <span className="font-semibold text-blue-600">{getCompletionPercentage()}%</span>
          </div>

          <div className="h-2 w-full rounded-full bg-gray-200">
            <div
              className="h-2 rounded-full bg-blue-600 transition-all duration-300"
              style={{ width: `${getCompletionPercentage()}%` }}
            ></div>
          </div>

          {callComplete && (
            <div className="mt-3 rounded-lg bg-green-100 p-2 text-center">
              <span className="text-sm font-semibold text-green-700">✓ Call Complete</span>
            </div>
          )}
        </div>

        {/* Lead Information */}
        <div className="flex-1 overflow-y-auto p-4">
          <h3 className="mb-3 font-semibold text-gray-900">Lead Information</h3>

          <div className="space-y-3">
            {/* Name */}
            <div className="rounded-lg border border-gray-200 p-3">
              <div className="mb-1 flex items-center justify-between">
                <span className="text-xs font-medium text-gray-500">NAME</span>
                {leadData.name && <span className="text-xs text-green-600">✓</span>}
              </div>
              <div className="text-sm font-medium text-gray-900">
                {leadData.name || <span className="text-gray-400">Not provided yet</span>}
              </div>
            </div>

            {/* Email */}
            <div className="rounded-lg border border-gray-200 p-3">
              <div className="mb-1 flex items-center justify-between">
                <span className="text-xs font-medium text-gray-500">EMAIL</span>
                {leadData.email && <span className="text-xs text-green-600">✓</span>}
              </div>
              <div className="text-sm font-medium text-gray-900">
                {leadData.email || <span className="text-gray-400">Not provided yet</span>}
              </div>
            </div>

            {/* Company */}
            <div className="rounded-lg border border-gray-200 p-3">
              <div className="mb-1 flex items-center justify-between">
                <span className="text-xs font-medium text-gray-500">COMPANY</span>
                {leadData.company && <span className="text-xs text-blue-600">✓</span>}
              </div>
              <div className="text-sm font-medium text-gray-900">
                {leadData.company || <span className="text-gray-400">Optional</span>}
              </div>
            </div>

            {/* Role */}
            <div className="rounded-lg border border-gray-200 p-3">
              <div className="mb-1 flex items-center justify-between">
                <span className="text-xs font-medium text-gray-500">ROLE</span>
                {leadData.role && <span className="text-xs text-blue-600">✓</span>}
              </div>
              <div className="text-sm font-medium text-gray-900">
                {leadData.role || <span className="text-gray-400">Optional</span>}
              </div>
            </div>

            {/* Use Case */}
            <div className="rounded-lg border border-gray-200 p-3">
              <div className="mb-1 flex items-center justify-between">
                <span className="text-xs font-medium text-gray-500">USE CASE</span>
                {leadData.use_case && <span className="text-xs text-green-600">✓</span>}
              </div>
              <div className="text-sm font-medium text-gray-900">
                {leadData.use_case || <span className="text-gray-400">Not provided yet</span>}
              </div>
            </div>

            {/* Team Size */}
            <div className="rounded-lg border border-gray-200 p-3">
              <div className="mb-1 flex items-center justify-between">
                <span className="text-xs font-medium text-gray-500">TEAM SIZE</span>
                {leadData.team_size && <span className="text-xs text-blue-600">✓</span>}
              </div>
              <div className="text-sm font-medium text-gray-900">
                {leadData.team_size || <span className="text-gray-400">Optional</span>}
              </div>
            </div>

            {/* Timeline */}
            <div className="rounded-lg border border-gray-200 p-3">
              <div className="mb-1 flex items-center justify-between">
                <span className="text-xs font-medium text-gray-500">TIMELINE</span>
                {leadData.timeline && <span className="text-xs text-blue-600">✓</span>}
              </div>
              <div className="text-sm font-medium text-gray-900">
                {leadData.timeline ? (
                  <span
                    className={`inline-block rounded px-2 py-1 text-xs font-semibold ${
                      leadData.timeline === 'now'
                        ? 'bg-red-100 text-red-700'
                        : leadData.timeline === 'soon'
                          ? 'bg-yellow-100 text-yellow-700'
                          : 'bg-gray-100 text-gray-700'
                    }`}
                  >
                    {leadData.timeline.toUpperCase()}
                  </span>
                ) : (
                  <span className="text-gray-400">Optional</span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Missing Fields Alert */}
        {getMissingFields().length > 0 && !callComplete && (
          <div className="border-t border-gray-200 bg-yellow-50 p-4">
            <h4 className="mb-2 text-sm font-semibold text-yellow-800">Still Needed:</h4>
            <ul className="space-y-1">
              {getMissingFields().map((field) => (
                <li key={field.key} className="text-sm text-yellow-700">
                  • {field.label}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Stats */}
        <div className="border-t border-gray-200 p-4">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">Questions Asked</span>
            <span className="font-semibold text-indigo-600">{questionsAsked}</span>
          </div>
          {lastUpdate && (
            <div className="mt-2 text-xs text-gray-500">Last update: {lastUpdate}</div>
          )}
        </div>
      </div>

      {/* Main Session View */}
      <div className="flex flex-1 flex-col">
        <SessionView appConfig={appConfig} />
      </div>
    </div>
  );
}
