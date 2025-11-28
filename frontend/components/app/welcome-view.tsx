import { Button } from '@/components/livekit/button';

function FoodIcon() {
  return (
    <svg
      width="64"
      height="64"
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="mb-4 size-16 text-green-600"
    >
      <path
        d="M8 16H56L52 48H12L8 16Z"
        stroke="currentColor"
        strokeWidth="3"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
      <path
        d="M8 16L6 8H2"
        stroke="currentColor"
        strokeWidth="3"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <circle cx="20" cy="56" r="4" stroke="currentColor" strokeWidth="3" fill="none" />
      <circle cx="44" cy="56" r="4" stroke="currentColor" strokeWidth="3" fill="none" />
      <path
        d="M16 24H48"
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
  mode?: 'food';
}

export const WelcomeView = ({
  startButtonText,
  onStartCall,
  mode = 'food',
  ref,
}: React.ComponentProps<'div'> & WelcomeViewProps) => {
  return (
    <div ref={ref}>
      <section className="bg-background flex flex-col items-center justify-center text-center">
        <FoodIcon />

        <h1 className="text-foreground mb-2 text-3xl font-bold">FreshMart</h1>
        <h2 className="text-foreground mb-4 text-xl font-semibold text-green-600">
          Food & Grocery Ordering
        </h2>

        <p className="text-foreground max-w-prose pt-1 leading-6 font-medium">
          Order fresh groceries and prepared foods with our AI-powered voice assistant. 
          Simply speak your order and we'll take care of the rest!
        </p>

        <div className="mt-6 grid max-w-3xl grid-cols-1 gap-4 md:grid-cols-3">
          <div className="rounded-lg bg-green-50 p-4">
            <div className="mb-2 text-2xl">🛒</div>
            <h3 className="font-semibold text-green-700">Smart Shopping</h3>
            <p className="text-sm text-green-600">
              Add items by name or ask for recipe ingredients
            </p>
          </div>
          <div className="rounded-lg bg-blue-50 p-4">
            <div className="mb-2 text-2xl">🎯</div>
            <h3 className="font-semibold text-blue-700">Easy Ordering</h3>
            <p className="text-sm text-blue-600">
              Manage your cart with simple voice commands
            </p>
          </div>
          <div className="rounded-lg bg-purple-50 p-4">
            <div className="mb-2 text-2xl">📦</div>
            <h3 className="font-semibold text-purple-700">Quick Pickup</h3>
            <p className="text-sm text-purple-600">
              Complete your order and we'll have it ready
            </p>
          </div>
        </div>

        <div className="mt-6 max-w-2xl rounded-lg border-2 border-green-200 bg-gradient-to-r from-green-50 to-blue-50 p-4">
          <h3 className="mb-2 font-semibold text-gray-900">🎤 Try saying:</h3>
          <ul className="space-y-1 text-left text-sm text-gray-700">
            <li>✓ "I need some bread and milk"</li>
            <li>✓ "Add ingredients for pasta to my cart"</li>
            <li>✓ "What's in my cart?"</li>
            <li>✓ "Remove the eggs"</li>
            <li>✓ "I'm done, place my order"</li>
          </ul>
        </div>

        <Button
          variant="primary"
          size="lg"
          onClick={onStartCall}
          className="mt-6 w-64 bg-green-600 font-mono hover:bg-green-700"
        >
          {startButtonText}
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
            FreshMart Grocery
          </a>
        </p>
      </div>
    </div>
  );
};