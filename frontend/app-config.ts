 export interface AppConfig {
  pageTitle: string;
  pageDescription: string;
  companyName: string;

  supportsChatInput: boolean;
  supportsVideoInput: boolean;
  supportsScreenShare: boolean;
  isPreConnectBufferEnabled: boolean;

  logo: string;
  startButtonText: string;
  accent?: string;
  logoDark?: string;
  accentDark?: string;

  // for LiveKit Cloud Sandbox
  sandboxId?: string;
  agentName?: string;
  agentType?: AgentType;
}

export type AgentType = 'food' | 'wellness' | 'tutor' | 'sdr' | 'fraud' | 'gm' | 'commerce';

export interface AgentConfig {
  id: AgentType;
  name: string;
  description: string;
  icon: string;
  color: string;
  colorDark: string;
  config: AppConfig;
}

export const AGENT_CONFIGS: Record<AgentType, AgentConfig> = {
  food: {
    id: 'food',
    name: 'Food & Grocery Agent',
    description: 'Order fresh groceries and prepared foods with our AI-powered voice assistant.',
    icon: '🛒',
    color: '#16a34a',
    colorDark: '#22c55e',
    config: {
      companyName: 'Murf Voices',
      pageTitle: 'Food & Grocery Agent',
      pageDescription: 'Order fresh groceries and prepared foods with our AI-powered voice assistant. Simply speak your order and we\'ll take care of the rest!',
      supportsChatInput: true,
      supportsVideoInput: false,
      supportsScreenShare: false,
      isPreConnectBufferEnabled: true,
      logo: '/lk-logo.svg',
      accent: '#16a34a',
      logoDark: '/lk-logo-dark.svg',
      accentDark: '#22c55e',
      startButtonText: 'Start Ordering',
    }
  },
  wellness: {
    id: 'wellness',
    name: 'Wellness Agent',
    description: 'Daily check-ins to help you reflect on your mood, energy, and daily intentions.',
    icon: '💚',
    color: '#059669',
    colorDark: '#10b981',
    config: {
      companyName: 'Murf Voices',
      pageTitle: 'Wellness Agent',
      pageDescription: 'Daily check-ins to help you reflect on your mood, energy, and daily intentions with Alex, your supportive wellness companion.',
      supportsChatInput: true,
      supportsVideoInput: false,
      supportsScreenShare: false,
      isPreConnectBufferEnabled: true,
      logo: '/lk-logo.svg',
      accent: '#059669',
      logoDark: '/lk-logo-dark.svg',
      accentDark: '#10b981',
      startButtonText: 'Start Check-in',
    }
  },
  tutor: {
    id: 'tutor',
    name: 'Tutor Agent',
    description: 'Learn programming concepts through three different modes: Learn, Quiz, and Teach-back.',
    icon: '📚',
    color: '#2563eb',
    colorDark: '#3b82f6',
    config: {
      companyName: 'Murf Voices',
      pageTitle: 'Tutor Agent',
      pageDescription: 'Learn programming concepts through active recall with three different learning modes: Learn, Quiz, and Teach-back.',
      supportsChatInput: true,
      supportsVideoInput: false,
      supportsScreenShare: false,
      isPreConnectBufferEnabled: true,
      logo: '/lk-logo.svg',
      accent: '#2563eb',
      logoDark: '/lk-logo-dark.svg',
      accentDark: '#3b82f6',
      startButtonText: 'Start Learning',
    }
  },
  sdr: {
    id: 'sdr',
    name: 'SDR Agent',
    description: 'Professional sales conversations and lead capture for Razorpay payment solutions.',
    icon: '📞',
    color: '#7c3aed',
    colorDark: '#8b5cf6',
    config: {
      companyName: 'Murf Voices',
      pageTitle: 'SDR Agent',
      pageDescription: 'Professional sales conversations and lead capture for Razorpay payment gateway solutions.',
      supportsChatInput: true,
      supportsVideoInput: false,
      supportsScreenShare: false,
      isPreConnectBufferEnabled: true,
      logo: '/lk-logo.svg',
      accent: '#7c3aed',
      logoDark: '/lk-logo-dark.svg',
      accentDark: '#8b5cf6',
      startButtonText: 'Start Conversation',
    }
  },
  fraud: {
    id: 'fraud',
    name: 'Fraud Detection Agent',
    description: 'Secure fraud detection calls to verify suspicious transactions on your account.',
    icon: '🚨',
    color: '#dc2626',
    colorDark: '#ef4444',
    config: {
      companyName: 'Murf Voices',
      pageTitle: 'Fraud Detection Agent',
      pageDescription: 'Secure fraud detection calls to verify suspicious transactions and protect your account.',
      supportsChatInput: true,
      supportsVideoInput: false,
      supportsScreenShare: false,
      isPreConnectBufferEnabled: true,
      logo: '/lk-logo.svg',
      accent: '#dc2626',
      logoDark: '/lk-logo-dark.svg',
      accentDark: '#ef4444',
      startButtonText: 'Verify Transaction',
    }
  },
  gm: {
    id: 'gm',
    name: 'Game Master Agent',
    description: 'Embark on an epic fantasy adventure with an AI Game Master guiding your story.',
    icon: '🎲',
    color: '#9333ea',
    colorDark: '#a855f7',
    config: {
      companyName: 'Murf Voices',
      pageTitle: 'Game Master Agent',
      pageDescription: 'Embark on an epic fantasy adventure with an AI Game Master. Your choices shape the story!',
      supportsChatInput: true,
      supportsVideoInput: false,
      supportsScreenShare: false,
      isPreConnectBufferEnabled: true,
      logo: '/lk-logo.svg',
      accent: '#9333ea',
      logoDark: '/lk-logo-dark.svg',
      accentDark: '#a855f7',
      startButtonText: 'Begin Adventure',
    }
  },
  commerce: {
    id: 'commerce',
    name: 'E-commerce Agent',
    description: 'Shop for products with our AI-powered voice assistant following the Agentic Commerce Protocol.',
    icon: '🛍️',
    color: '#ea580c',
    colorDark: '#f97316',
    config: {
      companyName: 'Murf Voices',
      pageTitle: 'E-commerce Agent',
      pageDescription: 'Browse and shop for products with our AI-powered voice assistant. Simply speak what you want to buy!',
      supportsChatInput: true,
      supportsVideoInput: false,
      supportsScreenShare: false,
      isPreConnectBufferEnabled: true,
      logo: '/lk-logo.svg',
      accent: '#ea580c',
      logoDark: '/lk-logo-dark.svg',
      accentDark: '#f97316',
      startButtonText: 'Start Shopping',
    }
  }
};

export const APP_CONFIG_DEFAULTS: AppConfig = AGENT_CONFIGS.food.config;