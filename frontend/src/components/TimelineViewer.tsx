import React from 'react';
import { Timeline as TimelineIcon, Clock } from 'lucide-react';
import { Timeline as TimelineType } from '../types';
import { formatTime } from '../utils/format';

interface TimelineViewerProps {
  timelines: TimelineType[];
}

const TimelineViewer: React.FC<TimelineViewerProps> = ({ timelines }) => {
  if (timelines.length === 0) {
    return (
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">
            <TimelineIcon size={20} style={{ marginRight: 8 }} />
            粗剪时间线
          </h2>
        </div>
        <div className="empty-state">
          <div className="empty-state-icon">⏱️</div>
          <p>暂无时间线数据</p>
        </div>
      </div>
    );
  }

  return (
    <>
      {timelines.map((timeline) => {
        const maxEndTime = Math.max(...timeline.clips.map(c => c.end_time), 100);
        const totalDuration = Math.ceil(maxEndTime / 60) * 60;

        const marks = [];
        const markInterval = totalDuration > 300 ? 60 : 30;
        for (let t = 0; t <= totalDuration; t += markInterval) {
          marks.push(t);
        }

        return (
          <div key={timeline.id} className="card">
            <div className="card-header">
              <h2 className="card-title">
                <TimelineIcon size={20} style={{ marginRight: 8 }} />
                {timeline.title}
              </h2>
              <span className="badge badge-info">
                {timeline.clips.length} 个片段 · 总时长 {formatTime(maxEndTime)}
              </span>
            </div>

            <div className="timeline-container">
              <div className="timeline-track">
                {timeline.clips.map((clip) => {
                  const left = (clip.start_time / totalDuration) * 100;
                  const width = Math.max(((clip.end_time - clip.start_time) / totalDuration) * 100, 2);

                  return (
                    <div
                      key={clip.id}
                      className="timeline-clip"
                      style={{
                        left: `${left}%`,
                        width: `${width}%`,
                      }}
                      title={`${clip.clip_name}\n${formatTime(clip.start_time)} - ${formatTime(clip.end_time)}`}
                    >
                      <div style={{ fontWeight: 500 }}>{clip.clip_name}</div>
                      <div style={{ fontSize: 10, opacity: 0.8 }}>
                        {formatTime(clip.start_time)}
                      </div>
                    </div>
                  );
                })}
              </div>

              <div className="timeline-ruler">
                {marks.map((mark, index) => (
                  <div key={index} className="timeline-ruler-mark">
                    {formatTime(mark)}
                  </div>
                ))}
              </div>
            </div>

            <div style={{ marginTop: 16 }}>
              <h4 style={{ marginBottom: 12, color: '#475569', fontSize: 14 }}>片段列表</h4>
              <div style={{ display: 'grid', gap: 8 }}>
                {timeline.clips.map((clip) => (
                  <div
                    key={clip.id}
                    style={{
                      padding: 12,
                      background: '#f8fafc',
                      borderRadius: 8,
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                    }}
                  >
                    <div>
                      <div style={{ fontWeight: 500, color: '#1e293b' }}>
                        {clip.clip_name}
                      </div>
                      {clip.notes && (
                        <div style={{ fontSize: 12, color: '#64748b', marginTop: 4 }}>
                          {clip.notes}
                        </div>
                      )}
                    </div>
                    <div style={{
                      fontSize: 12,
                      color: '#64748b',
                      background: '#e2e8f0',
                      padding: '4px 12px',
                      borderRadius: 12,
                    }}>
                      <Clock size={12} style={{ marginRight: 4, verticalAlign: 'middle' }} />
                      {formatTime(clip.start_time)} - {formatTime(clip.end_time)}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        );
      })}
    </>
  );
};

export default TimelineViewer;
