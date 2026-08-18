import React, { useState } from 'react';
import Navbar from './components/Navbar';
import DashboardStats from './components/DashboardStats';
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
  },
  {
    "Mfg_Part_Num": "ADR5117512CS",
    "Part_Desc": "1x12-12' Coastline - Vintage Azek PVC Fascia",
    "Part_Manuf": "Parksite (6151)",
    "MANUFACTURER_NAME": "The AZEK Company LLC",
    "BRAND_NAME": "AZEK®",
    "Classpath": "Building Materials>Decking & Railing>Fascia Boards",
    "SHORT_DESC": "AZEK® Vintage ADR5117512CS Fascia Board, Composite PVC",
    "INVOICE_DESC": "FASCIA BOARD 1X12 12FT COASTLINE",
    "MOBILE_DESC": "The AZEK Company LLC AZEK, Fascia Board, Vintage, ADR5117512CS",
    "LENGTH": "12",
    "WIDTH": "12",
    "HEIGHT": "1",
    "Product Image": "AZEK_ADR5117512CS.jpg",
    "Specification Sheet": "AZEK_ADR5117512CS_Specification_Sheet.pdf",
    _confidence: 0.98
  },
  {
    "Mfg_Part_Num": "3MABR-7100075678",
    "Part_Desc": "3M 775L Stikit Film P150 - Cubitron II 50 Disc/Box",
    "Part_Manuf": "Jam Industrial Supply LLC (JAMIN)",
    "MANUFACTURER_NAME": "3M Co",
    "BRAND_NAME": "3M™",
    "Classpath": "Abrasives & Polishing>Sandpaper & Abrasive Pads>Sanding Discs",
    "SHORT_DESC": "3M™ Cubitron™ II 7100075678 Sanding Film Disc, P150 Grit",
    "INVOICE_DESC": "DISC SANDING FILM P150 50PK",
    "MOBILE_DESC": "3M Co 3M, Sanding Disc, Cubitron II, 7100075678",
    "LENGTH": "5",
    "WIDTH": "5",
    "HEIGHT": "",
    "Product Image": "3M_7100075678.jpg",
    "Specification Sheet": "3M_7100075678_Specification_Sheet.pdf",
    _confidence: 0.98
  }
];

export default function App() {
  const [items, setItems] = useState(SEED_ITEMS);
  const [activeItem, setActiveItem] = useState(SEED_ITEMS[0]);
  const [selectedReviewItem, setSelectedReviewItem] = useState(null);
  const [isUploadOpen, setIsUploadOpen] = useState(false);

  const handleExportCSV = () => {
    // Generate CSV string from items
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

  const handleSaveReviewedItem = (updatedItem) => {
    setItems(prev => prev.map(item => 
      (item.Mfg_Part_Num === updatedItem.Mfg_Part_Num || item.mfg_part_num === updatedItem.mfg_part_num) 
        ? updatedItem 
        : item
    ));
    setActiveItem(updatedItem);
  };

  const handleUploadSuccess = (filename) => {
    // In demo, confirm upload
    console.log(`Uploaded ${filename}`);
  };

  const avgConfidence = items.reduce((acc, it) => acc + (it._confidence || 1.0), 0) / items.length;
  const hitlCount = items.filter(it => (it._confidence || 1.0) < 0.85).length;

  return (
    <div className="min-h-screen bg-background text-slate-100 flex flex-col">
      {/* Top Navigation */}
      <Navbar
        onUploadClick={() => setIsUploadOpen(true)}
        onExportClick={handleExportCSV}
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

        {/* 9-Agent LangGraph Swarm Visualizer */}
        <AgentSwarmVisualizer
          activeItem={activeItem}
          isEnriching={false}
        />

        {/* 252-Column Data Grid Table */}
        <Grid252
          items={items}
          onSelectReviewItem={(item) => {
            setActiveItem(item);
            setSelectedReviewItem(item);
          }}
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
