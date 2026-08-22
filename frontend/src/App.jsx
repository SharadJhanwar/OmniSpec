import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import TopHeader from './components/TopHeader';
import LandingNavbar from './components/LandingNavbar';
import { CatalogProvider, useCatalog } from './context/CatalogContext';
import DashboardPage from './pages/DashboardPage';
import LandingPage from './pages/LandingPage';
import StudioPage from './pages/StudioPage';
import ReviewPage from './pages/ReviewPage';
import SearchPage from './pages/SearchPage';
import IntelligencePage from './pages/IntelligencePage';
import LedgerPage from './pages/LedgerPage';
import DBOMModal from './components/DBOMModal';
import BatchUploadModal from './components/BatchUploadModal';

function AppShell() {
  const location = useLocation();
  const {
    isDbomModalOpen,
    setIsDbomModalOpen,
    dbomData,
    isDbomLoading,
    isUploadOpen,
    setIsUploadOpen,
    handleUploadSuccess
  } = useCatalog();

  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Check if current route is the Landing Page
  const isLandingPage = location.pathname === '/' || location.pathname === '/about' || location.pathname === '/help';

  if (isLandingPage) {
    return (
      <div className="min-h-screen bg-[#0B0F17] text-slate-100 flex flex-col font-sans">
        {/* Full-Width Clean Landing Navbar (No Sidebar) */}
        <LandingNavbar />

        {/* Main Landing Content */}
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/about" element={<LandingPage />} />
            <Route path="/help" element={<LandingPage />} />
          </Routes>
        </main>

        {/* Global Batch Upload Modal */}
        <BatchUploadModal
          isOpen={isUploadOpen}
          onClose={() => setIsUploadOpen(false)}
          onUploadSuccess={handleUploadSuccess}
        />
      </div>
    );
  }

  // Workspace Shell with Left Sidebar & Top Header
  return (
    <div className="h-screen w-screen overflow-hidden bg-slate-950 text-slate-100 flex flex-row font-sans">
      
      {/* Left Vertical Sidebar Navigation */}
      <Sidebar
        isCollapsed={isSidebarCollapsed}
        setIsCollapsed={setIsSidebarCollapsed}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden min-w-0 bg-[#0B0F17]">
        
        {/* Top Stream Status Header */}
        <TopHeader
          isMobileMenuOpen={isMobileMenuOpen}
          onToggleMobileMenu={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        />

        {/* Routed Pages Container (Scrollable) */}
        <main className="flex-1 overflow-y-auto px-4 sm:px-8 py-6">
          <div className="max-w-[1780px] mx-auto">
            <Routes>
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/overview" element={<DashboardPage />} />
              <Route path="/studio" element={<StudioPage />} />
              <Route path="/search" element={<SearchPage />} />
              <Route path="/discovery" element={<SearchPage />} />
              <Route path="/review" element={<ReviewPage />} />
              <Route path="/audit" element={<ReviewPage />} />
              <Route path="/evidence" element={<DashboardPage />} />
              <Route path="/ledger" element={<LedgerPage />} />
              <Route path="/intelligence" element={<IntelligencePage />} />
              <Route path="/history" element={<DashboardPage />} />
            </Routes>
          </div>
        </main>
      </div>

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
