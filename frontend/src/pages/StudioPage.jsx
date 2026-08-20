import React, { useState } from 'react';
import DashboardStats from '../components/DashboardStats';
import SingleSkuSandbox from '../components/SingleSkuSandbox';
import AgentSwarmVisualizer from '../components/AgentSwarmVisualizer';
import Grid252 from '../components/Grid252';
import HITLReviewModal from '../components/HITLReviewModal';
import { useCatalog } from '../context/CatalogContext';
import { useNavigate } from 'react-router-dom';

export default function StudioPage() {
  const {
    items,
    activeItem,
    setActiveItem,
    activeTraces,
    isEnriching,
    avgConfidence,
    hitlCount,
    handleSingleEnrichSuccess,
    handleOpenDbom,
    handleSaveReviewedItem
  } = useCatalog();

  const [selectedReviewItem, setSelectedReviewItem] = useState(null);
  const navigate = useNavigate();

  const handleOpenReview = (item) => {
    setActiveItem(item);
    setSelectedReviewItem(item);
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Metric Cards */}
      <DashboardStats
        totalItems={items.length}
        avgConfidence={avgConfidence}
        violationsCount={0}
        hitlQueueCount={hitlCount}
      />

      {/* Live Single-SKU Sandbox */}
      <SingleSkuSandbox
        onEnrichSuccess={handleSingleEnrichSuccess}
        onInspectDbomClick={handleOpenDbom}
        onOpenCompatibility={() => navigate('/intelligence')}
        onOpenParametricSearch={() => navigate('/search')}
        onOpenFamilies={() => navigate('/intelligence')}
      />

      {/* 9-Agent LangGraph Swarm Visualizer */}
      <AgentSwarmVisualizer
        activeItem={activeItem}
        isEnriching={isEnriching}
        traces={activeTraces}
      />

      {/* 252-Column Data Grid Table */}
      <Grid252
        items={items}
        onSelectReviewItem={handleOpenReview}
        onInspectDbom={handleOpenDbom}
      />

      {/* HITL Quick Modal if clicked from grid */}
      {selectedReviewItem && (
        <HITLReviewModal
          item={selectedReviewItem}
          onClose={() => setSelectedReviewItem(null)}
          onSave={handleSaveReviewedItem}
        />
      )}
    </div>
  );
}
