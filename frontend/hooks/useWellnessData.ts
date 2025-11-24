'use client';

import { useEffect, useState } from 'react';
import { useDataChannel } from '@livekit/components-react';

interface WellnessState {
  mood?: string;
  energy_level?: string;
  stress_factors: string[];
  daily_objectives: string[];
  self_care_intentions: string[];
  check_in_complete: boolean;
}

interface WellnessEntry {
  mood: string;
  energy_level: string;
  stress_factors: string[];
  daily_objectives: string[];
  self_care_intentions: string[];
  check_in_complete: boolean;
  date: string;
  time: string;
  timestamp: string;
  summary: string;
}

export function useWellnessData() {
  const [currentState, setCurrentState] = useState<WellnessState>({
    stress_factors: [],
    daily_objectives: [],
    self_care_intentions: [],
    check_in_complete: false,
  });
  const [recentEntries, setRecentEntries] = useState<WellnessEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Listen for wellness updates via data channel
  const { message } = useDataChannel('wellness_checkin');

  useEffect(() => {
    if (message) {
      try {
        const data = JSON.parse(new TextDecoder().decode(message.payload));
        if (data.type === 'wellness_update') {
          setCurrentState(data.data);
        }
      } catch (error) {
        console.error('Error parsing wellness data:', error);
      }
    }
  }, [message]);

  // Load recent entries from API
  useEffect(() => {
    const loadRecentEntries = async () => {
      try {
        setIsLoading(true);
        const response = await fetch('/api/wellness/recent');
        if (response.ok) {
          const data = await response.json();
          setRecentEntries(data.entries?.slice(-5) || []);
        }
      } catch (error) {
        console.error('Error loading recent entries:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadRecentEntries();

    // Refresh every 30 seconds
    const interval = setInterval(loadRecentEntries, 30000);
    return () => clearInterval(interval);
  }, []);

  const getCompletionPercentage = () => {
    const fields = [
      currentState.mood,
      currentState.energy_level,
      currentState.stress_factors.length > 0,
      currentState.daily_objectives.length > 0,
      currentState.self_care_intentions.length > 0,
    ];
    const completed = fields.filter(Boolean).length;
    return (completed / fields.length) * 100;
  };

  const getMoodTrend = () => {
    if (recentEntries.length < 2) return 'neutral';

    const moodScores: Record<string, number> = {
      sad: 1,
      stressed: 2,
      anxious: 2,
      tired: 3,
      calm: 4,
      focused: 4,
      relaxed: 4,
      happy: 5,
      optimistic: 5,
      energetic: 5,
    };

    const recent = recentEntries.slice(-2);
    const currentScore = moodScores[recent[1]?.mood?.toLowerCase()] || 3;
    const previousScore = moodScores[recent[0]?.mood?.toLowerCase()] || 3;

    if (currentScore > previousScore) return 'improving';
    if (currentScore < previousScore) return 'declining';
    return 'stable';
  };

  return {
    currentState,
    recentEntries,
    isLoading,
    completionPercentage: getCompletionPercentage(),
    moodTrend: getMoodTrend(),
  };
}
