'use client';

import React from 'react';
import { BaseEdge, EdgeProps, getBezierPath } from '@xyflow/react';

export function CustomEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  style = {},
  markerEnd,
  data,
}: EdgeProps<any>) {
  const [edgePath] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  const isInvalid = data?.isInvalid;
  const isActive = data?.isActive;

  return (
    <>
      <BaseEdge
        path={edgePath}
        markerEnd={markerEnd}
        style={{
          ...style,
          strokeWidth: isInvalid ? 2 : 2.5,
          stroke: isInvalid ? '#f43f5e' : isActive ? '#00f2fe' : '#334155',
          strokeDasharray: isInvalid ? '5,5' : undefined,
          filter: isActive ? 'drop-shadow(0 0 6px rgba(0, 242, 254, 0.6))' : undefined,
        }}
      />
      {isActive && (
        <circle r="4" fill="#00f2fe">
          <animateMotion dur="1.8s" repeatCount="indefinite" path={edgePath} />
        </circle>
      )}
    </>
  );
}
