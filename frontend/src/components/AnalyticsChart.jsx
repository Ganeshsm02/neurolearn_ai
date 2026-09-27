import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  PointElement,
  LineElement,
  RadialLinearScale
} from 'chart.js';
import { Bar, Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  RadialLinearScale,
  Title,
  Tooltip,
  Legend
);

export function TopicMasteryChart({ topicData }) {
  if (!topicData || topicData.length === 0) {
    return <div style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '20px' }}>No topic data available yet.</div>;
  }

  const labels = topicData.map(t => t.topic);
  const scores = topicData.map(t => t.percentage);

  const backgroundColors = topicData.map(t => 
    t.percentage < 50 ? 'rgba(239, 68, 68, 0.75)' :
    t.percentage <= 75 ? 'rgba(245, 158, 11, 0.75)' : 'rgba(16, 185, 129, 0.75)'
  );

  const data = {
    labels,
    datasets: [
      {
        label: 'Topic Mastery %',
        data: scores,
        backgroundColor: backgroundColors,
        borderRadius: 8,
      }
    ]
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (context) => `Mastery: ${context.parsed.y}%`
        }
      }
    },
    scales: {
      y: {
        min: 0,
        max: 100,
        ticks: { color: '#94a3b8' },
        grid: { color: 'rgba(255, 255, 255, 0.05)' }
      },
      x: {
        ticks: { color: '#94a3b8' },
        grid: { display: false }
      }
    }
  };

  return <Bar data={data} options={options} />;
}

export function TopicHistogramChart({ histogramData }) {
  if (!histogramData || histogramData.length === 0) {
    return <div style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '20px' }}>No topic histogram data available for this IA yet.</div>;
  }

  const labels = histogramData.map(t => t.topic);
  const scores = histogramData.map(t => t.percentage);
  const backgroundColors = histogramData.map(t => t.color || (t.percentage < 50 ? 'rgba(239, 68, 68, 0.85)' : 'rgba(16, 185, 129, 0.85)'));

  const data = {
    labels,
    datasets: [
      {
        label: 'IA Topic Score %',
        data: scores,
        backgroundColor: backgroundColors,
        borderRadius: 6,
        barPercentage: 0.7,
      }
    ]
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (context) => `Score: ${context.parsed.y}% ${context.parsed.y < 50 ? '(LACKING)' : '(PROFICIENT)'}`
        }
      }
    },
    scales: {
      y: {
        min: 0,
        max: 100,
        ticks: { color: '#94a3b8' },
        grid: { color: 'rgba(255, 255, 255, 0.05)' }
      },
      x: {
        ticks: { color: '#94a3b8', font: { size: 11 } },
        grid: { display: false }
      }
    }
  };

  return <Bar data={data} options={options} />;
}

export function TrendLineChart({ examHistory }) {
  if (!examHistory || examHistory.length === 0) {
    return <div style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '20px' }}>No exam history yet.</div>;
  }

  const labels = examHistory.map(e => e.exam_name);
  const percentages = examHistory.map(e => e.percentage);

  const data = {
    labels,
    datasets: [
      {
        label: 'Assessment Score %',
        data: percentages,
        borderColor: '#6366f1',
        backgroundColor: 'rgba(99, 102, 241, 0.2)',
        tension: 0.4,
        fill: true,
        pointBackgroundColor: '#8b5cf6',
        pointRadius: 6
      }
    ]
  };

  const options = {
    responsive: true,
    plugins: { legend: { display: false } },
    scales: {
      y: {
        min: 0,
        max: 100,
        ticks: { color: '#94a3b8' },
        grid: { color: 'rgba(255, 255, 255, 0.05)' }
      },
      x: {
        ticks: { color: '#94a3b8' },
        grid: { display: false }
      }
    }
  };

  return <Line data={data} options={options} />;
}
