import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import DashboardStats from './components/DashboardStats';
import SingleSkuSandbox from './components/SingleSkuSandbox';
import AgentSwarmVisualizer from './components/AgentSwarmVisualizer';
import Grid252 from './components/Grid252';
import HITLReviewModal from './components/HITLReviewModal';
import BatchUploadModal from './components/BatchUploadModal';

// Initial Ground-Truth Seed Items for instant interactive showcase
const SEED_ITEMS = [
  {
    "Mfg_Part_Num": "PDSH4816AF",
    "Part_Desc": "PDSH4816AF Dishwasher SS - Display Only 24 in W x 24.25 in D 120V 15A 47dBA",
    "Part_Manuf": "Appliance Dealers Cooperative (APPDE)",
    "MANUFACTURER_NAME": "Rheem Manufacturing",
    "BRAND_NAME": "FRIGIDAIRE®",
    "Classpath": "Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers",
    "SHORT_DESC": "FRIGIDAIRE® Professional Series PDSH4816AF Dishwasher With CleanBoost™, Leg Mounting, 5-Wash Cycle, Stainless Steel",
    "INVOICE_DESC": "DISHWASHER LEG 5 SST 120V 15A 50-1/4IN",
    "MOBILE_DESC": "Rheem Manufacturing FRIGIDAIRE, Dishwasher, Professional Series, PDSH4816AF",
    "LENGTH": "24-1/4",
    "WIDTH": "24",
    "HEIGHT": "33-7/16",
    "Product Image": "FRIGIDAIRE_PDSH4816AF.jpg",
    "Specification Sheet": "FRIGIDAIRE_PDSH4816AF_Specification_Sheet.pdf",
    _confidence: 1.0
  },
  {
    "Mfg_Part_Num": "WDTS7024RZ",
    "Part_Desc": "WDTS7024RZ Dishwasher SS - Display Only 120V 10A 41DBA",
    "Part_Manuf": "Appliance Dealers Cooperative (APPDE)",
    "MANUFACTURER_NAME": "Whirlpool Corporation",
    "BRAND_NAME": "Whirlpool®",
    "Classpath": "Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers",
    "SHORT_DESC": "Whirlpool® Eco Series WDTS7024RZ Dishwasher, Built-in Mounting, Stainless Steel, Stainless Steel",
    "INVOICE_DESC": "DISHWASHER BLTLN SST SST 120V 10A 41DBA",
    "MOBILE_DESC": "Whirlpool, Dishwasher, Eco Series, WDTS7024RZ, Built-in Mounting",
    "LENGTH": "22-5/8",
    "WIDTH": "23-7/8",
    "HEIGHT": "33-7/16",
    "Product Image": "WHIRLPOOL_WDTS7024RZ.jpg",
    "Specification Sheet": "WHIRLPOOL_WDTS7024RZ_Specification_Sheet.pdf",
    _confidence: 1.0
  },
  {
    "Mfg_Part_Num": "558213",
    "Part_Desc": "9.5A19/LED/827/FR/P/ND 4/2FB LED A19 60W Equivalent 2700K Medium Base 2PK",
    "Part_Manuf": "Phillips Lighting (5831)",
    "MANUFACTURER_NAME": "Signify North America Corporation",
    "BRAND_NAME": "Philips®",
    "Classpath": "Lighting & Electrical>Light Bulbs & Lamps>LED Light Bulbs",
    "SHORT_DESC": "Philips® 558213 LED Light Bulb, A19 Shape, 2700 K, Medium E26 Base",
    "INVOICE_DESC": "LED A19 60 27K MED 558213",
    "MOBILE_DESC": "Signify North America Corporation Philips, LED Light Bulb, A19 LED Lamp, 558213",
    "Product Image": "PHILIPS_558213.jpg",
    "Specification Sheet": "PHILIPS_558213_Specification_Sheet.pdf",
    _confidence: 1.0
  },
  {
    "Mfg_Part_Num": "DCS361B",
    "Part_Desc": "DCS361B DEWALT 20V MAX 7-1/4 IN Cordless Sliding Miter Saw Brushless",
    "Part_Manuf": "Black & Decker/dewlt (2585)",
    "MANUFACTURER_NAME": "Stanley Black & Decker Inc",
    "BRAND_NAME": "DEWALT®",
    "Classpath": "Tools & Instruments>Power Tools>Saws & Blades>Circular & Miter Saws",
    "SHORT_DESC": "DEWALT® MAX* DCS361B Power Saw, Brushless Motor",
    "INVOICE_DESC": "SAW MAX* 20V BL DCS361B",
    "MOBILE_DESC": "Stanley Black & Decker Inc DEWALT, Power Saw, Cordless Tool, DCS361B",
    "Product Image": "DEWALT_DCS361B.jpg",
    "Specification Sheet": "DEWALT_DCS361B_Specification_Sheet.pdf",
    _confidence: 0.98
  },
  {
    "Mfg_Part_Num": "49-94-0013",
    "Part_Desc": "49-94-0013 Milw 5\"x.045\"x7/8\" Metal Cut Off Disc",
    "Part_Manuf": "Milwaukee Accessory (4031)",
    "MANUFACTURER_NAME": "Milwaukee Electric Tool Corporation",
    "BRAND_NAME": "Milwaukee®",
    "Classpath": "Abrasives & Polishing>Cut-Off & Grinding Wheels>Cut-Off Wheels",
    "SHORT_DESC": "Milwaukee® Performance+ 49-94-0013 5 in x .045 in x 7/8 in Metal Cut-Off Disc",
    "INVOICE_DESC": "DISC CUT OFF 5X.045X7/8 MTL",
    "MOBILE_DESC": "Milwaukee Electric Tool Corporation Milwaukee, Metal Cut-Off Disc, 49-94-0013",
    "LENGTH": "5",
    "WIDTH": ".045",
    "HEIGHT": "7/8",
    "Product Image": "MILWAUKEE_49-94-0013.jpg",
    "Specification Sheet": "MILWAUKEE_49-94-0013_Specification_Sheet.pdf",
    _confidence: 0.98
  },
  {
    "Mfg_Part_Num": "1513720",
    "Part_Desc": "1nx6-16' Honey Grove Grooved - Trex Enhance Naturals Decking",
    "Part_Manuf": "Boise Cascade Building Materials (BOICA)",
    "MANUFACTURER_NAME": "Trex Company Inc",
    "BRAND_NAME": "Trex®",
    "Classpath": "Building Materials>Decking & Railing>Decking Boards",
    "SHORT_DESC": "Trex® Enhance Naturals 1513720 Decking Board, Composite Wood",
    "INVOICE_DESC": "DECKING BOARD 1X6 16FT HONEY GROVE",
    "MOBILE_DESC": "Trex Company Inc Trex, Decking Board, Enhance Naturals, 1513720",
    "LENGTH": "16",
    "WIDTH": "6",
    "HEIGHT": "1",
    "Product Image": "TREX_1513720.jpg",
    "Specification Sheet": "TREX_1513720_Specification_Sheet.pdf",
    _confidence: 1.0
  }
];

