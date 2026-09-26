import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Calendar, Play, CheckCircle, Clock, FileAudio, FileText, Mail } from 'lucide-react';
import { meetingApi } from '../services/api';
import { Meeting } from '../types';
import { formatDate, getStatusBadge } from '../utils/format';

const MeetingList: React.FC = () => {
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newMeeting, setNewMeeting] = useState({ title: '', description: '' });

  useEffect(() => {
    loadMeetings();
  }, []);

  const loadMeetings = async () => {
    try {
      const data = await meetingApi.getMeetings();
      setMeetings(data);
    } catch (error) {
      console.error('Failed to load meetings:', error);
      const mockMeetings: Meeting[] = [
        {
          id: 1,
          title: '《山间记忆》粗剪评审会议',
          description: '讨论纪录片的叙事结构和影像伦理问题',
          created_at: new Date().toISOString(),
          status: 'completed',
        },
        {
          id: 2,
          title: '《城市边缘》导演剪辑讨论会',
          description: '确定最终剪辑版本的节奏和风格',
          created_at: new Date(Date.now() - 86400000).toISOString(),
          status: 'transcribed',
        },
        {
          id: 3,
          title: '《海岸人家》初剪讨论会',
          description: '人类学顾问与剪辑师的首次讨论',
          created_at: new Date(Date.now() - 172800000).toISOString(),
          status: 'pending',
        },
      ];
      setMeetings(mockMeetings);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateMeeting = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await meetingApi.createMeeting(newMeeting);
      setShowCreateForm(false);
      setNewMeeting({ title: '', description: '' });
      loadMeetings();
    } catch (error) {
      console.error('Failed to create meeting:', error);
      const mockMeeting: Meeting = {
        id: meetings.length + 1,
        ...newMeeting,
        created_at: new Date().toISOString(),
        status: 'pending',
      };
      setMeetings([mockMeeting, ...meetings]);
      setShowCreateForm(false);
      setNewMeeting({ title: '', description: '' });
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle size={16} color="#059669" />;
      case 'summarized':
        return <FileText size={16} color="#7c3aed" />;
      case 'transcribed':
        return <FileAudio size={16} color="#3b82f6" />;
      default:
        return <Clock size={16} color="#64748b" />;
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 28, fontWeight: 700, color: '#1e293b', marginBottom: 4 }}>
            剪辑会议列表
          </h1>
          <p style={{ color: '#64748b' }}>管理和查看所有民族志纪录片剪辑会议</p>
        </div>
        <button
          className="btn btn-primary"
          onClick={() => setShowCreateForm(true)}
        >
          <Plus size={18} />
          新建会议
        </button>
      </div>

      {showCreateForm && (
        <div className="card" style={{ marginBottom: 24 }}>
          <h3 style={{ marginBottom: 16 }}>创建新会议</h3>
          <form onSubmit={handleCreateMeeting}>
            <div className="form-group">
              <label className="form-label">会议标题</label>
              <input
                type="text"
                className="form-input"
                value={newMeeting.title}
                onChange={(e) => setNewMeeting({ ...newMeeting, title: e.target.value })}
                placeholder="请输入会议标题"
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label">会议描述</label>
              <textarea
                className="form-textarea"
                value={newMeeting.description}
                onChange={(e) => setNewMeeting({ ...newMeeting, description: e.target.value })}
                placeholder="请输入会议描述（可选）"
              />
            </div>
            <div style={{ display: 'flex', gap: 12, justifyContent: 'flex-end' }}>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setShowCreateForm(false)}
              >
                取消
              </button>
              <button type="submit" className="btn btn-primary">
                创建
              </button>
            </div>
          </form>
        </div>
      )}

      <div style={{ display: 'grid', gap: 16 }}>
        {meetings.map((meeting) => {
          const badge = getStatusBadge(meeting.status);

          return (
            <Link
              key={meeting.id}
              to={`/meetings/${meeting.id}`}
              style={{
                textDecoration: 'none',
                color: 'inherit',
              }}
            >
              <div
                className="card"
                style={{
                  cursor: 'pointer',
                  transition: 'transform 0.2s ease, box-shadow 0.2s ease',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-2px)';
                  e.currentTarget.style.boxShadow = '0 10px 15px -3px rgb(0 0 0 / 0.1)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 1px 3px 0 rgb(0 0 0 / 0.1)';
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
                      {getStatusIcon(meeting.status)}
                      <h3 style={{ fontSize: 18, fontWeight: 600, color: '#1e293b', margin: 0 }}>
                        {meeting.title}
                      </h3>
                      <span className={badge.className}>{badge.text}</span>
                    </div>
                    {meeting.description && (
                      <p style={{ color: '#64748b', marginBottom: 12 }}>{meeting.description}</p>
                    )}
                    <div style={{ display: 'flex', gap: 24, fontSize: 13, color: '#94a3b8' }}>
                      <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                        <Calendar size={14} />
                        {formatDate(meeting.created_at)}
                      </span>
                      <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                        <Play size={14} />
                        查看详情
                      </span>
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: 8 }}>
                    <div style={{
                      padding: 8,
                      borderRadius: 8,
                      background: '#f1f5f9',
                    }}>
                      <FileAudio size={20} color="#64748b" />
                    </div>
                    <div style={{
                      padding: 8,
                      borderRadius: 8,
                      background: '#f1f5f9',
                    }}>
                      <FileText size={20} color="#64748b" />
                    </div>
                    <div style={{
                      padding: 8,
                      borderRadius: 8,
                      background: '#f1f5f9',
                    }}>
                      <Mail size={20} color="#64748b" />
                    </div>
                  </div>
                </div>
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
};

export default MeetingList;
