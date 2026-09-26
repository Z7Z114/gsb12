import React, { useState } from 'react';
import { Scissors, Clock, AlertCircle, CheckCircle, MinusCircle } from 'lucide-react';
import { EditDecision } from '../types';

interface EditDecisionsListProps {
  decisions: EditDecision[];
}

const EditDecisionsList: React.FC<EditDecisionsListProps> = ({ decisions }) => {
  const [filter, setFilter] = useState<string>('all');

  const filteredDecisions = filter === 'all'
    ? decisions
    : decisions.filter(d => d.priority === filter);

  const priorityConfig = {
    high: { icon: AlertCircle, color: '#dc2626' },
    medium: { icon: MinusCircle, color: '#d97706' },
    low: { icon: CheckCircle, color: '#059669' },
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">
          <Scissors size={20} style={{ marginRight: 8 }} />
          剪辑决定清单
        </h2>
        <div style={{ display: 'flex', gap: 8 }}>
          <button
            className={`btn ${filter === 'all' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ padding: '6px 12px', fontSize: '12px' }}
            onClick={() => setFilter('all')}
          >
            全部 ({decisions.length})
          </button>
          <button
            className={`btn ${filter === 'high' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ padding: '6px 12px', fontSize: '12px' }}
            onClick={() => setFilter('high')}
          >
            高 ({decisions.filter(d => d.priority === 'high').length})
          </button>
          <button
            className={`btn ${filter === 'medium' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ padding: '6px 12px', fontSize: '12px' }}
            onClick={() => setFilter('medium')}
          >
            中 ({decisions.filter(d => d.priority === 'medium').length})
          </button>
          <button
            className={`btn ${filter === 'low' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ padding: '6px 12px', fontSize: '12px' }}
            onClick={() => setFilter('low')}
          >
            低 ({decisions.filter(d => d.priority === 'low').length})
          </button>
        </div>
      </div>

      <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
        {filteredDecisions.map((decision, index) => {
          const config = priorityConfig[decision.priority];
          const Icon = config.icon;

          return (
            <div
              key={index}
              className={`edit-decision priority-${decision.priority}`}
            >
              <div className="edit-decision-header">
                <span className="edit-decision-category">
                  {decision.category}
                </span>
                <span className={`edit-decision-priority`}>
                  <Icon size={12} style={{ marginRight: 4, verticalAlign: 'middle' }} />
                  {decision.priority === 'high' ? '高优先级' :
                   decision.priority === 'medium' ? '中优先级' : '低优先级'}
                </span>
              </div>
              <div className="edit-decision-description">
                {decision.description}
              </div>
              {decision.timeline_reference && (
                <div className="edit-decision-timeline">
                  <Clock size={12} style={{ marginRight: 4, verticalAlign: 'middle' }} />
                  时间线参考: {decision.timeline_reference}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default EditDecisionsList;
