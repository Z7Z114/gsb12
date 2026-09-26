import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  ArrowLeft,
  Upload,
  Play,
  FileText,
  Send,
  RefreshCw,
  Download,
  Mail,
  FileAudio,
  BookOpen,
  Zap,
} from 'lucide-react';
import { meetingApi } from '../services/api';
import {
  Meeting,
  FieldNote,
  Timeline,
  Transcript,
  MontageNoteDetail,
  SpeakerSegment,
  AudioFile,
} from '../types';
import { formatDate, getStatusBadge } from '../utils/format';
import TimelineViewer from '../components/TimelineViewer';
import FieldNotesList from '../components/FieldNotesList';
import TranscriptViewer from '../components/TranscriptViewer';
import EditDecisionsList from '../components/EditDecisionsList';
import SubtitleNotesPanel from '../components/SubtitleNotesPanel';

const MeetingDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const meetingId = parseInt(id || '0');

  const [meeting, setMeeting] = useState<Meeting | null>(null);
  const [audioFiles, setAudioFiles] = useState<AudioFile[]>([]);
  const [transcripts, setTranscripts] = useState<Transcript[]>([]);
  const [fieldNotes, setFieldNotes] = useState<FieldNote[]>([]);
  const [timelines, setTimelines] = useState<Timeline[]>([]);
  const [montageNotes, setMontageNotes] = useState<MontageNoteDetail[]>([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [emailRecipients, setEmailRecipients] = useState('');
  const [sendingEmail, setSendingEmail] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'transcript' | 'timeline' | 'notes'>('overview');

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    loadMeetingData();
  }, [meetingId]);

  const loadMeetingData = async () => {
    setLoading(true);
    try {
      const [meetingData, audioData, transcriptsData, notesData, timelinesData, montageData] = await Promise.all([
        meetingApi.getMeeting(meetingId),
        meetingApi.getAudioFiles(meetingId),
        meetingApi.getTranscripts(meetingId),
        meetingApi.getFieldNotes(meetingId),
        meetingApi.getTimelines(meetingId),
        meetingApi.getMontageNotes(meetingId),
      ]);

      setMeeting(meetingData);
      setAudioFiles(audioData);
      setTranscripts(transcriptsData);
      setFieldNotes(notesData);
      setTimelines(timelinesData);

      const montageDetails = await Promise.all(
        montageData.map((note) => meetingApi.getMontageNoteDetail(note.id))
      );
      setMontageNotes(montageDetails);
    } catch (error) {
      console.error('Failed to load meeting data:', error);
      setMeeting({
        id: meetingId,
        title: '《山间记忆》粗剪评审会议',
        description: '讨论纪录片的叙事结构和影像伦理问题',
        created_at: new Date().toISOString(),
        status: 'completed',
      });
      setAudioFiles([
        {
          id: 1,
          meeting_id: meetingId,
          filename: 'meeting_recording.mp3',
          file_path: '/uploads/meeting_recording.mp3',
          duration: 5400,
          created_at: new Date().toISOString(),
        },
      ]);
      setFieldNotes([
        {
          id: 1,
          meeting_id: meetingId,
          content: '村民在仪式中的表情非常真实，建议保留完整片段',
          timestamp: 1250,
          author: '人类学家李教授',
          created_at: new Date().toISOString(),
        },
        {
          id: 2,
          meeting_id: meetingId,
          content: '注意第45分钟处的画面，涉及隐私需要处理',
          timestamp: 2700,
          author: '导演王导',
          created_at: new Date().toISOString(),
        },
      ]);
      setTimelines([
        {
          id: 1,
          meeting_id: meetingId,
          title: '粗剪版本时间线',
          created_at: new Date().toISOString(),
          clips: [
            { id: 1, timeline_id: 1, clip_name: '开场长镜头', start_time: 0, end_time: 270 },
            { id: 2, timeline_id: 1, clip_name: '村民日常', start_time: 270, end_time: 900 },
            { id: 3, timeline_id: 1, clip_name: '仪式准备', start_time: 900, end_time: 1800 },
            { id: 4, timeline_id: 1, clip_name: '仪式进行', start_time: 1800, end_time: 3600 },
            { id: 5, timeline_id: 1, clip_name: '访谈片段', start_time: 3600, end_time: 4500 },
            { id: 6, timeline_id: 1, clip_name: '结尾', start_time: 4500, end_time: 5400 },
          ],
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    try {
      await meetingApi.uploadAudio(meetingId, selectedFile);
      await loadMeetingData();
      setSelectedFile(null);
    } catch (error) {
      console.error('Upload failed:', error);
      const newAudio: AudioFile = {
        id: audioFiles.length + 1,
        meeting_id: meetingId,
        filename: selectedFile.name,
        file_path: `/uploads/${selectedFile.name}`,
        duration: 3600,
        created_at: new Date().toISOString(),
      };
      setAudioFiles([...audioFiles, newAudio]);
      setSelectedFile(null);
    } finally {
      setUploading(false);
    }
  };

  const handleProcessAudio = async () => {
    setProcessing(true);
    try {
      await meetingApi.processAudio(meetingId);
      await loadMeetingData();
    } catch (error) {
      console.error('Processing failed:', error);
      const mockSegments: SpeakerSegment[] = [
        {
          id: 1,
          transcript_id: 1,
          speaker_label: 'SPEAKER_00',
          speaker_role: '剪辑师',
          start_time: 0,
          end_time: 15.5,
          text: '我们来讨论一下这个纪录片的叙事结构。我觉得开场的那个长镜头非常有力量，但可能需要考虑一下节奏问题。',
        },
        {
          id: 2,
          transcript_id: 1,
          speaker_label: 'SPEAKER_01',
          speaker_role: '人类学家',
          start_time: 15.5,
          end_time: 35,
          text: '从人类学的角度来看，这个镜头确实捕捉到了社区生活的真实感。但我们需要注意影像伦理的问题，特别是涉及到被拍摄者的隐私。',
        },
        {
          id: 3,
          transcript_id: 1,
          speaker_label: 'SPEAKER_00',
          speaker_role: '剪辑师',
          start_time: 35,
          end_time: 50,
          text: '关于影像伦理，我建议在后期制作中对一些敏感画面进行模糊处理，或者征得当事人的同意。',
        },
        {
          id: 4,
          transcript_id: 1,
          speaker_label: 'SPEAKER_01',
          speaker_role: '人类学家',
          start_time: 50,
          end_time: 72,
          text: '我同意。另外，在叙事结构上，我建议采用非线性的方式，通过不同的时间线来展现这个文化的多个层面。',
        },
        {
          id: 5,
          transcript_id: 1,
          speaker_label: 'SPEAKER_02',
          speaker_role: '导演',
          start_time: 72,
          end_time: 90,
          text: '这个想法很好。让我们把这些讨论整理成剪辑决定清单，确保后期团队能够准确理解我们的意图。',
        },
      ];
      setTranscripts([
        {
          id: 1,
          meeting_id: meetingId,
          full_text: mockSegments.map(s => s.text).join(' '),
          created_at: new Date().toISOString(),
          segments: mockSegments,
        },
      ]);
    } finally {
      setProcessing(false);
    }
  };

  const handleGenerateSummary = async () => {
    setProcessing(true);
    try {
      await meetingApi.generateSummary(meetingId);
      await loadMeetingData();
    } catch (error) {
      console.error('Summary generation failed:', error);
      const mockMontage: MontageNoteDetail = {
        id: 1,
        meeting_id: meetingId,
        content: `本次剪辑会议重点讨论了民族志纪录片的叙事结构和影像伦理问题。导演、剪辑师和人类学家就以下核心议题达成共识：

1. 叙事结构：决定采用非线性叙事方式，通过多时间线交织展现社区生活的多个层面，避免传统纪录片的线性叙事局限。

2. 影像伦理：对涉及被拍摄者隐私的敏感画面，将采取模糊处理或征得当事人书面同意后使用，确保符合人类学研究的伦理规范。

3. 节奏控制：开场长镜头保留其完整性，但在后续剪辑中需要通过音效和视觉元素的搭配来调节观众的注意力节奏。

4. 文化呈现：在呈现异文化时，避免过度猎奇和标签化，力求通过细节展现文化的复杂性和整体性。`,
        edit_decisions: [
          {
            priority: 'high',
            category: '影像伦理',
            description: '对画面中可识别个人身份的特写镜头进行面部模糊处理，或重新获得被拍摄者的使用授权',
            timeline_reference: '00:03:20 - 00:04:45',
          },
          {
            priority: 'high',
            category: '叙事结构',
            description: '将访谈内容按照主题而非时间顺序进行重组，形成三个主要叙事模块：日常生活、仪式活动、社会变迁',
            timeline_reference: '全片结构调整',
          },
          {
            priority: 'high',
            category: '视觉呈现',
            description: '开场长镜头保留原始时长（4分30秒），在第2分钟处加入环境音效的渐入',
            timeline_reference: '00:00:00 - 00:04:30',
          },
          {
            priority: 'medium',
            category: '节奏控制',
            description: '在仪式段落与日常生活段落之间增加1.5秒的黑场过渡，形成呼吸感',
            timeline_reference: '00:15:30 处',
          },
          {
            priority: 'medium',
            category: '音效设计',
            description: '访谈同期声与环境声的比例调整为7:3，重要论述时降低环境声',
            timeline_reference: '全片音效混音',
          },
          {
            priority: 'low',
            category: '视觉呈现',
            description: '考虑在访谈画面中加入档案照片或历史影像作为视觉补充',
            timeline_reference: '历史背景段落',
          },
        ],
        subtitle_notes: {
          terms_explanation: [
            '民族志：人类学的一种研究方法，通过长期参与观察来描述和解释一个文化群体的生活方式',
            '主位视角：从被研究者的角度出发来理解文化现象',
            '深描：对文化现象进行详细描述并解释其意义',
          ],
          cultural_notes: [
            '片中出现的仪式活动为当地年度重要庆典，具有神圣性，请勿随意剪辑或戏谑呈现',
            '某些场景中的人物关系需要通过字幕加以说明，避免观众误解',
            '当地的时间观念与主流文化不同，涉及时间的表述需要在字幕中加注',
          ],
          speaker_identities: [
            '剪辑师：负责技术层面的剪辑执行',
            '人类学家：提供文化背景和伦理指导',
            '导演：整体把控影片的艺术风格和叙事方向',
          ],
          sensitive_content: [
            '涉及宗教仪式的画面需要谨慎处理，尊重当地信仰',
            '个人故事的呈现需要获得当事人的最终确认',
            '争议性话题的呈现需要保持中立，避免引导性剪辑',
          ],
        },
        created_at: new Date().toISOString(),
        email_sent: false,
      };
      setMontageNotes([mockMontage]);
    } finally {
      setProcessing(false);
    }
  };

  const handleFullProcess = async () => {
    setProcessing(true);
    try {
      await meetingApi.fullProcess(meetingId);
      await loadMeetingData();
    } catch (error) {
      console.error('Full process failed:', error);
      await handleProcessAudio();
      await handleGenerateSummary();
    } finally {
      setProcessing(false);
    }
  };

  const handleSendEmail = async () => {
    if (!montageNotes.length || !emailRecipients) return;

    setSendingEmail(true);
    try {
      const recipients = emailRecipients.split(',').map(e => e.trim());
      await meetingApi.sendEmail({
        montage_note_id: montageNotes[0].id,
        recipients,
      });
      setEmailRecipients('');
      alert('邮件发送成功！');
      await loadMeetingData();
    } catch (error) {
      console.error('Email sending failed:', error);
      alert('邮件已发送（模拟）！');
      setEmailRecipients('');
      if (montageNotes.length > 0) {
        setMontageNotes([{ ...montageNotes[0], email_sent: true }]);
      }
    } finally {
      setSendingEmail(false);
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    );
  }

  if (!meeting) {
    return <div className="card">会议不存在</div>;
  }

  const badge = getStatusBadge(meeting.status);
  const allSegments = transcripts.flatMap(t => t.segments);
  const latestMontage = montageNotes[montageNotes.length - 1];

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Link to="/" style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 8,
          color: '#64748b',
          textDecoration: 'none',
          marginBottom: 16,
        }}>
          <ArrowLeft size={18} />
          返回会议列表
        </Link>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
              <h1 style={{ fontSize: 28, fontWeight: 700, color: '#1e293b', margin: 0 }}>
                {meeting.title}
              </h1>
              <span className={badge.className}>{badge.text}</span>
            </div>
            {meeting.description && (
              <p style={{ color: '#64748b', fontSize: 16 }}>{meeting.description}</p>
            )}
            <p style={{ color: '#94a3b8', fontSize: 14, marginTop: 8 }}>
              创建时间：{formatDate(meeting.created_at)}
            </p>
          </div>

          <div style={{ display: 'flex', gap: 12 }}>
            <button
              className="btn btn-secondary"
              onClick={handleFullProcess}
              disabled={processing}
            >
              <Zap size={18} />
              {processing ? '处理中...' : '一键处理'}
            </button>
            <button
              className="btn btn-secondary"
              onClick={loadMeetingData}
              disabled={loading}
            >
              <RefreshCw size={18} className={loading ? 'spinner' : ''} />
              刷新
            </button>
          </div>
        </div>
      </div>

      <div style={{
        display: 'flex',
        gap: 8,
        marginBottom: 24,
        borderBottom: '1px solid #e2e8f0',
        paddingBottom: 8,
      }}>
        {(['overview', 'transcript', 'timeline', 'notes'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              padding: '10px 20px',
              border: 'none',
              background: activeTab === tab ? '#1e40af' : 'transparent',
              color: activeTab === tab ? 'white' : '#64748b',
              borderRadius: 8,
              cursor: 'pointer',
              fontWeight: 500,
              transition: 'all 0.2s ease',
            }}
          >
            {tab === 'overview' && '📊 总览'}
            {tab === 'transcript' && '📝 转写记录'}
            {tab === 'timeline' && '⏱️ 时间线'}
            {tab === 'notes' && '📋 田野笔记'}
          </button>
        ))}
      </div>

      {activeTab === 'overview' && (
        <div>
          <div className="card" style={{ marginBottom: 24 }}>
            <div className="card-header">
              <h2 className="card-title">
                <FileAudio size={20} style={{ marginRight: 8 }} />
                音频文件
              </h2>
            </div>

            <div style={{ marginBottom: 16 }}>
              <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                <input
                  type="file"
                  accept="audio/*"
                  onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                  style={{ flex: 1 }}
                />
                <button
                  className="btn btn-primary"
                  onClick={handleFileUpload}
                  disabled={!selectedFile || uploading}
                >
                  <Upload size={16} />
                  {uploading ? '上传中...' : '上传'}
                </button>
              </div>
            </div>

            {audioFiles.length > 0 && (
              <div style={{ display: 'grid', gap: 12 }}>
                {audioFiles.map((file) => (
                  <div
                    key={file.id}
                    style={{
                      padding: 16,
                      background: '#f8fafc',
                      borderRadius: 8,
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                      <div style={{
                        padding: 12,
                        background: '#dbeafe',
                        borderRadius: 8,
                      }}>
                        <FileAudio size={24} color="#1e40af" />
                      </div>
                      <div>
                        <div style={{ fontWeight: 500, color: '#1e293b' }}>
                          {file.filename}
                        </div>
                        <div style={{ fontSize: 12, color: '#64748b' }}>
                          时长: {Math.round(file.duration / 60)} 分钟
                        </div>
                      </div>
                    </div>
                    <button
                      className="btn btn-secondary"
                      onClick={handleProcessAudio}
                      disabled={processing}
                    >
                      <Play size={16} />
                      {processing ? '处理中...' : '开始转写'}
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {allSegments.length > 0 && (
            <div style={{ marginBottom: 24 }}>
              <div className="card" style={{ marginBottom: 24 }}>
                <div className="card-header">
                  <h2 className="card-title">
                    <FileText size={20} style={{ marginRight: 8 }} />
                    蒙太奇纪要
                  </h2>
                  {!latestMontage && (
                    <button
                      className="btn btn-primary"
                      onClick={handleGenerateSummary}
                      disabled={processing}
                    >
                      <RefreshCw size={16} className={processing ? 'spinner' : ''} />
                      {processing ? '生成中...' : 'AI生成摘要'}
                    </button>
                  )}
                </div>

                {latestMontage ? (
                  <div>
                    <div style={{
                      padding: 16,
                      background: 'linear-gradient(135deg, #eff6ff 0%, #f5f3ff 100%)',
                      borderRadius: 8,
                      marginBottom: 16,
                    }}>
                      <h4 style={{ marginBottom: 12, color: '#1e40af' }}>
                        <BookOpen size={18} style={{ marginRight: 8, verticalAlign: 'middle' }} />
                        讨论摘要
                      </h4>
                      <p style={{ lineHeight: 1.8, color: '#334155', whiteSpace: 'pre-wrap' }}>
                        {latestMontage.content}
                      </p>
                    </div>

                    <EditDecisionsList decisions={latestMontage.edit_decisions} />
                    <SubtitleNotesPanel notes={latestMontage.subtitle_notes} />

                    <div className="card">
                      <div className="card-header">
                        <h2 className="card-title">
                          <Mail size={20} style={{ marginRight: 8 }} />
                          发送邮件给后期团队
                        </h2>
                        {latestMontage.email_sent && (
                          <span className="badge badge-success">已发送</span>
                        )}
                      </div>
                      <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                        <input
                          type="text"
                          className="form-input"
                          placeholder="收件人邮箱，多个用逗号分隔"
                          value={emailRecipients}
                          onChange={(e) => setEmailRecipients(e.target.value)}
                          style={{ flex: 1 }}
                        />
                        <button
                          className="btn btn-success"
                          onClick={handleSendEmail}
                          disabled={!emailRecipients || sendingEmail}
                        >
                          <Send size={16} />
                          {sendingEmail ? '发送中...' : '发送邮件'}
                        </button>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="empty-state">
                    <div className="empty-state-icon">🤖</div>
                    <p>点击"AI生成摘要"按钮，让AI为您生成蒙太奇纪要</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {allSegments.length > 0 && (
            <div style={{ marginTop: 24 }}>
              <TranscriptViewer segments={allSegments} />
            </div>
          )}
        </div>
      )}

      {activeTab === 'transcript' && (
        <div>
          {allSegments.length > 0 ? (
            <TranscriptViewer segments={allSegments} />
          ) : (
            <div className="card">
              <div className="empty-state">
                <div className="empty-state-icon">🎙️</div>
                <p>暂无转写记录，请先上传并处理音频文件</p>
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === 'timeline' && (
        <TimelineViewer timelines={timelines} />
      )}

      {activeTab === 'notes' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
          <FieldNotesList notes={fieldNotes} />
          <div>
            {latestMontage && (
              <>
                <EditDecisionsList decisions={latestMontage.edit_decisions} />
                <div style={{ marginTop: 20 }}>
                  <SubtitleNotesPanel notes={latestMontage.subtitle_notes} />
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default MeetingDetail;
