import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiUrl } from '../config/api';

const CatalogContext = createContext(null);

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
    _confidence: 1.0,
    _needs_hitl: false
  },
  {
    "Mfg_Part_Num": "49-94-0101",
    "Part_Desc": "49-94-0101 Milw 4-1/2\"x.045\"x7/8\" Perform+ Metal Cut Off Disc 10pc",
    "Part_Manuf": "Milwaukee Accessory (4031)",
    "MANUFACTURER_NAME": "Milwaukee Tool",
    "BRAND_NAME": "Milwaukee®",
    "Classpath": "Abrasives & Polishing>Cut-Off & Grinding Wheels>Cut-Off Wheels",
    "SHORT_DESC": "Milwaukee® Performance Plus™ 49-94-0101 Cut-Off Disc, 4-1/2 in D, 0.045 in THK, 7/8 in Arbor, Aluminum Oxide Abrasive",
    "INVOICE_DESC": "CUT OFF WHEEL 4-1/2IN X .045IN X 7/8IN",
    "MOBILE_DESC": "Milwaukee Tool Milwaukee, Cut-Off Disc, Performance Plus, 49-94-0101",
    "DIAMETER": "4-1/2",
    "THICKNESS": ".045",
    "ARBOR_SIZE": "7/8",
    "Product Image": "Milwaukee_49-94-0101.jpg",
    "Specification Sheet": "Milwaukee_49-94-0101_Specification_Sheet.pdf",
    _confidence: 1.0,
    _needs_hitl: false
  },
  {
    "Mfg_Part_Num": "558213",
    "Part_Desc": "9.5A19/LED/827/FR/P/ND 4/2FB LED A19 60W Equivalent 2700K Medium Base 2PK",
    "Part_Manuf": "Phillips Lighting (5831)",
    "MANUFACTURER_NAME": "Philips Lighting",
    "BRAND_NAME": "Philips®",
    "Classpath": "Lighting & Electrical>Light Bulbs & Lamps>LED Light Bulbs",
    "SHORT_DESC": "Philips® 558213 LED Light Bulb, A19 Shape, 2700 K, Medium E26 Base, 60 W Equivalent, 9.5 W, 800 Lumens",
    "INVOICE_DESC": "LED BULB A19 9.5W 2700K E26 800LM 2PK",
    "MOBILE_DESC": "Philips Lighting Philips, LED Light Bulb, 558213, A19 9.5W 2700K",
    "VOLTS": "120",
    "WATTS": "9.5",
    "BASE_TYPE": "Medium (E26)",
    "Product Image": "Philips_558213.jpg",
    "Specification Sheet": "Philips_558213_Specification_Sheet.pdf",
    _confidence: 1.0,
    _needs_hitl: false
  },
  {
    "Mfg_Part_Num": "CPLG-38-BRS",
    "Part_Desc": "3/8 CPLG BRS 150# Female NPT Coupler",
    "Part_Manuf": "Jam Industrial Supply LLC (JAMIN)",
    "MANUFACTURER_NAME": "Mueller Industries",
    "BRAND_NAME": "Mueller Industries®",
    "Classpath": "Plumbing & Pumps>Pipe Fittings>Couplings",
    "SHORT_DESC": "Mueller Industries® 3/8 in Nominal Pipe Coupling, Brass Material, Class 150#, Threaded Female NPT Connection",
    "INVOICE_DESC": "COUPLING 3/8IN BRASS 150# FNPT",
    "MOBILE_DESC": "Mueller Industries Mueller, Pipe Coupling, CPLG-38-BRS, 3/8 in Brass",
    "MATERIAL": "Brass",
    "PRESSURE_CLASS": "150#",
    "THREAD_TYPE": "FNPT",
    "Product Image": "Mueller_CPLG-38-BRS.jpg",
    "Specification Sheet": "Mueller_CPLG-38-BRS_Specification_Sheet.pdf",
    _confidence: 1.0,
    _needs_hitl: false
  }
];

