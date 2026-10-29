# Fase 2 — Inventario de datos (CMS Open Data)

Fecha: 2026-10-21 (actualizado 2026-10-28 con los archivos 12358, 31102, 12355 y 12353)
Sesión: `data_agent` (fase 2 — Exploration)
Análisis: `prueba` — H→ττ, 8 TeV, 2012, canal μτ_h.

> **Nota de reemplazo.** Este documento sustituye al inventario previo, que afirmaba que no
> había ningún dato descargado (inventario sin datos). Aquel estado quedó registrado también en
> `inventario_datos_local.md`, que se conserva como histórico y **no** se modifica. El presente
> inventario refleja los dos archivos ROOT efectivamente descargados y explorados con las tools.

## 1. Archivos descargados

| recid | Archivo | Tamaño oficial (`cms files`) | URI | Estado |
|---|---|---|---|---|
| 12351 | `data/prueba/GluGluToHToTauTau.root` | 196 517 149 B (≈187 MB) | `root://eospublic.cern.ch//eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool/GluGluToHToTauTau.root` | Descargado de nuevo con `cms download --max-bytes 500000000` (sustituye a la copia incompleta de 64 225 280 B que había en el destino). |
| 12352 | `data/prueba/VBF_HToTauTau.root` | 231 849 713 B (≈221 MB) | `root://eospublic.cern.ch//eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool/VBF_HToTauTau.root` | Descargado con `cms download --max-bytes 500000000`. |

Total esperado ≈ 428.4 MB (0.42 GB). Espacio libre en `/` antes de descargar: 950 GB (`df -h`).
Ambos archivos son NanoAOD-like (derived data, formato plano: un solo árbol con ramas de
objetos como `float[]`), por lo que **no requieren CMSSW** para leerse.

Descargas registradas en `analyses/prueba/retrieval_log.md` (tipo `dataset`, una fila por archivo,
fuente `https://opendata.cern.ch/record/12351` y `.../12352`).

## 2. Estructura de los archivos

Ambos archivos presentan **idéntica estructura**:

- Árboles: un único TTree llamado `Events`.
- Eventos leídos por `root summary`: **100 000** en cada archivo (posible tope de la
  herramienta; ver §7).
- Ramas: **69** por árbol (lista completa verificada con `root branches`; ver §3).

## 3. Ramas (lista completa, idéntica en ambos archivos)

Escalares por evento:

- Identificadores: `run` (int32), `luminosityBlock` (uint32), `event` (uint64).
- Disparadores: `HLT_IsoMu24_eta2p1`, `HLT_IsoMu24`, `HLT_IsoMu17_eta2p1_LooseIsoPFTau20` (bool).
- Vértices: `PV_npvs` (int32), `PV_x`, `PV_y`, `PV_z` (float).
- MET: `MET_pt`, `MET_phi`, `MET_sumet`, `MET_significance`, `MET_CovXX`, `MET_CovXY`, `MET_CovYY` (float).
- Conteos de objetos: `nMuon`, `nTau`, `nJet`, `nGenPart` (uint32).

Colecciones de objetos (ramas tipo array):

- Muones: `Muon_pt`, `Muon_eta`, `Muon_phi`, `Muon_mass`, `Muon_charge`, `Muon_pfRelIso03_all`,
  `Muon_pfRelIso04_all`, `Muon_tightId`, `Muon_softId`, `Muon_dxy`, `Muon_dxyErr`, `Muon_dz`,
  `Muon_dzErr`, `Muon_jetIdx`, `Muon_genPartIdx`.
- Taus: `Tau_pt`, `Tau_eta`, `Tau_phi`, `Tau_mass`, `Tau_charge`, `Tau_decayMode`, `Tau_relIso_all`,
  `Tau_jetIdx`, `Tau_genPartIdx`, `Tau_idDecayMode`, `Tau_idIsoRaw`, `Tau_idIsoVLoose`,
  `Tau_idIsoLoose`, `Tau_idIsoMedium`, `Tau_idIsoTight`, `Tau_idAntiEleLoose`, `Tau_idAntiEleMedium`,
  `Tau_idAntiEleTight`, `Tau_idAntiMuLoose`, `Tau_idAntiMuMedium`, `Tau_idAntiMuTight`.
- Jets: `Jet_pt`, `Jet_eta`, `Jet_phi`, `Jet_mass`, `Jet_puId`, `Jet_btag`.
- Generación (MC truth): `GenPart_pt`, `GenPart_eta`, `GenPart_phi`, `GenPart_mass`,
  `GenPart_pdgId`, `GenPart_status`.

No hay ramas de pesos (`genWeight`, `sumw`), ni de MET filters, ni de jet energy corrections.

## 4. Resúmenes numéricos (`root summary`, árbol `Events`)

| Rama | `GluGluToHToTauTau.root` | `VBF_HToTauTau.root` |
|---|---|---|
| `run` | min 1, max 1, media 1, eventos 100 000 | min 1, max 1, media 1, eventos 100 000 |
| `event` | min 1, max 200 000, media 94 626.09, eventos 100 000 | min 201, max 200 000, media 87 202.75, eventos 100 000 |
| `nTau` | min 0, max 45, media 6.666, eventos 100 000 | min 0, max 45, media 7.869, eventos 100 000 |
| `MET_pt` (GeV) | min 0.142, max 649.03, media 32.72, eventos 100 000 | min 0.098, max 609.20, media 47.29, eventos 100 000 |

Muestra de las primeras filas (`root sample ... -n 3`, ramas `run,event,nMuon,nTau,MET_pt`):

- GluGlu: `run=[1,1,1]`, `event=[198601,198602,198603]`, `nMuon=[0,1,0]`, `nTau=[9,4,7]`,
  `MET_pt=[30.89, 91.90, 18.81]` GeV.
- VBF: `run=[1,1,1]`, `event=[1801,1802,1803]`, `nMuon=[2,1,0]`, `nTau=[8,21,4]`,
  `MET_pt=[29.02, 181.00, 42.95]` GeV.

Observaciones: `run` es constante = 1 en ambos archivos (típico de muestra simulada, no de
colisiones); `nTau` media alta (6.7–7.9) y `nMuon` frecuentemente 0 en la muestra, lo que indica
contenido de generación sin selección de canal aplicada.

## 5. ¿Permite el contenido confirmar año y energía?

**No.** No existe ninguna rama de metadatos de año, energía de colisión, `sqrtS`, luminosidad
integrada, campaña de producción ni etiqueta de generador (se revisó la lista completa de ramas:
nada con nombres tipo `year`, `energy`, `sqrtS`, `lumi`, `Generator`, `crossSection`, `sumw`).
Tampoco hay ramas de pesos de MC que permitieran normalizar.

Lo único relacionado con "condiciones de toma de datos" son `run` y `luminosityBlock`, y **no son
informativos**: `run` vale 1 en las 100 000 entradas de ambos archivos, por lo que no identifica
un periodo real de colisiones ni un año.

Además, el tamaño del archivo no prueba nada: la asignación de año/energía solo consta en la
ficha del catálogo (recid 12351/12352, datasets derivados `AOD2NanoAODOutreachTool`) y en la
documentación del registro, no dentro del ROOT. La confirmación de "2012 / 8 TeV" para este
análisis debe apoyarse en la ficha del registro y en la literatura, no en el contenido de los
archivos.

## 6. Idoneidad para el canal μτ_h

Los archivos contienen las ramas necesarias para reconstruir el canal: muones con aislamiento e ID
(`Muon_pt/eta/phi/mass/charge`, `Muon_pfRelIso03_all`, `Muon_tightId`), taus hadrónicos con
discriminación (`Tau_idIso*`, `Tau_idAntiMu/Electron*`, `Tau_decayMode`) y MET. Los triggers
presentes (`HLT_IsoMu24_eta2p1` y `HLT_IsoMu17_eta2p1_LooseIsoPFTau20`) son compatibles con la
selección de un muón + tau_h. **No hay ramas de datos reales (colecciones de colisión) en estos
dos archivos: son muestras de señal simuladas**, por lo que no sirven como estimación de fondo ni
de datos observados.

## 7. Advertencias metodológicas

