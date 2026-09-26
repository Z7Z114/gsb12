import axios from 'axios';
import {
  Meeting,
  FieldNote,
  Timeline,
  Transcript,
  MontageNote,
  MontageNoteDetail,
  AudioFile,
  ProcessResult,
  MeetingCreate,
  FieldNoteCreate,
  TimelineCreate,
  SendEmailRequest
} from '../types';

const API_BASE = '/api/v1/meetings';

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const meetingApi = {
  getMeetings: (): Promise<Meeting[]> =>
    api.get('/meetings').then(res => res.data),

  getMeeting: (id: number): Promise<Meeting> =>
    api.get(`/meetings/${id}`).then(res => res.data),

  createMeeting: (data: any): Promise<Meeting> =>
    api.post('/meetings', data).then(res => res.data),

  uploadAudio: (meetingId: number, file: File): Promise<AudioFile> => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`/meetings/${meetingId}/upload-audio`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then(res => res.data);
  },

  getAudioFiles: (meetingId: number): Promise<AudioFile[]> =>
    api.get(`/meetings/${meetingId}/audio`).then(res => res.data),

  processAudio: (meetingId: number, audioFileId?: number): Promise<ProcessResult> =>
    api.post('/meetings/process-audio', { meeting_id: meetingId, audio_file_id: audioFileId }).then(res => res.data),

  getTranscripts: (meetingId: number): Promise<Transcript[]> =>
    api.get(`/meetings/${meetingId}/transcripts`).then(res => res.data),

  getTranscript: (id: number): Promise<Transcript> =>
    api.get(`/transcripts/${id}`).then(res => res.data),

  createFieldNote: (data: any): Promise<FieldNote> =>
    api.post('/meetings/0/field-notes', data).then(res => res.data),

  getFieldNotes: (meetingId: number): Promise<FieldNote[]> =>
    api.get(`/meetings/${meetingId}/field-notes`).then(res => res.data),

  createTimeline: (data: any): Promise<Timeline> =>
    api.post('/meetings/0/timelines', data).then(res => res.data),

  getTimelines: (meetingId: number): Promise<Timeline[]> =>
    api.get(`/meetings/${meetingId}/timelines`).then(res => res.data),

  generateSummary: (meetingId: number): Promise<ProcessResult> =>
    api.post('/meetings/generate-summary', { meeting_id: meetingId }).then(res => res.data),

  getMontageNotes: (meetingId: number): Promise<MontageNote[]> =>
    api.get(`/meetings/${meetingId}/montage-notes`).then(res => res.data),

  getMontageNoteDetail: (id: number): Promise<MontageNoteDetail> =>
    api.get(`/montage-notes/${id}`).then(res => res.data),

  sendEmail: (data: any): Promise<ProcessResult> =>
    api.post('/send-email', data).then(res => res.data),

  fullProcess: (meetingId: number): Promise<ProcessResult> =>
    api.post('/meetings/full-process', { meeting_id: meetingId }).then(res => res.data),
};