export function CatalogProvider({ children }) {
  const [items, setItems] = useState(SEED_ITEMS);
  const [activeItem, setActiveItem] = useState(SEED_ITEMS[0]);
  const [activeTraces, setActiveTraces] = useState([]);
  const [isEnriching, setIsEnriching] = useState(false);
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [activeBatchName, setActiveBatchName] = useState(null);

  // DBOM Modal State
  const [isDbomModalOpen, setIsDbomModalOpen] = useState(false);
  const [dbomData, setDbomData] = useState(null);
  const [isDbomLoading, setIsDbomLoading] = useState(false);

  // Load backend catalog on mount defensively
  useEffect(() => {
    fetch(apiUrl('/api/v1/catalog?page=1&page_size=100'))
      .then(res => res.json())
      .then(data => {
        if (data && Array.isArray(data.items) && data.items.length > 0) {
          const loaded = data.items.filter(Boolean).map(it => ({
            ...it,
            _confidence: it._confidence !== undefined ? it._confidence : 1.0,
            _needs_hitl: Boolean(it._needs_hitl)
          }));
          if (loaded.length > 0) {
            setItems(loaded);
            setActiveItem(loaded[0]);
          }
        }
      })
      .catch(err => console.log('Using default catalog seed:', err));
  }, []);

  const UNILOG_DELIVERY_HEADERS = [
    "MFR URL", "Ref URL 1", "Ref URL 2", "Ref URL 3", "Ref URL 4", "Ref URL 5",
    "PART_NUMBER", "Dept", "Class", "Fine", "SKU - MY_PART_NUMBER", "Mfg_Part_Num", "Part_Desc",
    "E1_Brand", "Unilog_Brand", "DIB_Brand", "Part_Manuf", "MANUFACTURER_NAME", "BRAND_NAME",
    "TRADE_NAME", "MANUFACTURER_PART_NUMBER", "ALTERNATE_PART_NUMBER", "Classpath",
    "MOBILE_DESC", "INVOICE_DESC", "SHORT_DESC", "LONG_DESC1", "RETAIL_DESC", "MARKETING_DESCRIPTION",
    ...Array.from({ length: 20 }, (_, i) => `ITEM_FEATURES_${i + 1}`),
    "With", "Standard/Approvals", "Prop 65", "Application", "Includes", "Product Name",
    ...Array.from({ length: 50 }, (_, i) => [
      `ATTRIBUTE_LABEL ${i + 1}`,
      `ATTRIBUTE_VALUE ${i + 1}`,
      `ATTRIBUTE_UOM ${i + 1}`
    ]).flat(),
    "UPC", "EAN", "GTIN", "UNSPSC", "Warranty", "List Price", "Selling Qty", "Selling UOM", "Standard Packaging Information",
    "LENGTH", "LENGTH_UOM", "HEIGHT", "HEIGHT_UOM", "WIDTH", "WIDTH_UOM", "WEIGHT", "WEIGHT_UOM", "VOLUME", "VOLUME_UOM",
    "Product Image", "Alternate Image 1", "Alternate Image 2", "Alternate Image 3", "Alternate Image 4",
    "SDS", "SDS_1", "Warranty Information", "Catalog", "Specification Sheet",
    "Instruction/Installation Manual", "Service Manual", "Owners/User Manual", "Line Drawing", "MTR", "RoHS",
    "Full Engineering Drawing", "Energy Star Guide", "Technical Bulletin", "Submittal", "Compatibility Chart",
    "Size Chart", "Product Label/Insert", "Video Link", "Video Link 1", "Country Of Origin", "Discontinued", "Actual Image (Yes/No)"
  ];

  const handleExportCSV = () => {
    const validItems = (Array.isArray(items) ? items : []).filter(Boolean);
    if (validItems.length === 0) return;
    
    // Use canonical Unilog 252 delivery headers
    const keys = UNILOG_DELIVERY_HEADERS;
    const rows = [
      keys.join(','),
      ...validItems.map(item => keys.map(k => {
        let val = item[k];
        if (val === undefined || val === null) {
          val = (item.attributes && item.attributes[k]) !== undefined ? item.attributes[k] : '';
        }
        return `"${val.toString().replace(/"/g, '""')}"`;
      }).join(','))
    ];
    const cleanStem = activeBatchName ? activeBatchName.replace(/\.[^/.]+$/, "") : "Current_Batch";
    const blob = new Blob([rows.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `OmniSpec_Enriched_${cleanStem}_252.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleExportExcel = async () => {
    const validItems = (Array.isArray(items) ? items : []).filter(Boolean);
    try {
      const response = await fetch(apiUrl('/api/v1/enrich/export-excel'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          items: validItems,
          filename: activeBatchName || "Current_Batch"
        })
      });
      if (!response.ok) {
        throw new Error(`Excel export failed: ${response.status}`);
      }
      const cleanStem = activeBatchName ? activeBatchName.replace(/\.[^/.]+$/, "") : "Current_Batch";
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', `OmniSpec_Enriched_${cleanStem}_252.xlsx`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      console.error('Error downloading excel:', err);
    }
  };

  const handleOpenDbom = async (item) => {
    if (!item) return;
    setIsDbomLoading(true);
    setIsDbomModalOpen(true);
    try {
      const payload = {
        Mfg_Part_Num: item.Mfg_Part_Num || item.mfg_part_num || "",
        Part_Desc: item.Part_Desc || item.part_desc || item.SHORT_DESC || "",
        Part_Manuf: item.Part_Manuf || item.part_manuf || item.MANUFACTURER_NAME || "",
        E1_Brand: item.E1_Brand || "",
        Unilog_Brand: item.Unilog_Brand || item.BRAND_NAME || ""
      };
      const res = await fetch(apiUrl('/api/v1/provenance/dbom'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data.success) {
        setDbomData(data);
      }
    } catch (err) {
      console.error('Error fetching DBOM:', err);
    } finally {
      setIsDbomLoading(false);
    }
  };

  const selectActiveItem = (item) => {
    setActiveItem(item);
    if (item && item._traces) {
      setActiveTraces(item._traces);
    }
  };

  const handleSaveReviewedItem = (updatedItem) => {
    if (!updatedItem) return;
    const updatedMpn = updatedItem.Mfg_Part_Num || updatedItem.mfg_part_num;
    setItems(prev => (Array.isArray(prev) ? prev : []).filter(Boolean).map(item => {
      const currentMpn = item.Mfg_Part_Num || item.mfg_part_num;
      return currentMpn === updatedMpn ? updatedItem : item;
    }));
    selectActiveItem(updatedItem);
  };

  const handleUploadSuccess = (newRecords, filename) => {
    if (Array.isArray(newRecords) && newRecords.length > 0) {
      const valid = newRecords.filter(Boolean);
      // Set catalog to purely the uploaded batch
      setItems(valid);
      setActiveBatchName(filename || "Uploaded_Feed.csv");
      if (valid[0]) {
        selectActiveItem(valid[0]);
      }
    }
  };

  const handleSingleEnrichSuccess = (enrichedItem, traces) => {
    if (!enrichedItem) return;
    setItems(prev => [enrichedItem, ...(Array.isArray(prev) ? prev : []).filter(Boolean)]);
    setActiveItem(enrichedItem);
    setActiveTraces(traces || enrichedItem._traces || []);
  };

  const handleResetCatalog = () => {
    fetch('/api/v1/catalog?page=1&page_size=100')
      .then(res => res.json())
      .then(data => {
        if (data && Array.isArray(data.items) && data.items.length > 0) {
          const loaded = data.items.filter(Boolean).map(it => ({
            ...it,
            _confidence: it._confidence !== undefined ? it._confidence : 1.0,
            _needs_hitl: Boolean(it._needs_hitl)
          }));
          setItems(loaded);
          setActiveBatchName(null);
          if (loaded[0]) selectActiveItem(loaded[0]);
        }
      })
      .catch(err => console.log('Reset catalog error:', err));
  };

  const validItems = (Array.isArray(items) ? items : []).filter(Boolean);
  const avgConfidence = validItems.reduce((acc, it) => acc + (it && it._confidence !== undefined ? it._confidence : 1.0), 0) / Math.max(1, validItems.length);
  const hitlCount = validItems.filter(it => it && ((it._confidence !== undefined ? it._confidence : 1.0) < 0.85 || it._needs_hitl)).length;

  const value = {
    items: validItems,
    setItems,
    activeItem,
    setActiveItem: selectActiveItem,
    activeTraces,
    setActiveTraces,
    isEnriching,
    setIsEnriching,
    isUploadOpen,
    setIsUploadOpen,
    activeBatchName,
    isDbomModalOpen,
    setIsDbomModalOpen,
    dbomData,
    isDbomLoading,
    avgConfidence,
    hitlCount,
    handleExportCSV,
    handleExportExcel,
    handleOpenDbom,
    handleSaveReviewedItem,
    handleUploadSuccess,
    handleSingleEnrichSuccess,
    handleResetCatalog
  };

  return (
    <CatalogContext.Provider value={value}>
      {children}
    </CatalogContext.Provider>
  );
}

export function useCatalog() {
  const context = useContext(CatalogContext);
  if (!context) {
    throw new Error('useCatalog must be used within a CatalogProvider');
  }
  return context;
}
