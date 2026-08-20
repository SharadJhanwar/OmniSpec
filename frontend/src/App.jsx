import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import { CatalogProvider, useCatalog } from './context/CatalogContext';
import LandingPage from './pages/LandingPage';
import StudioPage from './pages/StudioPage';
import ReviewPage from './pages/ReviewPage';
import SearchPage from './pages/SearchPage';
import IntelligencePage from './pages/IntelligencePage';
import DBOMModal from './components/DBOMModal';
import BatchUploadModal from './components/BatchUploadModal';

function AppShell() {
  const {
    isDbomModalOpen,
    setIsDbomModalOpen,
    dbomData,
    isDbomLoading,
    isUploadOpen,
    setIsUploadOpen,
    handleUploadSuccess
  } = useCatalog();

  return (
    <div className="min-h-screen bg-background text-slate-100 flex flex-col font-sans">
      {/* Modern Responsive Navigation Bar */}
      <Navbar />

      {/* Main Routed Page Container */}
      <main className="max-w-7xl w-full mx-auto px-3 sm:px-6 lg:px-8 py-5 flex-1">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/studio" element={<StudioPage />} />
          <Route path="/review" element={<ReviewPage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/intelligence" element={<IntelligencePage />} />
        </Routes>
      </main>

      {/* Global Data Bill of Materials (DBOM) & Provenance Modal */}
      <DBOMModal
        isOpen={isDbomModalOpen}
        onClose={() => setIsDbomModalOpen(false)}
        dbomData={dbomData}
        isLoading={isDbomLoading}
      />

      {/* Global Batch Upload Modal */}
      <BatchUploadModal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        onUploadSuccess={handleUploadSuccess}
      />
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <CatalogProvider>
        <AppShell />
      </CatalogProvider>
    </BrowserRouter>
  );
}