- `root summary` reporta exactamente 100 000 eventos en ambos archivos; no se pudo verificar con
  las tools permitidas si es el total real del árbol o un tope interno de la herramienta. Los
  resúmenes deben considerarse posiblemente limitados a esa muestra.
- Los tamaños en disco verificados tras la descarga coinciden exactamente con los declarados
  por `cms files` (196 517 149 B y 231 849 713 B); la lectura de ramas escalares (incluida
  `MET_pt`) completó sin errores, lo que descarta una truncación como la de la copia previa
  de 64 225 280 B.
- `event` no es consecutivo ni monótono (`min`=1 con primeras filas en ~198 601 en GluGlu;
  `min`=201 en VBF): no debe usarse como índice fiable sin comprobación adicional.

## 8. Actualización de estado (2026-10-28)

El aviso anterior (2026-10-27) queda **resuelto**: los cuatro archivos autorizados
(12358, 31102, 12355, 12353) se descargaron completos y se exploraron. La verificación de
integridad es tamaño en disco = `size_bytes` de `files_<recid>.json` y ausencia de
`<archivo>.aria2` (detalle en `descargas.json` y `retrieval_log.md`).

| recid | archivo | tamaño en disco (B) | declarado (B) | estado |
|---|---|---|---|---|
| 12358 | `data/prueba_d/Run2012B_TauPlusX.root` | 10 918 632 568 | 10 918 632 568 | completa |
| 31102 | `data/prueba_d/24603428-8B2E-44B3-9E97-B991129E184D.root` | 1 986 138 847 | 1 986 138 847 | completa |
| 12355 | `data/prueba_d/W1JetsToLNu.root` | 10 731 401 995 | 10 731 401 995 | completa |
| 12353 | `data/prueba_d/DYJetsToLL.root` | 9 247 252 629 | 9 247 252 629 | completa |

`data/prueba/DYJetsToLL.root` (81 264 640 B) sigue siendo el **resto incompleto antiguo**:
no es un dato válido, no se ha leído y no se incluye en el inventario (`errores_tools.md` §5).

## 9. `Run2012B_TauPlusX.root` (recid 12358) — datos de colisión 2012B

- **Árbol:** uno, `Events`.
- **Ramas:** **62** (mismo esquema que 12351/12352 **sin** las 7 ramas de generación:
  no hay `nGenPart` ni `GenPart_*`). Tipos: `run` int32, `luminosityBlock` uint32,
  `event` uint64; el resto, igual que la lista de §3.
- **Eventos leídos:** **100 000** (posible tope de la tool; el total real no es verificable).
- **Rango de `run`:** 194 075 – 196 531 (números de run reales de 2012B; coherente con el
  título del dataset, pero la ficha no declara año ni energía). Muestra de las 3 primeras
  filas: `run=[194075,194075,194075]`, `luminosityBlock=[48,48,48]`,
  `event=[14880766,14844046,14872718]`.
- **Resúmenes (100 000 eventos):**

| Rama | min | max | media |
|---|---|---|---|
| `run` | 194 075 | 196 531 | 194 899.735 |
| `event` | 1 285 053 | 1 278 064 342 | 388 795 756.0 |
| `nMuon` | 0 | 14 | 0.8357 |
| `nTau` | 0 | 38 | 5.5773 |
| `MET_pt` (GeV) | 0.0222 | 433.50 | 25.698 |

### 9.1 Triggers: ¿de tau o de muón?

El archivo contiene **exactamente tres ramas de trigger**, y las tres son **de muón**
(no hay ningún trigger puro de tau, ni de doble tau, ni de electrón):

| Rama | Fracción con valor true (100 000 eventos) | Tipo |
|---|---|---|
| `HLT_IsoMu24_eta2p1` | 0.22347 (22.35 %) | muón aislado, single-muon |
| `HLT_IsoMu24` | 0.22398 (22.40 %) | muón aislado, single-muon |
| `HLT_IsoMu17_eta2p1_LooseIsoPFTau20` | 0.27685 (27.69 %) | **muón + tau_h** (cross trigger) |

**Conclusión para μτ_h:** el archivo **sí sirve** para el canal μτ_h en lo que respecta a
trigger: incluye el cross trigger `HLT_IsoMu17_eta2p1_LooseIsoPFTau20`, que es el usado por
la selección μτ_h, además de los single-muon. **No** contiene un trigger de tau puro, pese a
que el primary dataset se llame `TauPlusX`; las decisiones de trigger almacenadas son todas
de muón. Cobertura limitada al periodo **Run2012B** (no todo 2012).

## 10. `24603428-8B2E-44B3-9E97-B991129E184D.root` (recid 31102) — ttbar MC

