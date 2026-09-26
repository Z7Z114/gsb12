import React from 'react';
import { StickyNote, User, Clock } from 'lucide-react';
import { FieldNote } from '../types';
import { formatTime, formatDate } from '../utils/format';

interface FieldNotesListProps {
  notes: FieldNote[];
}

const FieldNotesList: React.FC<FieldNotesListProps> = ({ notes }) => {
  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">
          <StickyNote size={20} style={{ marginRight: 8 }} />
          田野笔记
        </h2>
        <span className="badge badge-warning">{notes.length} 条笔记</span>
      </div>

      {notes.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">📝</div>
          <p>暂无田野笔记</p>
        </div>
      ) : (
        <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
          {notes.map((note) => (
            <div key={note.id} className="field-note">
              <div className="field-note-header">
                <span>
                  {note.author && (
                    <>
                      <User size={12} style={{ marginRight: 4, verticalAlign: 'middle' }} />
                      {note.author}
                    </>
                  )}
                </span>
                <span>
                  {note.timestamp !== undefined && (
                    <>
                      <Clock size={12} style={{ marginRight: 4, verticalAlign: 'middle' }} />
                      {formatTime(note.timestamp)}
                    </>
                  )}
                  <span style={{ marginLeft: 12 }}>{formatDate(note.created_at)}</span>
                </span>
              </div>
              <div className="field-note-content">{note.content}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FieldNotesList;
