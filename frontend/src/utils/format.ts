export const formatTime = (seconds: number): string => {
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);

  if (hrs > 0) {
    return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};

export const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const getSpeakerColorClass = (role?: string): string => {
  switch (role) {
    case '剪辑师':
      return 'speaker-editor';
    case '人类学家':
    case '学者':
      return 'speaker-anthropologist';
    case '导演':
      return 'speaker-director';
    default:
      return '';
  }
};

export const getStatusBadge = (status: string): { text: string; className: string } => {
  switch (status) {
    case 'completed':
      return { text: '已完成', className: 'badge badge-success' };
    case 'summarized':
      return { text: '已生成摘要', className: 'badge badge-success' };
    case 'transcribed':
      return { text: '已转写', className: 'badge badge-info' };
    case 'processing':
      return { text: '处理中', className: 'badge badge-warning' };
    case 'pending':
    default:
      return { text: '待处理', className: 'badge badge-gray' };
  }
};