- **Árbol:** uno, `Events`.
- **Ramas: 928** (conteo exacto: `files/branches_31102.json` tiene 928 claves; la lista
  siguiente las reproduce todas, agrupadas por prefijo). Salida de
  `root branches data/prueba_d/24603428-8B2E-44B3-9E97-B991129E184D.root Events`, guardada en
  `phase2_exploration/files/branches_31102.json` (mismo contenido, formateado una rama por línea
  para poder contarlas).
  - **Identificadores y flags (46):** `run`, `event`, `luminosityBlock`, `CMSSW`,
    `GoodLumisection`, `Dataset_isMC`, `Dataset_ZeroBias`, `Dataset_MinimumBias`, `Dataset_Jet`,
    `Dataset_MultiJet`, `Dataset_JetMETTauMonitor`, `Dataset_Mu`, `Dataset_MuMonitor`,
    `Dataset_DoubleMu`, `Dataset_MuHad`, `Dataset_MuOnia`, `Dataset_Charmonium`,
    `Dataset_BParking`, `Dataset_BTau`, `Dataset_Electron`, `Dataset_DoubleElectron`,
    `Dataset_Photon`, `Dataset_EGMonitor`, `Dataset_MuEG`, `Dataset_METFwd`,
    `Dataset_Commissioning`, `Alsoon_ZeroBias`, `Alsoon_MinimumBias`, `Alsoon_Jet`,
    `Alsoon_MultiJet`, `Alsoon_JetMETTauMonitor`, `Alsoon_Mu`, `Alsoon_MuMonitor`,
    `Alsoon_DoubleMu`, `Alsoon_MuHad`, `Alsoon_MuOnia`, `Alsoon_Charmonium`, `Alsoon_BParking`,
    `Alsoon_BTau`, `Alsoon_Electron`, `Alsoon_DoubleElectron`, `Alsoon_Photon`,
    `Alsoon_EGMonitor`, `Alsoon_MuEG`, `Alsoon_METFwd`, `Alsoon_Commissioning`.
  - **Generación (24):** `nGenPart`, `GenPart_pt`, `GenPart_eta`, `GenPart_phi`,
    `GenPart_mass`, `GenPart_pdgId`, `GenPart_status`, `GenPart_statusFlags`,
    `GenPart_genPartIdMother`, `GenPart_genPartIdxMother`, `GenPart_Id`, `GenPart_isNano`,
    `GenPart_parpdgId`, `GenPart_sparpdgId`, `GenPart_numberOfDaughters`,
    `GenPart_nstchgdaug`, `GenPart_promptFlag`, `GenPart_vx`, `GenPart_vy`, `GenPart_vz`,
    `GenPart_mvx`, `GenPart_mvy`, `GenPart_mvz`, `GenPart_recId`.
  - **GenPV (5):** `GenPV_x`, `GenPV_y`, `GenPV_z`, `GenPV_recIdx`, `GenPV_chmult`.
  - **Tracks (2):** `nTrk`, `nIsoTrack`.
  - **Vértices primarios (9):** `PV_npvs`, `PV_npvsGood`, `PV_chi2`, `PV_ndof`, `PV_score`,
    `PV_x`, `PV_y`, `PV_z`, `nOtherPV`.
  - **Otros vértices (1):** `OtherPV_z`.
  - **PVtx (19):** `nPVtx`, `PVtx_Id`, `PVtx_isMain`, `PVtx_isMainSim`, `PVtx_isGood`,
    `PVtx_isValid`, `PVtx_isFake`, `PVtx_isTrigUnique`, `PVtx_isUnbiased`, `PVtx_ntrk`,
    `PVtx_ntrkfit`, `PVtx_chi2`, `PVtx_ndof`, `PVtx_score`, `PVtx_sumPt`, `PVtx_Rho`,
    `PVtx_x`, `PVtx_y`, `PVtx_z`.
  - **Beam spot (8):** `Bsp_x`, `Bsp_y`, `Bsp_z`, `Bsp_sigmaz`, `Bsp_dxdz`, `Bsp_dydz`,
    `Bsp_widthx`, `Bsp_widthy`.
  - **Muones (70):** `nMuon`, `Muon_charge`, `Muon_tightCharge`, `Muon_pt`, `Muon_ptErr`,
    `Muon_eta`, `Muon_phi`, `Muon_mass`, `Muon_dxy`, `Muon_dxyBest`, `Muon_dxyErr`,
    `Muon_dz`, `Muon_dzBest`, `Muon_dzErr`, `Muon_ip3d`, `Muon_sip3d`, `Muon_ip3dBest`,
    `Muon_sip3dBest`, `Muon_dxybs`, `Muon_pfRelIso03_all`, `Muon_pfRelIso03_chg`,
    `Muon_pfRelIso04_all`, `Muon_pfIsoId`, `Muon_miniPFRelIso_all`, `Muon_miniPFRelIso_chg`,
    `Muon_jetIdx`, `Muon_isPFcand`, `Muon_softId`, `Muon_mediumId`, `Muon_tightId`,
    `Muon_highPurity`, `Muon_highPtId`, `Muon_nStations`, `Muon_nTrackerLayers`,
    `Muon_segmentComp`, `Muon_pdgId`, `Muon_genPartFlav`, `Muon_genPartIdx`, `Muon_isGlobal`,
    `Muon_isTracker`, `Muon_Id`, `Muon_x`, `Muon_y`, `Muon_z`, `Muon_gpt`, `Muon_geta`,
    `Muon_gphi`, `Muon_looseId`, `Muon_softId4`, `Muon_softIdBest`, `Muon_isNano`,
    `Muon_isMini`, `Muon_isGood`, `Muon_isGoodLast`, `Muon_isGoodAng`, `Muon_isArbitrated`,
    `Muon_isStandAlone`, `Muon_isRPCcand`, `Muon_nValid`, `Muon_nPix`, `Muon_Chi2`,
    `Muon_gnValid`, `Muon_gnPix`, `Muon_gChi2`, `Muon_gnValidMu`, `Muon_vtxIdx`,
    `Muon_vtxFlag`, `Muon_trkId`, `Muon_simId`, `Muon_nNano`.
  - **Dimuones (29):** `nDimu`, `Dimu_t1muIdx`, `Dimu_t1dxy`, `Dimu_t1dz`, `Dimu_t2muIdx`,
    `Dimu_t2dxy`, `Dimu_t2dz`, `Dimu_pt`, `Dimu_eta`, `Dimu_phi`, `Dimu_rap`, `Dimu_mass`,
    `Dimu_charge`, `Dimu_simId`, `Dimu_genPartIdx`, `Dimu_vtxIdx`, `Dimu_chi2`, `Dimu_dlxy`,
    `Dimu_dlxyErr`, `Dimu_dlxySig`, `Dimu_cosphixy`, `Dimu_dl`, `Dimu_dlErr`, `Dimu_dlSig`,
    `Dimu_cosphi`, `Dimu_ptfrac`, `Dimu_x`, `Dimu_y`, `Dimu_z`.
  - **Electrones (49):** `nElectron`, `Electron_pt`, `Electron_eta`, `Electron_phi`,
    `Electron_mass`, `Electron_charge`, `Electron_tightCharge`, `Electron_pfRelIso03_all`,
    `Electron_pfRelIso03_chg`, `Electron_dr03TkSumPtOld`, `Electron_dr03TkSumPt`,
    `Electron_dr03EcalRecHitSumEtOld`, `Electron_dr03EcalRecHitSumEt`,
    `Electron_dr03HcalTowerSumEt`, `Electron_dr03HcalDepth1TowerSumEtOld`,
    `Electron_dr03HcalDepth1TowerSumEt`, `Electron_isEB`, `Electron_isEE`,
    `Electron_lostHits`, `Electron_isPFcand`, `Electron_isNano`, `Electron_convDist`,
    `Electron_convDcot`, `Electron_convVetoOld`, `Electron_convVeto`, `Electron_deltaEtaSC`,
    `Electron_deltaPhiSC`, `Electron_deltaEtaSCtr`, `Electron_deltaPhiSCtr`, `Electron_hoe`,
    `Electron_sieie`, `Electron_sieieR1`, `Electron_eInvMinusPInvOld`,
    `Electron_eInvMinusPInv`, `Electron_SCeta`, `Electron_cutBased`, `Electron_x`,
    `Electron_y`, `Electron_z`, `Electron_vtxIdx`, `Electron_dxy`, `Electron_dxyErr`,
    `Electron_dz`, `Electron_dzErr`, `Electron_ip3d`, `Electron_sip3d`, `Electron_simId`,
    `Electron_genPartIdx`, `Electron_nNano`.
  - **Taus (17):** `nTau`, `Tau_pt`, `Tau_eta`, `Tau_phi`, `Tau_mass`, `Tau_charge`,
    `Tau_decayMode`, `Tau_chargedIso`, `Tau_neutralIso`, `Tau_idDecaymode`, `Tau_idIsoraw`,
    `Tau_idIsovloose`, `Tau_idIsoloose`, `Tau_idIsomedium`, `Tau_idIsotight`,
    `Tau_idAntieletight`, `Tau_idAntimutight`.
  - **Fotones (10):** `nPhoton`, `Photon_pt`, `Photon_eta`, `Photon_phi`, `Photon_mass`,
    `Photon_charge`, `Photon_pfRelIso03_chg`, `Photon_pfRelIso03_all`, `Photon_phIso`,
    `Photon_cutBased`.
  - **MET (10):** `MET_pt`, `MET_phi`, `MET_sumEt`, `MET_significance`, `MET_covXX`,
    `MET_covXY`, `MET_covYY`, `CaloMET_pt`, `CaloMET_phi`, `CaloMET_sumEt`.
  - **Jets (16):** `nJet`, `Jet_pt`, `Jet_ptuncor`, `Jet_eta`, `Jet_phi`, `Jet_mass`,
    `Jet_area`, `Jet_nConstituents`, `Jet_nElectrons`, `Jet_nMuons`, `Jet_chEmEF`,
    `Jet_chHEF`, `Jet_neEmEF`, `Jet_neHEF`, `Jet_jetId`, `Jet_btag`.
  - **GenJets (5):** `nGenJet`, `GenJet_pt`, `GenJet_eta`, `GenJet_phi`, `GenJet_mass`.
  - **GenJets AK8 (5):** `nGenJetAK8`, `GenJetAK8_pt`, `GenJetAK8_eta`, `GenJetAK8_phi`,
    `GenJetAK8_mass`.
  - **FatJets (13):** `nFatJet`, `FatJet_pt`, `FatJet_eta`, `FatJet_phi`, `FatJet_mass`,
    `FatJet_area`, `FatJet_nConstituents`, `FatJet_nElectrons`, `FatJet_nMuons`,
    `FatJet_chEmEF`, `FatJet_chHEF`, `FatJet_neEmEF`, `FatJet_neHEF`.
  - **TrackJets (9):** `nTrackJet`, `TrackJet_pt`, `TrackJet_eta`, `TrackJet_phi`,
    `TrackJet_mass`, `TrackJet_area`, `TrackJet_nConstituents`, `TrackJet_nElectrons`,
    `TrackJet_nMuons`.
  - **TrigObj (6):** `nTrigObj`, `TrigObj_id`, `TrigObj_filterBits`, `TrigObj_pt`,
    `TrigObj_phi`, `TrigObj_eta`.
  - **Flags de trigger (25):** `Trig_goodMinBiasTrigger`, `Trig_goodJetTrigger`,
    `Trig_goodMuTrigger`, `Trig_goodETrigger`, `Trig_ZeroBiasFlag`, `Trig_MinBiasFlag`,
    `Trig_MinBiasMult`, `Trig_MuThresh`, `Trig_MuL1Thresh`, `Trig_MuL2Thresh`,
    `Trig_IsoMuThresh`, `Trig_DoubleMuThresh`, `Trig_JpsiThresh`, `Trig_MuHadFlag`,
    `Trig_MuEGFlag`, `Trig_ElectronThresh`, `Trig_DoubleElectronThresh`,
    `Trig_PhotonThresh`, `Trig_JetThresh`, `Trig_DiJetThresh`, `Trig_TriJetThresh`,
    `Trig_QuadJetThresh`, `Trig_HTThresh`, `Trig_BThresh`, `Trig_METThresh`.
  - **HLT (423):** `HLTriggerFirstPath`, `HLT_Activity_Ecal_SC7`, `HLT_L1SingleJet16`,
    `HLT_L1SingleJet36`, `HLT_Jet20_NoL1FastJet`, `HLT_PFJet40`, `HLT_Jet50_NoL1FastJet`,
    `HLT_PFJet80`, `HLT_PFJet140`, `HLT_PFJet200`, `HLT_PFJet260`, `HLT_PFJet320`,
    `HLT_Jet370_NoJetID`, `HLT_PFJet400`, `HLT_MonoCentralPFJet80_PFMETnoMu95_NHEF0p95`,
    `HLT_SingleJetC5`, `HLT_SingleForJet25`, `HLT_SingleForJet15`, `HLT_DiPFJetAve40`,
    `HLT_DiPFJetAve80`, `HLT_DiPFJetAve140`, `HLT_DiPFJetAve200`, `HLT_DiPFJetAve260`,
    `HLT_DiPFJetAve320`, `HLT_DiPFJetAve400`, `HLT_FatDiPFJetMass750_DR1p1_Deta1p5`,
    `HLT_DoubleJet20_ForwardBackward`, `HLT_DiJet80_DiJet60_DiJet20`,
    `HLT_DiPFJet40_PFMETnoMu65_MJJ800VBF_AllJets`,
    `HLT_DiPFJet40_PFMETnoMu65_MJJ600VBF_LeadingJets`, `HLT_DiJet40Eta2p6_BTagIP3DFastPV`,
    `HLT_DiJet80Eta2p6_BTagIP3DFastPVLoose`,
    `HLT_Jet60Eta1p7_Jet53Eta1p7_DiBTagIP3DFastPV`,
    `HLT_Jet80Eta1p7_Jet70Eta1p7_DiBTagIP3DFastPV`,
    `HLT_Jet160Eta2p4_Jet120Eta2p4_DiBTagIP3DFastPVLoose`, `HLT_QuadJet50`,
    `HLT_QuadJet50_Jet20`, `HLT_QuadJet60_DiJet20`, `HLT_QuadJet70`, `HLT_QuadJet80`,
    `HLT_QuadJet90`, `HLT_QuadJet75_55_35_20_BTagIP_VBF`, `HLT_QuadJet75_55_38_20_BTagIP_VBF`,
    `HLT_QuadPFJet78_61_44_31_BTagCSV_VBF`, `HLT_QuadPFJet82_65_48_35_BTagCSV_VBF`,
    `HLT_SixJet35`, `HLT_SixJet45`, `HLT_SixJet50`, `HLT_EightJet30_eta3p0`,
    `HLT_EightJet35_eta3p0`, `HLT_ExclDiJet35_HFOR`, `HLT_ExclDiJet35_HFAND`,
    `HLT_ExclDiJet80_HFAND`, `HLT_JetE30_NoBPTX`, `HLT_JetE30_NoBPTX3BX`,
    `HLT_JetE50_NoBPTX3BX`, `HLT_JetE70_NoBPTX3BX`, `HLT_HT200_AlphaT0p57`, `HLT_HT200`,
    `HLT_HT250_AlphaT0p55`, `HLT_HT250_AlphaT0p57`, `HLT_HT250`, `HLT_HT300_AlphaT0p53`,
    `HLT_HT300_AlphaT0p54`, `HLT_HT300`, `HLT_HT300_DoubleDisplacedPFJet60`,
    `HLT_HT300_DoubleDisplacedPFJet60_ChgFraction10`, `HLT_HT300_SingleDisplacedPFJet60`,
    `HLT_HT300_SingleDisplacedPFJet60_ChgFraction10`, `HLT_HT350`, `HLT_HT350_AlphaT0p52`,
    `HLT_HT350_AlphaT0p53`, `HLT_HT400`, `HLT_HT400_AlphaT0p51`, `HLT_HT400_AlphaT0p52`,
    `HLT_HT450_AlphaT0p51`, `HLT_HT450`, `HLT_HT500`, `HLT_HT550`, `HLT_HT650`,
    `HLT_HT650_Track50_dEdx3p6`, `HLT_HT650_Track60_dEdx3p7`, `HLT_HT750`, `HLT_PFHT350`,
    `HLT_PFHT650`, `HLT_PFHT650_DiCentralPFJet80_CenPFJet40`, `HLT_PFHT700`,
    `HLT_PFHT750`, `HLT_PFMET150`, `HLT_PFMET180`,
    `HLT_DiCentralJetSumpT100_dPhi05_DiCentralPFJet60_25_PFMET100_HBHENoiseCleaned`,
    `HLT_DiCentralPFJet30_PFMET80`, `HLT_DiCentralPFJet50_PFMET80`,
    `HLT_DiCentralPFJet30_PFMET80_BTagCSV07`, `HLT_DiPFJet80_DiPFJet30_BTagCSVd07d05d03`,
    `HLT_DiPFJet80_DiPFJet30_BTagCSVd07d05d05`,
    `HLT_DiPFJet80_DiPFJet30_BTagCSVd07d05d03_PFDiJetPt120`,
    `HLT_DiPFJet80_DiPFJet30_BTagCSVd07d05`, `HLT_MET80`, `HLT_MET80_Track50_dEdx3p6`,
    `HLT_MET80_Track60_dEdx3p7`, `HLT_MET120`, `HLT_MET120_HBHENoiseCleaned`, `HLT_MET200`,
    `HLT_MET200_HBHENoiseCleaned`, `HLT_MET300`, `HLT_MET300_HBHENoiseCleaned`,
    `HLT_MET400`, `HLT_MET400_HBHENoiseCleaned`, `HLT_L1SingleMuOpen`, `HLT_L1SingleMu12`,
    `HLT_L2Mu70_eta2p1_PFMET55`, `HLT_L2Mu70_eta2p1_PFMET60`,
    `HLT_L2Mu20_eta2p1_NoVertex`, `HLT_L2Mu10_NoVertex_NoBPTX3BX`,
    `HLT_L2Mu20_NoVertex_NoBPTX3BX`, `HLT_L2Mu30_NoVertex_NoBPTX3BX`,
    `HLT_L2TripleMu10_0_0_NoVertex_PFJet40Neutral`,
    `HLT_DoubleDisplacedMu4_DiPFJet40Neutral`, `HLT_Mu5`, `HLT_Mu8`, `HLT_Mu12`, `HLT_Mu17`,
    `HLT_Mu12_eta2p1_L1Mu10erJetC12WdEtaPhi1DiJetsC`, `HLT_Mu15_eta2p1`, `HLT_Mu24`,
    `HLT_Mu24_eta2p1`, `HLT_Mu30`, `HLT_Mu30_eta2p1`, `HLT_Mu40`, `HLT_Mu40_eta2p1`,
    `HLT_Mu50_eta2p1`, `HLT_RelIso1p0Mu5`, `HLT_RelIso1p0Mu20`,
    `HLT_IsoMu15_eta2p1_L1ETM20`, `HLT_IsoMu20_eta2p1`, `HLT_IsoMu24`,
    `HLT_IsoMu24_eta2p1`, `HLT_IsoMu30`, `HLT_IsoMu30_eta2p1`, `HLT_IsoMu34_eta2p1`,
    `HLT_IsoMu40_eta2p1`, `HLT_Mu40_eta2p1_Track50_dEdx3p6`,
    `HLT_Mu40_eta2p1_Track60_dEdx3p7`, `HLT_L2DoubleMu23_NoVertex`,
    `HLT_L2DoubleMu23_NoVertex_2Cha_Angle2p5`, `HLT_L2DoubleMu38_NoVertex_2Cha_Angle2p5`,
    `HLT_DoubleMu11_Acoplanarity03`, `HLT_DoubleMu4_Jpsi_Displaced`,
    `HLT_DoubleMu4_JpsiTk_Displaced`, `HLT_DoubleMu3_4_Dimuon5_Bs_Central`,
    `HLT_DoubleMu3p5_4_Dimuon5_Bs_Central`, `HLT_DoubleMu4_Dimuon7_Bs_Forward`,
    `HLT_DoubleMu3p5_LowMass_Displaced`, `HLT_DoubleMu3p5_LowMassNonResonant_Displaced`,
    `HLT_Dimuon0_Jpsi`, `HLT_Dimuon0_Jpsi_NoVertexing`, `HLT_Dimuon0_Upsilon`,
    `HLT_Dimuon0_PsiPrime`, `HLT_Dimuon5_Upsilon`, `HLT_Dimuon5_PsiPrime`,
    `HLT_Dimuon7_Upsilon`, `HLT_Dimuon8_Jpsi`, `HLT_Dimuon8_Upsilon`,
    `HLT_Dimuon9_PsiPrime`, `HLT_Dimuon10_Jpsi`, `HLT_Dimuon11_Upsilon`,
    `HLT_Dimuon0_Jpsi_Muon`, `HLT_Dimuon0_Upsilon_Muon`, `HLT_Dimuon3p5_SameSign`,
    `HLT_DoubleMu4_Acoplanarity03`, `HLT_Tau2Mu_ItTrack`, `HLT_Mu13_Mu8`, `HLT_Mu17_Mu8`,
    `HLT_Mu17_TkMu8`, `HLT_Mu22_TkMu8`, `HLT_Mu22_TkMu22`, `HLT_TripleMu5`,
    `HLT_DoubleMu5_IsoMu5`, `HLT_Mu5_L2Mu3_Jpsi`, `HLT_Mu5_Track2_Jpsi`,
    `HLT_Mu5_Track3p5_Jpsi`, `HLT_Mu7_Track7_Jpsi`, `HLT_Photon20_CaloIdVL`,
    `HLT_Photon20_CaloIdVL_IsoL`, `HLT_Photon22_R9Id90_HE10_Iso40_EBOnly`,
    `HLT_Photon26_Photon18`, `HLT_Photon26_R9Id85_Photon18_R9Id85_Mass60`,
    `HLT_Photon26_R9Id85_Photon18_CaloId10_Iso50_Mass60`,
    `HLT_Photon26_CaloId10_Iso50_Photon18_R9Id85_Mass60`,
    `HLT_Photon26_CaloId10_Iso50_Photon18_CaloId10_Iso50_Mass60`,
    `HLT_Photon26_R9Id85_OR_CaloId10_Iso50_Photon18_R9Id85_OR_CaloId10_Iso50_Mass60`,
    `HLT_Photon26_R9Id85_OR_CaloId10_Iso50_Photon18_R9Id85_OR_CaloId10_Iso50_Mass70`,
    `HLT_Photon26_R9Id85_OR_CaloId10_Iso50_Photon18`, `HLT_Photon30_CaloIdVL`,
    `HLT_Photon30_CaloIdVL_IsoL`, `HLT_Photon36_R9Id90_HE10_Iso40_EBOnly`,
    `HLT_Photon36_Photon22`, `HLT_Photon36_R9Id85_Photon22_R9Id85`,
    `HLT_Photon36_R9Id85_Photon22_CaloId10_Iso50`,
    `HLT_Photon36_CaloId10_Iso50_Photon22_R9Id85`,
    `HLT_Photon36_CaloId10_Iso50_Photon22_CaloId10_Iso50`,
    `HLT_Photon36_R9Id85_OR_CaloId10_Iso50_Photon22_R9Id85_OR_CaloId10_Iso50`,
    `HLT_Photon36_R9Id85_OR_CaloId10_Iso50_Photon22`, `HLT_Photon50_CaloIdVL`,
    `HLT_Photon50_CaloIdVL_IsoL`, `HLT_Photon50_R9Id90_HE10_Iso40_EBOnly`,
    `HLT_Photon60_CaloIdL_MHT70`, `HLT_Photon60_CaloIdL_HT300`,
    `HLT_Photon70_CaloIdXL_PFHT400`, `HLT_Photon70_CaloIdXL_PFHT500`,
    `HLT_Photon70_CaloIdXL_PFMET100`, `HLT_Photon75_CaloIdVL`,
    `HLT_Photon75_CaloIdVL_IsoL`, `HLT_Photon75_R9Id90_HE10_Iso40_EBOnly`,
    `HLT_Photon90_CaloIdVL`, `HLT_Photon90_CaloIdVL_IsoL`,
    `HLT_Photon90_R9Id90_HE10_Iso40_EBOnly`,
    `HLT_DisplacedPhoton65_CaloIdVL_IsoL_PFMET25`,
    `HLT_DisplacedPhoton65EBOnly_CaloIdVL_IsoL_PFMET30`, `HLT_Photon135`,
    `HLT_Photon150`, `HLT_Photon160`, `HLT_Photon300_NoHE`, `HLT_DoublePhoton48_HEVT`,
    `HLT_DoublePhoton53_HEVT`, `HLT_DoublePhoton70`, `HLT_DoublePhoton80`,
    `HLT_DoublePhoton5_IsoVL_CEP`, `HLT_L1SingleEG5`, `HLT_L1SingleEG12`,
    `HLT_L1DoubleEG3_FwdVeto`, `HLT_L1ETM30`, `HLT_L1ETM40`, `HLT_L1ETM70`,
    `HLT_L1ETM100`, `HLT_Ele8_CaloIdT_TrkIdVL`, `HLT_Ele8_CaloIdT_TrkIdVL_EG7`,
    `HLT_Ele8_CaloIdT_TrkIdVL_Jet30`, `HLT_Ele8_CaloIdL_CaloIsoVL`,
    `HLT_Ele8_CaloIdT_CaloIsoVL_TrkIdVL_TrkIsoVL`, `HLT_Ele17_CaloIdL_CaloIsoVL`,
    `HLT_Ele17_CaloIdT_CaloIsoVL_TrkIdVL_TrkIsoVL`,
    `HLT_Ele17_CaloIdT_CaloIsoVL_TrkIdVL_TrkIsoVL_Ele8_CaloIdT_CaloIsoVL_TrkIdVL_TrkIsoVL`,
    `HLT_Ele17_CaloIdVT_CaloIsoVT_TrkIdT_TrkIsoVT_Ele8_Mass50`,
    `HLT_Ele20_CaloIdVT_CaloIsoVT_TrkIdT_TrkIsoVT_SC4_Mass50`,
    `HLT_Ele22_CaloIdL_CaloIsoVL`, `HLT_Ele27_CaloIdL_CaloIsoVL_TrkIdVL_TrkIsoVL`,
    `HLT_Ele27_CaloIdT_CaloIsoVL_TrkIdVL_TrkIsoVL_Ele15_CaloIdT_CaloIsoVL_trackless`,
    `HLT_Ele27_CaloIdT_CaloIsoVL_TrkIdVL_TrkIsoVL_HFT15`,
    `HLT_Ele23_CaloIdT_CaloIsoVL_TrkIdVL_TrkIsoVL_HFT30`,
    `HLT_Ele25_CaloIdVT_CaloIsoVL_TrkIdVL_TrkIsoT_TriCentralPFNoPUJet30`,
    `HLT_Ele25_CaloIdVT_CaloIsoVL_TrkIdVL_TrkIsoT_TriCentralPFNoPUJet50_40_30`,
    `HLT_Ele27_WP80`, `HLT_Ele27_WP80_PFMET_MT50`, `HLT_Ele30_CaloIdVT_TrkIdT`,
    `HLT_Ele32_CaloIdL_CaloIsoVL_TrkIdVL_TrkIsoVL`,
    `HLT_Ele32_CaloIdT_CaloIsoT_TrkIdT_TrkIsoT_SC17_Mass50`,
    `HLT_Ele80_CaloIdVT_GsfTrkIdT`, `HLT_Ele90_CaloIdVT_GsfTrkIdT`,
    `HLT_DoubleEle8_CaloIdT_TrkIdVL`, `HLT_DoubleEle33_CaloIdL`,
    `HLT_DoubleEle33_CaloIdL_GsfTrkIdVL`, `HLT_DoubleEle33_CaloIdT`,
    `HLT_Ele15_Ele8_Ele5_CaloIdL_TrkIdVL`, `HLT_LooseIsoPFTau35_Trk20_Prong1`,
    `HLT_LooseIsoPFTau35_Trk20_Prong1_MET70`, `HLT_LooseIsoPFTau35_Trk20_Prong1_MET75`,
    `HLT_IsoMu15_eta2p1_LooseIsoPFTau35_Trk20_Prong1_L1ETM20`,
    `HLT_DoubleMediumIsoPFTau30_Trk5_eta2p1_Jet30`,
    `HLT_DoubleMediumIsoPFTau30_Trk5_eta2p1`, `HLT_DoubleMediumIsoPFTau35_Trk5_eta2p1`,
    `HLT_DoubleMediumIsoPFTau35_Trk5_eta2p1_Prong1`,
    `HLT_IsoMu18_eta2p1_MediumIsoPFTau25_Trk5_eta2p1`, `HLT_BTagMu_DiJet20_Mu5`,
    `HLT_BTagMu_DiJet40_Mu5`, `HLT_BTagMu_DiJet70_Mu5`, `HLT_BTagMu_DiJet110_Mu5`,
    `HLT_BTagMu_Jet300_Mu5`, `HLT_Mu7_Ele7_CaloIdT_CaloIsoVL`,
    `HLT_Mu8_Ele17_CaloIdT_CaloIsoVL_TrkIdVL_TrkIsoVL`, `HLT_Mu8_DiJet30`,
    `HLT_Mu8_TriJet30`, `HLT_Mu8_QuadJet30`, `HLT_IsoMu12_DoubleCentralJet65`,
    `HLT_Mu15_eta2p1_L1ETM20`, `HLT_Mu24_PFJet30_PFJet25_Deta3_CentralPFJet25`,
    `HLT_Mu24_CentralPFJet30_CentralPFJet25`,
    `HLT_IsoMu24_PFJet30_PFJet25_Deta3_CentralPFJet25`,
    `HLT_IsoMu24_CentralPFJet30_CentralPFJet25`,
    `HLT_IsoMu24_CentralPFJet30_CentralPFJet25_PFMET20`,
    `HLT_Ele32_WP80_PFJet30_PFJet25_Deta3`,
    `HLT_Ele32_WP80_PFJet30_PFJet25_Deta3_CentralPFJet30`,
    `HLT_Ele32_WP80_CentralPFJet35_CentralPFJet25`,
    `HLT_Ele32_WP80_CentralPFJet35_CentralPFJet25_PFMET20`,
    `HLT_IsoMu17_eta2p1_CentralPFNoPUJet30_BTagIPIter`,
    `HLT_IsoMu17_eta2p1_CentralPFNoPUJet30`, `HLT_IsoMu17_eta2p1_DiCentralPFNoPUJet30`,
    `HLT_IsoMu17_eta2p1_TriCentralPFNoPUJet30_30_20`,
    `HLT_IsoMu17_eta2p1_TriCentralPFNoPUJet50_40_30`,
    `HLT_Mu17_eta2p1_CentralPFNoPUJet30_BTagIPIter`,
    `HLT_Mu17_eta2p1_TriCentralPFNoPUJet30_30_20`,
    `HLT_Mu17_eta2p1_TriCentralPFNoPUJet50_40_30`, `HLT_IsoMu20_WCandPt80`,
    `HLT_Mu17_Ele8_CaloIdT_CaloIsoVL_TrkIdVL_TrkIsoVL`,
    `HLT_Mu12_eta2p1_DiCentral_40_20_DiBTagIP3D1stTrack`,
    `HLT_Mu12_eta2p1_DiCentral_40_20_BTagIP3D1stTrack`, `HLT_Mu12_eta2p1_DiCentral_40_20`,
    `HLT_Mu12_eta2p1_DiCentral_20`, `HLT_Mu15_eta2p1_TriCentral_40_20_20_DiBTagIP3D1stTrack`,
    `HLT_Mu15_eta2p1_TriCentral_40_20_20_BTagIP3D1stTrack`,
    `HLT_Mu15_eta2p1_TriCentral_40_20_20`, `HLT_Mu30_Ele30_CaloIdL`,
    `HLT_IsoMu17_eta2p1_DiCentralPFJet30_PFHT350_PFMHT40`,
    `HLT_IsoMu20_eta2p1_CentralPFJet80`, `HLT_DoubleRelIso1p0Mu5_Mass8_PFHT175`,
    `HLT_DoubleRelIso1p0Mu5_Mass8_PFHT225`, `HLT_DoubleMu8_Mass8_PFHT225`,
    `HLT_DoubleMu8_Mass8_PFHT175`, `HLT_RelIso1p0Mu5_Ele8_CaloIdT_TrkIdVL_Mass8_PFHT175`,
    `HLT_RelIso1p0Mu5_Ele8_CaloIdT_TrkIdVL_Mass8_PFHT225`,
    `HLT_Mu8_Ele8_CaloIdT_TrkIdVL_Mass8_PFHT175`,
    `HLT_Mu8_Ele8_CaloIdT_TrkIdVL_Mass8_PFHT225`, `HLT_PFHT350_Mu15_PFMET45`,
    `HLT_PFHT350_Mu15_PFMET50`, `HLT_PFHT400_Mu5_PFMET45`, `HLT_PFHT400_Mu5_PFMET50`,
    `HLT_Mu40_PFHT350`, `HLT_Mu60_PFHT350`, `HLT_Mu40_HT200`,
    `HLT_DoubleMu5_Ele8_CaloIdT_TrkIdVL`, `HLT_DoubleMu8_Ele8_CaloIdT_TrkIdVL`,
    `HLT_Ele8_CaloIdT_CaloIsoVL_TrkIdVL_TrkIsoVL_Jet30`, `HLT_Ele8_CaloIdT_TrkIdT_DiJet30`,
    `HLT_Ele8_CaloIdT_TrkIdT_TriJet30`, `HLT_Ele8_CaloIdT_TrkIdT_QuadJet30`,
    `HLT_Ele17_CaloIdT_CaloIsoVL_TrkIdVL_TrkIsoVL_Jet30`,
    `HLT_Ele25_CaloIdVT_TrkIdT_TriCentralPFNoPUJet30_30_20`,
    `HLT_Ele25_CaloIdVT_TrkIdT_TriCentralPFNoPUJet50_40_30`,
    `HLT_Ele25_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_CentralPFNoPUJet30`,
    `HLT_Ele25_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_DiCentralPFNoPUJet30`,
    `HLT_Ele25_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_TriCentralPFNoPUJet30_30_20`,
    `HLT_Ele25_CaloIdVL_CaloIsoT_TrkIdVL_TrkIsoT_TriCentralPFNoPUJet30_30_20`,
    `HLT_Ele25_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_CentralPFNoPUJet30_BTagIPIter`,
    `HLT_Ele25_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_TriCentralPFNoPUJet50_40_30`,
    `HLT_Ele27_WP80_CentralPFJet80`, `HLT_Ele27_WP80_WCandPt80`,
    `HLT_Ele30_CaloIdVT_TrkIdT_PFJet100_PFJet25`,
    `HLT_Ele30_CaloIdVT_TrkIdT_PFJet150_PFJet25`,
    `HLT_Ele30_CaloIdVT_TrkIdT_PFNoPUJet100_PFNoPUJet25`,
    `HLT_Ele30_CaloIdVT_TrkIdT_PFNoPUJet150_PFNoPUJet25`,
    `HLT_DoubleEle8_CaloIdT_TrkIdVL_Mass8_PFHT175`,
    `HLT_DoubleEle8_CaloIdT_TrkIdVL_Mass8_PFHT225`,
    `HLT_DoubleEle10_CaloIdL_TrkIdVL_Ele10_CaloIdT_TrkIdVL`,
    `HLT_TripleEle10_CaloIdL_TrkIdVL`, `HLT_RsqMR40_Rsq0p04`, `HLT_RsqMR45_Rsq0p09`,
    `HLT_RsqMR55_Rsq0p09_MR150`, `HLT_RsqMR60_Rsq0p09_MR150`,
    `HLT_RsqMR65_Rsq0p09_MR150`, `HLT_IsoMu12_RsqMR30_Rsq0p04_MR200`,
    `HLT_IsoMu12_RsqMR40_Rsq0p04_MR200`,
    `HLT_Ele12_CaloIdT_CaloIsoVL_TrkIdVL_TrkIsoVL_RsqMR30_Rsq0p04_MR200`,
    `HLT_Ele12_CaloIdT_CaloIsoVL_TrkIdVL_TrkIsoVL_RsqMR40_Rsq0p04_MR200`,
    `HLT_Ele12_CaloIdT_CaloIsoVL_TrkIdVL_TrkIsoVL_DoubleCentralJet65`,
    `HLT_Photon40_CaloIdL_RsqMR35_Rsq0p09_MR150`,
    `HLT_Photon40_CaloIdL_RsqMR40_Rsq0p09_MR150`,
    `HLT_Photon40_CaloIdL_RsqMR45_Rsq0p09_MR150`,
    `HLT_Photon40_CaloIdL_RsqMR50_Rsq0p09_MR150`, `HLT_DoublePhoton40_CaloIdL_Rsq0p035`,
    `HLT_DoublePhoton40_CaloIdL_Rsq0p06`, `HLT_Mu22_Photon22_CaloIdL`,
    `HLT_Mu8_DoubleEle8_CaloIdT_TrkIdVL`,
    `HLT_Mu8_Ele8_CaloIdT_TrkIdVL_Ele8_CaloIdL_TrkIdVL`, `HLT_DoubleMu14_Mass8_PFMET40`,
    `HLT_DoubleMu14_Mass8_PFMET50`, `HLT_DoubleEle14_CaloIdT_TrkIdVL_Mass8_PFMET40`,
    `HLT_DoubleEle14_CaloIdT_TrkIdVL_Mass8_PFMET50`,
    `HLT_Mu14_Ele14_CaloIdT_TrkIdVL_Mass8_PFMET40`,
    `HLT_Mu14_Ele14_CaloIdT_TrkIdVL_Mass8_PFMET50`, `HLT_PFHT350_PFMET100`,
    `HLT_PFHT400_PFMET100`,
    `HLT_CleanPFHT350_Ele5_CaloIdT_CaloIsoVL_TrkIdT_TrkIsoVL_PFMET45`,
    `HLT_CleanPFHT350_Ele5_CaloIdT_CaloIsoVL_TrkIdT_TrkIsoVL_PFMET50`,
    `HLT_CleanPFHT300_Ele15_CaloIdT_CaloIsoVL_TrkIdT_TrkIsoVL_PFMET45`,
    `HLT_CleanPFHT300_Ele15_CaloIdT_CaloIsoVL_TrkIdT_TrkIsoVL_PFMET50`,
    `HLT_CleanPFHT300_Ele40_CaloIdVT_TrkIdT`, `HLT_CleanPFHT300_Ele60_CaloIdVT_TrkIdT`,
    `HLT_Ele5_SC5_Jpsi_Mass2to15`, `HLT_DiJet35_MJJ650_AllJets_DEta3p5_VBF`,
    `HLT_DiJet35_MJJ700_AllJets_DEta3p5_VBF`, `HLT_DiJet35_MJJ750_AllJets_DEta3p5_VBF`,
    `HLT_Ele22_eta2p1_WP90Rho_LooseIsoPFTau20`,
    `HLT_Ele22_eta2p1_WP90NoIso_LooseIsoPFTau20`, `HLT_IsoMu17_eta2p1_LooseIsoPFTau20`,
    `HLT_Mu17_eta2p1_LooseIsoPFTau20`, `HLT_PixelTracks_Multiplicity70`,
    `HLT_PixelTracks_Multiplicity80`, `HLT_PixelTracks_Multiplicity90`,
    `HLT_BeamGas_HF_Beam1`, `HLT_BeamGas_HF_Beam2`, `HLT_BeamHalo`, `HLT_IsoTrackHE`,
    `HLT_IsoTrackHB`, `HLT_HcalPhiSym`, `HLT_HcalNZS`, `HLT_GlobalRunHPDNoise`,
    `HLT_L1Tech_HBHEHO_totalOR`, `HLT_L1Tech_HCAL_HF_single_channel`, `HLT_ZeroBias`,
    `HLT_ZeroBiasPixel_DoubleTrack`, `HLT_Physics`, `HLT_DTCalibration`,
    `HLT_EcalCalibration`, `HLT_HcalCalibration`, `HLT_TrackerCalibration`, `HLT_Random`,
    `HLT_L1SingleMuOpen_AntiBPTX`, `HLT_L1TrackerCosmics`, `HLT_LogMonitor`,
    `HLT_DTErrors`, `HLT_L1DoubleJet36Central`, `HLTriggerFinalPath`.
  - **L1 (127):** `L1_BeamGas_Hf`, `L1_BeamGas_Hf_BptxMinusPostQuiet`,
    `L1_BeamGas_Hf_BptxPlusPostQuiet`, `L1_BeamHalo`, `L1_BptxMinus_NotBptxPlus`,
    `L1_BptxPlus_NotBptxMinus`, `L1_Bsc2Minus_BptxMinus`, `L1_Bsc2Plus_BptxPlus`,
    `L1_BscMinBiasOR_BptxPlusANDMinus`, `L1_DoubleEG10`, `L1_DoubleEG2_FwdVeto`,
    `L1_DoubleEG3`, `L1_DoubleEG5`, `L1_DoubleEG5_HTT50`, `L1_DoubleEG5_HTT75`,
    `L1_DoubleEG_12_5`, `L1_DoubleEG_12_5_Eta1p39`, `L1_DoubleEG_15_5`,
    `L1_DoubleForJet32_EtaOpp`, `L1_DoubleForJet44_EtaOpp`, `L1_DoubleIsoEG10`,
    `L1_DoubleJet36_Central`, `L1_DoubleJet44_Central`, `L1_DoubleJet52`,
    `L1_DoubleJet52_Central`, `L1_DoubleJet64_Central`, `L1_DoubleMu0`,
    `L1_DoubleMu0_HighQ`, `L1_DoubleMu0_HighQ_EtaCuts`, `L1_DoubleMu3`,
    `L1_DoubleMu3p5`, `L1_DoubleMu5`, `L1_DoubleMuOpen_EG5`, `L1_DoubleMu_10_Open`,
    `L1_DoubleMu_5_Open`, `L1_DoubleTauJet32_Eta2p17`, `L1_DoubleTauJet36_Eta2p17`,
    `L1_DoubleTauJet40_Eta2p17`, `L1_DoubleTauJet44_Eta2p17`,
    `L1_EG12_Jet24_Central_deltaPhi1`, `L1_EG15_ForJet16`, `L1_EG18_ForJet16`,
    `L1_EG5_DoubleJet20_Central`, `L1_EG5_HTT100`, `L1_EG5_HTT125`, `L1_EG5_HTT75`,
    `L1_EG5_Jet36_deltaPhi1`, `L1_EG8_Jet20_Central_deltaPhi1`, `L1_ETM100`,
    `L1_ETM20`, `L1_ETM30`, `L1_ETM50`, `L1_ETM70`, `L1_ETT220`, `L1_ETT300_EG5`,
    `L1_HTM50`, `L1_HTT100`, `L1_HTT150`, `L1_HTT50`, `L1_HTT50_HTM30`,
    `L1_HTT50_HTM50`, `L1_HTT75`, `L1_InterBunch_Bsc`, `L1_Jet52_Central_ETM30`,
    `L1_Mu0_HTT50`, `L1_Mu0_HTT75`, `L1_Mu10_ETM20`,
    `L1_Mu10_Eta2p1_DoubleJet_16_8_Central`, `L1_Mu10_Jet36_Central`, `L1_Mu12_EG5`,
    `L1_Mu3_EG5`, `L1_Mu3_Jet16_Central`, `L1_Mu3_Jet20_Central`,
    `L1_Mu3_Jet28_Central`, `L1_Mu5_EG12`, `L1_Mu7_EG5`, `L1_Mu7_Jet20_Central`,
    `L1_MuOpen_DoubleEG5`, `L1_MuOpen_EG12`, `L1_PreCollisions`,
    `L1_QuadJet20_Central`, `L1_QuadJet28_Central`, `L1_SingleEG12`, `L1_SingleEG15`,
    `L1_SingleEG18`, `L1_SingleEG20`, `L1_SingleEG22`, `L1_SingleEG30`,
    `L1_SingleEG5`, `L1_SingleIsoEG12`, `L1_SingleIsoEG12_Eta2p17`,
    `L1_SingleJet128`, `L1_SingleJet16`, `L1_SingleJet20_Central_NotBptxOR`,
    `L1_SingleJet20_Central_NotBptxOR_NotMuBeamHalo`,
    `L1_SingleJet32_NotBptxOR_NotMuBeamHalo`, `L1_SingleJet36`,
    `L1_SingleJet36_FwdVeto`, `L1_SingleJet52`, `L1_SingleJet52_Central`,
    `L1_SingleJet68`, `L1_SingleJet80_Central`, `L1_SingleJet92`,
    `L1_SingleJet92_Central`, `L1_SingleMu10`, `L1_SingleMu12`,
    `L1_SingleMu12_Debug`, `L1_SingleMu14_Eta2p1`, `L1_SingleMu16`,
    `L1_SingleMu16_Eta2p1`, `L1_SingleMu20`, `L1_SingleMu25`, `L1_SingleMu3`,
    `L1_SingleMu5_Eta1p5_Q80`, `L1_SingleMu7`, `L1_SingleMuBeamHalo`,
    `L1_SingleMuOpen`, `L1_TripleEG5`, `L1_TripleEG7`, `L1_TripleEG_8_5_5`,
    `L1_TripleEG_8_8_5`, `L1_TripleJet28_Central`, `L1_TripleJet_36_36_12_Central`,
    `L1_TripleJet_36_36_16_Central`, `L1_TripleMu0`, `L1_ZeroBias`,
    `L1_ZeroBias_Instance1`.
