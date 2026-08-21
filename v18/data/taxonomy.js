/* Canonical V18 taxonomy overlay. Keeps source IDs stable while normalizing navigation. */
(()=>{
  const rows=window.SINERGY_ENTITIES||[];
  for(const x of rows){
    if(x.id?.startsWith('token.')){
      x.domain='Исследования';
      x.subdomain='Tokenomics';
      if(x.id==='token.triple') x.entityType='tokenomics-simulation';
      else x.entityType='tokenomics-r&d';
      x.canonicalClass=x.status==='legacy'?'legacy-token-branch':'experimental-token-branch';
    }
    if(x.id?.startsWith('research.')) x.subdomain=x.subdomain||(
      x.entityType==='market-research'?'Market AI':
      x.entityType==='real-economy-r&d'?'Real Economy R&D':
      x.entityType==='deep-tech-r&d'?'Deep Tech':
      x.entityType==='data-research'?'Data & Macro':'Theory & Methods'
    );
  }
  if(!rows.some(x=>x.id==='archive.v18')) rows.push({
    id:'archive.v18',name:'Top Architecture V18',domain:'Архив',subdomain:'Current Release',
    entityType:'current-release',status:'prototype',evidence:'L3',moneyRole:'provenance',
    summary:'Текущая additive multi-page architecture: shared visual/runtime layer, canonical entity registry, typed graph, passports, Evidence/Repository/Coverage Explorer, Financial OS decomposition and versioned Knowledge Library.',
    href:'../'
  });
})();
