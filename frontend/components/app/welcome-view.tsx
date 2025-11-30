import { useState } from 'react';
import { Button } from '@/components/livekit/button';
import { AGENT_CONFIGS, type AgentType } from '@/app-config';

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
  mode?: AgentType;
}

export const WelcomeView = ({
  startButtonText,
  onStartCall,
  mode = 'food',
  ref,
}: React.ComponentProps<'div'> & WelcomeViewProps) => {
  const [isConnecting, setIsConnecting] = useState(false);
  const agentConfig = AGENT_CONFIGS[mode];
  
  const handleStartCall = () => {
    setIsConnecting(true);
    onStartCall();
    // Reset after a timeout in case connection fails
    setTimeout(() => setIsConnecting(false), 10000);
  };
  
  // Agent-specific content
  const content = {
    food: {
      title: 'Food & Grocery Ordering',
      subtitle: 'AI-Powered Shopping Assistant',
      description: 'Order fresh groceries and prepared foods with our AI-powered voice assistant. Simply speak your order and we\'ll take care of the rest!',
      icon: '🛒',
      features: [
        { emoji: '🛒', title: 'Smart Shopping', desc: 'Add items by name or ask for recipe ingredients', color: 'green' },
        { emoji: '🎯', title: 'Easy Ordering', desc: 'Manage your cart with simple voice commands', color: 'blue' },
        { emoji: '📦', title: 'Quick Pickup', desc: 'Complete your order and we\'ll have it ready', color: 'purple' },
      ],
      examples: [
        '"I need some bread and milk"',
        '"Add ingredients for pasta to my cart"',
        '"What\'s in my cart?"',
        '"Remove the eggs"',
        '"I\'m done, place my order"',
      ],
    },
    gm: {
      title: 'Fantasy Quest',
      subtitle: 'D&D Game Master',
      description: 'Embark on an epic fantasy adventure with an AI Game Master. Your choices shape the story in this immersive voice-driven RPG experience!',
      icon: '🎲',
      features: [
        { emoji: '⚔️', title: 'Epic Adventures', desc: 'Explore dungeons, fight monsters, and discover treasures', color: 'purple' },
        { emoji: '🎭', title: 'Dynamic Story', desc: 'Your choices matter - every decision shapes the narrative', color: 'blue' },
        { emoji: '🗺️', title: 'Rich World', desc: 'Immerse yourself in a detailed fantasy universe', color: 'green' },
      ],
      examples: [
        '"I want to explore the ancient ruins"',
        '"I attack the goblin with my sword"',
        '"Can I search the room for treasure?"',
        '"I try to persuade the guard"',
        '"What do I see around me?"',
      ],
    },
    wellness: {
      title: 'Wellness Companion',
      subtitle: 'Health & Wellness Check-in',
      description: 'Daily check-ins to help you reflect on your mood, energy, and daily intentions with Alex, your supportive wellness companion.',
      icon: '💚',
      features: [
        { emoji: '😊', title: 'Mood Tracking', desc: 'Reflect on your emotional state and patterns', color: 'green' },
        { emoji: '⚡', title: 'Energy Levels', desc: 'Monitor your vitality throughout the day', color: 'blue' },
        { emoji: '🎯', title: 'Daily Intentions', desc: 'Set and track your wellness goals', color: 'purple' },
      ],
      examples: [
        '"I\'m feeling pretty good today"',
        '"My energy is low this morning"',
        '"I want to focus on mindfulness"',
        '"Show me my wellness trends"',
        '"What should I work on today?"',
      ],
    },
    tutor: {
      title: 'Teach-the-Tutor',
      subtitle: 'AI Active Recall Coach',
      description: 'Learn programming concepts through active recall with three different learning modes: Learn, Quiz, and Teach-back.',
      icon: '📚',
      features: [
        { emoji: '📖', title: 'Learn Mode', desc: 'Understand new programming concepts', color: 'blue' },
        { emoji: '❓', title: 'Quiz Mode', desc: 'Test your knowledge with questions', color: 'purple' },
        { emoji: '🎓', title: 'Teach-back', desc: 'Explain concepts to reinforce learning', color: 'green' },
      ],
      examples: [
        '"Teach me about recursion"',
        '"Quiz me on data structures"',
        '"I want to explain what I learned"',
        '"What are the key concepts?"',
        '"Can you give me an example?"',
      ],
    },
    sdr: {
      title: 'Razorpay SDR',
      subtitle: 'AI Sales Development Representative',
      description: 'Professional sales conversations and lead capture for Razorpay payment gateway solutions.',
      icon: '📞',
      features: [
        { emoji: '💼', title: 'Professional Sales', desc: 'Engage in natural sales conversations', color: 'purple' },
        { emoji: '📊', title: 'Lead Capture', desc: 'Qualify and capture potential customers', color: 'blue' },
        { emoji: '💳', title: 'Payment Solutions', desc: 'Learn about Razorpay\'s offerings', color: 'green' },
      ],
      examples: [
        '"Tell me about Razorpay"',
        '"What payment methods do you support?"',
        '"I need a payment gateway for my business"',
        '"What are your pricing plans?"',
        '"How does integration work?"',
      ],
    },
    fraud: {
      title: 'SecureBank',
      subtitle: 'Fraud Detection Alert',
      description: 'Secure fraud detection calls to verify suspicious transactions and protect your account.',
      icon: '🚨',
      features: [
        { emoji: '🔒', title: 'Secure Verification', desc: 'Verify your identity safely', color: 'red' },
        { emoji: '💳', title: 'Transaction Review', desc: 'Review suspicious activity', color: 'orange' },
        { emoji: '✅', title: 'Quick Resolution', desc: 'Resolve issues immediately', color: 'green' },
      ],
      examples: [
        '"Yes, I made that purchase"',
        '"No, I didn\'t authorize that transaction"',
        '"Can you tell me more about the charge?"',
        '"I want to block my card"',
        '"What should I do next?"',
      ],
    },
    commerce: {
      title: 'E-commerce Shopping',
      subtitle: 'AI Shopping Assistant',
      description: 'Shop for products with our AI-powered voice assistant following the Agentic Commerce Protocol. Browse, compare, and buy with ease!',
      icon: '🛍️',
      features: [
        { emoji: '🔍', title: 'Smart Search', desc: 'Find products by category, price, or features', color: 'orange' },
        { emoji: '🛒', title: 'Easy Cart', desc: 'Add items and manage your shopping cart', color: 'blue' },
        { emoji: '✅', title: 'Quick Checkout', desc: 'Complete your purchase with voice commands', color: 'green' },
      ],
      examples: [
        '"Show me all coffee mugs"',
        '"Do you have any t-shirts under 1000?"',
        '"I\'m looking for a black hoodie"',
        '"Add the second item to my cart"',
        '"What\'s in my cart?"',
      ],
    },
  };

  const currentContent = content[mode];
  const colorMap: Record<string, string> = {
    green: 'bg-green-50 text-green-700 border-green-200',
    blue: 'bg-blue-50 text-blue-700 border-blue-200',
    purple: 'bg-purple-50 text-purple-700 border-purple-200',
    red: 'bg-red-50 text-red-700 border-red-200',
    orange: 'bg-orange-50 text-orange-700 border-orange-200',
  };

  return (
    <div ref={ref}>
      <section className="bg-background flex flex-col items-center justify-center text-center px-4">
        <div className="text-6xl mb-4">{currentContent.icon}</div>

        <h1 className="text-foreground mb-2 text-3xl font-bold">{currentContent.title}</h1>
        <h2 className="text-foreground mb-4 text-xl font-semibold" style={{ color: agentConfig.color }}>
          {currentContent.subtitle}
        </h2>

        <p className="text-foreground max-w-prose pt-1 leading-6 font-medium">
          {currentContent.description}
        </p>

        <div className="mt-6 grid max-w-3xl grid-cols-1 gap-4 md:grid-cols-3">
          {currentContent.features.map((feature, idx) => (
            <div key={idx} className={`rounded-lg p-4 ${colorMap[feature.color]}`}>
              <div className="mb-2 text-2xl">{feature.emoji}</div>
              <h3 className="font-semibold">{feature.title}</h3>
              <p className="text-sm opacity-80">{feature.desc}</p>
            </div>
          ))}
        </div>

        <div className="mt-6 max-w-2xl rounded-lg border-2 p-4" style={{ 
          borderColor: agentConfig.color + '33',
          background: `linear-gradient(to right, ${agentConfig.color}11, ${agentConfig.color}22)`
        }}>
          <h3 className="mb-2 font-semibold text-gray-900">🎤 Try saying:</h3>
          <ul className="space-y-1 text-left text-sm text-gray-700">
            {currentContent.examples.map((example, idx) => (
              <li key={idx}>✓ {example}</li>
            ))}
          </ul>
        </div>

        <Button
          variant="primary"
          size="lg"
          onClick={handleStartCall}
          disabled={isConnecting}
          className="mt-6 w-64 font-mono"
          style={{ 
            backgroundColor: agentConfig.color,
            opacity: isConnecting ? 0.7 : 1,
          }}
        >
          {isConnecting ? (
            <span className="flex items-center gap-2">
              <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Connecting...
            </span>
          ) : (
            startButtonText
          )}
        </Button>
      </section>

      <div className="fixed bottom-5 left-0 flex w-full items-center justify-center">
        <p className="text-muted-foreground max-w-prose pt-1 text-xs leading-5 font-normal text-pretty md:text-sm">
          Powered by LiveKit Voice AI •{' '}
          <a
            target="_blank"
            rel="noopener noreferrer"
            href="https://livekit.io"
            className="underline"
          >
            {currentContent.title}
          </a>
        </p>
      </div>
    </div>
  );
};