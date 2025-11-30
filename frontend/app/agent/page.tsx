import { headers } from 'next/headers';
import { App } from '@/components/app/app';
import { getAppConfig } from '@/lib/utils';
import { AGENT_CONFIGS, type AgentType } from '@/app-config';
import type { Metadata } from 'next';

interface PageProps {
  searchParams: Promise<{ agent?: string }>;
}

export async function generateMetadata({ searchParams }: PageProps): Promise<Metadata> {
  const params = await searchParams;
  const agentType = (params.agent || 'food') as AgentType;
  const agentConfig = AGENT_CONFIGS[agentType] || AGENT_CONFIGS.food;
  
  return {
    title: agentConfig.config.pageTitle,
    description: agentConfig.config.pageDescription,
  };
}

export default async function Page({ searchParams }: PageProps) {
  const hdrs = await headers();
  const params = await searchParams;
  const agentType = (params.agent || 'food') as AgentType;
  
  // Get the config for the specified agent type
  const agentConfig = AGENT_CONFIGS[agentType] || AGENT_CONFIGS.food;
  const appConfig = await getAppConfig(hdrs);
  
  // Merge agent-specific config with app config
  const finalConfig = {
    ...appConfig,
    ...agentConfig.config,
    agentType,
  };

  return <App appConfig={finalConfig} />;
}
