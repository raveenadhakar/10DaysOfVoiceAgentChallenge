import { headers } from 'next/headers';
import { App } from '@/components/app/app';
import { getAppConfig } from '@/lib/utils';
import { AGENT_CONFIGS, type AgentType } from '@/app-config';

interface PageProps {
  searchParams: Promise<{ agent?: string }>;
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
