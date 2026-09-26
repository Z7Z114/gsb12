import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Video, Mic, FileText, Send } from 'lucide-react';

const Header: React.FC = () => {
  const location = useLocation();

  return (
    <header style={{
      background: 'linear-gradient(135deg, #1e40af 0%, #3730a3 100%)',
      color: 'white',
      padding: '16px 24px',
      boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
    }}>
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        <Link to="/" style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          textDecoration: 'none',
          color: 'white',
        }}>
          <Video size={32} />
          <div>
            <h1 style={{ fontSize: '20px', fontWeight: 700, margin: 0 }}>
              民族志纪录片剪辑会议系统
            </h1>
            <p style={{ fontSize: '12px', opacity: 0.8, margin: 0 }}>
              Ethnographic Documentary Montage System
            </p>
          </div>
        </Link>

        <div style={{ display: 'flex', gap: '24px', alignItems: 'center' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            fontSize: '13px',
            opacity: 0.9,
          }}>
            <Mic size={16} />
            <span>说话人识别</span>
          </div>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            fontSize: '13px',
            opacity: 0.9,
          }}>
            <FileText size={16} />
            <span>AI转写摘要</span>
          </div>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            fontSize: '13px',
            opacity: 0.9,
          }}>
            <Send size={16} />
            <span>邮件通知</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