export default function App() {
  const [items, setItems] = useState(SEED_ITEMS);
  const [activeItem, setActiveItem] = useState(SEED_ITEMS[0]);
  const [activeTraces, setActiveTraces] = useState([]);
  const [isEnriching, setIsEnriching] = useState(false);
  const [selectedReviewItem, setSelectedReviewItem] = useState(null);
  const [isUploadOpen, setIsUploadOpen] = useState(false);

  // Load server catalog on initial mount
  useEffect(() => {
    fetch('/api/v1/catalog?page=1&page_size=50')
      .then(res => res.json())
      .then(data => {
        if (data && data.items && data.items.length > 0) {
          const loaded = data.items.map(it => ({
            ...it,
            _confidence: 1.0,
            _needs_hitl: false
          }));
          setItems(loaded);
          setActiveItem(loaded[0]);
        }
      })
      .catch(err => console.log('Using initial seed items:', err));
  }, []);

  const handleExportCSV = () => {
    if (items.length === 0) return;
    const keys = Object.keys(items[0]).filter(k => !k.startsWith('_'));
    const rows = [
      keys.join(','),
      ...items.map(item => keys.map(k => `"${(item[k] || '').toString().replace(/"/g, '""')}"`).join(','))
    ];
    const blob = new Blob([rows.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', 'OmniSpec_Delivery_Enriched_252.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleExportExcel = async () => {
    try {
      const response = await fetch('/api/v1/enrich/export-excel', {
        method: 'POST'
      });
      if (!response.ok) {
        throw new Error(`Excel export failed with status: ${response.status}`);
      }
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', 'OmniSpec_Enriched_1000_Catalog_Master_252.xlsx');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      console.error('Error downloading excel:', err);
    }
  };

  const handleSaveReviewedItem = (updatedItem) => {
    const updatedMpn = updatedItem.Mfg_Part_Num || updatedItem.mfg_part_num;
    setItems(prev => prev.map(item => {
      const currentMpn = item.Mfg_Part_Num || item.mfg_part_num;
      return currentMpn === updatedMpn ? updatedItem : item;
    }));
    setActiveItem(updatedItem);
  };

  const handleUploadSuccess = (newRecords, filename) => {
    if (newRecords && newRecords.length > 0) {
      setItems(prev => [...newRecords, ...prev]);
      setActiveItem(newRecords[0]);
    }
  };

  const handleSingleEnrichSuccess = (enrichedItem, traces) => {
    setItems(prev => [enrichedItem, ...prev]);
    setActiveItem(enrichedItem);
    setActiveTraces(traces);
  };

  const handleOpenReview = (item) => {
    setActiveItem(item);
    setSelectedReviewItem(item);
  };

  const avgConfidence = items.reduce((acc, it) => acc + (it._confidence !== undefined ? it._confidence : 1.0), 0) / items.length;
  const hitlCount = items.filter(it => (it._confidence !== undefined ? it._confidence : 1.0) < 0.85).length;

  return (
    <div className="min-h-screen bg-background text-slate-100 flex flex-col">
      {/* Top Navigation */}
      <Navbar
        onUploadClick={() => setIsUploadOpen(true)}
        onExportClick={handleExportCSV}
        onExportExcelClick={handleExportExcel}
        totalRows={items.length}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
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
        />
      </main>

      {/* HITL Review Modal */}
      {selectedReviewItem && (
        <HITLReviewModal
          item={selectedReviewItem}
          onClose={() => setSelectedReviewItem(null)}
          onSave={handleSaveReviewedItem}
        />
      )}

      {/* Batch Upload Modal */}
      <BatchUploadModal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        onUploadSuccess={handleUploadSuccess}
      />
    </div>
  );
}
