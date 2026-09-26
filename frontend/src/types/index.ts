export interface Meeting {
  id: number;
  title: string;
  description?: string;
  created_at: string;
  status: string;
}

export interface FieldNote {
  id: number;
  meeting_id: number;
  content: string;
  timestamp?: number;
  author?: string;
  created_at: string;
}

export interface TimelineClip {
  id: number;
  timeline_id: number;
  clip_name: string;
  start_time: number;
  end_time: number;
  source_file?: string;
  notes?: string;
}

export interface Timeline {
  id: number;
  meeting_id: number;
  title: string;
  created_at: string;
  clips: TimelineClip[];
}

export interface SpeakerSegment {
  id: number;
  transcript_id: number;
  speaker_label: string;
  speaker_role?: string;
  start_time: number;
  end_time: number;
  text: string;
}

export interface Transcript {
  id: number;
  meeting_id: number;
  audio_file_id?: number;
  full_text: string;
  created_at: string;
  segments: SpeakerSegment[];
}

export interface EditDecision {
  priority: 'high' | 'medium' | 'low';
  category: string;
  description: string;
  timeline_reference?: string;
}

export interface SubtitleNotes {
  terms_explanation: string[];
  cultural_notes: string[];
  speaker_identities: string[];
  sensitive_content: string[];
}

export interface MontageNote {
  id: number;
  meeting_id: number;
  content: string;
  edit_decisions: string;
  subtitle_notes: string;
  created_at: string;
  email_sent: boolean;
  email_recipients?: string;
}

export interface MontageNoteDetail {
  id: number;
  meeting_id: number;
  content: string;
  edit_decisions: EditDecision[];
  subtitle_notes: SubtitleNotes;
  created_at: string;
  email_sent: boolean;
  email_recipients?: string;
}

export interface AudioFile {
  id: number;
  meeting_id: number;
  filename: string;
  file_path: string;
  duration?: number;
  created_at: string;
}

export interface ProcessResult {
  success: boolean;
  message: string;
  data?: any;
}