- **Eventos leídos:** **100 000** (tope de la tool; total real no verificable).
- **Resúmenes (100 000 eventos):** `run` = 1 constante (min=max=media=1, típico de MC);
  `event` 5 101 – 493 800 (media 251 315.1); `nTau` 0 – 53 (media 8.531);
  `MET_pt` 0.257 – 43 653.0 GeV (media 52.669; el máximo es un valor extremo aislado).
  Muestra: `run=[1,1,1]`, `event=[388801,388802,388803]`, `nMuon=[2,1,0]`,
  `nTau=[12,10,12]`, `MET_pt=[49.77, 21.60, 58.97]` GeV.
- **Cobertura:** un solo archivo suelto de los 17 del recid 31102; **no** es la muestra
  completa ni representa toda la luminosidad. Es MC (ttbar), no datos.

## 11. `W1JetsToLNu.root` (recid 12355) — W+jets MC

- **Árbol:** uno, `Events`.
- **Ramas:** **69** (62 del esquema de datos + `nGenPart` + 6 `GenPart_*`).
- **Eventos leídos:** **100 000** (tope de la tool; total real no verificable).
- **Resúmenes (100 000 eventos):** `run` = 1 constante (MC); `event` 30 907 – 98 838 999
  (media 48 902 283.6); `nMuon` 0 – 7 (media 0.3869); `nTau` 0 – 50 (media 5.888);
  `MET_pt` 0.0735 – 329.87 GeV (media 38.022); `HLT_IsoMu24_eta2p1` media 0.14339.
  Muestra: `run=[1,1,1]`, `event=[50693803,50693805,50693814]`, `nMuon=[1,1,0]`,
  `nTau=[5,3,0]`, `MET_pt=[50.40, 28.05, 19.60]` GeV.
