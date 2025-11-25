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
