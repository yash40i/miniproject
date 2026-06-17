"use client";

import React from 'react';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip
} from 'recharts';

export default function SkillRadarChart({ nodesData }: { nodesData: any }) {
  // Transform the nodesData into recharts compatible format
  // nodesData is expected to be { nodes: NodeActivation[], ... }
  // NodeActivation { skill: string, state: string, similarity_score: number }
  
  const data = nodesData?.nodes?.map((node: any) => {
    // Score is 0-1, multiply by 100
    const score = Math.round((node.similarity_score || 0) * 100);
    return {
      skill: node.skill,
      score: score,
      fullMark: 100,
      state: node.state
    };
  }) || [];

  // Sort by score or just take top 10 if there are too many for a radar chart
  const displayData = data.slice(0, 12); // Radar charts get messy with too many points

  const handlePointerEnter = (dataItem: any) => {
    // If the window exposes the focus function from SkillGraph
    if (typeof window !== 'undefined' && (window as any).focusSkillNode && dataItem?.skill) {
      (window as any).focusSkillNode(dataItem.skill);
    }
  };

  const handleClick = (dataItem: any) => {
    if (typeof window !== 'undefined' && (window as any).focusSkillNode && dataItem?.payload?.skill) {
      (window as any).focusSkillNode(dataItem.payload.skill);
    }
  };

  if (!displayData.length) {
    return <div className="text-slate-400 text-center py-10">No skill data available for radar chart</div>;
  }

  return (
    <div style={{ width: '100%', height: '400px' }}>
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="70%" data={displayData}>
          <PolarGrid stroke="#4b5563" />
          <PolarAngleAxis 
            dataKey="skill" 
            tick={{ fill: '#94a3b8', fontSize: 12 }} 
            onClick={handleClick}
            style={{ cursor: 'pointer' }}
          />
          <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
          <Tooltip 
            contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f8fafc' }}
            itemStyle={{ color: '#3b82f6' }}
            formatter={(value: number) => [`${value}%`, 'Match Score']}
          />
          <Radar
            name="Skill Match"
            dataKey="score"
            stroke="#3b82f6"
            fill="#3b82f6"
            fillOpacity={0.5}
            activeDot={{ r: 6, fill: '#60a5fa', stroke: '#fff', strokeWidth: 2 }}
            onMouseEnter={handlePointerEnter}
            onClick={handleClick}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
