'use client';

import { useEffect, useMemo, useState } from 'react';
import { useDataChannel } from '@livekit/components-react';
import { AppConfig } from '@/app-config';
import { SessionView } from '@/components/app/session-view';

interface TutorData {
  type: string;
  mode?: string;
  data?: {
    concept_id?: string;
    current_concept?: Concept | string;
    activity?: string;
    score?: number;
    timestamp?: string;
  };
  new_mode?: string;
  previous_mode?: string;
}

interface Concept {
  id: string;
  title: string;
  summary: string;
  sample_question: string;
}

interface LearningProgress {
  conceptsLearned: string[];
  questionsAnswered: number;
  teachBackSessions: number;
  currentStreak: number;
}

interface TutorSessionViewProps {
  appConfig: AppConfig;
}

export function TutorSessionView({ appConfig }: TutorSessionViewProps) {
  const [currentMode, setCurrentMode] = useState<string>('coordinator');
  const [currentConcept, setCurrentConcept] = useState<Concept | null>(null);
  const [sessionData, setSessionData] = useState<Record<string, unknown>>({});
  const [learningProgress, setLearningProgress] = useState<LearningProgress>({
    conceptsLearned: [],
    questionsAnswered: 0,
    teachBackSessions: 0,
    currentStreak: 0,
  });
  const [lastActivity, setLastActivity] = useState<string>('');
  const [feedbackScore, setFeedbackScore] = useState<number | null>(null);

  const availableConcepts: Concept[] = useMemo(
    () => [
      {
        id: 'variables',
        title: 'Variables',
        summary: 'Variables are containers that store data values...',
        sample_question: 'What is a variable and why is it useful in programming?',
      },
      {
        id: 'loops',
        title: 'Loops',
        summary: 'Loops are programming constructs that let you repeat code...',
        sample_question: 'Explain the difference between a for loop and a while loop.',
      },
      {
        id: 'functions',
        title: 'Functions',
        summary: 'Functions are reusable blocks of code that perform specific tasks...',
        sample_question: 'What are functions and how do they help organize code?',
      },
      {
        id: 'conditionals',
        title: 'Conditionals',
        summary: 'Conditionals allow your program to make decisions...',
        sample_question: 'How do if-else statements help programs make decisions?',
      },
    ],
    []
  );

  const { message } = useDataChannel('tutor_session');

  // COLOR MAPPING (safe for Tailwind)
  const modeColorToBg: Record<string, string> = {
    'text-blue-600': 'bg-blue-600',
    'text-purple-600': 'bg-purple-600',
    'text-green-600': 'bg-green-600',
    'text-gray-600': 'bg-gray-600',
  };

  useEffect(() => {
    if (!message) return;

    try {
      const rawText = new TextDecoder().decode(message.payload).trim();
      const data: TutorData = JSON.parse(rawText);

      console.log('Received tutor data:', data);

      if (data.type === 'mode_change') {
        const newMode = data.new_mode || 'coordinator';
        setCurrentMode(newMode);
        setLastActivity(`Switched to ${newMode} mode`);

        if (data.data?.concept_id) {
          const concept = availableConcepts.find((c) => c.id === data.data?.concept_id);
          if (concept) setCurrentConcept(concept);
        }
      } else if (data.type === 'tutor_update') {
        setCurrentMode(data.mode || currentMode);

        if (data.data?.current_concept) {
          const conceptId =
            typeof data.data.current_concept === 'string'
              ? data.data.current_concept
              : data.data.current_concept.id;

          const concept = availableConcepts.find((c) => c.id === conceptId);
          if (concept) setCurrentConcept(concept);
        }

        // Activity Tracking
        if (data.data?.activity) {
          setLastActivity(data.data.activity);

          if (data.data.activity.includes('question answered')) {
            setLearningProgress((prev) => ({
              ...prev,
              questionsAnswered: prev.questionsAnswered + 1,
              currentStreak: prev.currentStreak + 1,
            }));
          }

          if (data.data.activity.includes('concept explained')) {
            setLearningProgress((prev) => ({
              ...prev,
              teachBackSessions: prev.teachBackSessions + 1,
            }));
          }

          if (data.data.activity.includes('concept learned')) {
            const cid = data.data.concept_id;
            if (cid) {
              setLearningProgress((prev) => ({
                ...prev,
                conceptsLearned: prev.conceptsLearned.includes(cid)
                  ? prev.conceptsLearned
                  : [...prev.conceptsLearned, cid],
              }));
            }
          }
        }

        if (data.data?.score !== undefined) {
          setFeedbackScore(data.data.score);
        }

        setSessionData((prev) => ({ ...prev, ...data.data }));
      }
    } catch (error) {
      console.error('Failed to parse tutor data:', error);
    }
  }, [message, currentMode, availableConcepts]);

  const getModeInfo = () => {
    switch (currentMode) {
      case 'learn':
        return {
          title: 'Learn Mode',
          subtitle: 'Matthew is explaining concepts',
          color: 'text-blue-600',
          bgColor: 'bg-blue-50',
          voice: 'Matthew',
        };
      case 'quiz':
        return {
          title: 'Quiz Mode',
          subtitle: 'Alicia is testing your knowledge',
          color: 'text-purple-600',
          bgColor: 'bg-purple-50',
          voice: 'Alicia',
        };
      case 'teach_back':
        return {
          title: 'Teach Back Mode',
          subtitle: 'Ken is listening to your explanation',
          color: 'text-green-600',
          bgColor: 'bg-green-50',
          voice: 'Ken',
        };
      default:
        return {
          title: 'Tutor Coordinator',
          subtitle: 'Choose your learning mode',
          color: 'text-gray-600',
          bgColor: 'bg-gray-50',
          voice: 'Coordinator',
        };
    }
  };

  const modeInfo = getModeInfo();

  return (
    <div className="flex h-full">
      {/* Left Sidebar */}
      <div className="flex w-80 flex-col border-r border-gray-200 bg-white">
        {/* Header */}
        <div className="border-b border-gray-200 p-4">
          <h1 className="text-xl font-bold text-gray-900">Active Recall Coach</h1>
          <p className="text-sm text-gray-600">Learn • Quiz • Teach Back</p>
        </div>

        {/* Current Mode */}
        <div className={`${modeInfo.bgColor} border-b border-gray-200 p-4`}>
          <div className="flex items-center gap-3">
            <div className={`h-3 w-3 rounded-full ${modeColorToBg[modeInfo.color]}`}></div>
            <div>
              <h2 className={`font-semibold ${modeInfo.color}`}>{modeInfo.title}</h2>
              <p className="text-xs text-gray-600">{modeInfo.subtitle}</p>
            </div>
          </div>

          {currentConcept && (
            <div className="mt-2 rounded bg-white/50 p-2">
              <div className="text-sm font-medium text-gray-900">{currentConcept.title}</div>
              <div className="mt-1 text-xs text-gray-600">
                {currentConcept.summary.substring(0, 100)}...
              </div>
            </div>
          )}
        </div>

        {/* Learning Progress */}
        <div className="border-b border-gray-200 p-4">
          <h3 className="mb-3 font-semibold text-gray-900">Learning Progress</h3>

          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Concepts Learned</span>
              <span className="font-semibold text-emerald-600">
                {learningProgress.conceptsLearned.length}/4
              </span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Questions Answered</span>
              <span className="font-semibold text-blue-600">
                {learningProgress.questionsAnswered}
              </span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Teach Back Sessions</span>
              <span className="font-semibold text-purple-600">
                {learningProgress.teachBackSessions}
              </span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Current Streak</span>
              <span className="font-semibold text-orange-600">
                {learningProgress.currentStreak}
              </span>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="mt-3">
            <div className="mb-1 flex justify-between text-xs text-gray-600">
              <span>Overall Progress</span>
              <span>{Math.round((learningProgress.conceptsLearned.length / 4) * 100)}%</span>
            </div>

            <div className="h-2 w-full rounded-full bg-gray-200">
              <div
                className="h-2 rounded-full bg-emerald-500 transition-all duration-300"
                style={{
                  width: `${(learningProgress.conceptsLearned.length / 4) * 100}%`,
                }}
              ></div>
            </div>
          </div>
        </div>

        {/* Concepts List */}
        <div className="border-b border-gray-200 p-4">
          <h3 className="mb-3 font-semibold text-gray-900">Concepts</h3>

          <div className="space-y-2">
            {availableConcepts.map((concept) => (
              <div
                key={concept.id}
                className={`rounded-lg border p-2 transition-colors ${
                  currentConcept?.id === concept.id
                    ? 'border-emerald-300 bg-emerald-50'
                    : 'border-gray-200 hover:border-gray-300'
                } ${
                  learningProgress.conceptsLearned.includes(concept.id)
                    ? 'border-green-200 bg-green-50'
                    : ''
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-900">{concept.title}</span>
                  {learningProgress.conceptsLearned.includes(concept.id) && (
                    <span className="text-xs text-green-600">✓</span>
                  )}
                </div>
                <p className="mt-1 text-xs text-gray-600">{concept.summary.substring(0, 60)}...</p>
              </div>
            ))}
          </div>
        </div>

        {/* Learning Mode Buttons */}
        <div className="border-b border-gray-200 p-4">
          <h3 className="mb-3 font-semibold text-gray-900">Learning Modes</h3>

          <div className="space-y-2">
            <button
              className={`w-full rounded-lg border p-3 text-left transition-colors ${
                currentMode === 'learn'
                  ? 'border-blue-300 bg-blue-100 text-blue-700'
                  : 'border-gray-200 bg-gray-50 text-gray-700 hover:bg-gray-100'
              }`}
              onClick={() => console.log('Switch to learn mode')}
            >
              <div className="flex items-center gap-2">
                <span className="text-lg">📚</span>
                <div>
                  <div className="font-medium">Learn Mode</div>
                  <div className="text-xs opacity-75">Matthew explains concepts</div>
                </div>
              </div>
            </button>

            <button
              className={`w-full rounded-lg border p-3 text-left transition-colors ${
                currentMode === 'quiz'
                  ? 'border-purple-300 bg-purple-100 text-purple-700'
                  : 'border-gray-200 bg-gray-50 text-gray-700 hover:bg-gray-100'
              }`}
              onClick={() => console.log('Switch to quiz mode')}
            >
              <div className="flex items-center gap-2">
                <span className="text-lg">🧠</span>
                <div>
                  <div className="font-medium">Quiz Mode</div>
                  <div className="text-xs opacity-75">Alicia tests your knowledge</div>
                </div>
              </div>
            </button>

            <button
              className={`w-full rounded-lg border p-3 text-left transition-colors ${
                currentMode === 'teach_back'
                  ? 'border-green-300 bg-green-100 text-green-700'
                  : 'border-gray-200 bg-gray-50 text-gray-700 hover:bg-gray-100'
              }`}
              onClick={() => console.log('Switch to teach back mode')}
            >
              <div className="flex items-center gap-2">
                <span className="text-lg">👨‍🏫</span>
                <div>
                  <div className="font-medium">Teach Back Mode</div>
                  <div className="text-xs opacity-75">Ken listens to your explanations</div>
                </div>
              </div>
            </button>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="flex-1 p-4">
          <h3 className="mb-3 font-semibold text-gray-900">Recent Activity</h3>

          {lastActivity ? (
            <div className="rounded bg-gray-50 p-2 text-sm text-gray-600">{lastActivity}</div>
          ) : (
            <div className="text-sm text-gray-400">No recent activity</div>
          )}

          {feedbackScore !== null && (
            <div className="mt-2 rounded bg-blue-50 p-2">
              <div className="text-sm font-medium text-blue-900">Latest Score</div>
              <div className="text-lg font-bold text-blue-600">
                {Math.round(feedbackScore * 100)}%
              </div>
            </div>
          )}
        </div>

        {/* Debug Data */}
        {process.env.NEXT_PUBLIC_NODE_ENV === 'development' &&
          Object.keys(sessionData).length > 0 && (
            <div className="border-t border-gray-200 p-4">
              <details className="text-xs">
                <summary className="cursor-pointer font-medium text-gray-700">Debug Data</summary>
                <pre className="mt-2 max-h-32 overflow-auto rounded bg-gray-50 p-2 text-gray-600">
                  {JSON.stringify(sessionData, null, 2)}
                </pre>
              </details>
            </div>
          )}
      </div>

      {/* Main Session View */}
      <div className="flex flex-1 flex-col">
        <SessionView appConfig={appConfig} />
      </div>
    </div>
  );
}
