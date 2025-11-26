import { Button } from '@/components/livekit/button';

function BookIcon() {
  return (
    <svg
      width="64"
      height="64"
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="mb-4 size-16 text-emerald-600"
    >
      <path
        d="M8 8V52C8 53.0609 8.42143 54.0783 9.17157 54.8284C9.92172 55.5786 10.9391 56 12 56H52C53.0609 56 54.0783 55.5786 54.8284 54.8284C55.5786 54.0783 56 53.0609 56 52V12C56 10.9391 55.5786 9.92172 54.8284 9.17157C54.0783 8.42143 53.0609 8 52 8H16"
        stroke="currentColor"
        strokeWidth="3"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
      <path
        d="M8 8C8 6.93913 8.42143 5.92172 9.17157 5.17157C9.92172 4.42143 10.9391 4 12 4H48"
        stroke="currentColor"
        strokeWidth="3"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M16 20H44"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M16 28H44"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M16 36H36"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function PaymentIcon() {
  return (
    <svg
      width="64"
      height="64"
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="mb-4 size-16 text-blue-600"
    >
      <rect
        x="8"
        y="16"
        width="48"
        height="32"
        rx="4"
        stroke="currentColor"
        strokeWidth="3"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M8 24H56"
        stroke="currentColor"
        strokeWidth="3"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M16 36H24"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M32 36H40"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
  mode?: 'tutor' | 'sdr';
}

export const WelcomeView = ({
  startButtonText,
  onStartCall,
  mode = 'sdr',
  ref,
}: React.ComponentProps<'div'> & WelcomeViewProps) => {
  // SDR Mode Content
  if (mode === 'sdr') {
    return (
      <div ref={ref}>
        <section className="bg-background flex flex-col items-center justify-center text-center">
          <PaymentIcon />

          <h1 className="text-foreground mb-2 text-3xl font-bold">Razorpay</h1>
          <h2 className="text-foreground mb-4 text-xl font-semibold text-blue-600">
            India's Leading Payment Gateway
          </h2>

          <p className="text-foreground max-w-prose pt-1 leading-6 font-medium">
            Connect with our AI-powered Sales Development Representative to learn about Razorpay's
            payment solutions and explore how we can help your business grow.
          </p>

          <div className="mt-6 grid max-w-3xl grid-cols-1 gap-4 md:grid-cols-3">
            <div className="rounded-lg bg-blue-50 p-4">
              <div className="mb-2 text-2xl">💳</div>
              <h3 className="font-semibold text-blue-700">Payment Gateway</h3>
              <p className="text-sm text-blue-600">
                Accept payments via 100+ modes including cards, UPI, and wallets
              </p>
            </div>
            <div className="rounded-lg bg-indigo-50 p-4">
              <div className="mb-2 text-2xl">🔄</div>
              <h3 className="font-semibold text-indigo-700">Subscriptions</h3>
              <p className="text-sm text-indigo-600">
                Automate recurring billing and subscription management
              </p>
            </div>
            <div className="rounded-lg bg-purple-50 p-4">
              <div className="mb-2 text-2xl">🏪</div>
              <h3 className="font-semibold text-purple-700">Marketplace</h3>
              <p className="text-sm text-purple-600">
                Split payments automatically for multi-vendor platforms
              </p>
            </div>
          </div>

          <div className="mt-6 rounded-lg bg-gradient-to-r from-blue-50 to-indigo-50 p-4 max-w-2xl">
            <h3 className="font-semibold text-gray-900 mb-2">What to Expect:</h3>
            <ul className="text-sm text-gray-700 space-y-1 text-left">
              <li>✓ Learn about Razorpay's products and pricing</li>
              <li>✓ Get answers to your payment solution questions</li>
              <li>✓ Share your business needs and use case</li>
              <li>✓ Receive personalized recommendations</li>
            </ul>
          </div>

          <Button variant="primary" size="lg" onClick={onStartCall} className="mt-6 w-64 font-mono">
            {startButtonText}
          </Button>
        </section>

        <div className="fixed bottom-5 left-0 flex w-full items-center justify-center">
          <p className="text-muted-foreground max-w-prose pt-1 text-xs leading-5 font-normal text-pretty md:text-sm">
            Powered by LiveKit Voice AI •{' '}
            <a
              target="_blank"
              rel="noopener noreferrer"
              href="https://razorpay.com"
              className="underline"
            >
              Visit Razorpay.com
            </a>
          </p>
        </div>
      </div>
    );
  }

  // Tutor Mode Content (original)
  return (
    <div ref={ref}>
      <section className="bg-background flex flex-col items-center justify-center text-center">
        <BookIcon />

        <h1 className="text-foreground mb-2 text-3xl font-bold">Teach-the-Tutor</h1>
        <h2 className="text-foreground mb-4 text-xl font-semibold text-emerald-600">
          Active Recall Coach
        </h2>

        <p className="text-foreground max-w-prose pt-1 leading-6 font-medium">
          Learn programming concepts through active recall! Choose from three learning modes:
        </p>

        <div className="mt-4 grid max-w-2xl grid-cols-1 gap-4 md:grid-cols-3">
          <div className="rounded-lg bg-blue-50 p-4">
            <div className="mb-2 text-2xl">📚</div>
            <h3 className="font-semibold text-blue-700">Learn</h3>
            <p className="text-sm text-blue-600">Matthew explains concepts clearly</p>
          </div>
          <div className="rounded-lg bg-purple-50 p-4">
            <div className="mb-2 text-2xl">🧠</div>
            <h3 className="font-semibold text-purple-700">Quiz</h3>
            <p className="text-sm text-purple-600">Alicia tests your understanding</p>
          </div>
          <div className="rounded-lg bg-green-50 p-4">
            <div className="mb-2 text-2xl">👨‍🏫</div>
            <h3 className="font-semibold text-green-700">Teach Back</h3>
            <p className="text-sm text-green-600">Ken listens to your explanations</p>
          </div>
        </div>

        <Button variant="primary" size="lg" onClick={onStartCall} className="mt-6 w-64 font-mono">
          {startButtonText}
        </Button>
      </section>

      <div className="fixed bottom-5 left-0 flex w-full items-center justify-center">
        <p className="text-muted-foreground max-w-prose pt-1 text-xs leading-5 font-normal text-pretty md:text-sm">
          Need help getting set up? Check out the{' '}
          <a
            target="_blank"
            rel="noopener noreferrer"
            href="https://docs.livekit.io/agents/start/voice-ai/"
            className="underline"
          >
            Voice AI quickstart
          </a>
          .
        </p>
      </div>
    </div>
  );
};
