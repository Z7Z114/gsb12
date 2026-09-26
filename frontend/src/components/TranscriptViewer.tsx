import React from 'react';
import { FileText, Clock, User } from 'lucide-react';
import { SpeakerSegment } from '../types';
import { formatTime, getSpeakerColorClass } from '../utils/format';

interface TranscriptViewerProps {
  segments: SpeakerSegment[];
}

const TranscriptViewer: React.FC<TranscriptViewerProps> = ({ segments }) => {
  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">
          <FileText size={20} style={{ marginRight: 8 }} />
          会议转写记录
        </h2>
        <span className="badge badge-info">{segments.length} 段对话</span>
      </div>

      <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
        {segments.map((segment) => (
          <div
            key={segment.id}
            className={`transcript-segment ${getSpeakerColorClass(segment.speaker_role)}`}
          >
            <div className="transcript-meta">
              <span className="transcript-speaker">
                <User size={14} style={{ marginRight: 4, verticalAlign: 'middle' }} />
                {segment.speaker_role || segment.speaker_label}
              </span>
              <span className="transcript-time">
                <Clock size={14} style={{ marginRight: 4, verticalAlign: 'middle' }} />
                {formatTime(segment.start_time)} - {formatTime(segment.end_time)}
              </span>
            </div>
            <div className="transcript-text">{segment.text}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TranscriptViewer;
