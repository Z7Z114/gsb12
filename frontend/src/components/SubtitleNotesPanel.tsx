import React from 'react';
import { BookOpen, Globe, Users, AlertTriangle } from 'lucide-react';
import { SubtitleNotes } from '../types';

interface SubtitleNotesPanelProps {
  notes: SubtitleNotes;
}

const SubtitleNotesPanel: React.FC<SubtitleNotesPanelProps> = ({ notes }) => {
  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">
          <BookOpen size={20} style={{ marginRight: 8 }} />
          字幕说明
        </h2>
      </div>

      <div style={{ display: 'grid', gap: '20px' }}>
        {notes.terms_explanation && notes.terms_explanation.length > 0 && (
          <div>
            <h4 style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              marginBottom: 12,
              color: '#1e40af',
            }}>
              <BookOpen size={16} />
              专业术语解释
            </h4>
            <ul style={{ paddingLeft: '20px', color: '#475569' }}>
              {notes.terms_explanation.map((term, index) => (
                <li key={index} style={{ marginBottom: 8, lineHeight: 1.6 }}>
                  {term}
                </li>
              ))}
            </ul>
          </div>
        )}

        {notes.cultural_notes && notes.cultural_notes.length > 0 && (
          <div>
            <h4 style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              marginBottom: 12,
              color: '#7c3aed',
            }}>
              <Globe size={16} />
              文化背景注释
            </h4>
            <ul style={{ paddingLeft: '20px', color: '#475569' }}>
              {notes.cultural_notes.map((note, index) => (
                <li key={index} style={{ marginBottom: 8, lineHeight: 1.6 }}>
                  {note}
                </li>
              ))}
            </ul>
          </div>
        )}

        {notes.speaker_identities && notes.speaker_identities.length > 0 && (
          <div>
            <h4 style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              marginBottom: 12,
              color: '#059669',
            }}>
              <Users size={16} />
              人物身份说明
            </h4>
            <ul style={{ paddingLeft: '20px', color: '#475569' }}>
              {notes.speaker_identities.map((speaker, index) => (
                <li key={index} style={{ marginBottom: 8, lineHeight: 1.6 }}>
                  {speaker}
                </li>
              ))}
            </ul>
          </div>
        )}

        {notes.sensitive_content && notes.sensitive_content.length > 0 && (
          <div>
            <h4 style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              marginBottom: 12,
              color: '#dc2626',
            }}>
              <AlertTriangle size={16} />
              敏感内容提示
            </h4>
            <ul style={{ paddingLeft: '20px', color: '#475569' }}>
              {notes.sensitive_content.map((content, index) => (
                <li key={index} style={{ marginBottom: 8, lineHeight: 1.6 }}>
                  {content}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default SubtitleNotesPanel;
