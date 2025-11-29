import Link from 'next/link';
import { AGENT_CONFIGS, type AgentType } from '@/app-config';

export default function HomePage() {
  const agents = Object.values(AGENT_CONFIGS);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 dark:text-white mb-4">
            AI Voice Agents
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300">
            Choose an AI agent to interact with
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
          {agents.map((agent) => (
            <Link
              key={agent.id}
              href={`/?agent=${agent.id}`}
              className="group relative overflow-hidden rounded-2xl bg-white dark:bg-gray-800 p-6 shadow-lg hover:shadow-xl transition-all duration-300 border-2 border-transparent hover:border-current"
              style={{ color: agent.color }}
            >
              <div className="flex flex-col h-full">
                <div className="text-5xl mb-4">{agent.icon}</div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                  {agent.name}
                </h2>
                <p className="text-gray-600 dark:text-gray-300 mb-4 flex-grow">
                  {agent.description}
                </p>
                <div
                  className="inline-flex items-center gap-2 text-sm font-semibold group-hover:gap-3 transition-all"
                  style={{ color: agent.color }}
                >
                  <span>{agent.config.startButtonText}</span>
                  <svg
                    className="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 5l7 7-7 7"
                    />
                  </svg>
                </div>
              </div>
            </Link>
          ))}
        </div>

        <div className="mt-16 text-center">
          <div className="inline-block bg-white dark:bg-gray-800 rounded-lg p-6 shadow-md">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              💡 How it works
            </h3>
            <p className="text-gray-600 dark:text-gray-300 text-sm max-w-md">
              Click on any agent card to start a voice conversation. Make sure your microphone is
              enabled and speak naturally to interact with the AI.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