- **Cobertura:** archivo único del recid; es la muestra entera W1Jets, no una fracción.

## 12. `DYJetsToLL.root` (recid 12353) — Drell–Yan MC

- **Árbol:** uno, `Events`.
- **Ramas:** **69** (idénticas a §11).
- **Eventos leídos:** **100 000** (tope de la tool; total real no verificable).
- **Resúmenes (100 000 eventos):** `event` 54 003 – 70 833 199 (media 28 341 641.5);
  `nMuon` 0 – 9 (media 0.6356); `nTau` 0 – 36 (media 3.9429);
  `MET_pt` 0.0741 – 268.70 GeV (media 21.978); `nGenPart` 0 – 41 (media 5.215);
  `HLT_IsoMu24_eta2p1` media 0.20596.
- **Muestra:** `run=[200519,...]`, `luminosityBlock=[12007,...]`,
  `event=[4798803,4798806,4798811,...]`, `nMuon=[1,1,1,0,1]`,
  `nTau=[17,14,1,8,3]`, `MET_pt=[49.17,34.63,35.58,35.77,22.80]` GeV.
- **Anomalía de metadatos (advertencia):** a diferencia de 12351/12352/12355 (donde `run`=1),
  aquí `run` toma **números de run de colisión de 2012** (194 533 – 206 859; media
  200 422.05) pese a que el contenido de generación (`GenPart_*` con taus, electrones y
  muones) indica que es MC. No se puede resolver con las tools si es una elección de
  producción o una etiqueta heredada; **no usar `run` de este archivo como identificador de
  periodo de datos**.
