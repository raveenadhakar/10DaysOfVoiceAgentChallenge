import { Button } from '@/components/livekit/button';

function CoffeeIcon() {
  return (
    <svg
      width="64"
      height="64"
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="text-amber-600 mb-4 size-16"
    >
      <path
        d="M12 18V48C12 50.1217 12.8429 52.1566 14.3431 53.6569C15.8434 55.1571 17.8783 56 20 56H36C38.1217 56 40.1566 55.1571 41.6569 53.6569C43.1571 52.1566 44 50.1217 44 48V18H12Z"
        stroke="currentColor"
        strokeWidth="3"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
      <path
        d="M44 24H48C49.0609 24 50.0783 24.4214 50.8284 25.1716C51.5786 25.9217 52 26.9391 52 28V32C52 33.0609 51.5786 34.0783 50.8284 34.8284C50.0783 35.5786 49.0609 36 48 36H44"
        stroke="currentColor"
        strokeWidth="3"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
      <path
        d="M8 18H48"
        stroke="currentColor"
        strokeWidth="3"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M20 8C20 8 22 12 28 12C34 12 36 8 36 8"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
    </svg>
  );
}

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
}

export const WelcomeView = ({
  startButtonText,
  onStartCall,
  ref,
}: React.ComponentProps<'div'> & WelcomeViewProps) => {
  return (
    <div ref={ref}>
      <section className="bg-background flex flex-col items-center justify-center text-center">
        <CoffeeIcon />
        
        <h1 className="text-3xl font-bold text-foreground mb-2">
          Brew & Bean Coffee Shop
        </h1>
        
        <p className="text-foreground max-w-prose pt-1 leading-6 font-medium">
          Hi! I'm Rav, your friendly barista. Let me help you order the perfect coffee!
        </p>

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