- **Cobertura:** archivo único del recid; es la muestra entera DY, no una fracción.

## 13. Huecos comunes y variables de interés ausentes

Común a los cuatro archivos:

- **No verificable el total de eventos**: `root summary` devuelve siempre 100 000; no hay
  contador total expuesto por la tool.
- **Sin pesos de MC ni normalización**: no existe `genWeight`, `sumw`, `LHEWeight`, sección
  eficaz, ni número de eventos generados. No se puede normalizar ninguna muestra MC.
- **Sin luminosidad integrada** ni metadatos de año/energía/campaña dentro del ROOT.
- **Sin MET filters, JEC/JER, ni puntos de trabajo de b-tagging**; `Jet_btag` es un valor
  crudo y `Jet_puId` falta en 31102.
- **Variables derivadas no almacenadas**: `m_vis(mu,tau_h)`, `dR(mu,tau_h)`, `pT` del par,
  `dphi(mu,MET)` y masa transversa hay que calcularlas.

Por archivo, respecto a `variables_de_interes` del config:

| Variable | 12358 datos | 12355 W | 12353 DY | 31102 ttbar |
|---|---|---|---|---|
| `Muon_*` (pt/eta/phi/mass/charge/pfRelIso03_all/tightId/dxy/dz) | sí | sí | sí | sí |
| `Tau_pt/eta/phi/mass/charge/decayMode` | sí | sí | sí | sí |
| `Tau_relIso_all` | sí | sí | sí | **no** (solo `Tau_chargedIso`, `Tau_neutralIso`, `Tau_idIsoraw`) |
| `Tau_idIsoMedium/Tight` | sí | sí | sí | sí (`idIsomedium`, `idIsotight`) |
| `Tau_idAntiMuLoose/Tight` | sí | sí | sí | **no** (solo `idAntimutight`) |
| `Tau_idAntiEleLoose/Medium` | sí | sí | sí | **no** (solo `idAntieletight`) |
| `MET_pt/phi` | sí | sí | sí | sí |
| `Jet_pt/eta/phi/btag` | sí | sí | sí | sí |
| `Jet_puId` | sí | sí | sí | **no** |
| `PV_npvs`, `nMuon`, `nTau`, `nJet` | sí | sí | sí | sí |
| `HLT_IsoMu24_eta2p1`, `HLT_IsoMu24`, `HLT_IsoMu17_eta2p1_LooseIsoPFTau20` | sí (las 3) | sí (las 3) | sí (las 3) | sí (entre centenares de HLT) |
| `GenPart_*` | **no** (datos) | sí | sí | sí |
| Pesos MC / `sumw` / normalización | no aplica | **no** | **no** | **no** |
| Luminosidad integrada | **no** | **no** | **no** | **no** |

Otras ausencias por archivo:

- **12358 (datos):** sin `GenPart_*` (correcto para datos), sin triggers puros de tau, sin
  flags de MET filters; solo cubre Run2012B.
- **31102 (ttbar):** sin `Tau_relIso_all`, sin `Tau_idAntiMuLoose/Medium`,
  sin `Tau_idAntiEleLoose/Medium`, sin `Jet_puId`; nombres de tau en minúsculas
  (`idIsomedium`, `idAntimutight`, …), no los de NanoAOD estándar.
- **12355 y 12353:** sin `genWeight`/`sumw`; sin año/energía declarados en la ficha.
