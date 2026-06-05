
// ============================================================
// DATA: Full reactions database (replaces PocketBase)
// ============================================================
const REACTIONS = [
  {
    id:"r1", name:"Wurtz Reaction", class_level:11,
    reactants:"CH₃Cl,Na",
    products:"C₂H₆,NaCl",
    equation:"2CH₃Cl + 2Na → C₂H₆ + 2NaCl",
    conditions:"Dry ether",
    explanation:"Two alkyl halide molecules react with sodium metal in dry ether. The sodium donates electrons to the carbon-halogen bond, forming a carbanion intermediate. Two carbanion species couple together, forming a new C–C bond and releasing sodium chloride. This is a classic coupling reaction to form alkanes.",
    applications:"Used in synthesis of symmetric alkanes in the laboratory. Important in understanding C–C bond formation.",
    not_occur:"Does not occur with tertiary alkyl halides (forms alkenes instead), aryl halides (C-X bond too strong), or in presence of moisture (Na reacts with water). Ineffective for unsymmetrical alkanes due to mixture of products."
  },
  {
    id:"r2", name:"Friedel-Crafts Alkylation", class_level:12,
    reactants:"C₆H₆,CH₃Cl,AlCl₃",
    products:"C₆H₅CH₃,HCl",
    equation:"C₆H₆ + CH₃Cl → C₆H₅CH₃ + HCl (AlCl₃ catalyst)",
    conditions:"Anhydrous AlCl₃",
    explanation:"AlCl₃ acts as a Lewis acid and forms a carbocation (CH₃⁺) from CH₃Cl. The highly electrophilic carbocation attacks the electron-rich benzene ring. A sigma complex (arenium ion) forms, then loses H⁺ to restore aromaticity. The result is toluene.",
    applications:"Industrial production of ethylbenzene for styrene manufacture. Synthesis of alkylbenzenes in perfumes and detergents.",
    not_occur:"Does not occur on benzene rings with strong electron-withdrawing groups (NO₂, SO₃H, CN, COR). Fails with aryl halides and vinyl halides. Rearrangement of carbocations occurs with primary alkyl halides. Does not work with deactivated aromatic rings."
  },
  {
    id:"r3", name:"Sandmeyer Reaction", class_level:12,
    reactants:"C₆H₅NH₂,HNO₂,HCl,CuCl",
    products:"C₆H₅Cl,N₂",
    equation:"C₆H₅N₂⁺Cl⁻ + CuCl → C₆H₅Cl + N₂ + CuCl₂",
    conditions:"0–5°C, then CuCl",
    explanation:"Aniline is first diazotised with NaNO₂/HCl at 0–5°C to form a diazonium salt. The unstable diazonium ion is then treated with cuprous chloride (CuCl) in a copper-catalysed substitution, replacing the –N₂⁺ group with –Cl while releasing nitrogen gas.",
    applications:"Important method for introducing halogens onto aromatic rings. Used in dye synthesis and pharmaceutical manufacturing.",
    not_occur:"Does not occur at room temperature or higher temperatures (diazonium salt decomposes). Fails without cuprous halide catalyst. Does not work with aliphatic amines (they form unstable diazonium salts that decompose immediately)."
  },
  {
    id:"r4", name:"Rosenmund Reduction", class_level:12,
    reactants:"CH₃COCl,H₂",
    products:"CH₃CHO,HCl",
    equation:"CH₃COCl + H₂ → CH₃CHO + HCl (Pd/BaSO₄)",
    conditions:"Pd/BaSO₄, H₂ gas, toluene",
    explanation:"The acid chloride is hydrogenated over a poisoned palladium catalyst (Pd on BaSO₄). The catalyst is partially deactivated by BaSO₄ and quinoline to prevent over-reduction to the alcohol. One mole of H₂ selectively reduces the –COCl to –CHO, releasing HCl.",
    applications:"Selective synthesis of aldehydes from acid chlorides. The poisoning prevents full reduction. Used in fine chemicals and fragrance industry.",
    not_occur:"Does not occur without catalyst poisoning (over-reduction to alcohol occurs). Fails with unpoisoned Pd catalyst. Does not work with formyl chloride (unstable). Reaction stops at aldehyde stage only with proper catalyst poisoning."
  },
  {
    id:"r5", name:"Clemmensen Reduction", class_level:12,
    reactants:"CH₃COCH₃,Zn",
    products:"CH₃CH₂CH₃,ZnO",
    equation:"CH₃COCH₃ + 4[H] → CH₃CH₂CH₃ + H₂O (Zn-Hg, conc. HCl)",
    conditions:"Zn amalgam, conc. HCl, reflux",
    explanation:"The carbonyl group (C=O) of a ketone is reduced to a methylene group (–CH₂–) using zinc amalgam in concentrated HCl. The zinc surface generates nascent hydrogen which attacks the carbonyl. Water is eliminated and the C=O is replaced by C–H bonds, lowering oxidation state by two.",
    applications:"Reduces ketones to alkanes without affecting C=C double bonds. Used in steroid synthesis and conversion of Friedel-Crafts ketones to alkylbenzenes.",
    not_occur:"Does not occur with acid-sensitive functional groups (esters, ethers, acetals). Fails with phenols (decomposition occurs). Not suitable for pyridine derivatives. Does not work with concentrated H₂SO₄ instead of HCl."
  },
  {
    id:"r6", name:"Etard Reaction", class_level:11,
    reactants:"C₆H₅CH₃,K₂Cr₂O₇",
    products:"C₆H₅CHO,Cr₂O₃",
    equation:"C₆H₅CH₃ + [O] → C₆H₅CHO (CrO₂Cl₂, CS₂)",
    conditions:"Chromyl chloride CrO₂Cl₂, CS₂",
    explanation:"The methyl group of toluene is oxidised directly to an aldehyde using chromyl chloride in carbon disulfide. A chromium ester complex (Etard complex) forms first, then is hydrolysed to give benzaldehyde. This is selective — the ring is unaffected.",
    applications:"Selective oxidation of methyl groups on aromatic rings to aldehydes. Useful in perfumery (benzaldehyde synthesis).",
    not_occur:"Does not occur with methoxy or amino substituted toluenes (side reactions dominate). Fails with nitro-substituted toluenes. Does not oxidize tertiary alkyl groups. Requires careful control to prevent over-oxidation to acids."
  },
  {
    id:"r7", name:"Reimer-Tiemann Reaction", class_level:12,
    reactants:"C₆H₅OH,CHCl₃,NaOH",
    products:"C₆H₄OHCHO,NaCl",
    equation:"C₆H₅OH + CHCl₃ + NaOH → 2-HOC₆H₄CHO + NaCl + H₂O",
    conditions:"NaOH (aq), CHCl₃, heat",
    explanation:"NaOH deprotonates CHCl₃ to form a highly reactive dichlorocarbene (:CCl₂). The phenoxide ion (from phenol + NaOH) acts as a nucleophile and attacks the carbene at the ortho position. After hydrolysis of the intermediate, an aldehyde group (–CHO) is introduced onto the ring.",
    applications:"Classic method to introduce formyl groups onto phenols. Salicylaldehyde (2-hydroxybenzaldehyde) is produced this way — used in perfumes.",
    not_occur:"Does not occur with aniline (different products form). Fails with p-nitrophenol (electron-withdrawing group inhibits). Does not work with alcohols (only phenols). Ortho position must be free for reaction to proceed."
  },
  {
    id:"r8", name:"Kolbe's Reaction", class_level:12,
    reactants:"C₆H₅OH,CO₂,NaOH",
    products:"C₆H₄OHCOOH",
    equation:"C₆H₅ONa + CO₂ → C₆H₄(OH)COONa → C₆H₄(OH)COOH",
    conditions:"CO₂ under pressure, 125°C, then H⁺",
    explanation:"Sodium phenoxide is heated with CO₂ under pressure. CO₂, being electrophilic, attacks the ortho position of the phenoxide ring. After acidification, salicylic acid (2-hydroxybenzoic acid) is obtained. This is a classic electrophilic substitution on a phenoxide anion.",
    applications:"Industrial synthesis of salicylic acid, the precursor to aspirin (acetylsalicylic acid).",
    not_occur:"Does not occur at atmospheric pressure (requires 4-7 atm). Fails with cresols (substituted phenols give mixtures). Does not work with alcohols. Requires high temperature (125°C) - fails at room temperature."
  },
  {
    id:"r9", name:"Fries Rearrangement", class_level:12,
    reactants:"C₆H₅OH,CH₃COCl,AlCl₃",
    products:"HOC₆H₄COCH₃",
    equation:"Phenyl acetate → o-/p-Hydroxyacetophenone (AlCl₃, heat)",
    conditions:"AlCl₃, heat",
    explanation:"Phenyl esters rearrange in the presence of AlCl₃ to hydroxyaryl ketones. The ester is converted to an acylium–AlCl₃ complex, which then undergoes intramolecular electrophilic attack on the phenyl ring at ortho or para positions. The product is a hydroxy ketone.",
    applications:"Synthesis of hydroxyaryl ketones used in flavours, pharmaceuticals, and sunscreen molecules.",
    not_occur:"Does not occur with phenyl ethers (no ester group). Fails without Lewis acid catalyst. Does not work with aryl esters having electron-withdrawing groups. Low temperature favors para product, high temperature ortho - wrong conditions give poor yields."
  },
  {
    id:"r10", name:"Aldol Condensation", class_level:12,
    reactants:"CH₃CHO,NaOH",
    products:"CH₃CH(OH)CH₂CHO",
    equation:"2CH₃CHO → CH₃CH(OH)CH₂CHO (NaOH, H₂O)",
    conditions:"Dilute NaOH, room temperature",
    explanation:"NaOH abstracts an alpha-H from acetaldehyde to form an enolate. The enolate acts as a nucleophile and attacks the carbonyl carbon of a second acetaldehyde molecule. This gives a beta-hydroxy aldehyde (aldol product). On heating, water is eliminated to form an alpha,beta-unsaturated aldehyde (condensation product).",
    applications:"Key reaction in biological metabolism (glycolysis/gluconeogenesis). Used in synthesis of perfumes, flavours, and pharmaceuticals.",
    not_occur:"Does not occur with aldehydes having no α-hydrogen (formaldehyde, benzaldehyde - undergo Cannizzaro instead). Fails with strong base at high temperature (resin formation). Does not work with ketones having no α-hydrogen. Sterically hindered ketones react slowly or not at all."
  },
  {
    id:"r11", name:"Diazotization of Aniline", class_level:12,
    reactants:"C₆H₅NH₂,HNO₂,HCl",
    products:"C₆H₅N₂Cl",
    equation:"C₆H₅NH₂ + NaNO₂ + HCl → C₆H₅N₂⁺Cl⁻ + NaCl + H₂O",
    conditions:"0–5°C, NaNO₂/HCl",
    explanation:"Aniline is dissolved in excess HCl. Sodium nitrite is added below 5°C, generating nitrous acid (HNO₂) in situ. Nitrous acid nitrosonates the amine: the lone pair of nitrogen attacks NO⁺, forming an N-nitroso intermediate, which rearranges and loses water to give the diazonium ion (–N≡N⁺).",
    applications:"The diazonium salt is an intermediate in azo dye synthesis, Sandmeyer reaction, and pharmaceutical manufacturing.",
    not_occur:"Does not occur above 5°C (diazonium salt decomposes explosively). Fails with aliphatic amines (unstable diazonium salts). Does not work without excess acid. Secondary and tertiary aromatic amines give different products (N-nitroso compounds)."
  },
  {
    id:"r12", name:"Iodoform Test (Oxidation)", class_level:12,
    reactants:"CH₃COCH₃,I₂,NaOH",
    products:"CHI₃,CH₃COONa",
    equation:"CH₃COCH₃ + 3I₂ + 4NaOH → CHI₃ + CH₃COONa + 3NaI + 3H₂O",
    conditions:"NaOH (aq), I₂",
    explanation:"NaOH generates hypoiodite (IO⁻), which iodinates the methyl group next to the carbonyl three times (triiodomethyl group forms). The resulting –CI₃ group is a good leaving group, and NaOH cleaves the bond to give iodoform (CHI₃) — a yellow precipitate — and sodium acetate.",
    applications:"Qualitative test for methyl ketones and secondary alcohols with CH₃–CHOH– group. Iodoform smells antiseptic; historically used as antiseptic.",
    not_occur:"Does not occur with aldehydes (except acetaldehyde) or ketones without CH₃-CO- group. Fails with tertiary alcohols. Does not work with bromine or chlorine under same conditions (iodine is specific). Benzophenone does not give this test."
  },
  {
    id:"r13", name:"Finkelstein Reaction", class_level:12,
    reactants:"CH₃Cl,NaI",
    products:"CH₃I,NaCl",
    equation:"CH₃Cl + NaI → CH₃I + NaCl (acetone)",
    conditions:"Dry acetone, heat",
    explanation:"This is an SN2 nucleophilic substitution. NaI is soluble in acetone while NaCl is not. Iodide ion displaces chloride from the methyl chloride by backside attack. NaCl precipitates driving the equilibrium forward (Le Chatelier's principle).",
    applications:"Preparation of alkyl iodides from alkyl chlorides/bromides. Iodides are more reactive in many organic reactions.",
    not_occur:"Does not occur with tertiary alkyl halides (elimination dominates). Fails in protic solvents (water, alcohol). Does not work with aryl halides or vinyl halides. Requires dry acetone - moisture inhibits the reaction."
  },
  {
    id:"r14", name:"Swarts Reaction", class_level:12,
    reactants:"CH₃Cl,AgF",
    products:"CH₃F,AgCl",
    equation:"CH₃Cl + AgF → CH₃F + AgCl",
    conditions:"AgF or SbF₃, heat",
    explanation:"Silver fluoride or antimony trifluoride replaces chlorine with fluorine via nucleophilic substitution. The driving force is the insolubility and stability of AgCl (or SbCl₃) formed. Fluoride is small and very electronegative, forming a strong C–F bond.",
    applications:"Used in preparation of organofluorine compounds, refrigerants (Freons), and pharmaceuticals. C–F bond imparts metabolic stability to drugs.",
    not_occur:"Does not occur with NaF or KF (insufficient nucleophilicity). Fails with tertiary alkyl halides. Does not work with aryl halides. Requires heavy metal fluorides (AgF, SbF₃, HgF₂) - simple alkali metal fluorides are ineffective."
  },
  {
    id:"r15", name:"Perkin Condensation", class_level:12,
    reactants:"C₆H₅CHO,CH₃COCl",
    products:"C₆H₅CH=CHCOOH",
    equation:"C₆H₅CHO + (CH₃CO)₂O → C₆H₅CH=CHCOOH + CH₃COOH",
    conditions:"Sodium acetate, acetic anhydride, heat",
    explanation:"Sodium acetate generates an enolate (nucleophile) from acetic anhydride. This enolate attacks the benzaldehyde carbonyl. After an aldol-type addition, water is eliminated (from the OH and adjacent alpha-H). The product is cinnamic acid — an alpha,beta-unsaturated carboxylic acid.",
    applications:"Synthesis of cinnamic acid and its derivatives. Cinnamic acid is used in perfumes, flavours, and as a starting material for pharmaceuticals.",
    not_occur:"Does not occur with aliphatic aldehydes (self-condensation dominates). Fails without α-hydrogen in the acid anhydride. Does not work with ketones (steric hindrance). Requires weak base (sodium acetate) - strong bases cause side reactions."
  },
  {
    id:"r16", name:"Benzoin Condensation", class_level:12,
    reactants:"C₆H₅CHO,CHCl₃",
    products:"C₆H₅CHOHCOC₆H₅",
    equation:"2C₆H₅CHO → C₆H₅CH(OH)COC₆H₅ (KCN catalyst)",
    conditions:"KCN (aq-ethanolic), heat",
    explanation:"Cyanide ion acts as nucleophilic catalyst. CN⁻ attacks one benzaldehyde molecule to form a cyanohydrin anion (the umpolung intermediate). This nucleophile attacks the carbonyl of a second benzaldehyde, and CN⁻ is then expelled to give benzoin.",
    applications:"Synthesis of benzoin for use in pharmaceuticals, fragrance, and as a photoinitiator in polymer chemistry.",
    not_occur:"Does not occur with aliphatic aldehydes (enolizable, undergo aldol). Fails with aldehydes having electron-withdrawing groups. Does not work without cyanide catalyst (thiamine can be used instead). Aldehydes with α-hydrogen give Cannizzaro reaction instead."
  },
  {
    id:"r17", name:"Cannizzaro Reaction", class_level:12,
    reactants:"HCHO,NaOH",
    products:"CH₃OH,HCOONa",
    equation:"2HCHO + NaOH → CH₃OH + HCOONa",
    conditions:"Conc. NaOH, no alpha-H",
    explanation:"In concentrated NaOH, two molecules of formaldehyde undergo simultaneous oxidation and reduction (disproportionation). One molecule is oxidised to formate (reducing agent), and the other is reduced to methanol (oxidising agent). Requires an aldehyde with no alpha-H so aldol condensation cannot compete.",
    applications:"Industrial production of methanol and formic acid. Key in understanding redox reactions of carbonyl compounds.",
    not_occur:"Does not occur with aldehydes having α-hydrogen (aldol condensation dominates). Fails with dilute NaOH. Does not work with ketones. Benzaldehyde with electron-donating groups reacts slowly."
  },
  {
    id:"r18", name:"Hofmann Bromamide Reaction", class_level:12,
    reactants:"CH₃COCl,NaOH,Br₂",
    products:"CH₃NH₂,CO₂",
    equation:"RCONH₂ + Br₂ + 4NaOH → RNH₂ + Na₂CO₃ + 2NaBr + 2H₂O",
    conditions:"Br₂, NaOH (aq), heat",
    explanation:"Bromine in NaOH converts the amide to an N-bromoamide. Base removes the remaining N–H to form an anion. A 1,2-shift (rearrangement) of the R group from C to N occurs (with loss of bromide), forming an isocyanate intermediate. Water then hydrolyses the isocyanate to give an amine with one fewer carbon.",
    applications:"Preparation of primary amines from amides, with carbon chain shortening by one. Used in synthesis of amino acids and pharmaceuticals.",
    not_occur:"Does not occur with N-substituted amides (secondary, tertiary). Fails with urea (different products). Does not work with acid chlorides or esters. Requires aqueous NaOH - alcoholic NaOH gives different products."
  },
  {
    id:"r19", name:"Mendius Reduction", class_level:12,
    reactants:"C₆H₅CN,Na",
    products:"C₆H₅CH₂NH₂",
    equation:"RCN + 2[H₂] → RCH₂NH₂ (Na + C₂H₅OH or H₂/Ni)",
    conditions:"Na/C₂H₅OH or H₂/Ni",
    explanation:"The nitrile (–C≡N) is reduced in two steps: first to an imine (–CH=NH), then to a primary amine (–CH₂–NH₂). Sodium in ethanol generates nascent hydrogen (Na + C₂H₅OH → NaOC₂H₅ + H). The amine has one more carbon than the corresponding acid from which CN was derived.",
    applications:"Preparation of primary amines from nitriles. Useful in synthesis of amino acids and pharmaceutical intermediates.",
    not_occur:"Does not occur with isocyanides (isonitriles). Fails with partial reduction conditions (stops at imine). Does not work with aqueous Na (nitrile hydrolysis occurs). Requires anhydrous conditions - moisture inhibits reduction."
  },
  {
    id:"r20", name:"Gattermann-Koch Reaction", class_level:12,
    reactants:"C₆H₆,CO",
    products:"C₆H₅CHO",
    equation:"C₆H₆ + CO + HCl → C₆H₅CHO + HCl (AlCl₃/CuCl)",
    conditions:"CO + HCl, AlCl₃ + CuCl, high pressure",
    explanation:"Carbon monoxide and HCl in the presence of AlCl₃ and CuCl form formyl cation (HCO⁺), which is a powerful electrophile. This electrophile undergoes Friedel-Crafts type attack on the benzene ring, introducing a –CHO group. The result is benzaldehyde.",
    applications:"Direct formylation of arenes to give aromatic aldehydes. Industrial route to benzaldehyde for flavouring and chemical synthesis.",
    not_occur:"Does not occur with activated aromatic rings (phenols, anilines - coordinate with catalyst). Fails with deactivated rings (nitrobenzene). Does not work without CuCl co-catalyst. Requires high pressure CO - fails at atmospheric pressure."
  },
  {
    id:"r21", name:"Combustion of Methane", class_level:9,
    reactants:"CH₄,O₂",
    products:"CO₂,H₂O",
    equation:"CH₄ + 2O₂ → CO₂ + 2H₂O",
    conditions:"Ignition, excess O₂",
    explanation:"Methane undergoes complete combustion in the presence of excess oxygen. The C–H bonds are broken and new C=O and O–H bonds form, releasing a large amount of heat energy (exothermic). This is a free-radical chain reaction at high temperature.",
    applications:"Natural gas (mainly methane) used for cooking, heating, and electricity generation worldwide. CNG in vehicles.",
    not_occur:"Does not occur without ignition source (spark/flame). Fails with limited oxygen (incomplete combustion produces CO). Does not occur at room temperature without activation energy. Requires sufficient oxygen for complete combustion."
  },
  {
    id:"r22", name:"Halogenation of Methane (Free Radical)", class_level:11,
    reactants:"CH₄,Cl₂",
    products:"CH₃Cl,HCl",
    equation:"CH₄ + Cl₂ → CH₃Cl + HCl (hν or heat)",
    conditions:"UV light or high temperature",
    explanation:"A free radical substitution reaction. UV light or heat homolyticaly cleaves Cl₂ into two Cl• radicals (initiation). A chlorine radical abstracts H from CH₄ forming CH₃• and HCl (propagation step 1). CH₃• then reacts with Cl₂ to give CH₃Cl and another Cl• (propagation step 2). The chain continues until termination.",
    applications:"Industrial production of chloromethanes (CH₃Cl, CH₂Cl₂, CHCl₃, CCl₄) as solvents and intermediates.",
    not_occur:"Does not occur in dark at room temperature. Fails without UV light or heat (no radical initiation). Does not occur with fluorine in controlled manner (too reactive, explosion risk). Iodination is not favorable (HI is strong reducing agent)."
  },
  
  // ============================================================
  // CLASS 9-10 CBSE/NCERT BASIC REACTIONS
  // ============================================================
  
  // COMBINATION REACTIONS
  {
    id:"r23", name:"Formation of Calcium Oxide", class_level:9,
    reactants:"Ca,O₂",
    products:"CaO",
    equation:"2Ca + O₂ → 2CaO",
    conditions:"Heat",
    explanation:"Calcium metal burns in oxygen with a bright white flame to form calcium oxide (quicklime). This is a combination reaction where two substances combine to form a single product. The reaction is highly exothermic and releases bright white light.",
    applications:"Used in cement manufacture, steel making, and as a drying agent. Calcium oxide is also used in water treatment and flue gas desulfurization.",
    not_occur:"Does not occur at room temperature (requires ignition). Fails in absence of oxygen. Does not occur with calcium carbonate (requires decomposition, not combination). Less reactive metals like iron require higher temperatures."
  },
  {
    id:"r24", name:"Formation of Magnesium Oxide", class_level:9,
    reactants:"Mg,O₂",
    products:"MgO",
    equation:"2Mg + O₂ → 2MgO",
    conditions:"Burning/Heat",
    explanation:"Magnesium ribbon burns with a dazzling white flame when heated in air, forming magnesium oxide. This combination reaction releases a large amount of heat and light energy. The white powder formed is basic magnesium oxide.",
    applications:"Magnesium oxide is used as an antacid, in refractory materials for furnace linings, and as a supplement for magnesium deficiency.",
    not_occur:"Does not occur at room temperature (requires ignition). Fails in nitrogen atmosphere (Mg also reacts with N₂ at high temp). Does not occur with moist magnesium (surface oxide layer protects). Requires clean magnesium surface."
  },
  {
    id:"r25", name:"Formation of Calcium Hydroxide", class_level:9,
    reactants:"CaO,H₂O",
    products:"Ca(OH)₂",
    equation:"CaO + H₂O → Ca(OH)₂",
    conditions:"Room temperature",
    explanation:"Calcium oxide (quicklime) reacts vigorously with water to form calcium hydroxide (slaked lime). This reaction is highly exothermic and produces hissing sounds. The product is alkaline and used in whitewashing.",
    applications:"Used in whitewashing walls, in the manufacture of bleaching powder, and as a cheap base in many chemical industries.",
    not_occur:"Does not occur with calcium carbonate (insoluble). Fails with calcium sulfate (different product). Does not react with oils or organic solvents. Requires water - reaction is slow with atmospheric moisture only."
  },
  {
    id:"r26", name:"Formation of Ammonia", class_level:10,
    reactants:"N₂,H₂",
    products:"NH₃",
    equation:"N₂ + 3H₂ ⇌ 2NH₃",
    conditions:"High pressure (200-300 atm), 450°C, Iron catalyst",
    explanation:"Nitrogen and hydrogen combine in the Haber's process to form ammonia. This reversible reaction is the basis of the fertilizer industry. The iron catalyst speeds up the reaction without being consumed.",
    applications:"Used to manufacture nitrogenous fertilizers like urea, ammonium nitrate, and ammonium phosphate. Also used in refrigeration and chemical synthesis.",
    not_occur:"Does not occur at room temperature (very slow kinetics). Fails without catalyst (extremely slow). Does not proceed at atmospheric pressure (low yield). Requires 1:3 N₂:H₂ ratio - other ratios give poor conversion."
  },
  
  // DECOMPOSITION REACTIONS
  {
    id:"r27", name:"Decomposition of Calcium Carbonate", class_level:9,
    reactants:"CaCO₃",
    products:"CaO,CO₂",
    equation:"CaCO₃ → CaO + CO₂",
    conditions:"Strong heat (>825°C)",
    explanation:"Calcium carbonate decomposes on strong heating to give calcium oxide and carbon dioxide gas. This thermal decomposition is used to produce quicklime on an industrial scale. The CO₂ gas turns limewater milky.",
    applications:"Used in cement manufacture, extraction of metals, and production of lime for agriculture and construction.",
    not_occur:"Does not occur below 825°C. Fails in open system with high CO₂ pressure (Le Chatelier's principle). Does not decompose at room temperature. Requires continuous heat supply - stops if temperature drops."
  },
  {
    id:"r28", name:"Decomposition of Hydrogen Peroxide", class_level:10,
    reactants:"H₂O₂",
    products:"H₂O,O₂",
    equation:"2H₂O₂ → 2H₂O + O₂",
    conditions:"MnO₂ catalyst or heat",
    explanation:"Hydrogen peroxide decomposes into water and oxygen gas. The reaction is catalyzed by manganese dioxide (MnO₂). Oxygen gas is released as bubbles, which can be tested with a glowing splint that relights.",
    applications:"Used as a bleaching agent, disinfectant, and in rocket propulsion. The oxygen released is used in breathing apparatus.",
    not_occur:"Does not occur at room temperature without catalyst (very slow). Fails with strong acids (stabilizes H₂O₂). Does not decompose in dark at low temperature. Some metal ions (Fe³⁺) catalyze decomposition - storage containers must be clean."
  },
  {
    id:"r29", name:"Decomposition of Ferrous Sulfate", class_level:10,
    reactants:"FeSO₄",
    products:"Fe₂O₃,SO₂,SO₃",
    equation:"2FeSO₄ → Fe₂O₃ + SO₂ + SO₃",
    conditions:"Strong heat",
    explanation:"Green crystals of ferrous sulfate decompose on heating to form ferric oxide (brown), sulfur dioxide, and sulfur trioxide. The color change from green to brown indicates the formation of iron(III) oxide.",
    applications:"Used to demonstrate decomposition reactions and to produce sulfur dioxide in laboratories. Ferric oxide is used as a pigment.",
    not_occur:"Does not occur at room temperature (requires strong heating). Fails in aqueous solution (different decomposition). Does not occur with ferric sulfate (already oxidized). Requires anhydrous ferrous sulfate."
  },
  {
    id:"r30", name:"Decomposition of Lead Nitrate", class_level:10,
    reactants:"Pb(NO₃)₂",
    products:"PbO,NO₂,O₂",
    equation:"2Pb(NO₃)₂ → 2PbO + 4NO₂ + O₂",
    conditions:"Heat",
    explanation:"Colorless lead nitrate crystals decompose on heating to form lead oxide (yellow), brown nitrogen dioxide gas, and oxygen. The brown fumes of NO₂ are characteristic of this reaction.",
    applications:"Used in laboratory preparation of nitrogen dioxide and to demonstrate thermal decomposition of nitrates."
  },
  
  // DISPLACEMENT REACTIONS
  {
    id:"r31", name:"Zinc with Copper Sulfate", class_level:9,
    reactants:"Zn,CuSO₄",
    products:"ZnSO₄,Cu",
    equation:"Zn + CuSO₄ → ZnSO₄ + Cu",
    conditions:"Aqueous solution, room temperature",
    explanation:"More reactive zinc displaces copper from copper sulfate solution. The blue color of copper sulfate fades as colorless zinc sulfate forms, and reddish-brown copper metal deposits on the zinc strip. This proves zinc is more reactive than copper.",
    applications:"Used in metallurgy for extraction of metals, in electric batteries (Daniell cell), and to demonstrate the reactivity series of metals.",
    not_occur:"Does not occur if zinc is coated with oxide/grease (surface must be clean). Fails with solid CuSO₄ (needs aqueous solution). Does not occur with less reactive metals than copper (Ag, Au). Reverse reaction (Cu + ZnSO₄) does not occur."
  },
  {
    id:"r32", name:"Iron with Copper Sulfate", class_level:9,
    reactants:"Fe,CuSO₄",
    products:"FeSO₄,Cu",
    equation:"Fe + CuSO₄ → FeSO₄ + Cu",
    conditions:"Aqueous solution",
    explanation:"Iron being more reactive than copper displaces it from copper sulfate solution. The blue solution turns pale green due to formation of iron(II) sulfate, and copper gets deposited on the iron nail. This is the basis of the 'copper plating' experiment.",
    applications:"Used in extraction of less reactive metals, in electroplating, and to demonstrate metal reactivity series in classroom experiments.",
    not_occur:"Does not occur with solid CuSO₄ (needs aqueous solution). Fails if iron is coated with grease/paint. Does not occur with less reactive metals (Cu, Ag, Au). Reverse reaction (Cu + FeSO₄) does not occur."
  },
  {
    id:"r33", name:"Aluminium with Iron Oxide", class_level:10,
    reactants:"Al,Fe₂O₃",
    products:"Al₂O₃,Fe",
    equation:"2Al + Fe₂O₃ → Al₂O₃ + 2Fe",
    conditions:"Ignition by magnesium ribbon",
    explanation:"This is the thermite reaction. Aluminium being more reactive than iron reduces iron oxide to molten iron. The reaction is highly exothermic and produces temperatures around 2500°C, sufficient to melt the iron produced.",
    applications:"Used for welding railway tracks, repairing heavy machinery, and in incendiary devices. Also used to extract pure metals from their oxides.",
    not_occur:"Does not occur at room temperature (requires high activation energy). Fails without ignition source (Mg ribbon). Does not occur with wet aluminum (oxide layer prevents reaction). Powdered aluminum required - solid pieces won't react."
  },
  
  // DOUBLE DISPLACEMENT REACTIONS
  {
    id:"r34", name:"Barium Chloride with Sodium Sulfate", class_level:9,
    reactants:"BaCl₂,Na₂SO₄",
    products:"BaSO₄,NaCl",
    equation:"BaCl₂ + Na₂SO₄ → BaSO₄ + 2NaCl",
    conditions:"Aqueous solution",
    explanation:"When barium chloride and sodium sulfate solutions are mixed, a white precipitate of barium sulfate forms. This is a double displacement reaction where the ions exchange partners. BaSO₄ is insoluble in water and acids.",
    applications:"Used as a test for sulfate ions (SO₄²⁻) in qualitative analysis. Barium sulfate is used in X-ray imaging (barium meal) due to its insolubility.",
    not_occur:"Does not occur with solid reactants (need aqueous solutions). Fails with soluble sulfates that form complexes. Does not occur if BaCl₂ solution is acidic (different products). Requires ionic form of both compounds."
  },
  {
    id:"r35", name:"Silver Nitrate with Sodium Chloride", class_level:9,
    reactants:"AgNO₃,NaCl",
    products:"AgCl,NaNO₃",
    equation:"AgNO₃ + NaCl → AgCl + NaNO₃",
    conditions:"Aqueous solution",
    explanation:"Silver nitrate reacts with sodium chloride to form a curdy white precipitate of silver chloride. This is a double displacement reaction and a precipitation reaction. AgCl turns grey in sunlight due to decomposition.",
    applications:"Used as a test for chloride ions (Cl⁻) in qualitative analysis. Silver chloride is used in photographic films due to its light sensitivity.",
    not_occur:"Does not occur with solid reactants (need aqueous solutions). Fails with complex chlorides that don't dissociate. Does not occur in presence of strong ammonia (forms complex). Requires free Cl⁻ ions."
  },
  {
    id:"r36", name:"Lead Nitrate with Potassium Iodide", class_level:10,
    reactants:"Pb(NO₃)₂,KI",
    products:"PbI₂,KNO₃",
    equation:"Pb(NO₃)₂ + 2KI → PbI₂ + 2KNO₃",
    conditions:"Aqueous solution",
    explanation:"When colorless lead nitrate and potassium iodide solutions are mixed, a bright yellow precipitate of lead iodide forms. This 'golden rain' experiment is a classic double displacement reaction. The precipitate dissolves on heating and recrystallizes on cooling.",
    applications:"Used as a test for lead(II) ions or iodide ions. Lead iodide is used in solar cells and as a pigment.",
    not_occur:"Does not occur with solid reactants (need aqueous solutions). Fails with excess KI (forms soluble complex). Does not occur with lead(IV) compounds. Requires 2:1 ratio of KI to Pb(NO₃)₂."
  },
  
  // NEUTRALIZATION REACTIONS
  {
    id:"r37", name:"HCl with NaOH", class_level:10,
    reactants:"HCl,NaOH",
    products:"NaCl,H₂O",
    equation:"HCl + NaOH → NaCl + H₂O",
    conditions:"Aqueous solution",
    explanation:"Hydrochloric acid (strong acid) reacts with sodium hydroxide (strong base) to form sodium chloride (salt) and water. This is a neutralization reaction where H⁺ from acid combines with OH⁻ from base to form water. The solution becomes neutral (pH 7).",
    applications:"Used in antacid tablets, treatment of acidic soil, and in chemical industries to produce salts. Also used to adjust pH in swimming pools.",
    not_occur:"Does not occur in non-aqueous solvents (no free H⁺/OH⁻ ions). Fails if one reactant is in solid state (needs dissolution). Does not occur with insoluble bases like Cu(OH)₂ (slow reaction). Requires ionic form of reactants."
  },
  {
    id:"r38", name:"Sulfuric Acid with Copper Oxide", class_level:10,
    reactants:"H₂SO₄,CuO",
    products:"CuSO₄,H₂O",
    equation:"H₂SO₄ + CuO → CuSO₄ + H₂O",
    conditions:"Warm conditions",
    explanation:"Black copper oxide dissolves in dilute sulfuric acid to form blue copper sulfate solution and water. This is a neutralization reaction between a basic oxide and an acid. The color change from black to blue indicates the reaction.",
    applications:"Used to prepare copper sulfate crystals, in electroplating, and as a fungicide in agriculture.",
    not_occur:"Does not occur with concentrated H₂SO₄ (different reaction, SO₂ produced). Fails with copper metal (needs oxidation). Does not occur at room temperature (needs warming). Requires dilute acid, not concentrated."
  },
  {
    id:"r39", name:"Acetic Acid with Sodium Hydroxide", class_level:10,
    reactants:"CH₃COOH,NaOH",
    products:"CH₃COONa,H₂O",
    equation:"CH₃COOH + NaOH → CH₃COONa + H₂O",
    conditions:"Aqueous solution",
    explanation:"Weak acetic acid (vinegar) reacts with strong sodium hydroxide to form sodium acetate and water. This is a neutralization reaction. The heat released is less than strong acid-strong base neutralization due to weak acid.",
    applications:"Used in food preservation, buffer solutions, and in the production of dyes and pharmaceuticals."
  },
  
  // COMBUSTION REACTIONS
  {
    id:"r40", name:"Combustion of Hydrogen", class_level:9,
    reactants:"H₂,O₂",
    products:"H₂O",
    equation:"2H₂ + O₂ → 2H₂O",
    conditions:"Ignition/spark",
    explanation:"Hydrogen burns in oxygen with a pale blue flame to form water. This is a highly exothermic combustion reaction. The 'pop' sound when burning hydrogen is used as a test for hydrogen gas. The reaction releases large amounts of energy.",
    applications:"Used in oxy-hydrogen torches for cutting and welding metals. Hydrogen fuel cells use this reaction to generate electricity for vehicles.",
    not_occur:"Does not occur at room temperature without spark (kinetically stable mixture). Fails with limited oxygen (incomplete combustion). Does not occur with inert gases. Requires 2:1 H₂:O₂ ratio for complete combustion."
  },
  {
    id:"r41", name:"Combustion of Sulfur", class_level:9,
    reactants:"S,O₂",
    products:"SO₂",
    equation:"S + O₂ → SO₂",
    conditions:"Burning",
    explanation:"Sulfur burns in oxygen with a blue flame to form sulfur dioxide gas. This is a combustion reaction. SO₂ has a choking smell of burning sulfur and is acidic in nature, turning moist litmus paper red.",
    applications:"Used in the manufacture of sulfuric acid (Contact process), as a preservative in dried fruits, and in bleaching wool and silk."
  },
  {
    id:"r42", name:"Combustion of Magnesium", class_level:9,
    reactants:"Mg,O₂",
    products:"MgO",
    equation:"2Mg + O₂ → 2MgO",
    conditions:"Burning",
    explanation:"Magnesium burns with a dazzling white flame in oxygen, forming magnesium oxide. This combustion reaction releases very bright light and is used in flash photography and fireworks. The white ash formed is basic magnesium oxide.",
    applications:"Used in flash powders, fireworks, and emergency flares. Magnesium oxide is used as a refractory material and antacid."
  },
  
  // ============================================================
  // BASIC ELEMENT REACTIONS (METALS WITH ACIDS & WATER)
  // ============================================================
  
  // METALS WITH DILUTE HCl
  {
    id:"r43", name:"Zinc with Dilute HCl", class_level:10,
    reactants:"Zn,HCl",
    products:"ZnCl₂,H₂",
    equation:"Zn + 2HCl → ZnCl₂ + H₂",
    conditions:"Room temperature",
    explanation:"Zinc metal reacts with dilute hydrochloric acid to form zinc chloride and hydrogen gas. Bubbles of hydrogen gas are evolved. This is a single displacement reaction where zinc displaces hydrogen from the acid. Zinc is above hydrogen in the reactivity series.",
    applications:"Used in laboratory preparation of hydrogen gas. The reactivity of metals with acids is used to determine their position in the reactivity series.",
    not_occur:"Does not occur with concentrated HCl (different reaction pathway). Fails with copper, silver, gold (below hydrogen in reactivity series). Does not occur if zinc surface is passivated. Lead reacts slowly due to insoluble PbCl₂ coating."
  },
  {
    id:"r44", name:"Iron with Dilute HCl", class_level:10,
    reactants:"Fe,HCl",
    products:"FeCl₂,H₂",
    equation:"Fe + 2HCl → FeCl₂ + H₂",
    conditions:"Room temperature",
    explanation:"Iron reacts slowly with dilute hydrochloric acid to form ferrous chloride (light green solution) and hydrogen gas. The reaction is less vigorous than zinc. This confirms iron is less reactive than zinc but more reactive than hydrogen.",
    applications:"Used to demonstrate the reactivity series and to prepare ferrous salts. Iron containers should not be used to store acids.",
    not_occur:"Does not occur with concentrated HCl (forms FeCl₃). Fails with oxidizing acids (HNO₃, concentrated H₂SO₄). Does not occur if iron is rusted (oxide layer protects). Very slow with cold dilute acid."
  },
  {
    id:"r45", name:"Magnesium with Dilute HCl", class_level:10,
    reactants:"Mg,HCl",
    products:"MgCl₂,H₂",
    equation:"Mg + 2HCl → MgCl₂ + H₂",
    conditions:"Room temperature",
    explanation:"Magnesium reacts vigorously with dilute hydrochloric acid, producing magnesium chloride and hydrogen gas. The reaction is highly exothermic. Magnesium is highly reactive and displaces hydrogen rapidly from acids.",
    applications:"Used to prepare hydrogen gas in laboratories. The vigorous reaction demonstrates the high position of magnesium in the reactivity series.",
    not_occur:"Does not occur with concentrated HNO₃ (passivation, NO₂ formed). Fails with very dilute acid (slow). Does not occur if magnesium is coated with oxide (needs cleaning). Reaction stops if acid is consumed."
  },
  {
    id:"r46", name:"Aluminium with Dilute HCl", class_level:10,
    reactants:"Al,HCl",
    products:"AlCl₃,H₂",
    equation:"2Al + 6HCl → 2AlCl₃ + 3H₂",
    conditions:"Room temperature (after removing oxide layer)",
    explanation:"Aluminium reacts with dilute hydrochloric acid to form aluminium chloride and hydrogen gas. Initially, the reaction may be slow due to the protective oxide layer, but once removed, the reaction proceeds vigorously. Aluminium is more reactive than it appears due to this protective layer.",
    applications:"Used in the production of hydrogen and aluminium salts. Important in understanding why aluminium is corrosion-resistant despite being highly reactive."
  },
  
  // METALS WITH DILUTE H₂SO₄
  {
    id:"r47", name:"Zinc with Dilute H₂SO₄", class_level:10,
    reactants:"Zn,H₂SO₄",
    products:"ZnSO₄,H₂",
    equation:"Zn + H₂SO₄ → ZnSO₄ + H₂",
    conditions:"Room temperature",
    explanation:"Zinc reacts with dilute sulfuric acid to form zinc sulfate (colorless solution) and hydrogen gas. This is similar to the reaction with HCl. The hydrogen gas can be collected and tested with a burning splint.",
    applications:"Laboratory preparation of hydrogen gas. Zinc sulfate is used as a dietary supplement and in agriculture as a fertilizer."
  },
  {
    id:"r48", name:"Iron with Dilute H₂SO₄", class_level:10,
    reactants:"Fe,H₂SO₄",
    products:"FeSO₄,H₂",
    equation:"Fe + H₂SO₄ → FeSO₄ + H₂",
    conditions:"Room temperature",
    explanation:"Iron reacts with dilute sulfuric acid to form ferrous sulfate (pale green solution) and hydrogen gas. The reaction is moderate in speed. Concentrated sulfuric acid would produce different products (SO₂ instead of H₂).",
    applications:"Used to prepare ferrous sulfate (green vitriol) which is used as a fertilizer, in water treatment, and as a dietary supplement for iron."
  },
  {
    id:"r49", name:"Magnesium with Dilute H₂SO₄", class_level:10,
    reactants:"Mg,H₂SO₄",
    products:"MgSO₄,H₂",
    equation:"Mg + H₂SO₄ → MgSO₄ + H₂",
    conditions:"Room temperature",
    explanation:"Magnesium reacts vigorously with dilute sulfuric acid, producing magnesium sulfate (Epsom salt) and hydrogen gas. The reaction is highly exothermic and produces hydrogen rapidly.",
    applications:"Magnesium sulfate is used as Epsom salt for medicinal purposes, in agriculture as a fertilizer, and in fireproofing."
  },
  
  // METALS WITH WATER
  {
    id:"r50", name:"Sodium with Cold Water", class_level:10,
    reactants:"Na,H₂O",
    products:"NaOH,H₂",
    equation:"2Na + 2H₂O → 2NaOH + H₂",
    conditions:"Room temperature",
    explanation:"Sodium reacts vigorously with cold water, forming sodium hydroxide and hydrogen gas. The reaction is highly exothermic. Sodium melts into a silvery ball that darts around on the water surface. The solution turns pink with phenolphthalein, showing it is alkaline.",
    applications:"Demonstrates the high reactivity of alkali metals. Used to prepare sodium hydroxide and hydrogen. Caution: Sodium must be handled carefully due to violent reaction.",
    not_occur:"Does not occur with heavy metals (Cu, Ag, Au - no reaction). Fails with hot water (reaction too violent, explosion risk). Does not occur if sodium is coated with oxide (must be freshly cut). Kerosene-protected sodium must be cleaned before use."
  },
  {
    id:"r51", name:"Calcium with Cold Water", class_level:10,
    reactants:"Ca,H₂O",
    products:"Ca(OH)₂,H₂",
    equation:"Ca + 2H₂O → Ca(OH)₂ + H₂",
    conditions:"Room temperature",
    explanation:"Calcium reacts less vigorously than sodium with cold water, forming calcium hydroxide (limewater) and hydrogen gas. The reaction produces enough heat to make hydrogen burn with a orange-red flame. Calcium hydroxide solution is weakly alkaline.",
    applications:"Used to prepare calcium hydroxide (slaked lime) and demonstrate the reactivity of alkaline earth metals. Less violent than sodium reaction."
  },
  {
    id:"r52", name:"Magnesium with Hot Water", class_level:10,
    reactants:"Mg,H₂O",
    products:"Mg(OH)₂,H₂",
    equation:"Mg + 2H₂O → Mg(OH)₂ + H₂",
    conditions:"Hot water/Steam",
    explanation:"Magnesium reacts slowly with cold water but reacts readily with hot water or steam to form magnesium hydroxide and hydrogen gas. This shows magnesium is less reactive than calcium but still reacts with water when heated. The reaction is used to demonstrate steam reactions.",
    applications:"Demonstrates the relative reactivity of metals with water. Magnesium hydroxide is used as an antacid (milk of magnesia)."
  },
  {
    id:"r53", name:"Iron with Steam", class_level:10,
    reactants:"Fe,H₂O",
    products:"Fe₃O₄,H₂",
    equation:"3Fe + 4H₂O → Fe₃O₄ + 4H₂",
    conditions:"Red hot iron + steam",
    explanation:"When red-hot iron is passed over steam, it reacts to form tri-iron tetroxide (magnetite, Fe₃O₄) and hydrogen gas. This reaction shows that iron can react with steam but not with cold or hot water. The reaction is reversible.",
    applications:"Used in the Haber process to produce hydrogen. Demonstrates that iron is less reactive than magnesium, calcium, and sodium."
  },
  
  // COPPER WITH CONCENTRATED ACIDS
  {
    id:"r54", name:"Copper with Concentrated H₂SO₄", class_level:10,
    reactants:"Cu,H₂SO₄",
    products:"CuSO₄,SO₂,H₂O",
    equation:"Cu + 2H₂SO₄ → CuSO₄ + SO₂ + 2H₂O",
    conditions:"Heat",
    explanation:"Copper, being below hydrogen in the reactivity series, does not react with dilute acids. However, with hot concentrated sulfuric acid, copper is oxidized to copper sulfate, and sulfuric acid is reduced to sulfur dioxide. Brown fumes of SO₂ are evolved.",
    applications:"Used to prepare copper sulfate in laboratories. Demonstrates the oxidizing nature of concentrated sulfuric acid."
  },
  {
    id:"r55", name:"Zinc with Concentrated H₂SO₄", class_level:10,
    reactants:"Zn,H₂SO₄",
    products:"ZnSO₄,SO₂,H₂O",
    equation:"Zn + 2H₂SO₄ → ZnSO₄ + SO₂ + 2H₂O",
    conditions:"Heat",
    explanation:"With concentrated sulfuric acid, zinc produces sulfur dioxide gas instead of hydrogen. The hot concentrated acid acts as an oxidizing agent, oxidizing zinc to zinc sulfate while itself getting reduced to SO₂. This is different from the reaction with dilute acid.",
    applications:"Demonstrates the dual nature of sulfuric acid - as an acid with dilute solutions and as an oxidizing agent when concentrated."
  },
  
  // ACTIVE METAL OXIDES WITH WATER
  {
    id:"r56", name:"Sodium Oxide with Water", class_level:10,
    reactants:"Na₂O,H₂O",
    products:"NaOH",
    equation:"Na₂O + H₂O → 2NaOH",
    conditions:"Room temperature",
    explanation:"Sodium oxide reacts vigorously with water to form sodium hydroxide (caustic soda). The reaction is highly exothermic. The resulting solution is strongly alkaline and turns red litmus blue and phenolphthalein pink.",
    applications:"Used to prepare sodium hydroxide. Demonstrates that basic oxides of active metals react with water to form strong bases."
  },
  {
    id:"r57", name:"Potassium Oxide with Water", class_level:10,
    reactants:"K₂O,H₂O",
    products:"KOH",
    equation:"K₂O + H₂O → 2KOH",
    conditions:"Room temperature",
    explanation:"Potassium oxide reacts vigorously with water to form potassium hydroxide (caustic potash). The reaction is similar to sodium oxide but even more vigorous. The solution is strongly alkaline.",
    applications:"Used to prepare potassium hydroxide, which is used in making soft soaps, alkaline batteries, and as a laboratory reagent."
  },
  
  // NON-METAL OXIDES WITH WATER
  {
    id:"r58", name:"Carbon Dioxide with Water", class_level:10,
    reactants:"CO₂,H₂O",
    products:"H₂CO₃",
    equation:"CO₂ + H₂O ⇌ H₂CO₃",
    conditions:"Room temperature",
    explanation:"Carbon dioxide dissolves in water to form carbonic acid, a weak acid. This is a reversible reaction. The acid turns blue litmus slightly red. Carbonic acid is unstable and decomposes back to CO₂ and water when heated.",
    applications:"Explains why rainwater is slightly acidic. Carbonic acid is found in carbonated drinks. Important in the carbon cycle and ocean acidification."
  },
  {
    id:"r59", name:"Sulfur Dioxide with Water", class_level:10,
    reactants:"SO₂,H₂O",
    products:"H₂SO₃",
    equation:"SO₂ + H₂O ⇌ H₂SO₃",
    conditions:"Room temperature",
    explanation:"Sulfur dioxide dissolves in water to form sulfurous acid. This is a reversible reaction. Sulfurous acid is a weak acid that turns blue litmus red. It acts as a reducing agent and is used as a preservative.",
    applications:"Used as a preservative in jams and dried fruits. Sulfurous acid and its salts (sulfites) prevent oxidation and bacterial growth in food."
  },
  {
    id:"r60", name:"Sulfur Trioxide with Water", class_level:10,
    reactants:"SO₃,H₂O",
    products:"H₂SO₄",
    equation:"SO₃ + H₂O → H₂SO₄",
    conditions:"Room temperature",
    explanation:"Sulfur trioxide reacts vigorously with water to form sulfuric acid. This is a highly exothermic reaction. Sulfuric acid is a strong acid and is called the 'king of chemicals' due to its extensive industrial use.",
    applications:"This is the final step in the Contact process for manufacturing sulfuric acid. Sulfuric acid is used in fertilizers, dyes, detergents, and many industrial processes."
  },
  
  // ACIDIC OXIDES WITH BASES
  {
    id:"r61", name:"CO₂ with Calcium Hydroxide", class_level:10,
    reactants:"CO₂,Ca(OH)₂",
    products:"CaCO₃,H₂O",
    equation:"CO₂ + Ca(OH)₂ → CaCO₃ + H₂O",
    conditions:"Room temperature",
    explanation:"Carbon dioxide reacts with calcium hydroxide (limewater) to form calcium carbonate (white precipitate) and water. This is the test for CO₂ gas - limewater turns milky. If excess CO₂ is passed, the precipitate dissolves forming calcium bicarbonate.",
    applications:"Used as a test for carbon dioxide gas. Also used in water softening and in the manufacture of cement and glass."
  },
  {
    id:"r62", name:"CO₂ with Sodium Hydroxide", class_level:10,
    reactants:"CO₂,NaOH",
    products:"Na₂CO₃,H₂O",
    equation:"2NaOH + CO₂ → Na₂CO₃ + H₂O",
    conditions:"Room temperature",
    explanation:"Sodium hydroxide reacts with carbon dioxide to form sodium carbonate (washing soda) and water. This reaction explains why sodium hydroxide solutions cannot be stored in open containers - they absorb CO₂ from air and form carbonate.",
    applications:"Used to prepare sodium carbonate. Also explains why NaOH solutions must be stored in airtight containers. Important in the Solvay process."
  },
  
  // ============================================================
  // CLASS 11 CBSE/NCERT REACTIONS (30 reactions)
  // Inorganic + Physical Chemistry
  // ============================================================
  
  // GROUP 1: s-BLOCK ELEMENTS (Alkali & Alkaline Earth Metals)
  {
    id:"r63", name:"Preparation of Sodium Peroxide", class_level:11,
    reactants:"Na,O₂",
    products:"Na₂O₂",
    equation:"2Na + O₂ → Na₂O₂",
    conditions:"Burning in excess air",
    explanation:"When sodium metal burns in excess air or oxygen, it forms sodium peroxide (Na₂O₂) instead of the oxide. This is different from lithium which forms normal oxide and potassium which forms superoxide. The peroxide ion O₂²⁻ contains an O-O single bond.",
    applications:"Sodium peroxide is used as a bleaching agent, in oxygen masks for submarines and spacecraft, and as an oxidizing agent.",
    not_occur:"Does not occur with limited air (forms Na₂O instead). Fails with lithium (forms Li₂O). Does not occur at room temperature (requires ignition). Potassium forms superoxide (KO₂), not peroxide."
  },
  {
    id:"r64", name:"Preparation of Sodium Hydroxide (Castner-Kellner)", class_level:11,
    reactants:"NaCl,H₂O",
    products:"NaOH,H₂,Cl₂",
    equation:"2NaCl + 2H₂O → 2NaOH + H₂ + Cl₂ (electrolysis)",
    conditions:"Electrolysis of brine using mercury cathode",
    explanation:"In the Castner-Kellner process, electrolysis of aqueous NaCl (brine) produces sodium hydroxide, hydrogen gas at the cathode, and chlorine gas at the anode. Mercury acts as a cathode forming sodium amalgam which reacts with water to form NaOH.",
    applications:"Industrial production of caustic soda (NaOH), chlorine gas, and hydrogen. Used in paper, textile, and soap industries."
  },
  {
    id:"r65", name:"Reaction of Calcium Carbide with Water", class_level:11,
    reactants:"CaC₂,H₂O",
    products:"Ca(OH)₂,C₂H₂",
    equation:"CaC₂ + 2H₂O → Ca(OH)₂ + C₂H₂",
    conditions:"Room temperature",
    explanation:"Calcium carbide reacts with water to produce acetylene gas (ethyne) and calcium hydroxide. This is a hydrolysis reaction. The reaction is highly exothermic and acetylene burns with a sooty flame due to high carbon content.",
    applications:"Laboratory preparation of acetylene. Calcium carbide is used in carbide lamps and as a ripening agent for fruits. Acetylene is used in oxy-acetylene torches."
  },
  {
    id:"r66", name:"Plaster of Paris Setting", class_level:11,
    reactants:"CaSO₄·½H₂O,H₂O",
    products:"CaSO₄·2H₂O",
    equation:"CaSO₄·½H₂O + 1½H₂O → CaSO₄·2H₂O",
    conditions:"Mixing with water",
    explanation:"When plaster of Paris (calcium sulfate hemihydrate) is mixed with water, it hardens to form gypsum (calcium sulfate dihydrate). The setting process involves interlocking of crystals and slight expansion, making it useful for casts.",
    applications:"Used for making toys, statues, casts for sealing broken limbs, and in dentistry for making molds."
  },
  
  // GROUP 2: p-BLOCK ELEMENTS (Boron, Carbon, Nitrogen Family)
  {
    id:"r67", name:"Hydrolysis of Boron Trifluoride", class_level:11,
    reactants:"BF₃,H₂O",
    products:"H₃BO₃,HF",
    equation:"BF₃ + 3H₂O → H₃BO₃ + 3HF",
    conditions:"Room temperature",
    explanation:"Boron trifluoride undergoes hydrolysis to form boric acid and hydrogen fluoride. BF₃ is an electron-deficient compound and acts as a Lewis acid, accepting electron pairs from water molecules.",
    applications:"Demonstrates Lewis acid behavior of BF₃. Used in organic synthesis as a catalyst."
  },
  {
    id:"r68", name:"Reaction of Aluminum with Sodium Hydroxide", class_level:11,
    reactants:"Al,NaOH,H₂O",
    products:"NaAlO₂,H₂",
    equation:"2Al + 2NaOH + 2H₂O → 2NaAlO₂ + 3H₂",
    conditions:"Room temperature",
    explanation:"Aluminum reacts with aqueous sodium hydroxide to form sodium meta-aluminate and hydrogen gas. The protective oxide layer on aluminum dissolves in NaOH, allowing the metal to react. This shows the amphoteric nature of aluminum.",
    applications:"Used to demonstrate amphoteric nature of aluminum. Used in drain cleaners and in the production of hydrogen."
  },
  {
    id:"r69", name:"Preparation of Silicones (Hydrolysis of Alkyl Chlorosilanes)", class_level:11,
    reactants:"R₂SiCl₂,H₂O",
    products:"(R₂SiO)n,HCl",
    equation:"nR₂SiCl₂ + nH₂O → (R₂SiO)n + 2nHCl",
    conditions:"Hydrolysis followed by polymerization",
    explanation:"Dialkyldichlorosilanes undergo hydrolysis to form silanols which condense to form silicones (polysiloxanes). The Si-O-Si linkage gives silicones their unique properties like thermal stability and water repellency.",
    applications:"Silicones are used as lubricants, sealants, medical implants, water-repellent coatings, and in cosmetics."
  },
  {
    id:"r70", name:"Haber Process (Ammonia Synthesis)", class_level:11,
    reactants:"N₂,H₂",
    products:"NH₃",
    equation:"N₂ + 3H₂ ⇌ 2NH₃",
    conditions:"200-300 atm, 450°C, Iron catalyst",
    explanation:"Nitrogen and hydrogen combine in a reversible exothermic reaction to form ammonia. High pressure favors the forward reaction (Le Chatelier's principle). Iron with promoters (Al₂O₃, K₂O) acts as catalyst.",
    applications:"Industrial production of ammonia for fertilizers (urea, ammonium nitrate), nitric acid production, and refrigeration.",
    not_occur:"Does not occur at room temperature (kinetically hindered). Fails without catalyst (practically no reaction). Does not proceed at atmospheric pressure (poor yield). Impurities (CO, H₂O) poison the catalyst."
  },
  {
    id:"r71", name:"Ostwald Process (Nitric Acid Production)", class_level:11,
    reactants:"NH₃,O₂",
    products:"NO,H₂O",
    equation:"4NH₃ + 5O₂ → 4NO + 6H₂O (Pt catalyst)",
    conditions:"850-900°C, Pt-Rh catalyst",
    explanation:"Ammonia is catalytically oxidized to nitric oxide using platinum-rhodium catalyst at high temperature. NO is further oxidized to NO₂ and absorbed in water to form HNO₃. This is the basis of nitric acid manufacture.",
    applications:"Industrial production of nitric acid for fertilizers, explosives (TNT, nitroglycerin), and dyes."
  },
  {
    id:"r72", name:"Contact Process (Sulfuric Acid Production)", class_level:11,
    reactants:"SO₂,O₂",
    products:"SO₃",
    equation:"2SO₂ + O₂ ⇌ 2SO₃",
    conditions:"450°C, 1-2 atm, V₂O₅ catalyst",
    explanation:"Sulfur dioxide is oxidized to sulfur trioxide using vanadium pentoxide catalyst. This is a reversible exothermic reaction. Lower temperature favors higher yield but V₂O₅ works best at 450°C (compromise temperature).",
    applications:"Industrial production of sulfuric acid - the most important industrial chemical used in fertilizers, dyes, detergents, and petroleum refining."
  },
  
  // GROUP 3: HALOGENS (Group 17)
  {
    id:"r73", name:"Preparation of Chlorine (Deacon's Process)", class_level:11,
    reactants:"HCl,O₂",
    products:"Cl₂,H₂O",
    equation:"4HCl + O₂ → 2Cl₂ + 2H₂O",
    conditions:"400-450°C, CuCl₂ catalyst",
    explanation:"Hydrogen chloride is oxidized by oxygen in the presence of CuCl₂ catalyst to produce chlorine gas and water. This is an older process now largely replaced by electrolysis but still important.",
    applications:"Production of chlorine gas for bleaching, water treatment, and PVC manufacture."
  },
  {
    id:"r74", name:"Reaction of Chlorine with Cold Dilute NaOH", class_level:11,
    reactants:"Cl₂,NaOH",
    products:"NaCl,NaClO,H₂O",
    equation:"Cl₂ + 2NaOH → NaCl + NaClO + H₂O",
    conditions:"Cold dilute alkali",
    explanation:"Chlorine undergoes disproportionation in cold dilute sodium hydroxide to form sodium chloride and sodium hypochlorite. This is a comproportionation-disproportionation reaction where chlorine is both oxidized and reduced.",
    applications:"Used to manufacture bleaching powder and bleach solutions. Sodium hypochlorite is used as a disinfectant and bleaching agent.",
    not_occur:"Does not occur with hot concentrated NaOH (forms chlorate). Fails with fluorine (different products). Does not occur in acidic medium (Cl₂ + H₂O reaction). Requires cold conditions - warm conditions favor chlorate formation."
  },
  {
    id:"r75", name:"Reaction of Chlorine with Hot Concentrated NaOH", class_level:11,
    reactants:"Cl₂,NaOH",
    products:"NaCl,NaClO₃,H₂O",
    equation:"3Cl₂ + 6NaOH → 5NaCl + NaClO₃ + 3H₂O",
    conditions:"Hot concentrated alkali (>70°C)",
    explanation:"With hot concentrated sodium hydroxide, chlorine disproportionates to form sodium chloride and sodium chlorate instead of hypochlorite. The higher temperature favors the formation of chlorate over hypochlorite.",
    applications:"Used to produce sodium chlorate, which is used in matches, explosives, and as a herbicide."
  },
  {
    id:"r76", name:"Preparation of Hydrogen Chloride (Direct Synthesis)", class_level:11,
    reactants:"H₂,Cl₂",
    products:"HCl",
    equation:"H₂ + Cl₂ → 2HCl",
    conditions:"Burning in UV light or heat",
    explanation:"Hydrogen burns in chlorine to form hydrogen chloride gas. The reaction is explosive when initiated by light or heat. HCl dissolves in water to form hydrochloric acid. This is a chain reaction.",
    applications:"Industrial production of HCl for pickling steel, production of chlorides, and as a laboratory reagent."
  },
  
  // GROUP 4: NOBLE GASES (Group 18)
  {
    id:"r77", name:"Preparation of Xenon Fluorides", class_level:11,
    reactants:"Xe,F₂",
    products:"XeF₂",
    equation:"Xe + F₂ → XeF₂ (1:1 ratio)",
    conditions:"400°C, 1 atm, Ni or Monel vessel",
    explanation:"Xenon reacts with fluorine to form xenon fluorides. Different products (XeF₂, XeF₄, XeF₆) are obtained by varying the ratio of reactants and conditions. This demonstrates that noble gases can form compounds.",
    applications:"XeF₂ is used as a fluorinating agent in organic chemistry. Xenon compounds are used in specialized lasers and as oxidizing agents."
  },
  {
    id:"r78", name:"Hydrolysis of Xenon Tetrafluoride", class_level:11,
    reactants:"XeF₄,H₂O",
    products:"XeO₃,Xe,HF,O₂",
    equation:"6XeF₄ + 12H₂O → 4XeO₃ + 2Xe + 24HF + 3O₂",
    conditions:"Room temperature",
    explanation:"Xenon tetrafluoride undergoes hydrolysis to form xenon trioxide, xenon gas, hydrogen fluoride, and oxygen. This is a complex disproportionation reaction where xenon is both oxidized and reduced.",
    applications:"Demonstrates the reactivity of noble gas compounds. Xenon trioxide is a powerful explosive."
  },
  
  // GROUP 5: d-BLOCK ELEMENTS (Transition Metals)
  {
    id:"r79", name:"Preparation of Potassium Dichromate from Chromite Ore", class_level:11,
    reactants:"FeCr₂O₄,Na₂CO₃,O₂",
    products:"Na₂CrO₄,Fe₂O₃,CO₂",
    equation:"4FeCr₂O₄ + 8Na₂CO₃ + 7O₂ → 8Na₂CrO₄ + 2Fe₂O₃ + 8CO₂",
    conditions:"Fusion at high temperature",
    explanation:"Chromite ore is fused with sodium carbonate in the presence of air to convert chromium(III) to sodium chromate. The product is leached with water and acidified to form sodium dichromate, which is then converted to potassium dichromate using KCl.",
    applications:"Potassium dichromate is used as an oxidizing agent in organic chemistry, in volumetric analysis, and in chrome tanning."
  },
  {
    id:"r80", name:"Reaction of Potassium Permanganate with Oxalic Acid", class_level:11,
    reactants:"KMnO₄,H₂C₂O₄,H₂SO₄",
    products:"MnSO₄,CO₂,K₂SO₄,H₂O",
    equation:"2KMnO₄ + 5H₂C₂O₄ + 3H₂SO₄ → 2MnSO₄ + 10CO₂ + K₂SO₄ + 8H₂O",
    conditions:"Room temperature, acidic medium",
    explanation:"Potassium permanganate oxidizes oxalic acid to carbon dioxide in acidic medium, while itself getting reduced to manganese(II) sulfate. The purple color of KMnO₄ disappears as the reaction proceeds. This is an autocatalytic reaction (Mn²⁺ catalyzes it).",
    applications:"Used in volumetric analysis for estimating oxalates and iron(II) salts. Demonstrates redox titration.",
    not_occur:"Does not occur in alkaline medium (different products - MnO₂). Fails without acid (H₂SO₄ required). Does not occur with HCl (KMnO₄ oxidizes HCl). Requires heating initially - very slow at room temperature until Mn²⁺ builds up."
  },
  {
    id:"r81", name:"Preparation of Potassium Permanganate from Pyrolusite", class_level:11,
    reactants:"MnO₂,KOH,O₂",
    products:"K₂MnO₄,H₂O",
    equation:"2MnO₂ + 4KOH + O₂ → 2K₂MnO₄ + 2H₂O",
    conditions:"Fusion at high temperature (green color)",
    explanation:"Pyrolusite (MnO₂) is fused with KOH in presence of oxidizing agent (O₂ or KNO₃) to form potassium manganate (green). This is then electrolytically oxidized or treated with Cl₂ to form potassium permanganate (purple).",
    applications:"Industrial preparation of KMnO₄, a powerful oxidizing agent used in water treatment, disinfection, and organic synthesis."
  },
  {
    id:"r82", name:"Reaction of Copper with Concentrated Nitric Acid", class_level:11,
    reactants:"Cu,HNO₃",
    products:"Cu(NO₃)₂,NO₂,H₂O",
    equation:"Cu + 4HNO₃ → Cu(NO₃)₂ + 2NO₂ + 2H₂O",
    conditions:"Concentrated acid",
    explanation:"Copper reacts with concentrated nitric acid to form copper nitrate, nitrogen dioxide (brown gas), and water. The brown fumes of NO₂ are characteristic. Concentrated HNO₃ acts as an oxidizing agent.",
    applications:"Laboratory preparation of nitrogen dioxide. Demonstrates the oxidizing nature of concentrated nitric acid.",
    not_occur:"Does not occur with dilute HNO₃ (produces NO instead of NO₂). Fails with very dilute acid (reaction stops). Does not occur with gold or platinum (noble metals). Passivated with concentrated HNO₃ if iron/aluminum."
  },
  {
    id:"r83", name:"Reaction of Copper with Dilute Nitric Acid", class_level:11,
    reactants:"Cu,HNO₃",
    products:"Cu(NO₃)₂,NO,H₂O",
    equation:"3Cu + 8HNO₃ → 3Cu(NO₃)₂ + 2NO + 4H₂O",
    conditions:"Dilute acid",
    explanation:"With dilute nitric acid, copper forms copper nitrate and nitric oxide (colorless gas) which turns brown in air due to oxidation to NO₂. This shows the concentration-dependent behavior of nitric acid.",
    applications:"Laboratory preparation of nitric oxide. Used in qualitative analysis."
  },
  {
    id:"r84", name:"Reaction of Silver Nitrate with Sodium Thiosulfate", class_level:11,
    reactants:"AgNO₃,Na₂S₂O₃",
    products:"Na₃[Ag(S₂O₃)₂],NaNO₃",
    equation:"AgNO₃ + 2Na₂S₂O₃ → Na₃[Ag(S₂O₃)₂] + NaNO₃",
    conditions:"Aqueous solution",
    explanation:"Silver nitrate reacts with excess sodium thiosulfate to form a soluble complex salt sodium dithiosulfatoargentate(I). Initially a white precipitate of Ag₂S₂O₃ forms which dissolves in excess thiosulfate.",
    applications:"Used in photography as a fixing agent to remove unexposed AgBr. Demonstrates complex formation."
  },
  
  // GROUP 6: COORDINATION COMPOUNDS
  {
    id:"r85", name:"Preparation of Tetraamminecopper(II) Sulfate", class_level:11,
    reactants:"CuSO₄,NH₃",
    products:"[Cu(NH₃)₄]SO₄",
    equation:"CuSO₄ + 4NH₃ → [Cu(NH₃)₄]SO₄",
    conditions:"Aqueous ammonia",
    explanation:"Copper sulfate reacts with excess ammonia to form the deep blue complex tetraamminecopper(II) sulfate. The pale blue precipitate of Cu(OH)₂ first formed dissolves in excess ammonia to give the complex.",
    applications:"Used in qualitative analysis to detect copper ions. Demonstrates complex ion formation and color changes."
  },
  {
    id:"r86", name:"Preparation of Potassium Ferrocyanide", class_level:11,
    reactants:"Fe,NH₄CN,K₂CO₃",
    products:"K₄[Fe(CN)₆],NH₃,CO₂",
    equation:"Fe + 6NH₄CN + K₂CO₃ → K₄[Fe(CN)₆] + 2NH₃ + 2CO₂ + 4NH₄⁺",
    conditions:"Fusion process",
    explanation:"Iron filings are fused with potassium carbonate and nitrogenous organic matter to produce potassium ferrocyanide (yellow prussiate). This is a coordination compound with Fe in +2 oxidation state surrounded by six cyanide ligands.",
    applications:"Used to detect Fe³⁺ ions (gives Prussian blue). Used in blueprint paper and as an antidote for heavy metal poisoning."
  },
  {
    id:"r87", name:"Test for Fe³⁺ with Potassium Thiocyanate", class_level:11,
    reactants:"FeCl₃,KSCN",
    products:"[Fe(SCN)]Cl₂,KCl",
    equation:"FeCl₃ + KSCN → [Fe(SCN)]Cl₂ + KCl",
    conditions:"Aqueous solution",
    explanation:"Ferric chloride reacts with potassium thiocyanate to form blood-red colored complex pentaaquathiocyanatoiron(III) chloride. The intense red color is characteristic of Fe³⁺ and used for its detection.",
    applications:"Sensitive test for ferric ions. Used in qualitative analysis. The color intensity can be used for colorimetric estimation of iron."
  },
  
  // GROUP 7: ENVIRONMENTAL CHEMISTRY & QUALITATIVE ANALYSIS
  {
    id:"r88", name:"Bleaching Action of Sulfur Dioxide", class_level:11,
    reactants:"SO₂,H₂O",
    products:"H₂SO₃",
    equation:"SO₂ + H₂O ⇌ H₂SO₃ → H₂SO₄ + 2H (reduction)",
    conditions:"Moist conditions",
    explanation:"Sulfur dioxide bleaches by reduction. It removes oxygen from colored substances, making them colorless. The bleaching is temporary as atmospheric oxygen can reoxidize the substance. This is different from chlorine bleaching (oxidation).",
    applications:"Used for bleaching wool, silk, and straw. Used as a preservative for dried fruits and jams."
  },
  {
    id:"r89", name:"Ring Test for Nitrate Ion", class_level:11,
    reactants:"NO₃⁻,FeSO₄,H₂SO₄",
    products:"[Fe(NO)]SO₄",
    equation:"NO₃⁻ + 3Fe²⁺ + 4H⁺ → NO + 3Fe³⁺ + 2H₂O, then Fe²⁺ + NO → [Fe(NO)]²⁺",
    conditions:"Concentrated H₂SO₄ added slowly",
    explanation:"Nitrate is reduced to nitric oxide by Fe²⁺ in acidic medium. NO forms a brown ring complex with Fe²⁺ at the junction of the two liquids. This is the confirmatory test for nitrate ions.",
    applications:"Confirmatory test for nitrate ions in qualitative analysis. Used in water quality testing."
  },
  {
    id:"r90", name:"Chromyl Chloride Test for Chloride", class_level:11,
    reactants:"K₂Cr₂O₇,NaCl,H₂SO₄",
    products:"CrO₂Cl₂,KHSO₄,NaHSO₄,H₂O",
    equation:"K₂Cr₂O₇ + 4NaCl + 6H₂SO₄ → 2CrO₂Cl₂ + 2KHSO₄ + 4NaHSO₄ + 3H₂O",
    conditions:"Heat with concentrated H₂SO₄",
    explanation:"When a solid chloride is heated with potassium dichromate and concentrated sulfuric acid, red vapors of chromyl chloride (CrO₂Cl₂) are evolved. This is a confirmatory test for chloride ions in qualitative analysis.",
    applications:"Confirmatory test for chloride ions. Distinguishes chloride from other halides."
  },
  
  // ============================================================
  // CLASS 12 CBSE/NCERT REACTIONS (30 reactions)
  // Organic Chemistry + Named Reactions
  // ============================================================
  
  // GROUP 1: ALDEHYDES, KETONES AND CARBOXYLIC ACIDS
  {
    id:"r91", name:"Wolff-Kishner Reduction", class_level:12,
    reactants:"C₆H₅CHO,NH₂NH₂,KOH",
    products:"C₆H₅CH₃,N₂,H₂O",
    equation:"C₆H₅CHO + NH₂NH₂ → C₆H₅CH=NNH₂ → C₆H₅CH₃ + N₂ (KOH, heat)",
    conditions:"Hydrazine, KOH, heat (150-200°C)",
    explanation:"Aldehydes and ketones are reduced to alkanes by heating with hydrazine hydrate and strong base (KOH/NaOH) in ethylene glycol. The carbonyl group is converted to CH₂. This is an alternative to Clemmensen reduction for base-stable compounds.",
    applications:"Reduction of carbonyl compounds to hydrocarbons. Preferred over Clemmensen for acid-sensitive compounds.",
    not_occur:"Does not occur with base-sensitive functional groups (esters, lactones). Fails without strong base (KOH/NaOH required). Does not work at low temperature (requires 150-200°C). Acidic conditions prevent reaction."
  },
  {
    id:"r92", name:"Stephen Reaction (Nitrile to Aldehyde)", class_level:12,
    reactants:"CH₃CN,SnCl₂,HCl",
    products:"CH₃CHO,NH₄Cl,SnCl₄",
    equation:"CH₃CN + SnCl₂ + 2HCl → CH₃CH=NH·HCl → CH₃CHO + NH₄Cl (Hydrolysis)",
    conditions:"SnCl₂/HCl then H₂O",
    explanation:"Nitriles are reduced to imines using stannous chloride in HCl, which are then hydrolyzed to aldehydes. This is a selective reduction that stops at the aldehyde stage without further reduction to alcohol.",
    applications:"Preparation of aldehydes from nitriles. Used when aldehydes cannot be prepared by other methods."
  },
  {
    id:"r93", name:"Hell-Volhard-Zelinsky Reaction", class_level:12,
    reactants:"CH₃CH₂COOH,Br₂,P",
    products:"CH₃CHBrCOOH,HBr",
    equation:"CH₃CH₂COOH + Br₂ → CH₃CHBrCOOH + HBr (red P)",
    conditions:"Br₂, red phosphorus",
    explanation:"Carboxylic acids with α-hydrogen atoms undergo halogenation at the α-position when treated with chlorine or bromine in the presence of red phosphorus. The reaction proceeds via the acid bromide intermediate.",
    applications:"Synthesis of α-halo acids which are important intermediates in organic synthesis. Used to prepare α-amino acids.",
    not_occur:"Does not occur with acids having no α-hydrogen (trimethylacetic acid). Fails without red phosphorus catalyst. Does not work with iodine (HI is strong reducing agent). Aromatic acids react slowly or not at all."
  },
  {
    id:"r94", name:"Decarboxylation of Carboxylic Acids", class_level:12,
    reactants:"CH₃COOH,NaOH,CaO",
    products:"CH₄,Na₂CO₃",
    equation:"CH₃COONa + NaOH → CH₄ + Na₂CO₃ (CaO, heat)",
    conditions:"Soda lime (NaOH + CaO), heat",
    explanation:"Sodium salts of carboxylic acids lose CO₂ when heated with soda lime to form alkanes with one carbon less. CaO prevents NaOH from attacking glass and keeps it dry.",
    applications:"Preparation of alkanes from carboxylic acids. Used to descend the homologous series."
  },
  {
    id:"r95", name:"HVZ Reaction with Acetic Acid", class_level:12,
    reactants:"CH₃COOH,Cl₂,P",
    products:"ClCH₂COOH,HCl",
    equation:"CH₃COOH + Cl₂ → ClCH₂COOH + HCl (red P)",
    conditions:"Cl₂, red phosphorus",
    explanation:"Acetic acid undergoes α-chlorination to form chloroacetic acid. The reaction can continue to give dichloroacetic acid and trichloroacetic acid with excess chlorine.",
    applications:"Preparation of chloroacetic acid used in the synthesis of herbicides, dyes, and pharmaceuticals."
  },
  
  // GROUP 2: ALCOHOLS, PHENOLS AND ETHERS
  {
    id:"r96", name:"Reimer-Tiemann Reaction", class_level:12,
    reactants:"C₆H₅OH,CHCl₃,NaOH",
    products:"o-HOC₆H₄CHO,NaCl,H₂O",
    equation:"C₆H₅OH + CHCl₃ + 3NaOH → o-HOC₆H₄CHO + 3NaCl + 2H₂O",
    conditions:"CHCl₃, aqueous NaOH, 340K",
    explanation:"Phenol reacts with chloroform and aqueous sodium hydroxide to form o-hydroxybenzaldehyde (salicylaldehyde) as the major product. The reaction involves dichlorocarbene (:CCl₂) intermediate.",
    applications:"Introduction of formyl group (-CHO) at ortho position of phenol. Used to prepare salicylaldehyde."
  },
  {
    id:"r97", name:"Kolbe's Electrolytic Reaction", class_level:12,
    reactants:"CH₃COOK",
    products:"C₂H₆,CO₂,KOH,H₂",
    equation:"2CH₃COOK → C₂H₆ + 2CO₂ + 2KOH + H₂ (electrolysis)",
    conditions:"Electrolysis of concentrated sodium/potassium salt of fatty acid",
    explanation:"Electrolysis of sodium or potassium salt of fatty acids gives alkanes with even number of carbon atoms at the anode. The alkyl radicals couple to form the alkane. CO₂ is evolved and H₂ is formed at cathode.",
    applications:"Preparation of alkanes. Used to prepare symmetrical alkanes with even number of carbons."
  },
  {
    id:"r98", name:"Williamson Ether Synthesis", class_level:12,
    reactants:"C₂H₅ONa,CH₃I",
    products:"C₂H₅OCH₃,NaI",
    equation:"C₂H₅ONa + CH₃I → C₂H₅OCH₃ + NaI",
    conditions:"SN2 reaction conditions",
    explanation:"Sodium alkoxide reacts with alkyl halide to form ether. This is an SN2 reaction where the alkoxide ion acts as a nucleophile. Primary alkyl halides give good yields; tertiary halides undergo elimination.",
    applications:"General method for preparing mixed and symmetrical ethers. Used in pharmaceutical and perfume industries.",
    not_occur:"Does not occur with tertiary alkyl halides (elimination dominates). Fails with aryl halides (C-X bond too strong). Does not work with alcohols instead of alkoxides. Vinyl halides do not react."
  },
  {
    id:"r99", name:"Coupling Reaction of Phenol with Diazonium Salt", class_level:12,
    reactants:"C₆H₅OH,C₆H₅N₂⁺Cl⁻",
    products:"p-HOC₆H₄N=NC₆H₅,HCl",
    equation:"C₆H₅OH + C₆H₅N₂⁺Cl⁻ → p-HOC₆H₄N=NC₆H₅ + HCl",
    conditions:"Weakly alkaline (pH 9-10), 0-5°C",
    explanation:"Phenol couples with benzenediazonium chloride in weakly alkaline medium to form p-hydroxyazobenzene (an azo dye). The para position of phenol is activated by the -OH group.",
    applications:"Synthesis of azo dyes. Used in textile dyeing and as indicators."
  },
  
  // GROUP 3: AMINES AND DIAZONIUM SALTS
  {
    id:"r100", name:"Gabriel Phthalimide Synthesis", class_level:12,
    reactants:"C₆H₄(CO)₂NK,KOH,RCH₂Br",
    products:"C₆H₄(CO)₂NCH₂R,KBr",
    equation:"Phthalimide + KOH + RCH₂Br → N-alkylphthalimide → RCH₂NH₂ (hydrazinolysis)",
    conditions:"KOH, then R-X, then NH₂NH₂",
    explanation:"Primary amines are prepared from phthalimide by alkylation followed by hydrolysis or hydrazinolysis. The method gives pure primary amines without secondary or tertiary amine contamination.",
    applications:"Preparation of pure primary amines. Used in amino acid synthesis.",
    not_occur:"Does not occur with secondary alkyl halides (elimination dominates). Fails without strong base (KOH). Does not work with tertiary alkyl halides. Aryl halides do not react (need different method)."
  },
  {
    id:"r101", name:"Hoffmann Bromamide Degradation", class_level:12,
    reactants:"CH₃CONH₂,Br₂,NaOH",
    products:"CH₃NH₂,Na₂CO₃,NaBr,H₂O",
    equation:"CH₃CONH₂ + Br₂ + 4NaOH → CH₃NH₂ + Na₂CO₃ + 2NaBr + 2H₂O",
    conditions:"Br₂, aqueous NaOH",
    explanation:"Primary amides react with bromine and alkali to form primary amines with one carbon less. The reaction proceeds via isocyanate intermediate. This is a degradation reaction.",
    applications:"Conversion of amides to amines with loss of one carbon. Used in amino acid synthesis and structure determination."
  },
  {
    id:"r102", name:"Carbylamine Reaction", class_level:12,
    reactants:"CH₃NH₂,CHCl₃,KOH",
    products:"CH₃NC,3KCl,3H₂O",
    equation:"CH₃NH₂ + CHCl₃ + 3KOH → CH₃NC + 3KCl + 3H₂O",
    conditions:"CHCl₃, alcoholic KOH, heat",
    explanation:"Primary amines react with chloroform and alcoholic KOH to form isocyanides (carbylamines) with characteristic offensive odor. This is a test for primary amines. Secondary and tertiary amines do not give this test.",
    applications:"Test for primary amines. Distinguishes primary amines from secondary and tertiary amines."
  },
  {
    id:"r103", name:"Hoffmann's Mustard Oil Reaction", class_level:12,
    reactants:"C₆H₅NH₂,CS₂,HgCl₂",
    products:"C₆H₅NCS,HgS,HCl",
    equation:"C₆H₅NH₂ + CS₂ + HgCl₂ → C₆H₅NCS + HgS + 2HCl",
    conditions:"CS₂, then HgCl₂",
    explanation:"Primary amines react with carbon disulfide to form dithiocarbamic acid, which decomposes with HgCl₂ to give alkyl isothiocyanate (mustard oil) with characteristic smell. This is a test for primary amines.",
    applications:"Test for primary amines. Used to identify primary amines by their mustard oil smell."
  },
  {
    id:"r104", name:"Diazotization of Aniline", class_level:12,
    reactants:"C₆H₅NH₂,NaNO₂,HCl",
    products:"C₆H₅N₂⁺Cl⁻,NaCl,2H₂O",
    equation:"C₆H₅NH₂ + NaNO₂ + 2HCl → C₆H₅N₂⁺Cl⁻ + NaCl + 2H₂O",
    conditions:"0-5°C, NaNO₂ + HCl",
    explanation:"Primary aromatic amines react with nitrous acid (generated in situ from NaNO₂ and HCl) at low temperature to form diazonium salts. These are very reactive intermediates used in dye and drug synthesis.",
    applications:"Preparation of diazonium salts. Used in synthesis of azo dyes, phenols, and halobenzenes."
  },
  
  // GROUP 4: BIOMOLECULES AND POLYMERS
  {
    id:"r105", name:"Hydrolysis of Sucrose", class_level:12,
    reactants:"C₁₂H₂₂O₁₁,H₂O",
    products:"C₆H₁₂O₆,C₆H₁₂O₆",
    equation:"C₁₂H₂₂O₁₁ + H₂O → C₆H₁₂O₆ (glucose) + C₆H₁₂O₆ (fructose)",
    conditions:"Dilute H₂SO₄ or enzyme invertase",
    explanation:"Sucrose (cane sugar) undergoes hydrolysis in the presence of dilute acid or enzyme invertase to give equimolar mixture of glucose and fructose. This mixture is called invert sugar and is laevorotatory.",
    applications:"Preparation of invert sugar. Used in confectionery and brewing industries."
  },
  {
    id:"r106", name:"Molisch Test for Carbohydrates", class_level:12,
    reactants:"Carbohydrate,H₂SO₄,α-naphthol",
    products:"Furfural derivatives,purple complex",
    equation:"Carbohydrate → Furfural/HMF (dehydration) + α-naphthol → Purple ring",
    conditions:"α-naphthol in alcohol, then conc. H₂SO₄",
    explanation:"Carbohydrates are dehydrated by concentrated H₂SO₄ to form furfural or hydroxymethylfurfural, which condenses with α-naphthol to give a purple-colored complex at the junction of the two liquids.",
    applications:"General test for carbohydrates. Used to detect presence of sugars in solution."
  },
  {
    id:"r107", name:"Biuret Test for Proteins", class_level:12,
    reactants:"Protein,CuSO₄,NaOH",
    products:"Violet complex",
    equation:"Peptide bonds + Cu²⁺ + OH⁻ → Violet complex",
    conditions:"Dilute CuSO₄, NaOH",
    explanation:"Compounds containing two or more peptide bonds form a violet-colored complex with alkaline copper sulfate solution. The color is due to coordination complex formation between Cu²⁺ and peptide nitrogen atoms.",
    applications:"Test for proteins and peptides. Used in biochemical analysis and clinical testing."
  },
  {
    id:"r108", name:"Formation of Nylon-6,6", class_level:12,
    reactants:"HOOC(CH₂)₄COOH,H₂N(CH₂)₆NH₂",
    products:"[-OC(CH₂)₄CONH(CH₂)₆NH-]n,H₂O",
    equation:"nHO₂C(CH₂)₄CO₂H + nH₂N(CH₂)₆NH₂ → [Nylon-6,6]n + 2nH₂O",
    conditions:"High temperature, pressure",
    explanation:"Adipic acid reacts with hexamethylenediamine to form the polyamide Nylon-6,6 through condensation polymerization. Water is eliminated in the process. The numbers indicate the number of carbon atoms in each monomer.",
    applications:"Manufacture of Nylon fibers for textiles, ropes, and engineering plastics."
  },
  {
    id:"r109", name:"Formation of Bakelite", class_level:12,
    reactants:"C₆H₅OH,HCHO",
    products:"[C₆H₃(OH)CH₂]n,H₂O",
    equation:"nC₆H₅OH + nHCHO → Bakelite + nH₂O (acid/base catalyst)",
    conditions:"Acid or base catalyst, heat",
    explanation:"Phenol reacts with formaldehyde to form Bakelite (a thermosetting polymer). Initially a linear novolac is formed, which on further heating cross-links to form a hard, rigid three-dimensional network.",
    applications:"Used for making electrical switches, handles, combs, and decorative items. First synthetic plastic."
  },
  {
    id:"r110", name:"Formation of Teflon", class_level:12,
    reactants:"CF₂=CF₂",
    products:"[-CF₂-CF₂-]n",
    equation:"nCF₂=CF₂ → [-CF₂-CF₂-]n (polytetrafluoroethylene)",
    conditions:"High pressure, peroxide catalyst",
    explanation:"Tetrafluoroethylene undergoes addition polymerization to form Teflon (PTFE). The strong C-F bonds make it chemically inert and heat resistant. It has very low friction coefficient.",
    applications:"Non-stick cookware coatings, gaskets, seals, electrical insulation, and chemical-resistant linings."
  },
  
  // GROUP 5: NAMED REACTIONS - ADVANCED
  {
    id:"r111", name:"Clemmensen Reduction", class_level:12,
    reactants:"C₆H₅COCH₃,Zn,Hg,HCl",
    products:"C₆H₅CH₂CH₃,ZnCl₂,H₂O",
    equation:"C₆H₅COCH₃ + 4[H] → C₆H₅CH₂CH₃ + H₂O (Zn-Hg/HCl)",
    conditions:"Zn-Hg amalgam, concentrated HCl, heat",
    explanation:"Carbonyl compounds (aldehydes and ketones) are reduced to hydrocarbons using zinc amalgam and concentrated hydrochloric acid. The carbonyl group is reduced to CH₂ group. This works well for acid-stable compounds.",
    applications:"Reduction of carbonyl compounds to hydrocarbons. Alternative to Wolff-Kishner for base-sensitive compounds."
  },
  {
    id:"r112", name:"Meerwein-Ponndorf-Verley Reduction", class_level:12,
    reactants:"(CH₃)₂CHOH,R₂C=O",
    products:"(CH₃)₂C=O,R₂CHOH",
    equation:"R₂C=O + (CH₃)₂CHOH ⇌ R₂CHOH + (CH₃)₂C=O (Al(OCHMe₂)₃)",
    conditions:"Aluminum isopropoxide, isopropyl alcohol",
    explanation:"Aldehydes and ketones are reduced to alcohols by aluminum isopropoxide in isopropyl alcohol. The reaction proceeds via a cyclic transition state. Acetone is formed as byproduct and removed by distillation.",
    applications:"Selective reduction of carbonyl compounds. Does not affect double bonds or other reducible groups."
  },
  {
    id:"r113", name:"Acetoacetic Ester Synthesis", class_level:12,
    reactants:"CH₃COCH₂COOC₂H₅,NaOC₂H₅,RX",
    products:"CH₃COCHRCOOC₂H₅,NaX,C₂H₅OH",
    equation:"CH₃COCH₂COOC₂H₅ + NaOC₂H₅ → [CH₃COCHCOOC₂H₅]⁻Na⁺ → CH₃COCHRCOOC₂H₅ (alkylation)",
    conditions:"Strong base (NaOEt), then alkyl halide",
    explanation:"Ethyl acetoacetate has acidic α-hydrogens which are removed by strong base to form an enolate. This nucleophilic enolate attacks alkyl halides to give alkylated products, which can be hydrolyzed and decarboxylated to ketones.",
    applications:"Synthesis of ketones and substituted acetic acids. Important method for carbon-carbon bond formation."
  },
  {
    id:"r114", name:"Malonic Ester Synthesis", class_level:12,
    reactants:"CH₂(COOC₂H₅)₂,NaOC₂H₅,RX",
    products:"RCH(COOC₂H₅)₂,NaX,C₂H₅OH",
    equation:"CH₂(COOC₂H₅)₂ + NaOC₂H₅ → [CH(COOC₂H₅)₂]⁻Na⁺ → RCH(COOC₂H₅)₂",
    conditions:"Strong base (NaOEt), then alkyl halide",
    explanation:"Diethyl malonate has acidic α-hydrogens which are removed by strong base. The resulting enolate attacks alkyl halides. The alkylated malonic ester can be hydrolyzed and decarboxylated to give substituted acetic acids.",
    applications:"Synthesis of substituted acetic acids and carboxylic acids with extended carbon chains."
  },
  {
    id:"r115", name:"Diels-Alder Reaction", class_level:12,
    reactants:"1,3-butadiene,ethylene",
    products:"cyclohexene",
    equation:"CH₂=CH-CH=CH₂ + CH₂=CH₂ → Cyclohexene",
    conditions:"Heat or pressure",
    explanation:"A [4+2] cycloaddition reaction between a conjugated diene and a dienophile to form a six-membered ring. The reaction is concerted and stereospecific. It forms two new sigma bonds and one new pi bond.",
    applications:"Formation of six-membered rings in organic synthesis. Used in steroid and natural product synthesis."
  },
  {
    id:"r116", name:"Grignard Reaction with Carbonyl Compounds", class_level:12,
    reactants:"RMgX,R'CHO",
    products:"RCH(OMgX)R'",
    equation:"RMgX + R'CHO → RCH(OMgX)R' → RCH(OH)R' (hydrolysis)",
    conditions:"Dry ether, then H₂O/H⁺",
    explanation:"Grignard reagents add to the carbonyl carbon of aldehydes and ketones. The reaction forms a new C-C bond. After hydrolysis, alcohols are obtained. Formaldehyde gives primary alcohols, other aldehydes give secondary alcohols.",
    applications:"Synthesis of alcohols with new carbon skeletons. One of the most important C-C bond forming reactions.",
    not_occur:"Does not occur with water or alcohols (Grignard reagent decomposes). Fails with carboxylic acids (acid-base reaction first). Does not work in protic solvents. CO₂ must be dry - moisture destroys Grignard reagent."
  },
  {
    id:"r117", name:"Cannizzaro Reaction (Crossed)", class_level:12,
    reactants:"HCHO,C₆H₅CHO,NaOH",
    products:"CH₃OH,C₆H₅COONa",
    equation:"HCHO + C₆H₅CHO + NaOH → CH₃OH + C₆H₅COONa",
    conditions:"Concentrated NaOH",
    explanation:"In crossed Cannizzaro reaction, one molecule of formaldehyde is oxidized to formic acid (then formate) while another aldehyde (without α-H) is reduced to alcohol. Formaldehyde is always oxidized preferentially.",
    applications:"Preparation of alcohols and acids from aldehydes without α-hydrogens."
  },
  {
    id:"r118", name:"Pinacol-Pinacolone Rearrangement", class_level:12,
    reactants:"(CH₃)₂C(OH)C(OH)(CH₃)₂",
    products:"(CH₃)₃CCOCH₃,H₂O",
    equation:"Pinacol → Pinacolone (H⁺ catalyst)",
    conditions:"Acid catalyst (H₂SO₄)",
    explanation:"Vicinal diols (glycols) undergo acid-catalyzed rearrangement to form carbonyl compounds. One -OH group is protonated and leaves as water, forming a carbocation which rearranges by alkyl shift to give a more stable carbocation, then ketone.",
    applications:"Conversion of glycols to ketones. Demonstrates carbocation rearrangements and migratory aptitude."
  },
  {
    id:"r119", name:"Beckmann Rearrangement", class_level:12,
    reactants:"C₆H₅C(=NOH)CH₃,PCl₅",
    products:"C₆H₅NHCOCH₃,POCl₃,HCl",
    equation:"Oxime → Amide (acid catalyst)",
    conditions:"Acid catalyst (H₂SO₄, PCl₅, etc.)",
    explanation:"Oximes rearrange to amides under acidic conditions. The group anti to the -OH group migrates to nitrogen with simultaneous loss of water. This is a stereospecific rearrangement.",
    applications:"Conversion of ketoximes to amides. Used in the industrial production of caprolactam for Nylon-6."
  },
  {
    id:"r120", name:"Hydroboration-Oxidation of Alkenes", class_level:12,
    reactants:"RCH=CH₂,BH₃,H₂O₂,NaOH",
    products:"RCH₂CH₂OH",
    equation:"6RCH=CH₂ + B₂H₆ → 2(RCH₂CH₂)₃B → 3RCH₂CH₂OH + B(OH)₃",
    conditions:"1) BH₃·THF, 2) H₂O₂, NaOH",
    explanation:"Borane adds to alkenes in anti-Markovnikov fashion (H to more substituted carbon). The organoborane is then oxidized with H₂O₂/NaOH to give alcohol. The addition is syn (cis).",
    applications:"Preparation of alcohols from alkenes with anti-Markovnikov regioselectivity. Important synthetic method.",
    not_occur:"Does not occur with alkynes (different products - aldehydes/ketones). Fails without oxidation step (H₂O₂/NaOH). Does not work with hindered alkenes (disubstituted boranes used instead). Requires dry THF - moisture reacts with BH₃."
  },
  {
    id:"r121", name:"Ozonolysis of Alkenes", class_level:12,
    reactants:"RCH=CHR',O₃",
    products:"RCHO,R'CHO",
    equation:"RCH=CHR' + O₃ → Ozonide → RCHO + R'CHO (reductive workup)",
    conditions:"1) O₃, 2) Zn/H₂O or (CH₃)₂S",
    explanation:"Ozone adds to alkenes to form molozonide which rearranges to ozonide. Reductive workup (Zn/H₂O or dimethyl sulfide) cleaves the ozonide to give aldehydes/ketones. Oxidative workup gives carboxylic acids.",
    applications:"Cleavage of double bonds to carbonyl compounds. Used to locate double bonds and in organic synthesis."
  },
  {
    id:"r122", name:"Wittig Reaction", class_level:12,
    reactants:"Ph₃P=CHR,R'CHO",
    products:"RCH=CHR',Ph₃P=O",
    equation:"Ph₃P=CHR + R'CHO → RCH=CHR' + Ph₃P=O",
    conditions:"Polar aprotic solvent",
    explanation:"Phosphorus ylides react with aldehydes or ketones to form alkenes and triphenylphosphine oxide. The reaction is stereoselective - unstabilized ylides give Z-alkenes, stabilized ylides give E-alkenes.",
    applications:"Synthesis of alkenes from carbonyl compounds. Used in vitamin A and pheromone synthesis.",
    not_occur:"Does not occur with esters or amides (ylide attacks carbonyl but doesn't eliminate). Fails with highly hindered ketones. Does not work with carboxylic acids (deprotonates ylide). Requires anhydrous conditions."
  },
  
  // ============================================================
  // CLASS 9 CBSE/NCERT REACTIONS (30 reactions)
  // Matter, Atoms, Molecules, Structure, Chemical Bonding
  // ============================================================
  
  // GROUP 1: MATTER IN OUR SURROUNDINGS & IS MATTER AROUND US PURE
  {
    id:"r123", name:"Sublimation of Ammonium Chloride", class_level:9,
    reactants:"NH₄Cl",
    products:"NH₄Cl",
    equation:"NH₄Cl(s) ⇌ NH₄Cl(g)",
    conditions:"Heat and cool",
    explanation:"Ammonium chloride undergoes sublimation - it changes directly from solid to gas on heating and back to solid on cooling without passing through the liquid state. This is a physical change used to separate mixtures.",
    applications:"Used to demonstrate sublimation. Used in separation techniques to purify NH₄Cl from sand and other non-sublimable substances."
  },
  {
    id:"r124", name:"Crystallization of Copper Sulfate", class_level:9,
    reactants:"CuSO₄",
    products:"CuSO₄·5H₂O",
    equation:"CuSO₄ + 5H₂O → CuSO₄·5H₂O",
    conditions:"Evaporation and cooling",
    explanation:"When a hot saturated solution of copper sulfate is cooled, blue crystals of copper sulfate pentahydrate form. This is a physical change involving hydration. The water molecules become part of the crystal structure.",
    applications:"Used to obtain pure solids from impure solutions. Used in purification of salts."
  },
  {
    id:"r125", name:"Chromatography Separation", class_level:9,
    reactants:"Ink mixture",
    products:"Separated pigments",
    equation:"Separation based on differential adsorption",
    conditions:"Filter paper, solvent",
    explanation:"Chromatography separates components of a mixture based on their differential adsorption on a stationary phase and differential solubility in a mobile phase. Different pigments travel at different rates.",
    applications:"Used to separate and identify components of mixtures. Used in forensic science, food testing, and pharmaceutical analysis."
  },
  
  // GROUP 2: ATOMS AND MOLECULES - CHEMICAL FORMULAS
  {
    id:"r126", name:"Formation of Water Molecule", class_level:9,
    reactants:"H₂,O₂",
    products:"H₂O",
    equation:"2H₂ + O₂ → 2H₂O",
    conditions:"Spark/Electric discharge",
    explanation:"Hydrogen and oxygen combine in a 2:1 ratio by volume to form water. This demonstrates the law of constant proportions and the concept of atoms combining in fixed ratios to form molecules.",
    applications:"Demonstrates chemical combination at molecular level. Used in fuel cells and hydrogen economy concepts."
  },
  {
    id:"r127", name:"Formation of Ammonia Molecule", class_level:9,
    reactants:"N₂,H₂",
    products:"NH₃",
    equation:"N₂ + 3H₂ → 2NH₃",
    conditions:"High pressure, catalyst",
    explanation:"Nitrogen and hydrogen combine in a 1:3 ratio to form ammonia molecules. This demonstrates diatomic molecules breaking apart and recombining to form new compounds with different properties.",
    applications:"Introduction to chemical bonding and molecular formulas. Foundation for understanding fertilizer production."
  },
  {
    id:"r128", name:"Formation of Carbon Dioxide", class_level:9,
    reactants:"C,O₂",
    products:"CO₂",
    equation:"C + O₂ → CO₂",
    conditions:"Burning/Combustion",
    explanation:"Carbon burns in oxygen to form carbon dioxide. One atom of carbon combines with one molecule of oxygen (two atoms) to form one molecule of carbon dioxide. This illustrates the law of conservation of mass.",
    applications:"Demonstrates atomic theory and conservation of mass. Used in understanding combustion and respiration."
  },
  
  // GROUP 3: STRUCTURE OF THE ATOM - NUCLEAR CHEMISTRY BASICS
  {
    id:"r129", name:"Radioactive Decay of Uranium-238", class_level:9,
    reactants:"²³⁸U",
    products:"²³⁴Th,⁴He",
    equation:"²³⁸U → ²³⁴Th + ⁴He (α-decay)",
    conditions:"Spontaneous",
    explanation:"Uranium-238 undergoes alpha decay, emitting an alpha particle (helium nucleus) and transforming into thorium-234. This demonstrates nuclear reactions where elements transform into other elements.",
    applications:"Used in radioactive dating, nuclear power generation, and understanding Earth's age."
  },
  {
    id:"r130", name:"Beta Decay of Carbon-14", class_level:9,
    reactants:"¹⁴C",
    products:"¹⁴N,e⁻",
    equation:"¹⁴C → ¹⁴N + e⁻ + ν̄ (β-decay)",
    conditions:"Spontaneous",
    explanation:"Carbon-14 undergoes beta decay where a neutron converts to a proton, emitting an electron (beta particle) and an antineutrino. The atomic number increases by 1 but mass number stays same.",
    applications:"Carbon-14 dating used in archaeology and paleontology to determine age of organic materials."
  },
  
  // GROUP 4: CHEMICAL BONDING - IONIC AND COVALENT
  {
    id:"r131", name:"Formation of Sodium Chloride (Ionic Bond)", class_level:9,
    reactants:"Na,Cl₂",
    products:"NaCl",
    equation:"2Na + Cl₂ → 2NaCl",
    conditions:"Heat",
    explanation:"Sodium (metal) loses one electron to form Na⁺ ion, while chlorine (non-metal) gains one electron to form Cl⁻ ion. The electrostatic attraction between oppositely charged ions forms an ionic bond.",
    applications:"Demonstrates ionic bonding. NaCl is common salt used as food preservative and in chemical industries."
  },
  {
    id:"r132", name:"Formation of Hydrogen Molecule (Covalent Bond)", class_level:9,
    reactants:"H,H",
    products:"H₂",
    equation:"H· + ·H → H:H or H-H",
    conditions:"Normal conditions",
    explanation:"Two hydrogen atoms share one pair of electrons to form a covalent bond. Each hydrogen atom achieves the stable duplet configuration of helium. This is the simplest covalent bond.",
    applications:"Demonstrates covalent bonding. Hydrogen is used as fuel and in Haber process for ammonia synthesis."
  },
  {
    id:"r133", name:"Formation of Water (Covalent Bond)", class_level:9,
    reactants:"H₂,O₂",
    products:"H₂O",
    equation:"2H₂ + O₂ → 2H₂O",
    conditions:"Spark",
    explanation:"Oxygen shares two electron pairs with two hydrogen atoms forming two O-H covalent bonds. Oxygen achieves octet configuration while each hydrogen achieves duplet. The molecule has a bent shape.",
    applications:"Demonstrates polar covalent bonding and molecular geometry. Essential for all life processes."
  },
  {
    id:"r134", name:"Formation of Magnesium Oxide (Ionic Bond)", class_level:9,
    reactants:"Mg,O₂",
    products:"MgO",
    equation:"2Mg + O₂ → 2MgO",
    conditions:"Burning",
    explanation:"Magnesium loses two electrons to form Mg²⁺ ion, while oxygen gains two electrons to form O²⁻ ion. The strong electrostatic attraction between these doubly charged ions forms magnesium oxide with high melting point.",
    applications:"Demonstrates formation of ionic compounds with 2+ and 2- ions. MgO is used as refractory material and antacid."
  },
  
  // GROUP 5: PHYSICAL CHEMISTRY - STATES OF MATTER
  {
    id:"r135", name:"Evaporation of Water", class_level:9,
    reactants:"H₂O(l)",
    products:"H₂O(g)",
    equation:"H₂O(l) + Heat → H₂O(g)",
    conditions:"Heat",
    explanation:"When water is heated, the kinetic energy of molecules increases. Molecules at the surface overcome intermolecular forces and escape into the air as water vapor. This is a physical change.",
    applications:"Cooling effect of evaporation used in sweating, earthen pots, and air conditioning."
  },
  {
    id:"r136", name:"Condensation of Steam", class_level:9,
    reactants:"H₂O(g)",
    products:"H₂O(l)",
    equation:"H₂O(g) → H₂O(l) + Heat",
    conditions:"Cooling",
    explanation:"When water vapor is cooled, the kinetic energy of molecules decreases. Intermolecular forces bring molecules closer together, forming liquid water. Heat is released in this exothermic process.",
    applications:"Used in power plants, distillation processes, and understanding weather phenomena like cloud formation."
  },
  {
    id:"r137", name:"Melting of Ice", class_level:9,
    reactants:"H₂O(s)",
    products:"H₂O(l)",
    equation:"H₂O(s) + Heat → H₂O(l)",
    conditions:"0°C, 1 atm",
    explanation:"At 0°C, ice absorbs latent heat of fusion (334 J/g) to overcome hydrogen bonding between water molecules and transform into liquid water. Temperature remains constant during phase change.",
    applications:"Understanding phase changes, refrigeration cycles, and climate science (melting glaciers)."
  },
  
  // GROUP 6: ORGANIC CHEMISTRY BASICS - CARBON COMPOUNDS INTRO
  {
    id:"r138", name:"Complete Combustion of Methane", class_level:9,
    reactants:"CH₄,O₂",
    products:"CO₂,H₂O",
    equation:"CH₄ + 2O₂ → CO₂ + 2H₂O",
    conditions:"Ignition",
    explanation:"Methane undergoes complete combustion in excess oxygen to form carbon dioxide and water. This is an exothermic reaction releasing large amount of heat energy. All hydrocarbons produce CO₂ and H₂O on complete combustion.",
    applications:"Natural gas (methane) used for cooking and heating. Basis of fuel energy calculations."
  },
  {
    id:"r139", name:"Incomplete Combustion of Methane", class_level:9,
    reactants:"CH₄,O₂",
    products:"CO,H₂O",
    equation:"2CH₄ + 3O₂ → 2CO + 4H₂O",
    conditions:"Limited oxygen",
    explanation:"When methane burns in limited oxygen supply, incomplete combustion occurs producing carbon monoxide (poisonous gas) instead of carbon dioxide. Soot (carbon particles) may also form.",
    applications:"Demonstrates importance of proper ventilation. CO poisoning awareness. Used in production of synthesis gas."
  },
  {
    id:"r140", name:"Combustion of Ethanol", class_level:9,
    reactants:"C₂H₅OH,O₂",
    products:"CO₂,H₂O",
    equation:"C₂H₅OH + 3O₂ → 2CO₂ + 3H₂O",
    conditions:"Ignition",
    explanation:"Ethanol (alcohol) burns in oxygen to produce carbon dioxide and water. Being an oxygen-containing compound, it burns more cleanly than hydrocarbons with similar carbon number.",
    applications:"Ethanol is used as biofuel (gasohol), in spirit lamps, and as a cleaner burning fuel additive."
  },
  {
    id:"r141", name:"Oxidation of Ethanol to Ethanoic Acid", class_level:9,
    reactants:"C₂H₅OH,O₂",
    products:"CH₃COOH,H₂O",
    equation:"C₂H₅OH + O₂ → CH₃COOH + H₂O (catalyst)",
    conditions:"Bacterial oxidation (Acetobacter)",
    explanation:"Ethanol is oxidized to ethanoic acid (acetic acid) by oxidation with oxygen in presence of acetobacter bacteria. This is the process of vinegar formation from wine.",
    applications:"Manufacture of vinegar. Demonstrates oxidation of alcohols to acids."
  },
  {
    id:"r142", name:"Esterification - Formation of Ethyl Ethanoate", class_level:9,
    reactants:"CH₃COOH,C₂H₅OH",
    products:"CH₃COOC₂H₅,H₂O",
    equation:"CH₃COOH + C₂H₅OH ⇌ CH₃COOC₂H₅ + H₂O",
    conditions:"Conc. H₂SO₄, heat",
    explanation:"Carboxylic acid reacts with alcohol in presence of concentrated sulfuric acid to form ester and water. H₂SO₄ acts as catalyst and dehydrating agent. The reaction is reversible.",
    applications:"Synthesis of esters used in perfumes, flavorings, and solvents. Demonstrates functional group transformation."
  },
  
  // GROUP 7: ACIDS, BASES AND SALTS
  {
    id:"r143", name:"Reaction of Zinc with Sulfuric Acid", class_level:9,
    reactants:"Zn,H₂SO₄",
    products:"ZnSO₄,H₂",
    equation:"Zn + H₂SO₄ → ZnSO₄ + H₂",
    conditions:"Dilute acid",
    explanation:"Zinc metal reacts with dilute sulfuric acid to form zinc sulfate and hydrogen gas. This is a single displacement reaction where more reactive zinc displaces hydrogen from the acid.",
    applications:"Laboratory preparation of hydrogen gas. Demonstrates metal-acid reactions and reactivity series."
  },
  {
    id:"r144", name:"Neutralization - HCl and NaOH", class_level:9,
    reactants:"HCl,NaOH",
    products:"NaCl,H₂O",
    equation:"HCl + NaOH → NaCl + H₂O",
    conditions:"Aqueous solution",
    explanation:"Acid and base react to form salt and water. H⁺ ions from acid combine with OH⁻ ions from base to form water. The solution becomes neutral with pH 7. Heat is evolved (exothermic).",
    applications:"Used in antacids, treating acidic soil, and in chemical industries to produce salts."
  },
  {
    id:"r145", name:"Reaction of Metal Oxide with Acid", class_level:9,
    reactants:"CuO,H₂SO₄",
    products:"CuSO₄,H₂O",
    equation:"CuO + H₂SO₄ → CuSO₄ + H₂O",
    conditions:"Warm conditions",
    explanation:"Basic copper oxide reacts with sulfuric acid to form copper sulfate (blue solution) and water. Metal oxides are basic and react with acids to form salts.",
    applications:"Preparation of copper sulfate. Demonstrates basic nature of metal oxides."
  },
  {
    id:"r146", name:"Reaction of Non-metal Oxide with Base", class_level:9,
    reactants:"CO₂,NaOH",
    products:"Na₂CO₃,H₂O",
    equation:"2NaOH + CO₂ → Na₂CO₃ + H₂O",
    conditions:"Room temperature",
    explanation:"Carbon dioxide (acidic oxide) reacts with sodium hydroxide (base) to form sodium carbonate and water. Non-metal oxides are acidic and react with bases to form salts.",
    applications:"Used to absorb CO₂ gas. Demonstrates acidic nature of non-metal oxides."
  },
  {
    id:"r147", name:"Preparation of Washing Soda", class_level:9,
    reactants:"Na₂CO₃,H₂O",
    products:"Na₂CO₃·10H₂O",
    equation:"Na₂CO₃ + 10H₂O → Na₂CO₃·10H₂O",
    conditions:"Crystallization",
    explanation:"Sodium carbonate dissolves in water and crystallizes as washing soda (sodium carbonate decahydrate). It contains 10 water molecules in its crystal structure.",
    applications:"Used in glass manufacture, paper industry, and as a cleansing agent."
  },
  {
    id:"r148", name:"Preparation of Bleaching Powder", class_level:9,
    reactants:"Ca(OH)₂,Cl₂",
    products:"CaOCl₂,H₂O",
    equation:"Ca(OH)₂ + Cl₂ → CaOCl₂ + H₂O",
    conditions:"Cold",
    explanation:"Slaked lime reacts with chlorine gas to form bleaching powder (calcium oxychloride). It is a mixture of calcium hypochlorite and basic calcium chloride.",
    applications:"Used as bleaching agent in textile and paper industries, disinfectant, and in water treatment."
  },
  
  // GROUP 8: METALS AND NON-METALS
  {
    id:"r149", name:"Reaction of Iron with Steam", class_level:9,
    reactants:"Fe,H₂O",
    products:"Fe₃O₄,H₂",
    equation:"3Fe + 4H₂O → Fe₃O₄ + 4H₂",
    conditions:"Red hot iron + steam",
    explanation:"Iron reacts with steam at high temperature to form tri-iron tetroxide (magnetite) and hydrogen gas. Iron is less reactive than sodium and calcium which react with cold water.",
    applications:"Demonstrates relative reactivity of metals with water. Used in steam reforming processes."
  },
  {
    id:"r150", name:"Reaction of Aluminum with Iron Oxide", class_level:9,
    reactants:"Al,Fe₂O₃",
    products:"Al₂O₃,Fe",
    equation:"2Al + Fe₂O₃ → Al₂O₃ + 2Fe + Heat",
    conditions:"Ignition (thermite)",
    explanation:"Aluminum reduces iron oxide to iron in a highly exothermic reaction (thermite reaction). Aluminum has higher affinity for oxygen than iron. Large amount of heat is released, melting the iron produced.",
    applications:"Used for welding railway tracks, repairing heavy machinery, and in incendiary devices."
  },
  
  // GROUP 9: CARBON AND ITS COMPOUNDS
  {
    id:"r151", name:"Formation of Carbon Monoxide", class_level:9,
    reactants:"C,O₂",
    products:"CO",
    equation:"2C + O₂ → 2CO",
    conditions:"Limited air supply",
    explanation:"Carbon burns in limited oxygen to form carbon monoxide instead of carbon dioxide. CO is a poisonous gas that binds to hemoglobin preventing oxygen transport.",
    applications:"Used as reducing agent in metallurgy. Producer gas and water gas contain CO as fuel component."
  },
  {
    id:"r152", name:"Reduction of Copper Oxide by Carbon", class_level:9,
    reactants:"CuO,C",
    products:"Cu,CO₂",
    equation:"2CuO + C → 2Cu + CO₂",
    conditions:"Strong heat",
    explanation:"Carbon reduces copper oxide to copper metal. Carbon is more reactive than copper and can displace it from its oxide. This demonstrates reduction of metal oxides by carbon.",
    applications:"Used in extraction of less reactive metals from their oxides. Demonstrates redox reactions."
  },
  
  // ============================================================
  // CLASS 10 CBSE/NCERT REACTIONS (30 reactions)
  // Chemical Reactions, Acids/Bases/Salts, Metals, Carbon Compounds
  // ============================================================
  
  // GROUP 1: CHEMICAL REACTIONS AND EQUATIONS
  {
    id:"r153", name:"Thermal Decomposition of Potassium Chlorate", class_level:10,
    reactants:"KClO₃",
    products:"KCl,O₂",
    equation:"2KClO₃ → 2KCl + 3O₂",
    conditions:"Heat, MnO₂ catalyst",
    explanation:"Potassium chlorate decomposes on heating in presence of manganese dioxide catalyst to give potassium chloride and oxygen gas. MnO₂ lowers the decomposition temperature and speeds up the reaction.",
    applications:"Laboratory preparation of oxygen gas. Used in matchstick industry and fireworks."
  },
  {
    id:"r154", name:"Photochemical Decomposition of Silver Bromide", class_level:10,
    reactants:"AgBr",
    products:"Ag,Br₂",
    equation:"2AgBr → 2Ag + Br₂ (sunlight)",
    conditions:"Sunlight",
    explanation:"Silver bromide decomposes in presence of sunlight to form silver metal and bromine. The silver appears as greyish-black stain. This is the basis of black and white photography.",
    applications:"Used in photographic films and papers. Demonstrates photochemical reactions."
  },
  {
    id:"r155", name:"Electrolysis of Water", class_level:10,
    reactants:"H₂O",
    products:"H₂,O₂",
    equation:"2H₂O → 2H₂ + O₂ (electrolysis)",
    conditions:"Electrolysis with acid/base",
    explanation:"Water decomposes into hydrogen and oxygen gases when electric current is passed through it. Hydrogen is liberated at cathode (double volume) and oxygen at anode. Small amount of acid or base is added to increase conductivity.",
    applications:"Demonstrates composition of water (2:1 H:O ratio). Used in hydrogen production and fuel cells."
  },
  {
    id:"r156", name:"Displacement of Copper by Zinc", class_level:10,
    reactants:"Zn,CuSO₄",
    products:"ZnSO₄,Cu",
    equation:"Zn + CuSO₄ → ZnSO₄ + Cu",
    conditions:"Aqueous solution",
    explanation:"Zinc being more reactive than copper displaces copper from copper sulfate solution. Blue color of CuSO₄ fades as colorless ZnSO₄ forms and reddish-brown copper metal deposits.",
    applications:"Demonstrates reactivity series. Used in metallurgy and electroplating."
  },
  {
    id:"r157", name:"Double Displacement - Precipitation of AgCl", class_level:10,
    reactants:"AgNO₃,NaCl",
    products:"AgCl,NaNO₃",
    equation:"AgNO₃ + NaCl → AgCl + NaNO₃",
    conditions:"Aqueous solution",
    explanation:"Silver nitrate reacts with sodium chloride to form a white curdy precipitate of silver chloride. This is a precipitation reaction where ions exchange partners. AgCl is insoluble in water but soluble in ammonia.",
    applications:"Test for chloride ions. Used in photographic films."
  },
  {
    id:"r158", name:"Double Displacement - Precipitation of BaSO₄", class_level:10,
    reactants:"BaCl₂,Na₂SO₄",
    products:"BaSO₄,NaCl",
    equation:"BaCl₂ + Na₂SO₄ → BaSO₄ + 2NaCl",
    conditions:"Aqueous solution",
    explanation:"Barium chloride reacts with sodium sulfate to form a white precipitate of barium sulfate. This is a test for sulfate ions. BaSO₄ is insoluble in water and acids.",
    applications:"Test for sulfate ions. Barium meal for X-ray imaging of digestive tract."
  },
  
  // GROUP 2: ACIDS, BASES AND SALTS - ADVANCED
  {
    id:"r159", name:"Dilution of Sulfuric Acid", class_level:10,
    reactants:"H₂SO₄,H₂O",
    products:"H₂SO₄(aq)",
    equation:"H₂SO₄ + H₂O → H₃O⁺ + HSO₄⁻",
    conditions:"Always add acid to water",
    explanation:"Concentrated sulfuric acid releases large amount of heat when mixed with water. Always add acid to water slowly with stirring, never water to acid. The reaction produces hydronium ions.",
    applications:"Preparation of dilute acids. Safety demonstration in handling concentrated acids."
  },
  {
    id:"r160", name:"Reaction of Acid with Metal Carbonate", class_level:10,
    reactants:"HCl,Na₂CO₃",
    products:"NaCl,H₂O,CO₂",
    equation:"Na₂CO₃ + 2HCl → 2NaCl + H₂O + CO₂",
    conditions:"Room temperature",
    explanation:"Metal carbonates react with acids to form salt, water, and carbon dioxide gas. The effervescence is due to CO₂ evolution. This is used as a test for carbonate ions.",
    applications:"Test for carbonate ions. Used in fire extinguishers (soda-acid type) and antacids."
  },
  {
    id:"r161", name:"Reaction of Acid with Metal Hydrogen Carbonate", class_level:10,
    reactants:"HCl,NaHCO₃",
    products:"NaCl,H₂O,CO₂",
    equation:"NaHCO₃ + HCl → NaCl + H₂O + CO₂",
    conditions:"Room temperature",
    explanation:"Metal hydrogen carbonates (bicarbonates) react with acids similarly to carbonates but more vigorously. Baking soda (NaHCO₃) reacts with acids to produce CO₂ which makes cakes and bread rise.",
    applications:"Baking powder, fire extinguishers, and antacids. Test for bicarbonate ions."
  },
  {
    id:"r162", name:"Reaction of Base with Ammonium Salt", class_level:10,
    reactants:"NaOH,NH₄Cl",
    products:"NaCl,NH₃,H₂O",
    equation:"NaOH + NH₄Cl → NaCl + NH₃ + H₂O",
    conditions:"Heat",
    explanation:"Strong bases react with ammonium salts on heating to liberate ammonia gas. The gas has characteristic pungent smell and turns moist red litmus blue. This is a test for ammonium ions.",
    applications:"Test for ammonium ions in qualitative analysis. Laboratory preparation of ammonia."
  },
  {
    id:"r163", name:"Preparation of Plaster of Paris", class_level:10,
    reactants:"CaSO₄·2H₂O",
    products:"CaSO₄·½H₂O",
    equation:"CaSO₄·2H₂O → CaSO₄·½H₂O + 1½H₂O",
    conditions:"Heat at 373K",
    explanation:"Gypsum (calcium sulfate dihydrate) on heating at 373K loses water molecules to form plaster of Paris (calcium sulfate hemihydrate). It regains water on mixing with water and hardens.",
    applications:"Used for making toys, statues, casts for sealing broken limbs, and in dentistry."
  },
  {
    id:"r164", name:"Setting of Plaster of Paris", class_level:10,
    reactants:"CaSO₄·½H₂O,H₂O",
    products:"CaSO₄·2H₂O",
    equation:"CaSO₄·½H₂O + 1½H₂O → CaSO₄·2H₂O",
    conditions:"Mixing with water",
    explanation:"When plaster of Paris is mixed with water, it sets into a hard solid mass of gypsum. The setting is due to interlocking of crystals and slight expansion. Heat is evolved during setting.",
    applications:"Used for immobilizing fractured bones, making decorative items, and in dentistry."
  },
  {
    id:"r165", name:"Bleaching Action of Chlorine", class_level:10,
    reactants:"Cl₂,H₂O",
    products:"HCl,HClO",
    equation:"Cl₂ + H₂O → HCl + HClO (hypochlorous acid bleaches)",
    conditions:"Moist conditions",
    explanation:"Chlorine bleaches by oxidation. In presence of water, chlorine forms hypochlorous acid (HClO) which gives oxygen to colored matter, oxidizing it to colorless products. The bleaching is permanent.",
    applications:"Bleaching cotton, linen, and wood pulp. Water treatment and disinfection."
  },
  
  // GROUP 3: METALS AND NON-METALS - ADVANCED
  {
    id:"r166", name:"Reaction of Sodium with Water", class_level:10,
    reactants:"Na,H₂O",
    products:"NaOH,H₂",
    equation:"2Na + 2H₂O → 2NaOH + H₂",
    conditions:"Room temperature",
    explanation:"Sodium reacts vigorously with cold water to form sodium hydroxide and hydrogen gas. The reaction is highly exothermic. Sodium melts into a silvery ball that darts on water surface due to H₂ gas evolution.",
    applications:"Demonstrates high reactivity of alkali metals. Laboratory preparation of hydrogen."
  },
  {
    id:"r167", name:"Reaction of Calcium with Water", class_level:10,
    reactants:"Ca,H₂O",
    products:"Ca(OH)₂,H₂",
    equation:"Ca + 2H₂O → Ca(OH)₂ + H₂",
    conditions:"Room temperature",
    explanation:"Calcium reacts less vigorously than sodium with cold water, forming calcium hydroxide (slaked lime) and hydrogen gas. The reaction produces enough heat to ignite hydrogen.",
    applications:"Demonstrates reactivity of alkaline earth metals. Preparation of calcium hydroxide."
  },
  {
    id:"r168", name:"Reaction of Aluminum with Steam", class_level:10,
    reactants:"Al,H₂O",
    products:"Al₂O₃,H₂",
    equation:"2Al + 3H₂O → Al₂O₃ + 3H₂",
    conditions:"High temperature steam",
    explanation:"Aluminum reacts with steam at high temperature to form aluminum oxide and hydrogen gas. The protective oxide layer on aluminum prevents reaction at room temperature.",
    applications:"Demonstrates amphoteric nature of aluminum oxide. Used in some hydrogen generation systems."
  },
  {
    id:"r169", name:"Reaction of Zinc with Dilute HCl", class_level:10,
    reactants:"Zn,HCl",
    products:"ZnCl₂,H₂",
    equation:"Zn + 2HCl → ZnCl₂ + H₂",
    conditions:"Room temperature",
    explanation:"Zinc reacts with dilute hydrochloric acid to form zinc chloride and hydrogen gas. Zinc is above hydrogen in reactivity series and can displace it from acids.",
    applications:"Laboratory preparation of hydrogen. Demonstrates metal-acid reactions."
  },
  {
    id:"r170", name:"Reaction of Iron with Copper Sulfate", class_level:10,
    reactants:"Fe,CuSO₄",
    products:"FeSO₄,Cu",
    equation:"Fe + CuSO₄ → FeSO₄ + Cu",
    conditions:"Aqueous solution",
    explanation:"Iron being more reactive than copper displaces copper from copper sulfate solution. Blue color fades to pale green (FeSO₄) and reddish-brown copper deposits form.",
    applications:"Demonstrates reactivity series. Used in copper recovery and electroplating."
  },
  {
    id:"r171", name:"Reaction of Zinc with Iron Sulfate", class_level:10,
    reactants:"Zn,FeSO₄",
    products:"ZnSO₄,Fe",
    equation:"Zn + FeSO₄ → ZnSO₄ + Fe",
    conditions:"Aqueous solution",
    explanation:"Zinc being more reactive than iron displaces iron from iron(II) sulfate solution. Pale green color fades to colorless and grey iron metal deposits.",
    applications:"Demonstrates displacement reactions and reactivity series."
  },
  {
    id:"r172", name:"Extraction of Iron in Blast Furnace", class_level:10,
    reactants:"Fe₂O₃,CO",
    products:"Fe,CO₂",
    equation:"Fe₂O₃ + 3CO → 2Fe + 3CO₂",
    conditions:"High temperature (1500°C)",
    explanation:"Carbon monoxide acts as reducing agent in the blast furnace, reducing iron oxide to iron metal. This is the main reaction in iron extraction from hematite ore.",
    applications:"Industrial extraction of iron from its ores. Foundation of steel industry."
  },
  {
    id:"r173", name:"Formation of Slag in Blast Furnace", class_level:10,
    reactants:"CaCO₃,SiO₂",
    products:"CaSiO₃,CO₂",
    equation:"CaCO₃ + SiO₂ → CaSiO₃ + CO₂",
    conditions:"High temperature",
    explanation:"Limestone (CaCO₃) decomposes to CaO which reacts with sand (SiO₂) to form calcium silicate (slag). Slag being lighter floats on molten iron and protects it from oxidation.",
    applications:"Removal of impurities (gangue) during iron extraction. Slag is used in cement manufacture."
  },
  
  // GROUP 4: CARBON AND ITS COMPOUNDS - ORGANIC CHEMISTRY
  {
    id:"r174", name:"Combustion of Ethane", class_level:10,
    reactants:"C₂H₆,O₂",
    products:"CO₂,H₂O",
    equation:"2C₂H₆ + 7O₂ → 4CO₂ + 6H₂O",
    conditions:"Ignition",
    explanation:"Ethane undergoes complete combustion to form carbon dioxide and water. Like all hydrocarbons, it produces CO₂ and H₂O on complete combustion with a blue flame.",
    applications:"Natural gas component used as fuel. Demonstrates combustion of alkanes."
  },
  {
    id:"r175", name:"Combustion of Ethene", class_level:10,
    reactants:"C₂H₄,O₂",
    products:"CO₂,H₂O",
    equation:"C₂H₄ + 3O₂ → 2CO₂ + 2H₂O",
    conditions:"Ignition",
    explanation:"Ethene burns with a luminous flame producing carbon dioxide and water. The luminous flame is due to higher carbon content and incomplete combustion producing carbon particles that glow.",
    applications:"Ethene is used as fuel and in oxy-ethylene torches for cutting and welding."
  },
  {
    id:"r176", name:"Combustion of Ethyne (Acetylene)", class_level:10,
    reactants:"C₂H₂,O₂",
    products:"CO₂,H₂O",
    equation:"2C₂H₂ + 5O₂ → 4CO₂ + 2H₂O",
    conditions:"Ignition",
    explanation:"Acetylene burns with a very hot sooty flame. When burned with oxygen (oxy-acetylene flame), temperature reaches about 3000°C, hot enough to melt metals.",
    applications:"Oxy-acetylene torches for cutting and welding metals. Used in portable lamps."
  },
  {
    id:"r177", name:"Addition of Bromine to Ethene", class_level:10,
    reactants:"C₂H₄,Br₂",
    products:"C₂H₄Br₂",
    equation:"C₂H₄ + Br₂ → C₂H₄Br₂",
    conditions:"Room temperature",
    explanation:"Ethene (unsaturated hydrocarbon) undergoes addition reaction with bromine. The orange-brown color of bromine disappears as 1,2-dibromoethane forms. This is a test for unsaturation.",
    applications:"Test for unsaturation (double/triple bonds). Used in organic synthesis."
  },
  {
    id:"r178", name:"Hydrogenation of Vegetable Oils", class_level:10,
    reactants:"Vegetable oil,H₂",
    products:"Vanaspati ghee",
    equation:"Unsaturated fat + H₂ → Saturated fat (Ni catalyst)",
    conditions:"Nickel catalyst, 473K",
    explanation:"Unsaturated vegetable oils undergo addition of hydrogen in presence of nickel catalyst to form saturated fats (vanaspati ghee/dalda). The process is called hydrogenation or hardening of oils.",
    applications:"Manufacture of vanaspati ghee from vegetable oils. Margarine production."
  },
  {
    id:"r179", name:"Oxidation of Ethanol to Ethanoic Acid", class_level:10,
    reactants:"C₂H₅OH,O₂",
    products:"CH₃COOH,H₂O",
    equation:"C₂H₅OH + O₂ → CH₃COOH + H₂O (catalyst)",
    conditions:"Alkaline KMnO₄ or K₂Cr₂O₇",
    explanation:"Ethanol is oxidized to ethanoic acid by strong oxidizing agents like acidified potassium dichromate or alkaline potassium permanganate. The orange dichromate turns green due to Cr³⁺ formation.",
    applications:"Manufacture of vinegar. Breathalyzer test for alcohol."
  },
  {
    id:"r180", name:"Reaction of Ethanol with Sodium", class_level:10,
    reactants:"C₂H₅OH,Na",
    products:"C₂H₅ONa,H₂",
    equation:"2C₂H₅OH + 2Na → 2C₂H₅ONa + H₂",
    conditions:"Room temperature",
    explanation:"Sodium reacts with ethanol to form sodium ethoxide and hydrogen gas. The reaction is less vigorous than with water because the O-H bond in alcohol is less polar than in water.",
    applications:"Preparation of sodium ethoxide. Demonstrates acidic nature of alcohols."
  },
  {
    id:"r181", name:"Dehydration of Ethanol", class_level:10,
    reactants:"C₂H₅OH",
    products:"C₂H₄,H₂O",
    equation:"C₂H₅OH → C₂H₄ + H₂O (conc. H₂SO₄, 443K)",
    conditions:"Conc. H₂SO₄, 443K",
    explanation:"Ethanol loses a water molecule when heated with concentrated sulfuric acid at 443K to form ethene. At 413K, ether is formed instead. This is an elimination reaction.",
    applications:"Laboratory preparation of ethene. Demonstrates dehydration of alcohols."
  },
  {
    id:"r182", name:"Reaction of Ethanoic Acid with Sodium Carbonate", class_level:10,
    reactants:"CH₃COOH,Na₂CO₃",
    products:"CH₃COONa,H₂O,CO₂",
    equation:"2CH₃COOH + Na₂CO₃ → 2CH₃COONa + H₂O + CO₂",
    conditions:"Room temperature",
    explanation:"Weak acetic acid reacts with sodium carbonate to form sodium acetate, water, and carbon dioxide. Brisk effervescence confirms the presence of acid.",
    applications:"Test for carboxylic acids. Demonstrates acidic nature of weak acids."
  },
  {
    id:"r183", name:"Reaction of Ethanoic Acid with Sodium Hydroxide", class_level:10,
    reactants:"CH₃COOH,NaOH",
    products:"CH₃COONa,H₂O",
    equation:"CH₃COOH + NaOH → CH₃COONa + H₂O",
    conditions:"Room temperature",
    explanation:"Acetic acid undergoes neutralization with sodium hydroxide to form sodium acetate and water. Being a weak acid, the neutralization releases less heat than strong acid-strong base reactions.",
    applications:"Preparation of sodium acetate. Used in buffer solutions."
  },
  {
    id:"r184", name:"Esterification of Ethanoic Acid with Ethanol", class_level:10,
    reactants:"CH₃COOH,C₂H₅OH",
    products:"CH₃COOC₂H₅,H₂O",
    equation:"CH₃COOH + C₂H₅OH ⇌ CH₃COOC₂H₅ + H₂O",
    conditions:"Conc. H₂SO₄, heat",
    explanation:"Carboxylic acid reacts with alcohol in presence of concentrated sulfuric acid to form ester with fruity smell and water. H₂SO₄ acts as catalyst and dehydrating agent. Reaction is reversible.",
    applications:"Synthesis of esters used in perfumes, flavorings, and as solvents."
  },
  {
    id:"r185", name:"Saponification of Ethyl Ethanoate", class_level:10,
    reactants:"CH₃COOC₂H₅,NaOH",
    products:"CH₃COONa,C₂H₅OH",
    equation:"CH₃COOC₂H₅ + NaOH → CH₃COONa + C₂H₅OH",
    conditions:"Heat",
    explanation:"Esters react with alkalis (sodium hydroxide) to form salt of carboxylic acid and alcohol. This reaction is called saponification and is used in soap making.",
    applications:"Soap manufacture. Hydrolysis of esters under alkaline conditions."
  },
  {
    id:"r186", name:"Reaction of Ethanol with Conc. Sulfuric Acid at 413K", class_level:10,
    reactants:"C₂H₅OH",
    products:"C₂H₅OC₂H₅,H₂O",
    equation:"2C₂H₅OH → C₂H₅OC₂H₅ + H₂O (conc. H₂SO₄, 413K)",
    conditions:"Conc. H₂SO₄, 413K",
    explanation:"At 413K, two molecules of ethanol undergo intermolecular dehydration to form diethyl ether and water. This is a substitution reaction where one alcohol displaces -OH from another.",
    applications:"Laboratory preparation of diethyl ether. Demonstrates temperature-dependent products."
  },
  {
    id:"r187", name:"Oxidation of Methanol to Methanal", class_level:10,
    reactants:"CH₃OH,O₂",
    products:"HCHO,H₂O",
    equation:"2CH₃OH + O₂ → 2HCHO + 2H₂O (catalyst)",
    conditions:" Heated copper catalyst",
    explanation:"Methanol is oxidized by passing its vapor over heated copper to form methanal (formaldehyde) and water. The hot copper acts as catalyst and oxidizing agent.",
    applications:"Manufacture of formaldehyde used in plastics, resins, and preservatives."
  },
  {
    id:"r188", name:"Oxidation of Methanal to Methanoic Acid", class_level:10,
    reactants:"HCHO,O₂",
    products:"HCOOH",
    equation:"2HCHO + O₂ → 2HCOOH",
    conditions:"Oxidizing agent",
    explanation:"Formaldehyde is further oxidized to formic acid (methanoic acid) by strong oxidizing agents. This demonstrates the oxidation of aldehydes to carboxylic acids.",
    applications:"Demonstrates oxidation states of carbon compounds. Used in organic synthesis."
  },
  {
    id:"r189", name:"Reaction of Methanoic Acid with Tollens Reagent", class_level:10,
    reactants:"HCOOH,AgNO₃,NH₄OH",
    products:"CO₂,Ag,H₂O",
    equation:"HCOOH + 2[Ag(NH₃)₂]⁺ + 2OH⁻ → CO₂ + 2Ag + 4NH₃ + 2H₂O",
    conditions:"Warm",
    explanation:"Formic acid reduces Tollens' reagent (ammoniacal silver nitrate) to metallic silver, forming a silver mirror. This is because formic acid has an aldehyde-like structure (contains -CHO group).",
    applications:"Test for formic acid and aldehydes. Silver mirror test."
  },
  {
    id:"r190", name:"Reaction of Ethanol with Phosphorus Pentachloride", class_level:10,
    reactants:"C₂H₅OH,PCl₅",
    products:"C₂H₅Cl,POCl₃,HCl",
    equation:"C₂H₅OH + PCl₅ → C₂H₅Cl + POCl₃ + HCl",
    conditions:"Room temperature",
    explanation:"Ethanol reacts with phosphorus pentachloride to form chloroethane, phosphoryl chloride, and hydrogen chloride. This demonstrates the replacement of -OH group by -Cl.",
    applications:"Preparation of alkyl chlorides from alcohols. Test for -OH group."
  },
  {
    id:"r191", name:"Decarboxylation of Sodium Ethanoate", class_level:10,
    reactants:"CH₃COONa,NaOH",
    products:"CH₄,Na₂CO₃",
    equation:"CH₃COONa + NaOH → CH₄ + Na₂CO₃ (CaO, heat)",
    conditions:"Soda lime (NaOH + CaO), heat",
    explanation:"Sodium salts of carboxylic acids lose CO₂ when heated with soda lime to form alkanes with one carbon less. This is called decarboxylation or soda lime decarboxylation.",
    applications:"Laboratory preparation of methane. Method to descend homologous series."
  },
  {
    id:"r192", name:"Substitution Reaction of Methane with Chlorine", class_level:10,
    reactants:"CH₄,Cl₂",
    products:"CH₃Cl,HCl",
    equation:"CH₄ + Cl₂ → CH₃Cl + HCl (UV light)",
    conditions:"UV light or heat",
    explanation:"Methane undergoes free radical substitution with chlorine in presence of UV light. Hydrogen atoms are replaced one by one by chlorine atoms. The reaction can continue to form CH₂Cl₂, CHCl₃, and CCl₄.",
    applications:"Manufacture of chloromethanes used as solvents and refrigerants."
  },
  
  // ============================================================
  // 100 BASIC REACTIONS FOR CLASS 9-10
  // ============================================================
  
  // ========================================
  // CLASS 9 BASIC REACTIONS (50 reactions)
  // ========================================
  
  // PHYSICAL CHEMISTRY & STATES OF MATTER (10 reactions)
  {
    id:"r193", name:"Freezing of Water", class_level:9,
    reactants:"H₂O(l)",
    products:"H₂O(s)",
    equation:"H₂O(l) → H₂O(s) + Heat",
    conditions:"0°C or below",
    explanation:"Water releases latent heat of fusion (334 J/g) and transforms into ice at 0°C. The molecules arrange in a hexagonal crystal structure with hydrogen bonds holding them in fixed positions.",
    applications:"Ice formation, refrigeration, preservation of food."
  },
  {
    id:"r194", name:"Boiling of Water", class_level:9,
    reactants:"H₂O(l)",
    products:"H₂O(g)",
    equation:"H₂O(l) + Heat → H₂O(g)",
    conditions:"100°C at 1 atm",
    explanation:"At boiling point, water absorbs latent heat of vaporization (2260 J/g) and transforms into steam. Bubbles of water vapor form throughout the liquid and rise to the surface.",
    applications:"Steam generation, cooking, sterilization."
  },
  {
    id:"r195", name:"Dissolution of Sugar in Water", class_level:9,
    reactants:"C₁₂H₂₂O₁₁,H₂O",
    products:"C₁₂H₂₂O₁₁(aq)",
    equation:"C₁₂H₂₂O₁₁(s) + H₂O → C₁₂H₂₂O₁₁(aq)",
    conditions:"Room temperature, stirring",
    explanation:"Sugar molecules separate from the crystal lattice and disperse uniformly among water molecules. This is a physical change - no new substance is formed.",
    applications:"Food preparation, pharmaceuticals, beverages."
  },
  {
    id:"r196", name:"Dissolution of Salt in Water", class_level:9,
    reactants:"NaCl,H₂O",
    products:"Na⁺,Cl⁻",
    equation:"NaCl(s) → Na⁺(aq) + Cl⁻(aq)",
    conditions:"Room temperature",
    explanation:"Sodium chloride dissociates into sodium and chloride ions when dissolved in water. The ions become surrounded by water molecules (hydration).",
    applications:"Electrolyte solutions, saline solutions, chemical reactions."
  },
  {
    id:"r197", name:"Evaporation of Alcohol", class_level:9,
    reactants:"C₂H₅OH(l)",
    products:"C₂H₅OH(g)",
    equation:"C₂H₅OH(l) → C₂H₅OH(g)",
    conditions:"Room temperature",
    explanation:"Ethanol evaporates at room temperature because it has weaker intermolecular forces than water. The process is faster than water evaporation and produces cooling.",
    applications:"Cooling effect in fever treatment, hand sanitizers, perfumes."
  },
  {
    id:"r198", name:"Melting of Wax", class_level:9,
    reactants:"Wax(s)",
    products:"Wax(l)",
    equation:"Wax(s) + Heat → Wax(l)",
    conditions:"60-70°C",
    explanation:"Wax melts when heated, changing from solid to liquid state. This is a physical change - the chemical composition remains the same. Different waxes have different melting points.",
    applications:"Candle making, sealing, polishes."
  },
  {
    id:"r199", name:"Condensation of Water Vapor on Cold Surface", class_level:9,
    reactants:"H₂O(g)",
    products:"H₂O(l)",
    equation:"H₂O(g) → H₂O(l) + Heat",
    conditions:"Cold surface",
    explanation:"Water vapor loses heat when it contacts a cold surface and condenses into liquid water droplets. This is the reverse of evaporation and releases latent heat.",
    applications:"Water harvesting, air conditioning, dew formation."
  },
  {
    id:"r200", name:"Sublimation of Iodine", class_level:9,
    reactants:"I₂(s)",
    products:"I₂(g)",
    equation:"I₂(s) ⇌ I₂(g)",
    conditions:"Gentle heating",
    explanation:"Iodine sublimes when heated, changing directly from solid to purple vapor without melting. On cooling, the vapor deposits as shiny crystals. This demonstrates sublimation.",
    applications:"Demonstrating sublimation, iodine purification, fingerprint detection."
  },
  {
    id:"r201", name:"Sublimation of Dry Ice", class_level:9,
    reactants:"CO₂(s)",
    products:"CO₂(g)",
    equation:"CO₂(s) → CO₂(g)",
    conditions:"Room temperature",
    explanation:"Solid carbon dioxide (dry ice) sublimes at room temperature, changing directly from solid to gas. It never becomes liquid at atmospheric pressure.",
    applications:"Refrigeration, fog effects, cooling agents."
  },
  {
    id:"r202", name:"Distillation of Water", class_level:9,
    reactants:"Impure H₂O",
    products:"Pure H₂O,Impurities",
    equation:"H₂O(l) → H₂O(g) → H₂O(l)",
    conditions:"Heat, condensation",
    explanation:"Water is heated to form steam, which is then cooled and condensed back to liquid. Impurities remain behind, producing pure water.",
    applications:"Water purification, production of distilled water, separation of mixtures."
  },
  
  // ATOMIC STRUCTURE & PERIODIC TABLE (8 reactions)
  {
    id:"r203", name:"Formation of Hydrogen Molecule", class_level:9,
    reactants:"H,H",
    products:"H₂",
    equation:"2H → H₂",
    conditions:"Normal conditions",
    explanation:"Two hydrogen atoms share their electrons to form a covalent bond, achieving stable duplet configuration. The shared pair is attracted by both nuclei.",
    applications:"Understanding chemical bonding, hydrogen fuel."
  },
  {
    id:"r204", name:"Formation of Chlorine Molecule", class_level:9,
    reactants:"Cl,Cl",
    products:"Cl₂",
    equation:"2Cl → Cl₂",
    conditions:"Normal conditions",
    explanation:"Two chlorine atoms share one pair of electrons to form a single covalent bond. Each atom achieves stable octet configuration of argon.",
    applications:"Understanding halogen bonding, chlorine chemistry."
  },
  {
    id:"r205", name:"Formation of Oxygen Molecule", class_level:9,
    reactants:"O,O",
    products:"O₂",
    equation:"2O → O₂",
    conditions:"Normal conditions",
    explanation:"Two oxygen atoms share two pairs of electrons forming a double bond. This makes oxygen molecule more stable and less reactive than atomic oxygen.",
    applications:"Understanding diatomic molecules, oxygen chemistry."
  },
  {
    id:"r206", name:"Formation of Nitrogen Molecule", class_level:9,
    reactants:"N,N",
    products:"N₂",
    equation:"2N → N₂",
    conditions:"Normal conditions",
    explanation:"Two nitrogen atoms share three pairs of electrons forming a triple bond. This makes N₂ very stable and explains why nitrogen is inert.",
    applications:"Understanding triple bonds, nitrogen fixation, inert atmosphere."
  },
  {
    id:"r207", name:"Formation of Lithium Fluoride", class_level:9,
    reactants:"Li,F",
    products:"LiF",
    equation:"Li + F → Li⁺F⁻",
    conditions:"Reaction",
    explanation:"Lithium loses one electron to form Li⁺ ion, fluorine gains one electron to form F⁻ ion. The electrostatic attraction forms ionic bond in LiF.",
    applications:"Understanding ionic bonding, battery electrolytes."
  },
  {
    id:"r208", name:"Formation of Sodium Fluoride", class_level:9,
    reactants:"Na,F",
    products:"NaF",
    equation:"Na + F → Na⁺F⁻",
    conditions:"Reaction",
    explanation:"Sodium donates one electron to fluorine, forming Na⁺ and F⁻ ions. The strong ionic bond makes NaF stable with high melting point.",
    applications:"Toothpaste ingredient, water fluoridation, understanding ionic radii."
  },
  {
    id:"r209", name:"Formation of Potassium Chloride", class_level:9,
    reactants:"K,Cl",
    products:"KCl",
    equation:"K + Cl → K⁺Cl⁻",
    conditions:"Reaction",
    explanation:"Potassium (group 1) loses one electron and chlorine (group 17) gains one electron. The resulting ions form KCl through ionic bonding.",
    applications:"Fertilizers, medicine, food additive (low sodium salt)."
  },
  {
    id:"r210", name:"Formation of Calcium Fluoride", class_level:9,
    reactants:"Ca,F₂",
    products:"CaF₂",
    equation:"Ca + F₂ → Ca²⁺ + 2F⁻",
    conditions:"Reaction",
    explanation:"Calcium loses two electrons to form Ca²⁺, two fluorine atoms each gain one electron. The 1:2 ratio balances the charges in CaF₂.",
    applications:"Fluorite mineral, optical materials, source of fluorine."
  },
  
  // CHEMICAL BONDING & MOLECULAR STRUCTURE (8 reactions)
  {
    id:"r211", name:"Formation of Hydrogen Chloride", class_level:9,
    reactants:"H₂,Cl₂",
    products:"HCl",
    equation:"H₂ + Cl₂ → 2HCl",
    conditions:"Light or heat",
    explanation:"Hydrogen and chlorine gases react to form hydrogen chloride. The H-Cl bond is polar covalent due to electronegativity difference.",
    applications:"Hydrochloric acid production, understanding polar bonds."
  },
  {
    id:"r212", name:"Formation of Ammonia Molecule", class_level:9,
    reactants:"N₂,H₂",
    products:"NH₃",
    equation:"N₂ + 3H₂ → 2NH₃",
    conditions:"High pressure, catalyst",
    explanation:"Nitrogen triple bond breaks and each nitrogen forms three N-H bonds. The molecule has pyramidal shape with lone pair on nitrogen.",
    applications:"Fertilizer production, understanding coordinate bonds."
  },
  {
    id:"r213", name:"Formation of Methane Molecule", class_level:9,
    reactants:"C,H₂",
    products:"CH₄",
    equation:"C + 2H₂ → CH₄",
    conditions:"Reaction conditions",
    explanation:"Carbon forms four covalent bonds with hydrogen atoms. The molecule has tetrahedral geometry with bond angle of 109.5°.",
    applications:"Natural gas, understanding tetrahedral structure."
  },
  {
    id:"r214", name:"Formation of Water Molecule", class_level:9,
    reactants:"H₂,O₂",
    products:"H₂O",
    equation:"2H₂ + O₂ → 2H₂O",
    conditions:"Spark",
    explanation:"Oxygen forms two covalent bonds with two hydrogen atoms. The molecule is bent with bond angle of 104.5° due to lone pairs.",
    applications:"Understanding VSEPR theory, hydrogen bonding, life processes."
  },
  {
    id:"r215", name:"Formation of Carbon Dioxide Molecule", class_level:9,
    reactants:"C,O₂",
    products:"CO₂",
    equation:"C + O₂ → CO₂",
    conditions:"Combustion",
    explanation:"Carbon forms two double bonds with oxygen atoms. The molecule is linear with bond angle of 180°.",
    applications:"Understanding double bonds, photosynthesis, greenhouse gas."
  },
  {
    id:"r216", name:"Formation of Magnesium Chloride", class_level:9,
    reactants:"Mg,Cl₂",
    products:"MgCl₂",
    equation:"Mg + Cl₂ → MgCl₂",
    conditions:"Burning",
    explanation:"Magnesium loses two electrons to form Mg²⁺, each chlorine gains one electron. The 1:2 ratio forms ionic lattice.",
    applications:"De-icing agent, magnesium source, understanding ionic crystals."
  },
  {
    id:"r217", name:"Formation of Aluminum Oxide", class_level:9,
    reactants:"Al,O₂",
    products:"Al₂O₃",
    equation:"4Al + 3O₂ → 2Al₂O₃",
    conditions:"Heat",
    explanation:"Aluminum loses 3 electrons (Al³⁺), oxygen gains 2 electrons (O²⁻). The 2:3 ratio balances charges in Al₂O₃.",
    applications:"Alumina, ceramics, abrasives, protective coating."
  },
  {
    id:"r218", name:"Formation of Calcium Oxide", class_level:9,
    reactants:"Ca,O₂",
    products:"CaO",
    equation:"2Ca + O₂ → 2CaO",
    conditions:"Heat",
    explanation:"Calcium loses two electrons to form Ca²⁺, oxygen gains two electrons to form O²⁻. The 1:1 ratio forms CaO with high melting point.",
    applications:"Quicklime, cement, steel making, water treatment."
  },
  
  // BASIC CHEMICAL REACTIONS (12 reactions)
  {
    id:"r219", name:"Rusting of Iron", class_level:9,
    reactants:"Fe,O₂,H₂O",
    products:"Fe₂O₃·nH₂O",
    equation:"4Fe + 3O₂ + nH₂O → 2Fe₂O₃·nH₂O",
    conditions:"Moist air",
    explanation:"Iron reacts with oxygen in presence of water to form hydrated iron(III) oxide (rust). This is a slow oxidation process.",
    applications:"Understanding corrosion, protective coatings, galvanization."
  },
  {
    id:"r220", name:"Burning of Magnesium Ribbon", class_level:9,
    reactants:"Mg,O₂",
    products:"MgO",
    equation:"2Mg + O₂ → 2MgO",
    conditions:"Burning",
    explanation:"Magnesium burns with dazzling white flame to form magnesium oxide. The reaction is highly exothermic and produces bright light.",
    applications:"Flash photography, fireworks, understanding combustion."
  },
  {
    id:"r221", name:"Reaction of Zinc with Oxygen", class_level:9,
    reactants:"Zn,O₂",
    products:"ZnO",
    equation:"2Zn + O₂ → 2ZnO",
    conditions:"Heat",
    explanation:"Zinc reacts with oxygen when heated to form zinc oxide. The oxide is white when hot and yellow when cold.",
    applications:"Zinc white pigment, sunscreens, rubber manufacturing."
  },
  {
    id:"r222", name:"Reaction of Copper with Oxygen", class_level:9,
    reactants:"Cu,O₂",
    products:"CuO",
    equation:"2Cu + O₂ → 2CuO",
    conditions:"Strong heat",
    explanation:"Copper reacts with oxygen on strong heating to form black copper(II) oxide. The shiny copper surface turns black.",
    applications:"Understanding metal oxidation, catalyst, pigments."
  },
  {
    id:"r223", name:"Reaction of Sulfur with Oxygen", class_level:9,
    reactants:"S,O₂",
    products:"SO₂",
    equation:"S + O₂ → SO₂",
    conditions:"Burning",
    explanation:"Sulfur burns in oxygen with blue flame to form sulfur dioxide gas. The gas has choking smell and is acidic.",
    applications:"Sulfuric acid production, preservative, understanding non-metal combustion."
  },
  {
    id:"r224", name:"Reaction of Phosphorus with Oxygen", class_level:9,
    reactants:"P₄,O₂",
    products:"P₄O₁₀",
    equation:"P₄ + 5O₂ → P₄O₁₀",
    conditions:"Burning",
    explanation:"White phosphorus burns in oxygen with bright yellow flame to form phosphorus pentoxide. The reaction produces dense white fumes.",
    applications:"Smoke screens, fertilizer production, safety matches."
  },
  {
    id:"r225", name:"Reaction of Hydrogen with Chlorine", class_level:9,
    reactants:"H₂,Cl₂",
    products:"HCl",
    equation:"H₂ + Cl₂ → 2HCl",
    conditions:"Sunlight",
    explanation:"Hydrogen and chlorine react explosively in sunlight to form hydrogen chloride. This is a photochemical reaction initiated by light.",
    applications:"HCl production, understanding photochemical reactions."
  },
  {
    id:"r226", name:"Reaction of Nitrogen with Oxygen", class_level:9,
    reactants:"N₂,O₂",
    products:"NO",
    equation:"N₂ + O₂ → 2NO",
    conditions:"High temperature (3000°C)",
    explanation:"Nitrogen and oxygen combine at very high temperatures to form nitrogen monoxide. This occurs in lightning and combustion engines.",
    applications:"Understanding atmospheric chemistry, acid rain formation."
  },
  {
    id:"r227", name:"Reaction of Carbon with Steam", class_level:9,
    reactants:"C,H₂O",
    products:"CO,H₂",
    equation:"C + H₂O → CO + H₂",
    conditions:"1000°C",
    explanation:"Carbon reacts with steam at high temperature to form water gas (CO + H₂ mixture). This is an important industrial fuel.",
    applications:"Water gas production, synthetic fuel, hydrogen production."
  },
  {
    id:"r228", name:"Reaction of Calcium with Nitrogen", class_level:9,
    reactants:"Ca,N₂",
    products:"Ca₃N₂",
    equation:"3Ca + N₂ → Ca₃N₂",
    conditions:"Heat",
    explanation:"Calcium reacts with nitrogen when heated to form calcium nitride. This demonstrates that active metals can react with nitrogen.",
    applications:"Fertilizer production, understanding metal-nitrogen compounds."
  },
  {
    id:"r229", name:"Reaction of Sodium with Sulfur", class_level:9,
    reactants:"Na,S",
    products:"Na₂S",
    equation:"2Na + S → Na₂S",
    conditions:"Heat",
    explanation:"Sodium reacts vigorously with sulfur to form sodium sulfide. This is a highly exothermic reaction.",
    applications:"Understanding reactivity of alkali metals, sulfide chemistry."
  },
  {
    id:"r230", name:"Reaction of Aluminum with Sulfur", class_level:9,
    reactants:"Al,S",
    products:"Al₂S₃",
    equation:"2Al + 3S → Al₂S₃",
    conditions:"Heat",
    explanation:"Aluminum reacts with sulfur when heated to form aluminum sulfide. The compound hydrolyzes readily in water.",
    applications:"Understanding aluminum compounds, sulfide chemistry."
  },
  
  // ACIDS, BASES & SALTS - BASIC (12 reactions)
  {
    id:"r231", name:"Reaction of Magnesium with Dilute HCl", class_level:9,
    reactants:"Mg,HCl",
    products:"MgCl₂,H₂",
    equation:"Mg + 2HCl → MgCl₂ + H₂",
    conditions:"Room temperature",
    explanation:"Magnesium reacts with dilute hydrochloric acid to form magnesium chloride and hydrogen gas. The reaction is vigorous.",
    applications:"Laboratory preparation of hydrogen, understanding metal-acid reactions."
  },
  {
    id:"r232", name:"Reaction of Aluminum with Dilute H₂SO₄", class_level:9,
    reactants:"Al,H₂SO₄",
    products:"Al₂(SO₄)₃,H₂",
    equation:"2Al + 3H₂SO₄ → Al₂(SO₄)₃ + 3H₂",
    conditions:"Room temperature",
    explanation:"Aluminum reacts with dilute sulfuric acid to form aluminum sulfate and hydrogen. The oxide layer must be removed for reaction to start.",
    applications:"Hydrogen production, understanding amphoteric nature."
  },
  {
    id:"r233", name:"Reaction of Iron with Dilute HCl", class_level:9,
    reactants:"Fe,HCl",
    products:"FeCl₂,H₂",
    equation:"Fe + 2HCl → FeCl₂ + H₂",
    conditions:"Room temperature",
    explanation:"Iron reacts slowly with dilute HCl to form ferrous chloride and hydrogen. The solution turns pale green due to Fe²⁺ ions.",
    applications:"Understanding metal reactivity, iron chemistry."
  },
  {
    id:"r234", name:"Neutralization of H₂SO₄ with NaOH", class_level:9,
    reactants:"H₂SO₄,NaOH",
    products:"Na₂SO₄,H₂O",
    equation:"H₂SO₄ + 2NaOH → Na₂SO₄ + 2H₂O",
    conditions:"Aqueous solution",
    explanation:"Sulfuric acid reacts with sodium hydroxide to form sodium sulfate and water. Being diprotic, one mole of H₂SO₄ neutralizes two moles of NaOH.",
    applications:"Production of sodium sulfate, pH control, understanding diprotic acids."
  },
  {
    id:"r235", name:"Neutralization of HNO₃ with KOH", class_level:9,
    reactants:"HNO₃,KOH",
    products:"KNO₃,H₂O",
    equation:"HNO₃ + KOH → KNO₃ + H₂O",
    conditions:"Aqueous solution",
    explanation:"Nitric acid reacts with potassium hydroxide to form potassium nitrate and water. This is a typical strong acid-strong base neutralization.",
    applications:"Production of potassium nitrate (fertilizer), pH control."
  },
  {
    id:"r236", name:"Reaction of CaO with H₂O", class_level:9,
    reactants:"CaO,H₂O",
    products:"Ca(OH)₂",
    equation:"CaO + H₂O → Ca(OH)₂",
    conditions:"Room temperature",
    explanation:"Calcium oxide (quicklime) reacts vigorously with water to form calcium hydroxide (slaked lime). The reaction is highly exothermic.",
    applications:"Whitewashing, cement production, water treatment."
  },
  {
    id:"r237", name:"Reaction of Na₂O with H₂O", class_level:9,
    reactants:"Na₂O,H₂O",
    products:"NaOH",
    equation:"Na₂O + H₂O → 2NaOH",
    conditions:"Room temperature",
    explanation:"Sodium oxide reacts with water to form sodium hydroxide. The resulting solution is strongly alkaline.",
    applications:"Caustic soda production, understanding basic oxides."
  },
  {
    id:"r238", name:"Reaction of SO₂ with H₂O", class_level:9,
    reactants:"SO₂,H₂O",
    products:"H₂SO₃",
    equation:"SO₂ + H₂O ⇌ H₂SO₃",
    conditions:"Room temperature",
    explanation:"Sulfur dioxide dissolves in water to form sulfurous acid. This is a reversible reaction - the acid decomposes back to SO₂ and water.",
    applications:"Understanding acidic oxides, food preservation, bleaching."
  },
  {
    id:"r239", name:"Reaction of CO₂ with CaO", class_level:9,
    reactants:"CO₂,CaO",
    products:"CaCO₃",
    equation:"CaO + CO₂ → CaCO₃",
    conditions:"Room temperature",
    explanation:"Calcium oxide reacts with carbon dioxide to form calcium carbonate. This is the reverse of thermal decomposition of limestone.",
    applications:"Cement setting, carbon dioxide absorption, understanding reversible reactions."
  },
  {
    id:"r240", name:"Preparation of Gypsum from CaCO₃", class_level:9,
    reactants:"CaCO₃,H₂SO₄",
    products:"CaSO₄,H₂O,CO₂",
    equation:"CaCO₃ + H₂SO₄ → CaSO₄ + H₂O + CO₂",
    conditions:"Room temperature",
    explanation:"Calcium carbonate reacts with sulfuric acid to form calcium sulfate, water, and carbon dioxide. This is used to produce gypsum.",
    applications:"Gypsum production, understanding acid-carbonate reactions."
  },
  {
    id:"r241", name:"Reaction of ZnO with NaOH", class_level:9,
    reactants:"ZnO,NaOH",
    products:"Na₂ZnO₂,H₂O",
    equation:"ZnO + 2NaOH → Na₂ZnO₂ + H₂O",
    conditions:"Aqueous solution",
    explanation:"Zinc oxide reacts with sodium hydroxide to form sodium zincate and water. This demonstrates the amphoteric nature of ZnO.",
    applications:"Understanding amphoteric oxides, zinc chemistry."
  },
  {
    id:"r242", name:"Reaction of PbO with NaOH", class_level:9,
    reactants:"PbO,NaOH",
    products:"Na₂PbO₂,H₂O",
    equation:"PbO + 2NaOH → Na₂PbO₂ + H₂O",
    conditions:"Heat",
    explanation:"Lead(II) oxide reacts with sodium hydroxide to form sodium plumbite. This shows amphoteric character of PbO.",
    applications:"Understanding amphoteric oxides, lead chemistry."
  },
  
  // ========================================
  // CLASS 10 BASIC REACTIONS (50 reactions)
  // ========================================
  
  // CHEMICAL REACTIONS & EQUATIONS (10 reactions)
  {
    id:"r243", name:"Thermal Decomposition of Limestone", class_level:10,
    reactants:"CaCO₃",
    products:"CaO,CO₂",
    equation:"CaCO₃ → CaO + CO₂",
    conditions:"Strong heat (>825°C)",
    explanation:"Calcium carbonate decomposes on strong heating to give calcium oxide (quicklime) and carbon dioxide. This is the basis of lime production.",
    applications:"Cement manufacture, lime production, steel making."
  },
  {
    id:"r244", name:"Decomposition of Silver Chloride", class_level:10,
    reactants:"AgCl",
    products:"Ag,Cl₂",
    equation:"2AgCl → 2Ag + Cl₂ (sunlight)",
    conditions:"Sunlight",
    explanation:"Silver chloride is sensitive to light and decomposes to form silver metal and chlorine gas. The silver appears as greyish-black.",
    applications:"Photography, understanding photochemical decomposition."
  },
  {
    id:"r245", name:"Decomposition of Hydrogen Peroxide", class_level:10,
    reactants:"H₂O₂",
    products:"H₂O,O₂",
    equation:"2H₂O₂ → 2H₂O + O₂",
    conditions:"MnO₂ catalyst",
    explanation:"Hydrogen peroxide decomposes into water and oxygen gas. The reaction is catalyzed by MnO₂ and produces bubbles of oxygen.",
    applications:"Antiseptic, bleaching, rocket propellant, oxygen source."
  },
  {
    id:"r246", name:"Displacement of Silver by Copper", class_level:10,
    reactants:"Cu,AgNO₃",
    products:"Cu(NO₃)₂,Ag",
    equation:"Cu + 2AgNO₃ → Cu(NO₃)₂ + 2Ag",
    conditions:"Aqueous solution",
    explanation:"Copper being more reactive than silver displaces silver from silver nitrate solution. Blue color appears and silver metal deposits.",
    applications:"Understanding reactivity series, silver recovery."
  },
  {
    id:"r247", name:"Displacement of Mercury by Silver", class_level:10,
    reactants:"Ag,Hg(NO₃)₂",
    products:"AgNO₃,Hg",
    equation:"2Ag + Hg(NO₃)₂ → 2AgNO₃ + Hg",
    conditions:"Aqueous solution",
    explanation:"Silver being more reactive than mercury displaces mercury from mercury(II) nitrate solution. Silvery mercury droplets form.",
    applications:"Understanding reactivity series, mercury extraction."
  },
  {
    id:"r248", name:"Double Displacement - Lead Chloride Precipitation", class_level:10,
    reactants:"Pb(NO₃)₂,NaCl",
    products:"PbCl₂,NaNO₃",
    equation:"Pb(NO₃)₂ + 2NaCl → PbCl₂ + 2NaNO₃",
    conditions:"Aqueous solution",
    explanation:"Lead nitrate reacts with sodium chloride to form a white precipitate of lead chloride. This is a precipitation reaction.",
    applications:"Test for lead ions, understanding solubility rules."
  },
  {
    id:"r249", name:"Double Displacement - Calcium Phosphate Precipitation", class_level:10,
    reactants:"CaCl₂,Na₃PO₄",
    products:"Ca₃(PO₄)₂,NaCl",
    equation:"3CaCl₂ + 2Na₃PO₄ → Ca₃(PO₄)₂ + 6NaCl",
    conditions:"Aqueous solution",
    explanation:"Calcium chloride reacts with sodium phosphate to form a white precipitate of calcium phosphate. This is the basis of bone formation.",
    applications:"Fertilizers, bone chemistry, water treatment."
  },
  {
    id:"r250", name:"Neutralization of Oxalic Acid with NaOH", class_level:10,
    reactants:"H₂C₂O₄,NaOH",
    products:"Na₂C₂O₄,H₂O",
    equation:"H₂C₂O₄ + 2NaOH → Na₂C₂O₄ + 2H₂O",
    conditions:"Aqueous solution",
    explanation:"Oxalic acid (diprotic) reacts with sodium hydroxide to form sodium oxalate and water. It is used to standardize NaOH solutions.",
    applications:"Standardization of bases, removing rust stains."
  },
  {
    id:"r251", name:"Reaction of Acid with Metal Sulfide", class_level:10,
    reactants:"HCl,FeS",
    products:"FeCl₂,H₂S",
    equation:"FeS + 2HCl → FeCl₂ + H₂S",
    conditions:"Room temperature",
    explanation:"Iron sulfide reacts with hydrochloric acid to form ferrous chloride and hydrogen sulfide gas. The gas has rotten egg smell.",
    applications:"Laboratory preparation of H₂S, qualitative analysis."
  },
  {
    id:"r252", name:"Reaction of Acid with Metal Sulfite", class_level:10,
    reactants:"HCl,Na₂SO₃",
    products:"NaCl,H₂O,SO₂",
    equation:"Na₂SO₃ + 2HCl → 2NaCl + H₂O + SO₂",
    conditions:"Room temperature",
    explanation:"Sodium sulfite reacts with hydrochloric acid to form sodium chloride, water, and sulfur dioxide gas. This is used to generate SO₂.",
    applications:"Laboratory preparation of SO₂, understanding sulfite chemistry."
  },
  
  // ACIDS, BASES & SALTS - ADVANCED (12 reactions)
  {
    id:"r253", name:"Reaction of Concentrated H₂SO₄ with Sugar", class_level:10,
    reactants:"H₂SO₄,C₁₂H₂₂O₁₁",
    products:"C,H₂O",
    equation:"C₁₂H₂₂O₁₁ → 12C + 11H₂O (dehydration)",
    conditions:"Concentrated acid",
    explanation:"Concentrated sulfuric acid dehydrates sugar, removing water and leaving behind black carbon. The mixture expands dramatically.",
    applications:"Demonstrating dehydrating property, understanding concentrated acids."
  },
  {
    id:"r254", name:"Reaction of Concentrated H₂SO₄ with Copper", class_level:10,
    reactants:"Cu,H₂SO₄",
    products:"CuSO₄,SO₂,H₂O",
    equation:"Cu + 2H₂SO₄ → CuSO₄ + SO₂ + 2H₂O",
    conditions:"Heat",
    explanation:"Hot concentrated sulfuric acid oxidizes copper to copper sulfate, itself getting reduced to sulfur dioxide. Brown fumes of SO₂ are evolved.",
    applications:"Preparation of copper sulfate, understanding oxidizing acids."
  },
  {
    id:"r255", name:"Reaction of Dilute HNO₃ with Magnesium", class_level:10,
    reactants:"Mg,HNO₃",
    products:"Mg(NO₃)₂,H₂",
    equation:"Mg + 2HNO₃ → Mg(NO₃)₂ + H₂",
    conditions:"Very dilute",
    explanation:"Very dilute nitric acid reacts with magnesium to form magnesium nitrate and hydrogen gas. Magnesium is one of the few metals that can liberate H₂ from HNO₃.",
    applications:"Understanding behavior of dilute HNO₃, hydrogen production."
  },
  {
    id:"r256", name:"Reaction of Zinc with Concentrated HNO₃", class_level:10,
    reactants:"Zn,HNO₃",
    products:"Zn(NO₃)₂,NO₂,H₂O",
    equation:"Zn + 4HNO₃ → Zn(NO₃)₂ + 2NO₂ + 2H₂O",
    conditions:"Concentrated",
    explanation:"Concentrated nitric acid reacts with zinc to form zinc nitrate and brown fumes of nitrogen dioxide. The acid acts as oxidizing agent.",
    applications:"Understanding oxidizing nature of concentrated HNO₃."
  },
  {
    id:"r257", name:"Reaction of Aluminum with Concentrated HNO₃", class_level:10,
    reactants:"Al,HNO₃",
    products:"Passive layer",
    equation:"Al + HNO₃ → No reaction (passivation)",
    conditions:"Concentrated, cold",
    mechanism:"Passivation by oxide-film formation",
    not_occur:"Concentrated nitric acid rapidly oxidizes the aluminum surface and forms a tightly adherent Al₂O₃ protective film. This oxide layer blocks fresh acid from reaching the metal surface, suppresses electron transfer, and stops the normal metal-acid reaction, so no regular reaction products are observed.",
    explanation:"Concentrated nitric acid makes aluminum passive by forming a protective oxide layer. This prevents further reaction.",
    applications:"Understanding passivation, storing concentrated HNO₃ in aluminum containers."
  },
  {
    id:"r258", name:"Reaction of NaOH with Aluminum", class_level:10,
    reactants:"NaOH,Al,H₂O",
    products:"NaAlO₂,H₂",
    equation:"2Al + 2NaOH + 2H₂O → 2NaAlO₂ + 3H₂",
    conditions:"Aqueous solution",
    explanation:"Aluminum reacts with sodium hydroxide to form sodium aluminate and hydrogen gas. This shows the amphoteric nature of aluminum.",
    applications:"Understanding amphoteric metals, drain cleaners."
  },
  {
    id:"r259", name:"Reaction of NaOH with Zinc", class_level:10,
    reactants:"NaOH,Zn,H₂O",
    products:"Na₂ZnO₂,H₂",
    equation:"Zn + 2NaOH → Na₂ZnO₂ + H₂",
    conditions:"Aqueous solution",
    explanation:"Zinc reacts with sodium hydroxide to form sodium zincate and hydrogen gas. This demonstrates amphoteric behavior of zinc.",
    applications:"Understanding amphoteric metals, hydrogen production."
  },
  {
    id:"r260", name:"Preparation of Alum from Aluminum", class_level:10,
    reactants:"Al,H₂SO₄,K₂SO₄",
    products:"KAl(SO₄)₂·12H₂O",
    equation:"2Al + 3H₂SO₄ → Al₂(SO₄)₃ + 3H₂, then Al₂(SO₄)₃ + K₂SO₄ → 2KAl(SO₄)₂",
    conditions:"Reaction then crystallization",
    explanation:"Aluminum sulfate reacts with potassium sulfate to form potash alum, a double salt. It forms octahedral crystals.",
    applications:"Water purification, dyeing, baking powder."
  },
  {
    id:"r261", name:"Preparation of Mohr's Salt", class_level:10,
    reactants:"FeSO₄,(NH₄)₂SO₄",
    products:"FeSO₄·(NH₄)₂SO₄·6H₂O",
    equation:"FeSO₄ + (NH₄)₂SO₄ + 6H₂O → FeSO₄·(NH₄)₂SO₄·6H₂O",
    conditions:"Crystallization",
    explanation:"Ferrous sulfate and ammonium sulfate combine to form Mohr's salt, a double salt. It is more stable than ferrous sulfate alone.",
    applications:"Volumetric analysis, standard solution preparation."
  },
  {
    id:"r262", name:"Reaction of Chlorine with Water", class_level:10,
    reactants:"Cl₂,H₂O",
    products:"HCl,HOCl",
    equation:"Cl₂ + H₂O ⇌ HCl + HOCl",
    conditions:"Room temperature",
    explanation:"Chlorine dissolves in water to form hydrochloric acid and hypochlorous acid. This is a disproportionation reaction.",
    applications:"Water treatment, bleaching, understanding chlorine chemistry."
  },
  {
    id:"r263", name:"Reaction of Chlorine with NaOH (Cold)", class_level:10,
    reactants:"Cl₂,NaOH",
    products:"NaCl,NaClO,H₂O",
    equation:"Cl₂ + 2NaOH → NaCl + NaClO + H₂O",
    conditions:"Cold dilute",
    explanation:"Chlorine undergoes disproportionation in cold dilute NaOH to form sodium chloride and sodium hypochlorite (bleaching powder component).",
    applications:"Bleach production, understanding disproportionation."
  },
  {
    id:"r264", name:"Reaction of Chlorine with Ca(OH)₂", class_level:10,
    reactants:"Cl₂,Ca(OH)₂",
    products:"CaOCl₂,CaCl₂,H₂O",
    equation:"2Cl₂ + 2Ca(OH)₂ → CaOCl₂ + CaCl₂ + 2H₂O",
    conditions:"Cold",
    explanation:"Chlorine reacts with slaked lime to form bleaching powder (calcium oxychloride), calcium chloride, and water.",
    applications:"Bleaching powder manufacture, water treatment."
  },
  
  // METALS & NON-METALS (12 reactions)
  {
    id:"r265", name:"Reaction of Potassium with Water", class_level:10,
    reactants:"K,H₂O",
    products:"KOH,H₂",
    equation:"2K + 2H₂O → 2KOH + H₂",
    conditions:"Room temperature",
    explanation:"Potassium reacts explosively with cold water to form potassium hydroxide and hydrogen. The reaction is more vigorous than sodium.",
    applications:"Understanding alkali metal reactivity, hydrogen production."
  },
  {
    id:"r266", name:"Reaction of Lithium with Water", class_level:10,
    reactants:"Li,H₂O",
    products:"LiOH,H₂",
    equation:"2Li + 2H₂O → 2LiOH + H₂",
    conditions:"Room temperature",
    explanation:"Lithium reacts with water to form lithium hydroxide and hydrogen gas. The reaction is less vigorous than other alkali metals.",
    applications:"Understanding alkali metal trends, battery chemistry."
  },
  {
    id:"r267", name:"Reaction of Beryllium with Steam", class_level:10,
    reactants:"Be,H₂O",
    products:"Be(OH)₂,H₂",
    equation:"Be + 2H₂O → Be(OH)₂ + H₂",
    conditions:"Steam, high temperature",
    explanation:"Beryllium reacts with steam at high temperature to form beryllium hydroxide and hydrogen. It does not react with cold water.",
    applications:"Understanding alkaline earth metal reactivity."
  },
  {
    id:"r268", name:"Reaction of Strontium with Water", class_level:10,
    reactants:"Sr,H₂O",
    products:"Sr(OH)₂,H₂",
    equation:"Sr + 2H₂O → Sr(OH)₂ + H₂",
    conditions:"Room temperature",
    explanation:"Strontium reacts vigorously with cold water to form strontium hydroxide and hydrogen gas. The hydroxide is sparingly soluble.",
    applications:"Understanding alkaline earth metal trends, fireworks (red color)."
  },
  {
    id:"r269", name:"Reaction of Barium with Water", class_level:10,
    reactants:"Ba,H₂O",
    products:"Ba(OH)₂,H₂",
    equation:"Ba + 2H₂O → Ba(OH)₂ + H₂",
    conditions:"Room temperature",
    explanation:"Barium reacts vigorously with water to form barium hydroxide and hydrogen. The hydroxide is soluble and strongly alkaline.",
    applications:"Understanding alkaline earth metal trends, green fireworks."
  },
  {
    id:"r270", name:"Reaction of Tin with Steam", class_level:10,
    reactants:"Sn,H₂O",
    products:"SnO₂,H₂",
    equation:"Sn + 2H₂O → SnO₂ + 2H₂",
    conditions:"Steam, heat",
    explanation:"Tin reacts with steam when heated to form tin(IV) oxide and hydrogen gas. It does not react with cold or hot water.",
    applications:"Understanding metal reactivity series, tin chemistry."
  },
  {
    id:"r271", name:"Reaction of Lead with Steam", class_level:10,
    reactants:"Pb,H₂O",
    products:"PbO,H₂",
    equation:"Pb + H₂O → PbO + H₂",
    conditions:"Steam, heat",
    explanation:"Lead reacts slowly with steam to form lead(II) oxide and hydrogen. The reaction is reversible at high temperatures.",
    applications:"Understanding metal reactivity, lead chemistry."
  },
  {
    id:"r272", name:"Reaction of Silver with Sulfur", class_level:10,
    reactants:"Ag,S",
    products:"Ag₂S",
    equation:"2Ag + S → Ag₂S",
    conditions:"Room temperature (slow)",
    explanation:"Silver reacts slowly with sulfur in air to form black silver sulfide. This is why silver tarnishes over time.",
    applications:"Understanding silver tarnishing, jewelry care."
  },
  {
    id:"r273", name:"Reaction of Gold with Aqua Regia", class_level:10,
    reactants:"Au,HNO₃,HCl",
    products:"HAuCl₄,NO,H₂O",
    equation:"Au + HNO₃ + 4HCl → HAuCl₄ + NO + 2H₂O",
    conditions:"Aqua regia",
    explanation:"Gold dissolves in aqua regia (3:1 HCl:HNO₃) to form chloroauric acid. Neither acid alone can dissolve gold.",
    applications:"Gold refining, understanding noble metal chemistry."
  },
  {
    id:"r274", name:"Reaction of Platinum with Aqua Regia", class_level:10,
    reactants:"Pt,HNO₃,HCl",
    products:"H₂PtCl₆,NO,H₂O",
    equation:"3Pt + 4HNO₃ + 18HCl → 3H₂PtCl₆ + 4NO + 8H₂O",
    conditions:"Aqua regia",
    explanation:"Platinum dissolves in aqua regia to form chloroplatinic acid. This is used to purify platinum.",
    applications:"Platinum refining, catalyst preparation."
  },
  {
    id:"r275", name:"Reduction of Iron Oxide by Carbon Monoxide", class_level:10,
    reactants:"Fe₂O₃,CO",
    products:"Fe,CO₂",
    equation:"Fe₂O₃ + 3CO → 2Fe + 3CO₂",
    conditions:"High temperature",
    explanation:"Carbon monoxide reduces iron(III) oxide to iron metal in the blast furnace. This is the primary iron extraction reaction.",
    applications:"Iron extraction, metallurgy, steel production."
  },
  {
    id:"r276", name:"Reduction of Zinc Oxide by Carbon", class_level:10,
    reactants:"ZnO,C",
    products:"Zn,CO",
    equation:"ZnO + C → Zn + CO",
    conditions:"High temperature",
    explanation:"Carbon reduces zinc oxide to zinc metal. This is used in the extraction of zinc from its oxide ore.",
    applications:"Zinc extraction, understanding reduction with carbon."
  },
  
  // CARBON COMPOUNDS - BASIC ORGANIC (16 reactions)
  {
    id:"r277", name:"Complete Combustion of Propane", class_level:10,
    reactants:"C₃H₈,O₂",
    products:"CO₂,H₂O",
    equation:"C₃H₈ + 5O₂ → 3CO₂ + 4H₂O",
    conditions:"Ignition",
    explanation:"Propane undergoes complete combustion to form carbon dioxide and water. It is a clean-burning fuel used in LPG.",
    applications:"LPG fuel, heating, cooking."
  },
  {
    id:"r278", name:"Complete Combustion of Butane", class_level:10,
    reactants:"C₄H₁₀,O₂",
    products:"CO₂,H₂O",
    equation:"2C₄H₁₀ + 13O₂ → 8CO₂ + 10H₂O",
    conditions:"Ignition",
    explanation:"Butane burns completely to form CO₂ and H₂O. It is the main component of lighter fuel and cooking gas.",
    applications:"Lighter fuel, portable stoves, camping gas."
  },
  {
    id:"r279", name:"Incomplete Combustion of Ethane", class_level:10,
    reactants:"C₂H₆,O₂",
    products:"CO,H₂O",
    equation:"2C₂H₆ + 5O₂ → 4CO + 6H₂O",
    conditions:"Limited oxygen",
    explanation:"Ethane undergoes incomplete combustion in limited oxygen to form carbon monoxide and water. The flame is sooty.",
    applications:"Understanding incomplete combustion, carbon monoxide poisoning."
  },
  {
    id:"r280", name:"Reaction of Ethene with Hydrogen", class_level:10,
    reactants:"C₂H₄,H₂",
    products:"C₂H₆",
    equation:"C₂H₄ + H₂ → C₂H₆",
    conditions:"Ni/Pt catalyst, heat",
    explanation:"Ethene undergoes catalytic hydrogenation to form ethane. This is an addition reaction across the double bond.",
    applications:"Hydrogenation of oils, understanding catalytic addition."
  },
  {
    id:"r281", name:"Reaction of Ethene with Chlorine", class_level:10,
    reactants:"C₂H₄,Cl₂",
    products:"C₂H₄Cl₂",
    equation:"C₂H₄ + Cl₂ → C₂H₄Cl₂",
    conditions:"Room temperature",
    explanation:"Ethene reacts with chlorine to form 1,2-dichloroethane. The red-brown color of chlorine disappears.",
    applications:"PVC production, understanding addition reactions."
  },
  {
    id:"r282", name:"Reaction of Ethene with HCl", class_level:10,
    reactants:"C₂H₄,HCl",
    products:"C₂H₅Cl",
    equation:"C₂H₄ + HCl → C₂H₅Cl",
    conditions:"Catalyst",
    explanation:"Ethene reacts with hydrogen chloride to form chloroethane. This follows Markovnikov's rule.",
    applications:"Production of ethyl chloride, understanding electrophilic addition."
  },
  {
    id:"r283", name:"Reaction of Ethene with Water", class_level:10,
    reactants:"C₂H₄,H₂O",
    products:"C₂H₅OH",
    equation:"C₂H₄ + H₂O → C₂H₅OH",
    conditions:"H₃PO₄ catalyst, 300°C, 60 atm",
    explanation:"Ethene reacts with steam in presence of phosphoric acid catalyst to form ethanol. This is hydration of alkene.",
    applications:"Industrial ethanol production, understanding hydration."
  },
  {
    id:"r284", name:"Reaction of Ethyne with Hydrogen", class_level:10,
    reactants:"C₂H₂,H₂",
    products:"C₂H₄",
    equation:"C₂H₂ + H₂ → C₂H₄",
    conditions:"Lindlar's catalyst",
    explanation:"Ethyne undergoes partial hydrogenation to form ethene. Using Lindlar's catalyst stops at the alkene stage.",
    applications:"Controlled hydrogenation, understanding selective reduction."
  },
  {
    id:"r285", name:"Reaction of Ethyne with Chlorine", class_level:10,
    reactants:"C₂H₂,Cl₂",
    products:"C₂H₂Cl₂",
    equation:"C₂H₂ + Cl₂ → C₂H₂Cl₂",
    conditions:"Room temperature",
    explanation:"Ethyne reacts with chlorine to form dichloroethene. Further addition gives tetrachloroethane.",
    applications:"Understanding addition to alkynes, solvent production."
  },
  {
    id:"r286", name:"Reaction of Ethyne with HCl", class_level:10,
    reactants:"C₂H₂,HCl",
    products:"C₂H₃Cl",
    equation:"C₂H₂ + HCl → C₂H₃Cl",
    conditions:"HgCl₂ catalyst",
    explanation:"Ethyne reacts with HCl in presence of mercuric chloride to form vinyl chloride. This is the first step in PVC production.",
    applications:"PVC production, understanding Markovnikov addition to alkynes."
  },
  {
    id:"r287", name:"Trimerization of Ethyne", class_level:10,
    reactants:"C₂H₂",
    products:"C₆H₆",
    equation:"3C₂H₂ → C₆H₆",
    conditions:"Red hot iron tube",
    explanation:"Three molecules of ethyne polymerize to form benzene when passed through red hot iron tube. This is cyclic polymerization.",
    applications:"Benzene production, understanding polymerization."
  },
  {
    id:"r288", name:"Oxidation of Methanol to Formaldehyde", class_level:10,
    reactants:"CH₃OH,O₂",
    products:"HCHO,H₂O",
    equation:"2CH₃OH + O₂ → 2HCHO + 2H₂O",
    conditions:"Ag catalyst, 600°C",
    explanation:"Methanol is oxidized by passing over silver catalyst to form formaldehyde. This is an industrial process.",
    applications:"Formaldehyde production, plastics, resins."
  },
  {
    id:"r289", name:"Oxidation of Ethanol to Acetaldehyde", class_level:10,
    reactants:"C₂H₅OH,O₂",
    products:"CH₃CHO,H₂O",
    equation:"2C₂H₅OH + O₂ → 2CH₃CHO + 2H₂O",
    conditions:"Cu catalyst, 300°C",
    explanation:"Ethanol vapor is passed over heated copper to form acetaldehyde. This is catalytic dehydrogenation.",
    applications:"Acetaldehyde production, understanding oxidation of alcohols."
  },
  {
    id:"r290", name:"Reaction of Ethanol with PCl₃", class_level:10,
    reactants:"C₂H₅OH,PCl₃",
    products:"C₂H₅Cl,H₃PO₃",
    equation:"3C₂H₅OH + PCl₃ → 3C₂H₅Cl + H₃PO₃",
    conditions:"Room temperature",
    explanation:"Ethanol reacts with phosphorus trichloride to form chloroethane and phosphorous acid. The -OH group is replaced by -Cl.",
    applications:"Preparation of alkyl chlorides, understanding substitution."
  },
  {
    id:"r291", name:"Reaction of Ethanol with SOCl₂", class_level:10,
    reactants:"C₂H₅OH,SOCl₂",
    products:"C₂H₅Cl,SO₂,HCl",
    equation:"C₂H₅OH + SOCl₂ → C₂H₅Cl + SO₂ + HCl",
    conditions:"Room temperature",
    explanation:"Thionyl chloride converts ethanol to chloroethane. The byproducts (SO₂ and HCl) are gases, making purification easy.",
    applications:"Preferred method for preparing alkyl chlorides from alcohols."
  },
  {
    id:"r292", name:"Dehydration of Ethanol to Ethene", class_level:10,
    reactants:"C₂H₅OH",
    products:"C₂H₄,H₂O",
    equation:"C₂H₅OH → C₂H₄ + H₂O",
    conditions:"Conc. H₂SO₄, 170°C",
    explanation:"Ethanol loses water molecule when heated with concentrated sulfuric acid at 170°C to form ethene. This is intramolecular dehydration.",
    applications:"Laboratory preparation of ethene, understanding elimination reactions."
  },

  // ============================================================
  // BENZENE REACTIONS — Complete Coverage (from literature)
  // ============================================================

  // --- EAS: Halogenation ---
  {
    id:"r293", name:"Benzene Bromination (EAS)", class_level:12,
    reactants:"C₆H₆,Br₂",
    products:"C₆H₅Br,HBr",
    equation:"C₆H₆ + Br₂ → C₆H₅Br + HBr (AlBr₃ catalyst)",
    conditions:"Anhydrous AlBr₃ (Lewis acid)",
    explanation:"AlBr₃ polarises the Br–Br bond, generating a bromonium species (Br⁺-AlBr₄⁻). This electrophile attacks the benzene π-system, forming a resonance-stabilised arenium (Wheland) intermediate. AlBr₄⁻ then abstracts a proton to restore aromaticity, yielding bromobenzene and HBr. Aromaticity is preserved throughout the substitution rather than addition pathway.",
    applications:"Bromobenzene is an important intermediate in pharmaceutical synthesis and as a precursor to Grignard reagents (C₆H₅MgBr) for C–C bond-forming reactions."
  },
  {
    id:"r294", name:"Benzene Chlorination (EAS)", class_level:12,
    reactants:"C₆H₆,Cl₂",
    products:"C₆H₅Cl,HCl",
    equation:"C₆H₆ + Cl₂ → C₆H₅Cl + HCl (FeCl₃ catalyst)",
    conditions:"Anhydrous FeCl₃ or AlCl₃",
    explanation:"FeCl₃ coordinates to Cl₂ to polarise the Cl–Cl bond, making one Cl atom strongly electrophilic. It attacks the benzene π-system to form an arenium sigma-complex, which then loses H⁺ (taken by FeCl₄⁻) to regenerate aromaticity and yield chlorobenzene. This is a classic electrophilic aromatic substitution.",
    applications:"Chlorobenzene is used to manufacture phenol (via hydrolysis), as a high-boiling solvent, and as a precursor to pharmaceuticals and pesticides."
  },

  // --- EAS: Nitration ---
  {
    id:"r295", name:"Benzene Nitration (EAS)", class_level:12,
    reactants:"C₆H₆,HNO₃",
    products:"C₆H₅NO₂,H₂O",
    equation:"C₆H₆ + HNO₃ → C₆H₅NO₂ + H₂O (H₂SO₄ catalyst)",
    conditions:"Mixed acid: conc. HNO₃/conc. H₂SO₄, 50–55°C",
    explanation:"Conc. H₂SO₄ protonates HNO₃, generating the nitronium ion (NO₂⁺) — the active electrophile. NO₂⁺ attacks the benzene ring forming a resonance-stabilised arenium intermediate across three structures. HSO₄⁻ abstracts H⁺ to restore aromaticity. Temperature is held below 55°C to prevent dinitration.",
    applications:"Nitrobenzene is reduced to aniline — foundation of the synthetic dye and pharmaceutical industries. Also used in polyurethane manufacture via MDI."
  },

  // --- EAS: Sulfonation ---
  {
    id:"r296", name:"Benzene Sulfonation (EAS)", class_level:12,
    reactants:"C₆H₆,SO₃",
    products:"C₆H₅SO₃H",
    equation:"C₆H₆ + SO₃ → C₆H₅SO₃H (fuming H₂SO₄)",
    conditions:"Fuming H₂SO₄ (oleum) or SO₃, heat",
    explanation:"SO₃ (from oleum) is the electrophile — its sulfur atom attacks the benzene π-system. Unlike other EAS reactions, sulfonation is reversible: the –SO₃H group is removed by steam hydrolysis at higher temperatures. This reversibility makes sulfonation invaluable as a temporary blocking group in multi-step synthesis to direct other substituents.",
    applications:"Benzenesulfonic acid is a precursor to saccharin, sulfa drugs, ion-exchange resins, and detergents. Reversibility is exploited in synthetic strategies."
  },

  // --- EAS: Friedel-Crafts Acylation ---
  {
    id:"r297", name:"Friedel-Crafts Acylation of Benzene", class_level:12,
    reactants:"C₆H₆,CH₃COCl,AlCl₃",
    products:"C₆H₅COCH₃,HCl",
    equation:"C₆H₆ + CH₃COCl → C₆H₅COCH₃ + HCl (AlCl₃)",
    conditions:"Anhydrous AlCl₃, room temperature, inert solvent",
    explanation:"AlCl₃ abstracts Cl⁻ from the acyl chloride to form a resonance-stabilised acylium ion (CH₃C≡O⁺). This electrophile attacks benzene forming a sigma-complex. Loss of H⁺ restores aromaticity yielding acetophenone. Unlike alkylation, acylation does not suffer polysubstitution because –COR is electron-withdrawing and deactivates the ring.",
    applications:"Key route to aromatic ketones (acetophenone, benzophenone). Used in fragrance industry and as precursors to secondary alcohols via reduction."
  },

  // --- Addition: Catalytic Hydrogenation ---
  {
    id:"r298", name:"Benzene Catalytic Hydrogenation", class_level:12,
    reactants:"C₆H₆,H₂",
    products:"C₆H₁₂",
    equation:"C₆H₆ + 3H₂ → C₆H₁₂ (cyclohexane)",
    conditions:"Pt, Pd, or Ni catalyst; high pressure H₂, elevated temperature",
    explanation:"Three equivalents of H₂ are added across all three double bonds of benzene on a metal catalyst surface. Forcing conditions are required because the aromatic resonance energy (~150 kJ/mol) must be overcome. Selective partial hydrogenation to cyclohexene is possible over specialised Ru catalysts with water as modifier (Asahi process).",
    applications:"Cyclohexane is the primary feedstock for nylon-6 and nylon-6,6 manufacture via cyclohexanone and caprolactam/adipic acid."
  },

  // --- Addition: Birch Reduction ---
  {
    id:"r299", name:"Birch Reduction of Benzene", class_level:12,
    reactants:"C₆H₆,Na",
    products:"C₆H₈",
    equation:"C₆H₆ + 2Na + 2ROH → 1,4-cyclohexadiene + 2NaOR",
    conditions:"Na or Li metal in liquid NH₃ (−33°C), alcohol (ROH) as proton source",
    explanation:"Alkali metal dissolves in liquid NH₃ to give solvated electrons (e⁻aq). A solvated electron adds to benzene forming a radical anion. Protonation by ROH gives a cyclohexadienyl radical, which accepts another electron to form a carbanion, then is protonated again to give 1,4-cyclohexadiene. Electron-donating substituents direct reduction to unsubstituted positions; electron-withdrawing groups direct reduction to substituted positions.",
    applications:"One of the most powerful methods in total synthesis to access partially unsaturated six-membered rings. Widely used in steroid synthesis and natural product chemistry."
  },

  // --- Addition: Halogen Addition (Photochemical / Radical) ---
  {
    id:"r300", name:"Benzene Photochemical Halogen Addition", class_level:12,
    reactants:"C₆H₆,Cl₂",
    products:"C₆H₆Cl₆",
    equation:"C₆H₆ + 3Cl₂ → C₆H₆Cl₆ (BHC, benzene hexachloride)",
    conditions:"UV (hν) light, no Lewis acid catalyst",
    explanation:"UV irradiation causes homolytic cleavage of Cl₂ to form two Cl• radicals (initiation). Cl• adds across a C=C bond of benzene giving a ring radical, which reacts with another Cl₂ to continue the chain. 1,2,3,4,5,6-Addition across all three double bonds via a radical mechanism (not ionic EAS) gives hexachlorocyclohexane. The γ-isomer (lindane) has insecticidal properties.",
    applications:"The γ-isomer (lindane) was used as an insecticide, now banned due to environmental persistence. Important for contrasting radical addition vs. ionic substitution mechanisms."
  },

  // --- Combustion ---
  {
    id:"r301", name:"Benzene Complete Combustion", class_level:11,
    reactants:"C₆H₆,O₂",
    products:"CO₂,H₂O",
    equation:"2C₆H₆ + 15O₂ → 12CO₂ + 6H₂O",
    conditions:"Ignition, excess O₂",
    explanation:"In excess oxygen, benzene undergoes complete combustion. Benzene burns with a characteristically sooty yellow flame due to its high C:H ratio (1:1), causing incomplete combustion in normal air. Complete combustion requires 7.5 mol O₂ per mol benzene. The reaction is highly exothermic (ΔH°comb ≈ −3268 kJ/mol). Singlet oxygen reduces the activation energy of initiation and accelerates chain-branching mechanisms.",
    applications:"Combustion stoichiometry and thermochemistry of aromatic fuels. Benzene vapour is flammable and a known carcinogen — relevant to fire hazard and environmental pollution assessment."
  },

  // --- Catalytic Oxidation: Maleic Anhydride ---
  {
    id:"r302", name:"Benzene Catalytic Oxidation to Maleic Anhydride", class_level:12,
    reactants:"C₆H₆,O₂",
    products:"C₄H₂O₃,CO₂,H₂O",
    equation:"C₆H₆ + 4.5O₂ → C₄H₂O₃ + 2CO₂ + 2H₂O (V₂O₅, 400–500°C)",
    conditions:"V₂O₅ catalyst, 400–500°C, air",
    explanation:"Over a V₂O₅ catalyst, benzene undergoes partial oxidation. The ring is cleaved and four carbons become maleic anhydride while two are lost as CO₂. The Mars–van Krevelen mechanism operates: V⁵⁺ oxidises the substrate (V⁵⁺ → V⁴⁺), and O₂ re-oxidises V⁴⁺ back to V⁵⁺. Temperature and contact time are controlled to prevent complete combustion.",
    applications:"Maleic anhydride is used in unsaturated polyester resins (fibreglass), alkyd resins, agricultural chemicals, and as a Diels–Alder dienophile."
  },

  // --- Catalytic Oxidation: Phenol (Cumene Process) ---
  {
    id:"r303", name:"Benzene to Phenol (Cumene Process)", class_level:12,
    reactants:"C₆H₆,O₂",
    products:"C₆H₅OH,CH₃COCH₃",
    equation:"C₆H₆ + C₃H₆ → C₆H₅CH(CH₃)₂ → C₆H₅OH + CH₃COCH₃",
    conditions:"Step 1: H₃PO₄/SiO₂; Step 2: Air (O₂); Step 3: Dilute H₂SO₄",
    explanation:"Step 1: Benzene undergoes acid-catalysed Friedel-Crafts alkylation with propylene to give cumene (isopropylbenzene). Step 2: Cumene is oxidised by air via a free-radical mechanism to cumene hydroperoxide (ROOH). Step 3: H₂SO₄ cleaves the hydroperoxide by Hock rearrangement to give phenol and acetone simultaneously. Both products are commercially valuable.",
    applications:">90% of the world's phenol comes from this process. Phenol is used in Bakelite, bisphenol A (polycarbonates), aspirin. Acetone is used as solvent and for PMMA (Perspex) manufacture."
  },

  // --- Ozonolysis ---
  {
    id:"r304", name:"Benzene Ozonolysis", class_level:12,
    reactants:"C₆H₆,O₃",
    products:"OHCCHO",
    equation:"C₆H₆ + 3O₃ → 3 glyoxal fragments (workup gives OHC-CHO etc.)",
    conditions:"O₃ in CH₂Cl₂, low temperature; reductive workup (Zn/AcOH) or oxidative workup (H₂O₂)",
    explanation:"Benzene reacts slowly with ozone (slower than alkenes due to aromatic stabilisation). Each C=C unit of benzene undergoes 1,3-dipolar cycloaddition with O₃ to give a molozonide, which rearranges to a carbonyl oxide/aldehyde pair. Complete ozonolysis of all three bonds and hydrolytic workup cleaves the ring to give glyoxal (OHC-CHO) and glyoxylic acid. In the atmosphere, OH-radical oxidation of benzene leads to ring-opening yielding muconaldehyde.",
    applications:"Rarely used preparatively. Important in atmospheric chemistry — benzene ozonolysis contributes to secondary organic aerosol (SOA) formation and photochemical smog in urban environments."
  },

  // --- Dearomatization: Photochemical ---
  {
    id:"r305", name:"Benzene Photochemical Dearomatization", class_level:12,
    reactants:"C₆H₆,O₂",
    products:"C₆H₆O₂",
    equation:"C₆H₆ + ¹O₂ → benzene oxide / muconaldehyde (hν, sensitiser)",
    conditions:"UV light, photosensitiser (rose bengal), or direct irradiation",
    explanation:"Under UV irradiation, benzene undergoes dearomative reactions that break the aromatic π-system. Photooxygenation with singlet oxygen (¹O₂) gives benzene 1,2-dioxetane intermediates rearranging to muconaldehyde. Direct photoisomerisation gives highly strained isomers: Dewar benzene, benzvalene, and prismane. These dearomative pathways provide access to 3D building blocks (bicyclic/polycyclic frameworks) inaccessible by ground-state chemistry.",
    applications:"Total synthesis of natural products (terpenoids, alkaloids) to generate molecular complexity from flat rings. Also relevant in understanding photocarcinogenesis of benzene in biological systems."
  },

  // --- C–H Functionalization ---
  {
    id:"r306", name:"Benzene Direct C–H Functionalization", class_level:12,
    reactants:"C₆H₆,O₂",
    products:"C₆H₅R",
    equation:"C₆H₆ + R–X → C₆H₅–R + HX (TM or photoredox catalyst)",
    conditions:"Transition-metal (Pd, Rh, Ru) or photoredox catalyst, visible light or heat",
    explanation:"Direct C–H functionalization bypasses the need to pre-halogenate benzene. In TM-catalysed CMD (concerted metalation-deprotonation) mechanism, the metal inserts into the C–H bond giving an arylmetal intermediate that undergoes reductive elimination to form the new C–C or C–X bond. In photoredox pathways, visible light generates benzene radical cation (C₆H₆•⁺) enabling oxidative cross-coupling with a radical partner. Radical–radical cross-coupling gives modular direct arene C–H alkylation.",
    applications:"Atom-economical green chemistry. Growing importance in pharmaceutical manufacturing as an alternative to pre-functionalisation. Direct alkylation of benzene gives alkylbenzenes used in detergents."
  },

  // --- Enzymatic Ring Cleavage ---
  {
    id:"r307", name:"Benzene Ring C–C Bond Cleavage (Enzymatic/Catalytic)", class_level:12,
    reactants:"C₆H₆,O₂",
    products:"OHCCHO",
    equation:"C₆H₆ + O₂ → catechol → muconic acid (dioxygenase enzymes)",
    conditions:"Enzymatic: dioxygenase enzymes in bacteria; Abiotic: Rh/Fe/Cu catalysts",
    explanation:"Dioxygenase enzymes in soil bacteria first hydroxylate benzene to benzene-1,2-diol (catechol) using O₂ and NADH. A second dioxygenase cleaves the aromatic ring by inserting both O₂ atoms between the two –OH groups (extradiol or intradiol cleavage), giving cis,cis-muconic acid or 2-hydroxymuconate semialdehyde. Abiotic catalytic ring cleavage has been achieved with specialised Rh, Fe, and Cu complexes in research settings.",
    applications:"Bioremediation of benzene-contaminated soil and groundwater (benzene is a carcinogen). Muconic acid is a bio-based platform chemical for bio-nylon and bio-PET production."
  },

  // --- Benzylic Radical Bromination ---
  {
    id:"r308", name:"Toluene Benzylic Bromination (Radical)", class_level:12,
    reactants:"C₆H₅CH₃,Br₂",
    products:"C₆H₅CH₂Br,HBr",
    equation:"C₆H₅CH₃ + Br₂ → C₆H₅CH₂Br + HBr (hν, CCl₄)",
    conditions:"UV light or radical initiator (peroxide), CCl₄ solvent, reflux",
    explanation:"Under photochemical conditions (not Lewis acid, which would give ring bromination), Br• radical selectively abstracts the benzylic H from toluene because the resulting benzyl radical is stabilised by resonance delocalisation into the π-system. The benzyl radical then reacts with Br₂ to give benzyl bromide and regenerate Br•, propagating the chain. NBS (N-bromosuccinimide) is a milder and more selective alternative reagent.",
    applications:"Benzyl bromide is a versatile electrophile for SN2 reactions, used for benzyl protecting groups in sugar/amino acid chemistry, and as a building block in pharmaceutical and fragrance synthesis."
  },

  // --- Dearomative Partial Reduction (Crich/SmI₂) ---
  {
    id:"r309", name:"Benzene Dearomative Partial Reduction (Crich/SmI₂)", class_level:12,
    reactants:"C₆H₆,H₂",
    products:"C₆H₈",
    equation:"C₆H₆ → 1,3-cyclohexadiene or 1,4-cyclohexadiene (controlled conditions)",
    conditions:"SmI₂/proton source, or dissolving metal with controlled stoichiometry",
    explanation:"Beyond classical Birch reduction, dearomative partial reductions of benzene using SmI₂ or controlled dissolving-metal conditions can selectively give 1,3-cyclohexadiene (conjugated) in addition to the classical 1,4-isomer. Selectivity depends on relative acidities of proton donors and stability of radical anion intermediates. Recent ammonia-free Birch-type reductions use silanes or boron hydrides as H-donors under photoredox catalysis, avoiding hazardous liquid NH₃ and alkali metals.",
    applications:"1,3-Cyclohexadiene is a valuable diene for Diels–Alder cycloadditions. 1,4-Cyclohexadiene is used in steroid and natural product total synthesis."
  },

  // --- EAS: Iodination ---
  {
    id:"r310", name:"Benzene Iodination (EAS)", class_level:12,
    reactants:"C₆H₆,I₂",
    products:"C₆H₅I,HI",
    equation:"C₆H₆ + I₂ → C₆H₅I + HI (HNO₃ or HIO₃ oxidant)",
    conditions:"I₂ with oxidising agent (HNO₃, HIO₃, or H₂O₂); or I₂/Lewis acid (ICl)",
    explanation:"Iodine alone is too weak an electrophile to carry out EAS on benzene because iodination is thermodynamically reversible and the Wheland intermediate is not stabilised enough to lose HI. An oxidising agent (HNO₃, HIO₃) is required to drive the reaction forward by oxidising the HI byproduct or by generating a more reactive iodonium species (I⁺). Alternatively, ICl (iodine monochloride) with a Lewis acid generates a more reactive I⁺ species.",
    applications:"Iodobenzene is an important partner in palladium-catalysed cross-coupling reactions (Heck, Suzuki, Sonogashira) — key methods in pharmaceutical and material synthesis."
  },

  // --- Nucleophilic Aromatic Substitution (activated benzene) ---
  {
    id:"r311", name:"Nucleophilic Aromatic Substitution (NAS) on Nitrobenzene", class_level:12,
    reactants:"C₆H₅NO₂,NaOH",
    products:"C₆H₅OH,NaNO₂",
    equation:"2,4-dinitrochlorobenzene + OH⁻ → 2,4-dinitrophenol + Cl⁻ (SNAr)",
    conditions:"Strongly electron-withdrawing groups on ring (NO₂), nucleophile (OH⁻, NH₃, RNH₂), heat",
    explanation:"Unlike EAS, nucleophilic aromatic substitution (SNAr) proceeds by addition-elimination (Meisenheimer complex mechanism). A nucleophile (Nu⁻) attacks the ipso carbon bearing the leaving group (e.g., Cl), forming a negatively charged Meisenheimer complex stabilised by electron-withdrawing groups (NO₂) at ortho/para positions. The leaving group (Cl⁻) then departs to restore aromaticity. Multiple electron-withdrawing groups greatly activate the ring toward Nu attack.",
    applications:"SNAr is crucial in synthesis of pharmaceuticals and agrochemicals with heteroatom substituents. Used to introduce –OH, –OR, –NR₂, –SR groups onto electron-poor arenes."
  },

  // ============================================================
  // BENZENE BASIC REACTIONS (Core NCERT Curriculum)
  // ============================================================

  // --- Friedel-Crafts Alkylation with Methane Derivatives ---
  {
    id:"r312", name:"Benzene Friedel-Crafts Alkylation with Chloromethane", class_level:12,
    reactants:"C₆H₆,CH₃Cl,AlCl₃",
    products:"C₆H₅CH₃,HCl",
    equation:"C₆H₆ + CH₃Cl → C₆H₅CH₃ + HCl (AlCl₃ catalyst)",
    conditions:"Anhydrous AlCl₃, room temperature",
    explanation:"AlCl₃ acts as a Lewis acid and polarizes the C–Cl bond in chloromethane, generating a methyl carbocation (CH₃⁺) or polarized complex. This electrophile attacks the electron-rich benzene ring, forming a sigma complex (arenium ion). Loss of a proton restores aromaticity, yielding toluene. This is the fundamental Friedel-Crafts alkylation reaction for introducing alkyl groups to benzene.",
    applications:"Industrial synthesis of toluene from benzene. Toluene is a key starting material for TNT, benzoic acid, benzaldehyde, and polyurethane production."
  },

  // --- Benzene + Methane Reactions (Industrial Processes) ---
  {
    id:"r313", name:"Benzene Methylation (Methane to Toluene)", class_level:12,
    reactants:"C₆H₆,CH₄",
    products:"C₆H₅CH₃,H₂",
    equation:"C₆H₆ + CH₄ → C₆H₅CH₃ + H₂",
    conditions:"High temperature (600-700°C), metal catalyst (Pt, Mo, or ZnO-Al₂O₃), pressure",
    explanation:"Direct methylation of benzene with methane is a challenging reaction due to the high stability of methane. At high temperatures with metal catalysts, methane undergoes C–H activation to generate methyl radicals or surface-bound methyl species. These attack the benzene ring, displacing hydrogen to form toluene. This represents a direct C–H functionalization approach using abundant methane as the methyl source.",
    applications:"Emerging green chemistry route to toluene using methane (natural gas) instead of chloromethane. Reduces chloride waste and uses abundant feedstock. Research focus for sustainable chemical synthesis."
  },
  {
    id:"r314", name:"Benzene Hydrodealkylation (Reverse: Toluene to Benzene + Methane)", class_level:12,
    reactants:"C₆H₅CH₃,H₂",
    products:"C₆H₆,CH₄",
    equation:"C₆H₅CH₃ + H₂ → C₆H₆ + CH₄",
    conditions:"High temperature (500-600°C), hydrogen pressure (20-50 atm), Cr₂O₃ or MoO₃ catalyst",
    explanation:"Hydrodealkylation is the reverse of methylation. Toluene reacts with hydrogen at high temperature over a metal oxide catalyst. The methyl group is removed as methane, regenerating benzene. This is an important industrial process for converting toluene (often in excess) back to benzene when benzene demand is high. The reaction proceeds via radical or surface-mediated C–C bond cleavage.",
    applications:"Industrial process to produce benzene from toluene when benzene prices are high relative to toluene. Used in petroleum refineries and petrochemical plants for benzene-toluene-xylene (BTX) interconversion."
  },
  {
    id:"r315", name:"Benzene Steam Reforming with Methane", class_level:12,
    reactants:"C₆H₆,CH₄,H₂O",
    products:"CO,H₂,C₆H₅CH₃",
    equation:"C₆H₆ + CH₄ + H₂O → C₆H₅CH₃ + CO + 2H₂",
    conditions:"High temperature (800-900°C), Ni catalyst, steam",
    explanation:"In this combined reforming and methylation process, methane and steam react with benzene. The steam reforming of methane generates syngas (CO + H₂), while the methyl species from methane activate benzene to form toluene. This complex process represents an integrated approach to utilize both aromatic and aliphatic hydrocarbons from natural gas and petroleum feedstocks.",
    applications:"Advanced petrochemical processing for integrated BTX and syngas production. Potential route for utilizing natural gas and benzene together in chemical plants."
  },

  // --- Basic Benzene Electrophilic Substitution (NCERT Core) ---
  {
    id:"r316", name:"Benzene Nitration (Standard NCERT)", class_level:11,
    reactants:"C₆H₆,HNO₃",
    products:"C₆H₅NO₂,H₂O",
    equation:"C₆H₆ + HNO₃ → C₆H₅NO₂ + H₂O (conc. H₂SO₄)",
    conditions:"Conc. HNO₃ + Conc. H₂SO₄ (mixed acid), 50-60°C",
    explanation:"This is the standard nitration reaction of benzene as per NCERT curriculum. Concentrated sulfuric acid acts as a catalyst and dehydrating agent, generating the nitronium ion (NO₂⁺) electrophile from nitric acid. The NO₂⁺ attacks the benzene ring in an electrophilic aromatic substitution, forming nitrobenzene. The reaction is kept below 60°C to prevent dinitration.",
    applications:"Laboratory and industrial preparation of nitrobenzene. Nitrobenzene is reduced to aniline, which is the starting material for dyes, drugs, and explosives."
  },
  {
    id:"r317", name:"Benzene Sulfonation (Standard NCERT)", class_level:11,
    reactants:"C₆H₆,H₂SO₄",
    products:"C₆H₅SO₃H,H₂O",
    equation:"C₆H₆ + H₂SO₄ → C₆H₅SO₃H + H₂O",
    conditions:"Conc. H₂SO₄ or fuming H₂SO₄ (oleum), heat",
    explanation:"Benzene reacts with concentrated sulfuric acid to form benzenesulfonic acid. The electrophile is sulfur trioxide (SO₃) or protonated sulfuric acid. This is a reversible reaction - sulfonation can be reversed by heating with steam. The sulfonic acid group is electron-withdrawing and meta-directing in further substitutions.",
    applications:"Preparation of benzenesulfonic acid for detergents, dyes, and ion-exchange resins. The reversible nature is used in synthetic strategies."
  },
  {
    id:"r318", name:"Benzene Halogenation with Cl₂ (Standard NCERT)", class_level:11,
    reactants:"C₆H₆,Cl₂",
    products:"C₆H₅Cl,HCl",
    equation:"C₆H₆ + Cl₂ → C₆H₅Cl + HCl (FeCl₃ or AlCl₃)",
    conditions:"Anhydrous FeCl₃ or AlCl₃ catalyst, room temperature",
    explanation:"Chlorine reacts with benzene in the presence of a Lewis acid catalyst (FeCl₃ or AlCl₃) to form chlorobenzene. The catalyst polarizes the Cl–Cl bond, generating Cl⁺ electrophile. This is electrophilic aromatic substitution where one hydrogen is replaced by chlorine. The HCl byproduct is formed when the catalyst abstracts a proton from the sigma complex.",
    applications:"Industrial production of chlorobenzene, used to make phenol, DDT, and aniline. Important intermediate in organic synthesis."
  },
  {
    id:"r319", name:"Benzene Halogenation with Br₂ (Standard NCERT)", class_level:11,
    reactants:"C₆H₆,Br₂",
    products:"C₆H₅Br,HBr",
    equation:"C₆H₆ + Br₂ → C₆H₅Br + HBr (FeBr₃ or AlBr₃)",
    conditions:"Anhydrous FeBr₃, AlBr₃, or Lewis acid catalyst",
    explanation:"Bromine reacts with benzene in presence of Lewis acid catalyst to form bromobenzene. The mechanism is similar to chlorination - the catalyst generates Br⁺ electrophile which attacks the benzene ring. The reaction is slower than chlorination and requires a catalyst. Without catalyst, bromine does not react with benzene at room temperature.",
    applications:"Preparation of bromobenzene for Grignard reagents, pharmaceuticals, and dyes. Used as a solvent and intermediate in organic synthesis."
  },

  // --- Benzene Addition Reactions (NCERT Core) ---
  {
    id:"r320", name:"Benzene Hydrogenation to Cyclohexane (Standard NCERT)", class_level:11,
    reactants:"C₆H₆,H₂",
    products:"C₆H₁₂",
    equation:"C₆H₆ + 3H₂ → C₆H₁₂ (cyclohexane)",
    conditions:"Ni, Pt, or Pd catalyst, 200-300°C, high pressure",
    explanation:"Benzene undergoes catalytic hydrogenation to form cyclohexane. Three molecules of hydrogen add across the three double bonds. This is an addition reaction (not substitution) where the aromatic character is lost. High temperature and pressure are needed to overcome the resonance stabilization energy of benzene (~150 kJ/mol).",
    applications:"Industrial production of cyclohexane, which is oxidized to cyclohexanone and adipic acid for nylon-6,6 production. Major industrial process."
  },
  {
    id:"r321", name:"Benzene Addition with Chlorine (UV Light)", class_level:11,
    reactants:"C₆H₆,Cl₂",
    products:"C₆H₆Cl₆",
    equation:"C₆H₆ + 3Cl₂ → C₆H₆Cl₆ (Benzene hexachloride, BHC)",
    conditions:"UV light or sunlight, no catalyst",
    explanation:"In presence of UV light (not Lewis acid catalyst), chlorine adds to benzene rather than substituting. This is a free radical addition reaction across all three double bonds, forming benzene hexachloride (BHC). The gamma isomer is called lindane, an insecticide. This reaction demonstrates how conditions determine substitution vs addition.",
    applications:"Production of BHC (lindane) as an insecticide. Important example of photochemical addition to aromatic rings."
  },

  // --- Benzene Combustion (NCERT Core) ---
  {
    id:"r322", name:"Benzene Combustion (Standard NCERT)", class_level:11,
    reactants:"C₆H₆,O₂",
    products:"CO₂,H₂O",
    equation:"2C₆H₆ + 15O₂ → 12CO₂ + 6H₂O",
    conditions:"Ignition, excess oxygen",
    explanation:"Benzene undergoes complete combustion in excess oxygen to form carbon dioxide and water. Due to its high carbon content (C:H = 1:1), benzene burns with a sooty yellow flame. The reaction is highly exothermic. Incomplete combustion produces carbon (soot) and carbon monoxide.",
    applications:"Demonstrates the high carbon content of aromatic hydrocarbons. Important for understanding air pollution from aromatic fuel combustion."
  }
];

// ============================================================
// ELEMENTS available in the lab
// ============================================================
const ELEMENTS = [
  {symbol:"CH₄", name:"Methane", formula:"CH₄", type:"compound"},
  {symbol:"C₆H₆", name:"Benzene", formula:"C₆H₆", type:"compound"},
  {symbol:"C₆H₅OH", name:"Phenol", formula:"C₆H₅OH", type:"compound"},
  {symbol:"C₆H₅NH₂", name:"Aniline", formula:"C₆H₅NH₂", type:"compound"},
  {symbol:"CH₃Cl", name:"Methyl Chloride", formula:"CH₃Cl", type:"compound"},
  {symbol:"CH₃COCl", name:"Acetyl Chloride", formula:"CH₃COCl", type:"compound"},
  {symbol:"CHCl₃", name:"Chloroform", formula:"CHCl₃", type:"compound"},
  {symbol:"HCHO", name:"Formaldehyde", formula:"HCHO", type:"compound"},
  {symbol:"CH₃CHO", name:"Acetaldehyde", formula:"CH₃CHO", type:"compound"},
  {symbol:"CH₃COCH₃", name:"Acetone", formula:"CH₃COCH₃", type:"compound"},
  {symbol:"C₆H₅CHO", name:"Benzaldehyde", formula:"C₆H₅CHO", type:"compound"},
  {symbol:"C₆H₅CN", name:"Benzonitrile", formula:"C₆H₅CN", type:"compound"},
  {symbol:"O₂", name:"Oxygen", formula:"O₂", type:"nonmetal"},
  {symbol:"Cl₂", name:"Chlorine", formula:"Cl₂", type:"nonmetal"},
  {symbol:"Br₂", name:"Bromine", formula:"Br₂", type:"nonmetal"},
  {symbol:"I₂", name:"Iodine", formula:"I₂", type:"nonmetal"},
  {symbol:"Na", name:"Sodium", formula:"Na", type:"metal"},
  {symbol:"Zn", name:"Zinc", formula:"Zn", type:"metal"},
  {symbol:"Cu", name:"Copper", formula:"Cu", type:"metal"},
  {symbol:"Ag", name:"Silver", formula:"Ag", type:"metal"},
  {symbol:"HCl", name:"Hydrochloric Acid", formula:"HCl", type:"acid"},
  {symbol:"HNO₂", name:"Nitrous Acid", formula:"HNO₂", type:"acid"},
  {symbol:"H₂SO₄", name:"Sulfuric Acid", formula:"H₂SO₄", type:"acid"},
  {symbol:"NaOH", name:"Sodium Hydroxide", formula:"NaOH", type:"base"},
  {symbol:"KOH", name:"Potassium Hydroxide", formula:"KOH", type:"base"},
  {symbol:"NaNO₂", name:"Sodium Nitrite", formula:"NaNO₂", type:"compound"},
  {symbol:"AgNO₃", name:"Silver Nitrate", formula:"AgNO₃", type:"compound"},
  {symbol:"NaI", name:"Sodium Iodide", formula:"NaI", type:"compound"},
  {symbol:"AgF", name:"Silver Fluoride", formula:"AgF", type:"compound"},
  {symbol:"AlCl₃", name:"Aluminium Chloride", formula:"AlCl₃", type:"compound"},
  {symbol:"K₂Cr₂O₇", name:"Potassium Dichromate", formula:"K₂Cr₂O₇", type:"compound"},
  {symbol:"CO₂", name:"Carbon Dioxide", formula:"CO₂", type:"compound"},
  {symbol:"CO", name:"Carbon Monoxide", formula:"CO", type:"compound"},
  {symbol:"H₂", name:"Hydrogen", formula:"H₂", type:"nonmetal"},
  {symbol:"H₂O", name:"Water", formula:"H₂O", type:"compound"},
  
  // Benzene and Methane Reaction Elements
  {symbol:"C₆H₅CH₃", name:"Toluene", formula:"C₆H₅CH₃", type:"compound"},
  {symbol:"C₆H₁₂", name:"Cyclohexane", formula:"C₆H₁₂", type:"compound"},
  {symbol:"C₆H₅NO₂", name:"Nitrobenzene", formula:"C₆H₅NO₂", type:"compound"},
  {symbol:"C₆H₅SO₃H", name:"Benzenesulfonic Acid", formula:"C₆H₅SO₃H", type:"compound"},
  {symbol:"C₆H₅Cl", name:"Chlorobenzene", formula:"C₆H₅Cl", type:"compound"},
  {symbol:"C₆H₅Br", name:"Bromobenzene", formula:"C₆H₅Br", type:"compound"},
  {symbol:"C₆H₆Cl₆", name:"Benzene Hexachloride", formula:"C₆H₆Cl₆", type:"compound"},
  
  // Benzene Reaction Elements
  {symbol:"HNO₃", name:"Nitric Acid", formula:"HNO₃", type:"acid"},
  {symbol:"SO₃", name:"Sulfur Trioxide", formula:"SO₃", type:"compound"},
  {symbol:"O₃", name:"Ozone", formula:"O₃", type:"nonmetal"},
  {symbol:"AlBr₃", name:"Aluminium Bromide", formula:"AlBr₃", type:"compound"},
  {symbol:"FeCl₃", name:"Iron(III) Chloride", formula:"FeCl₃", type:"compound"},
  {symbol:"ICl", name:"Iodine Monochloride", formula:"ICl", type:"compound"},
  {symbol:"I₂", name:"Iodine", formula:"I₂", type:"nonmetal"},
  {symbol:"CuCl", name:"Cuprous Chloride", formula:"CuCl", type:"compound"},
  {symbol:"NaNO₂", name:"Sodium Nitrite", formula:"NaNO₂", type:"compound"},
  {symbol:"V₂O₅", name:"Vanadium Pentoxide", formula:"V₂O₅", type:"compound"},
  {symbol:"SmI₂", name:"Samarium Diiodide", formula:"SmI₂", type:"compound"},

  // Class 9-10 Elements and Compounds
  {symbol:"Ca", name:"Calcium", formula:"Ca", type:"metal"},
  {symbol:"Mg", name:"Magnesium", formula:"Mg", type:"metal"},
  {symbol:"Fe", name:"Iron", formula:"Fe", type:"metal"},
  {symbol:"Al", name:"Aluminium", formula:"Al", type:"metal"},
  {symbol:"Pb", name:"Lead", formula:"Pb", type:"metal"},
  {symbol:"S", name:"Sulfur", formula:"S", type:"nonmetal"},
  {symbol:"N₂", name:"Nitrogen", formula:"N₂", type:"nonmetal"},
  {symbol:"CaO", name:"Calcium Oxide", formula:"CaO", type:"compound"},
  {symbol:"Ca(OH)₂", name:"Calcium Hydroxide", formula:"Ca(OH)₂", type:"base"},
  {symbol:"CaCO₃", name:"Calcium Carbonate", formula:"CaCO₃", type:"compound"},
  {symbol:"CaSO₄", name:"Calcium Sulfate", formula:"CaSO₄", type:"compound"},
  {symbol:"MgO", name:"Magnesium Oxide", formula:"MgO", type:"compound"},
  {symbol:"CuSO₄", name:"Copper Sulfate", formula:"CuSO₄", type:"compound"},
  {symbol:"FeSO₄", name:"Ferrous Sulfate", formula:"FeSO₄", type:"compound"},
  {symbol:"Fe₂O₃", name:"Iron Oxide", formula:"Fe₂O₃", type:"compound"},
  {symbol:"Al₂O₃", name:"Aluminium Oxide", formula:"Al₂O₃", type:"compound"},
  {symbol:"PbO", name:"Lead Oxide", formula:"PbO", type:"compound"},
  {symbol:"Pb(NO₃)₂", name:"Lead Nitrate", formula:"Pb(NO₃)₂", type:"compound"},
  {symbol:"BaCl₂", name:"Barium Chloride", formula:"BaCl₂", type:"compound"},
  {symbol:"BaSO₄", name:"Barium Sulfate", formula:"BaSO₄", type:"compound"},
  {symbol:"Na₂SO₄", name:"Sodium Sulfate", formula:"Na₂SO₄", type:"compound"},
  {symbol:"AgCl", name:"Silver Chloride", formula:"AgCl", type:"compound"},
  {symbol:"KI", name:"Potassium Iodide", formula:"KI", type:"compound"},
  {symbol:"PbI₂", name:"Lead Iodide", formula:"PbI₂", type:"compound"},
  {symbol:"KNO₃", name:"Potassium Nitrate", formula:"KNO₃", type:"compound"},
  {symbol:"CH₃COOH", name:"Acetic Acid", formula:"CH₃COOH", type:"acid"},
  {symbol:"CH₃COONa", name:"Sodium Acetate", formula:"CH₃COONa", type:"compound"},
  {symbol:"NH₃", name:"Ammonia", formula:"NH₃", type:"compound"},
  {symbol:"H₂O₂", name:"Hydrogen Peroxide", formula:"H₂O₂", type:"compound"},
  {symbol:"SO₂", name:"Sulfur Dioxide", formula:"SO₂", type:"compound"},
  {symbol:"SO₃", name:"Sulfur Trioxide", formula:"SO₃", type:"compound"},
  {symbol:"CuO", name:"Copper Oxide", formula:"CuO", type:"compound"},
  {symbol:"ZnSO₄", name:"Zinc Sulfate", formula:"ZnSO₄", type:"compound"},
  {symbol:"NaCl", name:"Sodium Chloride", formula:"NaCl", type:"compound"},
  {symbol:"KCl", name:"Potassium Chloride", formula:"KCl", type:"compound"},
  {symbol:"H₂S", name:"Hydrogen Sulfide", formula:"H₂S", type:"compound"},
  {symbol:"NO₂", name:"Nitrogen Dioxide", formula:"NO₂", type:"compound"},
  {symbol:"Cu", name:"Copper", formula:"Cu", type:"metal"},
  {symbol:"MnO₂", name:"Manganese Dioxide", formula:"MnO₂", type:"compound"},
  
  // Additional elements for basic element reactions
  {symbol:"ZnCl₂", name:"Zinc Chloride", formula:"ZnCl₂", type:"compound"},
  {symbol:"FeCl₂", name:"Ferrous Chloride", formula:"FeCl₂", type:"compound"},
  {symbol:"MgCl₂", name:"Magnesium Chloride", formula:"MgCl₂", type:"compound"},
  {symbol:"AlCl₃", name:"Aluminium Chloride", formula:"AlCl₃", type:"compound"},
  {symbol:"MgSO₄", name:"Magnesium Sulfate", formula:"MgSO₄", type:"compound"},
  {symbol:"FeCl₃", name:"Ferric Chloride", formula:"FeCl₃", type:"compound"},
  {symbol:"Mg(OH)₂", name:"Magnesium Hydroxide", formula:"Mg(OH)₂", type:"base"},
  {symbol:"Fe₃O₄", name:"Magnetite", formula:"Fe₃O₄", type:"compound"},
  {symbol:"Na₂O", name:"Sodium Oxide", formula:"Na₂O", type:"compound"},
  {symbol:"K₂O", name:"Potassium Oxide", formula:"K₂O", type:"compound"},
  {symbol:"H₂CO₃", name:"Carbonic Acid", formula:"H₂CO₃", type:"acid"},
  {symbol:"H₂SO₃", name:"Sulfurous Acid", formula:"H₂SO₃", type:"acid"},
  {symbol:"Na₂CO₃", name:"Sodium Carbonate", formula:"Na₂CO₃", type:"compound"},
  
  // ============================================================
  // COMPLETE PERIODIC TABLE - ALL 118 ELEMENTS
  // ============================================================
  
  // Period 1
  {symbol:"H", name:"Hydrogen", formula:"H", type:"nonmetal"},
  {symbol:"He", name:"Helium", formula:"He", type:"noble"},
  
  // Period 2
  {symbol:"Li", name:"Lithium", formula:"Li", type:"metal"},
  {symbol:"Be", name:"Beryllium", formula:"Be", type:"metal"},
  {symbol:"B", name:"Boron", formula:"B", type:"metalloid"},
  {symbol:"C", name:"Carbon", formula:"C", type:"nonmetal"},
  {symbol:"N", name:"Nitrogen", formula:"N", type:"nonmetal"},
  {symbol:"O", name:"Oxygen", formula:"O", type:"nonmetal"},
  {symbol:"F", name:"Fluorine", formula:"F", type:"nonmetal"},
  {symbol:"Ne", name:"Neon", formula:"Ne", type:"noble"},
  
  // Period 3
  {symbol:"Na", name:"Sodium", formula:"Na", type:"metal"},
  {symbol:"Mg", name:"Magnesium", formula:"Mg", type:"metal"},
  {symbol:"Al", name:"Aluminium", formula:"Al", type:"metal"},
  {symbol:"Si", name:"Silicon", formula:"Si", type:"metalloid"},
  {symbol:"P", name:"Phosphorus", formula:"P", type:"nonmetal"},
  {symbol:"S", name:"Sulfur", formula:"S", type:"nonmetal"},
  {symbol:"Cl", name:"Chlorine", formula:"Cl", type:"nonmetal"},
  {symbol:"Ar", name:"Argon", formula:"Ar", type:"noble"},
  
  // Period 4
  {symbol:"K", name:"Potassium", formula:"K", type:"metal"},
  {symbol:"Ca", name:"Calcium", formula:"Ca", type:"metal"},
  {symbol:"Sc", name:"Scandium", formula:"Sc", type:"metal"},
  {symbol:"Ti", name:"Titanium", formula:"Ti", type:"metal"},
  {symbol:"V", name:"Vanadium", formula:"V", type:"metal"},
  {symbol:"Cr", name:"Chromium", formula:"Cr", type:"metal"},
  {symbol:"Mn", name:"Manganese", formula:"Mn", type:"metal"},
  {symbol:"Fe", name:"Iron", formula:"Fe", type:"metal"},
  {symbol:"Co", name:"Cobalt", formula:"Co", type:"metal"},
  {symbol:"Ni", name:"Nickel", formula:"Ni", type:"metal"},
  {symbol:"Cu", name:"Copper", formula:"Cu", type:"metal"},
  {symbol:"Zn", name:"Zinc", formula:"Zn", type:"metal"},
  {symbol:"Ga", name:"Gallium", formula:"Ga", type:"metal"},
  {symbol:"Ge", name:"Germanium", formula:"Ge", type:"metalloid"},
  {symbol:"As", name:"Arsenic", formula:"As", type:"metalloid"},
  {symbol:"Se", name:"Selenium", formula:"Se", type:"nonmetal"},
  {symbol:"Br", name:"Bromine", formula:"Br", type:"nonmetal"},
  {symbol:"Kr", name:"Krypton", formula:"Kr", type:"noble"},
  
  // Period 5
  {symbol:"Rb", name:"Rubidium", formula:"Rb", type:"metal"},
  {symbol:"Sr", name:"Strontium", formula:"Sr", type:"metal"},
  {symbol:"Y", name:"Yttrium", formula:"Y", type:"metal"},
  {symbol:"Zr", name:"Zirconium", formula:"Zr", type:"metal"},
  {symbol:"Nb", name:"Niobium", formula:"Nb", type:"metal"},
  {symbol:"Mo", name:"Molybdenum", formula:"Mo", type:"metal"},
  {symbol:"Tc", name:"Technetium", formula:"Tc", type:"metal"},
  {symbol:"Ru", name:"Ruthenium", formula:"Ru", type:"metal"},
  {symbol:"Rh", name:"Rhodium", formula:"Rh", type:"metal"},
  {symbol:"Pd", name:"Palladium", formula:"Pd", type:"metal"},
  {symbol:"Ag", name:"Silver", formula:"Ag", type:"metal"},
  {symbol:"Cd", name:"Cadmium", formula:"Cd", type:"metal"},
  {symbol:"In", name:"Indium", formula:"In", type:"metal"},
  {symbol:"Sn", name:"Tin", formula:"Sn", type:"metal"},
  {symbol:"Sb", name:"Antimony", formula:"Sb", type:"metalloid"},
  {symbol:"Te", name:"Tellurium", formula:"Te", type:"metalloid"},
  {symbol:"I", name:"Iodine", formula:"I", type:"nonmetal"},
  {symbol:"Xe", name:"Xenon", formula:"Xe", type:"noble"},
  
  // Period 6
  {symbol:"Cs", name:"Cesium", formula:"Cs", type:"metal"},
  {symbol:"Ba", name:"Barium", formula:"Ba", type:"metal"},
  {symbol:"La", name:"Lanthanum", formula:"La", type:"metal"},
  {symbol:"Ce", name:"Cerium", formula:"Ce", type:"metal"},
  {symbol:"Pr", name:"Praseodymium", formula:"Pr", type:"metal"},
  {symbol:"Nd", name:"Neodymium", formula:"Nd", type:"metal"},
  {symbol:"Pm", name:"Promethium", formula:"Pm", type:"metal"},
  {symbol:"Sm", name:"Samarium", formula:"Sm", type:"metal"},
  {symbol:"Eu", name:"Europium", formula:"Eu", type:"metal"},
  {symbol:"Gd", name:"Gadolinium", formula:"Gd", type:"metal"},
  {symbol:"Tb", name:"Terbium", formula:"Tb", type:"metal"},
  {symbol:"Dy", name:"Dysprosium", formula:"Dy", type:"metal"},
  {symbol:"Ho", name:"Holmium", formula:"Ho", type:"metal"},
  {symbol:"Er", name:"Erbium", formula:"Er", type:"metal"},
  {symbol:"Tm", name:"Thulium", formula:"Tm", type:"metal"},
  {symbol:"Yb", name:"Ytterbium", formula:"Yb", type:"metal"},
  {symbol:"Lu", name:"Lutetium", formula:"Lu", type:"metal"},
  {symbol:"Hf", name:"Hafnium", formula:"Hf", type:"metal"},
  {symbol:"Ta", name:"Tantalum", formula:"Ta", type:"metal"},
  {symbol:"W", name:"Tungsten", formula:"W", type:"metal"},
  {symbol:"Re", name:"Rhenium", formula:"Re", type:"metal"},
  {symbol:"Os", name:"Osmium", formula:"Os", type:"metal"},
  {symbol:"Ir", name:"Iridium", formula:"Ir", type:"metal"},
  {symbol:"Pt", name:"Platinum", formula:"Pt", type:"metal"},
  {symbol:"Au", name:"Gold", formula:"Au", type:"metal"},
  {symbol:"Hg", name:"Mercury", formula:"Hg", type:"metal"},
  {symbol:"Tl", name:"Thallium", formula:"Tl", type:"metal"},
  {symbol:"Pb", name:"Lead", formula:"Pb", type:"metal"},
  {symbol:"Bi", name:"Bismuth", formula:"Bi", type:"metal"},
  {symbol:"Po", name:"Polonium", formula:"Po", type:"metalloid"},
  {symbol:"At", name:"Astatine", formula:"At", type:"metalloid"},
  {symbol:"Rn", name:"Radon", formula:"Rn", type:"noble"},
  
  // Period 7
  {symbol:"Fr", name:"Francium", formula:"Fr", type:"metal"},
  {symbol:"Ra", name:"Radium", formula:"Ra", type:"metal"},
  {symbol:"Ac", name:"Actinium", formula:"Ac", type:"metal"},
  {symbol:"Th", name:"Thorium", formula:"Th", type:"metal"},
  {symbol:"Pa", name:"Protactinium", formula:"Pa", type:"metal"},
  {symbol:"U", name:"Uranium", formula:"U", type:"metal"},
  {symbol:"Np", name:"Neptunium", formula:"Np", type:"metal"},
  {symbol:"Pu", name:"Plutonium", formula:"Pu", type:"metal"},
  {symbol:"Am", name:"Americium", formula:"Am", type:"metal"},
  {symbol:"Cm", name:"Curium", formula:"Cm", type:"metal"},
  {symbol:"Bk", name:"Berkelium", formula:"Bk", type:"metal"},
  {symbol:"Cf", name:"Californium", formula:"Cf", type:"metal"},
  {symbol:"Es", name:"Einsteinium", formula:"Es", type:"metal"},
  {symbol:"Fm", name:"Fermium", formula:"Fm", type:"metal"},
  {symbol:"Md", name:"Mendelevium", formula:"Md", type:"metal"},
  {symbol:"No", name:"Nobelium", formula:"No", type:"metal"},
  {symbol:"Lr", name:"Lawrencium", formula:"Lr", type:"metal"},
  {symbol:"Rf", name:"Rutherfordium", formula:"Rf", type:"metal"},
  {symbol:"Db", name:"Dubnium", formula:"Db", type:"metal"},
  {symbol:"Sg", name:"Seaborgium", formula:"Sg", type:"metal"},
  {symbol:"Bh", name:"Bohrium", formula:"Bh", type:"metal"},
  {symbol:"Hs", name:"Hassium", formula:"Hs", type:"metal"},
  {symbol:"Mt", name:"Meitnerium", formula:"Mt", type:"metal"},
  {symbol:"Ds", name:"Darmstadtium", formula:"Ds", type:"metal"},
  {symbol:"Rg", name:"Roentgenium", formula:"Rg", type:"metal"},
  {symbol:"Cn", name:"Copernicium", formula:"Cn", type:"metal"},
  {symbol:"Nh", name:"Nihonium", formula:"Nh", type:"metal"},
  {symbol:"Fl", name:"Flerovium", formula:"Fl", type:"metal"},
  {symbol:"Mc", name:"Moscovium", formula:"Mc", type:"metal"},
  {symbol:"Lv", name:"Livermorium", formula:"Lv", type:"metal"},
  {symbol:"Ts", name:"Tennessine", formula:"Ts", type:"metal"},
  {symbol:"Og", name:"Oganesson", formula:"Og", type:"noble"},
  
  // ============================================================
  // CLASS 11-12 ADDITIONAL COMPOUNDS
  // ============================================================
  
  // Class 11 Inorganic Compounds
  {symbol:"Na₂O₂", name:"Sodium Peroxide", formula:"Na₂O₂", type:"compound"},
  {symbol:"CaC₂", name:"Calcium Carbide", formula:"CaC₂", type:"compound"},
  {symbol:"C₂H₂", name:"Acetylene", formula:"C₂H₂", type:"compound"},
  {symbol:"CaSO₄·½H₂O", name:"Plaster of Paris", formula:"CaSO₄·½H₂O", type:"compound"},
  {symbol:"CaSO₄·2H₂O", name:"Gypsum", formula:"CaSO₄·2H₂O", type:"compound"},
  {symbol:"BF₃", name:"Boron Trifluoride", formula:"BF₃", type:"compound"},
  {symbol:"H₃BO₃", name:"Boric Acid", formula:"H₃BO₃", type:"acid"},
  {symbol:"NaAlO₂", name:"Sodium Meta-aluminate", formula:"NaAlO₂", type:"compound"},
  {symbol:"NaClO", name:"Sodium Hypochlorite", formula:"NaClO", type:"compound"},
  {symbol:"NaClO₃", name:"Sodium Chlorate", formula:"NaClO₃", type:"compound"},
  {symbol:"XeF₂", name:"Xenon Difluoride", formula:"XeF₂", type:"compound"},
  {symbol:"XeF₄", name:"Xenon Tetrafluoride", formula:"XeF₄", type:"compound"},
  {symbol:"XeF₆", name:"Xenon Hexafluoride", formula:"XeF₆", type:"compound"},
  {symbol:"XeO₃", name:"Xenon Trioxide", formula:"XeO₃", type:"compound"},
  {symbol:"FeCr₂O₄", name:"Chromite Ore", formula:"FeCr₂O₄", type:"compound"},
  {symbol:"Na₂CrO₄", name:"Sodium Chromate", formula:"Na₂CrO₄", type:"compound"},
  {symbol:"K₂Cr₂O₇", name:"Potassium Dichromate", formula:"K₂Cr₂O₇", type:"compound"},
  {symbol:"KMnO₄", name:"Potassium Permanganate", formula:"KMnO₄", type:"compound"},
  {symbol:"H₂C₂O₄", name:"Oxalic Acid", formula:"H₂C₂O₄", type:"acid"},
  {symbol:"K₂MnO₄", name:"Potassium Manganate", formula:"K₂MnO₄", type:"compound"},
  {symbol:"Cu(NO₃)₂", name:"Copper Nitrate", formula:"Cu(NO₃)₂", type:"compound"},
  {symbol:"Na₂S₂O₃", name:"Sodium Thiosulfate", formula:"Na₂S₂O₃", type:"compound"},
  {symbol:"[Cu(NH₃)₄]SO₄", name:"Tetraamminecopper(II) Sulfate", formula:"[Cu(NH₃)₄]SO₄", type:"compound"},
  {symbol:"K₄[Fe(CN)₆]", name:"Potassium Ferrocyanide", formula:"K₄[Fe(CN)₆]", type:"compound"},
  {symbol:"KSCN", name:"Potassium Thiocyanate", formula:"KSCN", type:"compound"},
  {symbol:"[Fe(SCN)]Cl₂", name:"Ferric Thiocyanate Complex", formula:"[Fe(SCN)]Cl₂", type:"compound"},
  {symbol:"CrO₂Cl₂", name:"Chromyl Chloride", formula:"CrO₂Cl₂", type:"compound"},
  
  // Class 12 Organic Compounds
  {symbol:"NH₂NH₂", name:"Hydrazine", formula:"NH₂NH₂", type:"compound"},
  {symbol:"CH₃CN", name:"Acetonitrile", formula:"CH₃CN", type:"compound"},
  {symbol:"CH₃CHBrCOOH", name:"2-Bromopropanoic Acid", formula:"CH₃CHBrCOOH", type:"acid"},
  {symbol:"ClCH₂COOH", name:"Chloroacetic Acid", formula:"ClCH₂COOH", type:"acid"},
  {symbol:"o-HOC₆H₄CHO", name:"Salicylaldehyde", formula:"o-HOC₆H₄CHO", type:"compound"},
  {symbol:"C₂H₆", name:"Ethane", formula:"C₂H₆", type:"compound"},
  {symbol:"C₂H₅OCH₃", name:"Ethyl Methyl Ether", formula:"C₂H₅OCH₃", type:"compound"},
  {symbol:"p-HOC₆H₄N=NC₆H₅", name:"p-Hydroxyazobenzene", formula:"p-HOC₆H₄N=NC₆H₅", type:"compound"},
  {symbol:"C₆H₄(CO)₂NH", name:"Phthalimide", formula:"C₆H₄(CO)₂NH", type:"compound"},
  {symbol:"CH₃CONH₂", name:"Acetamide", formula:"CH₃CONH₂", type:"compound"},
  {symbol:"CH₃NC", name:"Methyl Isocyanide", formula:"CH₃NC", type:"compound"},
  {symbol:"C₆H₅NCS", name:"Phenyl Isothiocyanate", formula:"C₆H₅NCS", type:"compound"},
  {symbol:"C₆H₅N₂⁺Cl⁻", name:"Benzenediazonium Chloride", formula:"C₆H₅N₂⁺Cl⁻", type:"compound"},
  {symbol:"C₁₂H₂₂O₁₁", name:"Sucrose", formula:"C₁₂H₂₂O₁₁", type:"compound"},
  {symbol:"C₆H₁₂O₆", name:"Glucose", formula:"C₆H₁₂O₆", type:"compound"},
  {symbol:"C₆H₃(OH)CH₂", name:"Bakelite Unit", formula:"C₆H₃(OH)CH₂", type:"compound"},
  {symbol:"CF₂=CF₂", name:"Tetrafluoroethylene", formula:"CF₂=CF₂", type:"compound"},
  {symbol:"[-CF₂-CF₂-]n", name:"Teflon", formula:"[-CF₂-CF₂-]n", type:"compound"},
  {symbol:"CH₃COCH₂COOC₂H₅", name:"Ethyl Acetoacetate", formula:"CH₃COCH₂COOC₂H₅", type:"compound"},
  {symbol:"CH₂(COOC₂H₅)₂", name:"Diethyl Malonate", formula:"CH₂(COOC₂H₅)₂", type:"compound"},
  {symbol:"Pinacol", name:"Pinacol", formula:"(CH₃)₂C(OH)C(OH)(CH₃)₂", type:"compound"},
  {symbol:"Pinacolone", name:"Pinacolone", formula:"(CH₃)₃CCOCH₃", type:"compound"},
  {symbol:"Ph₃P=CH₂", name:"Methylenetriphenylphosphorane", formula:"Ph₃P=CH₂", type:"compound"},
  {symbol:"Ph₃P=O", name:"Triphenylphosphine Oxide", formula:"Ph₃P=O", type:"compound"},
  {symbol:"Cyclohexene", name:"Cyclohexene", formula:"C₆H₁₀", type:"compound"},
  {symbol:"RMgX", name:"Grignard Reagent", formula:"RMgX", type:"compound"},
  {symbol:"RCH(OMgX)R'", name:"Grignard Adduct", formula:"RCH(OMgX)R'", type:"compound"},
  
  // Additional Reagents
  {symbol:"PCl₅", name:"Phosphorus Pentachloride", formula:"PCl₅", type:"compound"},
  {symbol:"POCl₃", name:"Phosphoryl Chloride", formula:"POCl₃", type:"compound"},
  {symbol:"SnCl₂", name:"Stannous Chloride", formula:"SnCl₂", type:"compound"},
  {symbol:"SnCl₄", name:"Stannic Chloride", formula:"SnCl₄", type:"compound"},
  {symbol:"HgCl₂", name:"Mercuric Chloride", formula:"HgCl₂", type:"compound"},
  {symbol:"HgS", name:"Mercuric Sulfide", formula:"HgS", type:"compound"},
  {symbol:"V₂O₅", name:"Vanadium Pentoxide", formula:"V₂O₅", type:"compound"},
  {symbol:"CS₂", name:"Carbon Disulfide", formula:"CS₂", type:"compound"},
  {symbol:"Al(OCHMe₂)₃", name:"Aluminum Isopropoxide", formula:"Al(OCHMe₂)₃", type:"compound"},
  {symbol:"B₂H₆", name:"Diborane", formula:"B₂H₆", type:"compound"},
  {symbol:"O₃", name:"Ozone", formula:"O₃", type:"compound"},
  {symbol:"H₂S", name:"Hydrogen Sulfide", formula:"H₂S", type:"compound"},
  {symbol:"NO₃⁻", name:"Nitrate Ion", formula:"NO₃⁻", type:"compound"},
  {symbol:"α-naphthol", name:"Alpha-Naphthol", formula:"C₁₀H₇OH", type:"compound"},
  {symbol:"Nylon-6,6", name:"Nylon-6,6", formula:"[-OC(CH₂)₄CONH(CH₂)₆NH-]n", type:"compound"},
  {symbol:"HOOC(CH₂)₄COOH", name:"Adipic Acid", formula:"HOOC(CH₂)₄COOH", type:"acid"},
  {symbol:"H₂N(CH₂)₆NH₂", name:"Hexamethylenediamine", formula:"H₂N(CH₂)₆NH₂", type:"compound"},
  
  // ============================================================
  // CLASS 9-10 ADDITIONAL COMPOUNDS
  // ============================================================
  
  // Class 9 Compounds
  {symbol:"NH₄Cl", name:"Ammonium Chloride", formula:"NH₄Cl", type:"compound"},
  {symbol:"CuSO₄·5H₂O", name:"Copper Sulfate Pentahydrate", formula:"CuSO₄·5H₂O", type:"compound"},
  {symbol:"²³⁸U", name:"Uranium-238", formula:"²³⁸U", type:"metal"},
  {symbol:"²³⁴Th", name:"Thorium-234", formula:"²³⁴Th", type:"metal"},
  {symbol:"¹⁴C", name:"Carbon-14", formula:"¹⁴C", type:"nonmetal"},
  {symbol:"C₂H₅OH", name:"Ethanol", formula:"C₂H₅OH", type:"compound"},
  {symbol:"CH₃COOH", name:"Ethanoic Acid", formula:"CH₃COOH", type:"acid"},
  {symbol:"CH₃COOC₂H₅", name:"Ethyl Ethanoate", formula:"CH₃COOC₂H₅", type:"compound"},
  {symbol:"CaOCl₂", name:"Bleaching Powder", formula:"CaOCl₂", type:"compound"},
  {symbol:"Na₂CO₃·10H₂O", name:"Washing Soda", formula:"Na₂CO₃·10H₂O", type:"compound"},
  {symbol:"CO", name:"Carbon Monoxide", formula:"CO", type:"compound"},
  
  // Class 10 Compounds
  {symbol:"KClO₃", name:"Potassium Chlorate", formula:"KClO₃", type:"compound"},
  {symbol:"AgBr", name:"Silver Bromide", formula:"AgBr", type:"compound"},
  {symbol:"NaHCO₃", name:"Sodium Bicarbonate", formula:"NaHCO₃", type:"compound"},
  {symbol:"NH₄Cl", name:"Ammonium Chloride", formula:"NH₄Cl", type:"compound"},
  {symbol:"Fe₂O₃", name:"Iron(III) Oxide", formula:"Fe₂O₃", type:"compound"},
  {symbol:"Fe₃O₄", name:"Iron(II,III) Oxide", formula:"Fe₃O₄", type:"compound"},
  {symbol:"CaSiO₃", name:"Calcium Silicate", formula:"CaSiO₃", type:"compound"},
  {symbol:"C₂H₆", name:"Ethane", formula:"C₂H₆", type:"compound"},
  {symbol:"C₂H₄", name:"Ethene", formula:"C₂H₄", type:"compound"},
  {symbol:"C₂H₂", name:"Ethyne", formula:"C₂H₂", type:"compound"},
  {symbol:"C₂H₄Br₂", name:"1,2-Dibromoethane", formula:"C₂H₄Br₂", type:"compound"},
  {symbol:"C₂H₅ONa", name:"Sodium Ethoxide", formula:"C₂H₅ONa", type:"compound"},
  {symbol:"CH₃COONa", name:"Sodium Ethanoate", formula:"CH₃COONa", type:"compound"},
  {symbol:"C₂H₅Cl", name:"Chloroethane", formula:"C₂H₅Cl", type:"compound"},
  {symbol:"HCOOH", name:"Methanoic Acid", formula:"HCOOH", type:"acid"},
  {symbol:"C₂H₅OC₂H₅", name:"Diethyl Ether", formula:"C₂H₅OC₂H₅", type:"compound"},
  {symbol:"[Ag(NH₃)₂]⁺", name:"Diamminesilver(I) Ion", formula:"[Ag(NH₃)₂]⁺", type:"compound"},
  
  // ============================================================
  // 100 BASIC REACTIONS - ADDITIONAL COMPOUNDS
  // ============================================================
  
  // Physical Chemistry & States of Matter
  {symbol:"H₂O(s)", name:"Ice", formula:"H₂O", type:"compound"},
  {symbol:"H₂O(l)", name:"Liquid Water", formula:"H₂O", type:"compound"},
  {symbol:"H₂O(g)", name:"Water Vapor", formula:"H₂O", type:"compound"},
  {symbol:"C₁₂H₂₂O₁₁", name:"Sugar", formula:"C₁₂H₂₂O₁₁", type:"compound"},
  {symbol:"Na⁺", name:"Sodium Ion", formula:"Na⁺", type:"compound"},
  {symbol:"Cl⁻", name:"Chloride Ion", formula:"Cl⁻", type:"compound"},
  {symbol:"Wax", name:"Wax", formula:"CₙH₂ₙ₊₂", type:"compound"},
  {symbol:"CO₂(s)", name:"Dry Ice", formula:"CO₂", type:"compound"},
  
  // Atomic Structure & Isotopes
  {symbol:"²³⁸U", name:"Uranium-238", formula:"²³⁸U", type:"metal"},
  {symbol:"²³⁴Th", name:"Thorium-234", formula:"²³⁴Th", type:"metal"},
  {symbol:"¹⁴C", name:"Carbon-14", formula:"¹⁴C", type:"nonmetal"},
  {symbol:"⁴He", name:"Alpha Particle", formula:"⁴He", type:"noble"},
  
  // Ionic Compounds
  {symbol:"LiF", name:"Lithium Fluoride", formula:"LiF", type:"compound"},
  {symbol:"NaF", name:"Sodium Fluoride", formula:"NaF", type:"compound"},
  {symbol:"KF", name:"Potassium Fluoride", formula:"KF", type:"compound"},
  {symbol:"CaF₂", name:"Calcium Fluoride", formula:"CaF₂", type:"compound"},
  {symbol:"MgCl₂", name:"Magnesium Chloride", formula:"MgCl₂", type:"compound"},
  {symbol:"Al₂O₃", name:"Aluminum Oxide", formula:"Al₂O₃", type:"compound"},
  {symbol:"CaO", name:"Calcium Oxide", formula:"CaO", type:"compound"},
  {symbol:"Na₂O", name:"Sodium Oxide", formula:"Na₂O", type:"compound"},
  {symbol:"ZnO", name:"Zinc Oxide", formula:"ZnO", type:"compound"},
  {symbol:"PbO", name:"Lead(II) Oxide", formula:"PbO", type:"compound"},
  {symbol:"CuO", name:"Copper(II) Oxide", formula:"CuO", type:"compound"},
  {symbol:"Fe₂O₃", name:"Iron(III) Oxide", formula:"Fe₂O₃", type:"compound"},
  {symbol:"Fe₃O₄", name:"Iron(II,III) Oxide", formula:"Fe₃O₄", type:"compound"},
  {symbol:"ZnS", name:"Zinc Sulfide", formula:"ZnS", type:"compound"},
  {symbol:"PbS", name:"Lead(II) Sulfide", formula:"PbS", type:"compound"},
  {symbol:"Ag₂S", name:"Silver Sulfide", formula:"Ag₂S", type:"compound"},
  {symbol:"Al₂S₃", name:"Aluminum Sulfide", formula:"Al₂S₃", type:"compound"},
  {symbol:"Ca₃N₂", name:"Calcium Nitride", formula:"Ca₃N₂", type:"compound"},
  {symbol:"Na₂S", name:"Sodium Sulfide", formula:"Na₂S", type:"compound"},
  {symbol:"CaCO₃", name:"Calcium Carbonate", formula:"CaCO₃", type:"compound"},
  {symbol:"CaSO₄", name:"Calcium Sulfate", formula:"CaSO₄", type:"compound"},
  {symbol:"Na₂SO₄", name:"Sodium Sulfate", formula:"Na₂SO₄", type:"compound"},
  {symbol:"K₂SO₄", name:"Potassium Sulfate", formula:"K₂SO₄", type:"compound"},
  {symbol:"Al₂(SO₄)₃", name:"Aluminum Sulfate", formula:"Al₂(SO₄)₃", type:"compound"},
  {symbol:"ZnSO₄", name:"Zinc Sulfate", formula:"ZnSO₄", type:"compound"},
  {symbol:"FeSO₄", name:"Iron(II) Sulfate", formula:"FeSO₄", type:"compound"},
  {symbol:"FeCl₂", name:"Iron(II) Chloride", formula:"FeCl₂", type:"compound"},
  {symbol:"FeCl₃", name:"Iron(III) Chloride", formula:"FeCl₃", type:"compound"},
  {symbol:"MgCl₂", name:"Magnesium Chloride", formula:"MgCl₂", type:"compound"},
  {symbol:"AlCl₃", name:"Aluminum Chloride", formula:"AlCl₃", type:"compound"},
  {symbol:"ZnCl₂", name:"Zinc Chloride", formula:"ZnCl₂", type:"compound"},
  {symbol:"PbCl₂", name:"Lead(II) Chloride", formula:"PbCl₂", type:"compound"},
  {symbol:"AgCl", name:"Silver Chloride", formula:"AgCl", type:"compound"},
  {symbol:"NaClO", name:"Sodium Hypochlorite", formula:"NaClO", type:"compound"},
  {symbol:"CaOCl₂", name:"Bleaching Powder", formula:"CaOCl₂", type:"compound"},
  {symbol:"Na₂ZnO₂", name:"Sodium Zincate", formula:"Na₂ZnO₂", type:"compound"},
  {symbol:"Na₂PbO₂", name:"Sodium Plumbite", formula:"Na₂PbO₂", type:"compound"},
  {symbol:"NaAlO₂", name:"Sodium Aluminate", formula:"NaAlO₂", type:"compound"},
  {symbol:"Ca(OH)₂", name:"Calcium Hydroxide", formula:"Ca(OH)₂", type:"base"},
  {symbol:"NaOH", name:"Sodium Hydroxide", formula:"NaOH", type:"base"},
  {symbol:"KOH", name:"Potassium Hydroxide", formula:"KOH", type:"base"},
  {symbol:"Mg(OH)₂", name:"Magnesium Hydroxide", formula:"Mg(OH)₂", type:"base"},
  {symbol:"Sr(OH)₂", name:"Strontium Hydroxide", formula:"Sr(OH)₂", type:"base"},
  {symbol:"Ba(OH)₂", name:"Barium Hydroxide", formula:"Ba(OH)₂", type:"base"},
  {symbol:"Be(OH)₂", name:"Beryllium Hydroxide", formula:"Be(OH)₂", type:"base"},
  {symbol:"LiOH", name:"Lithium Hydroxide", formula:"LiOH", type:"base"},
  {symbol:"H₂SO₃", name:"Sulfurous Acid", formula:"H₂SO₃", type:"acid"},
  {symbol:"HNO₃", name:"Nitric Acid", formula:"HNO₃", type:"acid"},
  {symbol:"H₂SO₄", name:"Sulfuric Acid", formula:"H₂SO₄", type:"acid"},
  {symbol:"HCl", name:"Hydrochloric Acid", formula:"HCl", type:"acid"},
  {symbol:"H₂CO₃", name:"Carbonic Acid", formula:"H₂CO₃", type:"acid"},
  {symbol:"CH₃COOH", name:"Acetic Acid", formula:"CH₃COOH", type:"acid"},
  {symbol:"HCOOH", name:"Formic Acid", formula:"HCOOH", type:"acid"},
  {symbol:"H₃PO₄", name:"Phosphoric Acid", formula:"H₃PO₄", type:"acid"},
  
  // Organic Compounds
  {symbol:"CH₄", name:"Methane", formula:"CH₄", type:"compound"},
  {symbol:"C₂H₆", name:"Ethane", formula:"C₂H₆", type:"compound"},
  {symbol:"C₃H₈", name:"Propane", formula:"C₃H₈", type:"compound"},
  {symbol:"C₄H₁₀", name:"Butane", formula:"C₄H₁₀", type:"compound"},
  {symbol:"C₂H₄", name:"Ethene", formula:"C₂H₄", type:"compound"},
  {symbol:"C₂H₂", name:"Ethyne", formula:"C₂H₂", type:"compound"},
  {symbol:"CH₃OH", name:"Methanol", formula:"CH₃OH", type:"compound"},
  {symbol:"C₂H₅OH", name:"Ethanol", formula:"C₂H₅OH", type:"compound"},
  {symbol:"C₂H₅Cl", name:"Chloroethane", formula:"C₂H₅Cl", type:"compound"},
  {symbol:"C₂H₄Cl₂", name:"1,2-Dichloroethane", formula:"C₂H₄Cl₂", type:"compound"},
  {symbol:"C₂H₅Br", name:"Bromoethane", formula:"C₂H₅Br", type:"compound"},
  {symbol:"C₂H₅I", name:"Iodoethane", formula:"C₂H₅I", type:"compound"},
  {symbol:"C₂H₅ONa", name:"Sodium Ethoxide", formula:"C₂H₅ONa", type:"compound"},
  {symbol:"C₂H₅OC₂H₅", name:"Diethyl Ether", formula:"C₂H₅OC₂H₅", type:"compound"},
  {symbol:"CH₃CHO", name:"Acetaldehyde", formula:"CH₃CHO", type:"compound"},
  {symbol:"HCHO", name:"Formaldehyde", formula:"HCHO", type:"compound"},
  {symbol:"CH₃COCH₃", name:"Acetone", formula:"CH₃COCH₃", type:"compound"},
  {symbol:"CH₃COOC₂H₅", name:"Ethyl Acetate", formula:"CH₃COOC₂H₅", type:"compound"},
  {symbol:"CH₃COONa", name:"Sodium Acetate", formula:"CH₃COONa", type:"compound"},
  {symbol:"C₆H₆", name:"Benzene", formula:"C₆H₆", type:"compound"},
  {symbol:"C₆H₁₂O₆", name:"Glucose", formula:"C₆H₁₂O₆", type:"compound"},
  {symbol:"C₁₂H₂₂O₁₁", name:"Sucrose", formula:"C₁₂H₂₂O₁₁", type:"compound"},
  
  // Complex Salts
  {symbol:"KAl(SO₄)₂", name:"Potash Alum", formula:"KAl(SO₄)₂·12H₂O", type:"compound"},
  {symbol:"FeSO₄·(NH₄)₂SO₄", name:"Mohr's Salt", formula:"FeSO₄·(NH₄)₂SO₄·6H₂O", type:"compound"},
  {symbol:"HAuCl₄", name:"Chloroauric Acid", formula:"HAuCl₄", type:"acid"},
  {symbol:"H₂PtCl₆", name:"Chloroplatinic Acid", formula:"H₂PtCl₆", type:"acid"},
  {symbol:"Na₂C₂O₄", name:"Sodium Oxalate", formula:"Na₂C₂O₄", type:"compound"},
  {symbol:"Ca₃(PO₄)₂", name:"Calcium Phosphate", formula:"Ca₃(PO₄)₂", type:"compound"},
  {symbol:"CaSiO₃", name:"Calcium Silicate", formula:"CaSiO₃", type:"compound"},
  {symbol:"SnO₂", name:"Tin(IV) Oxide", formula:"SnO₂", type:"compound"},
  {symbol:"Hg(NO₃)₂", name:"Mercury(II) Nitrate", formula:"Hg(NO₃)₂", type:"compound"},
  {symbol:"AgNO₃", name:"Silver Nitrate", formula:"AgNO₃", type:"compound"},
  {symbol:"Pb(NO₃)₂", name:"Lead(II) Nitrate", formula:"Pb(NO₃)₂", type:"compound"},
  {symbol:"BaCl₂", name:"Barium Chloride", formula:"BaCl₂", type:"compound"},
  {symbol:"Na₃PO₄", name:"Sodium Phosphate", formula:"Na₃PO₄", type:"compound"},
  {symbol:"FeS", name:"Iron(II) Sulfide", formula:"FeS", type:"compound"},
  {symbol:"Na₂SO₃", name:"Sodium Sulfite", formula:"Na₂SO₃", type:"compound"},
  {symbol:"NaHCO₃", name:"Sodium Bicarbonate", formula:"NaHCO₃", type:"compound"},
  {symbol:"KClO₃", name:"Potassium Chlorate", formula:"KClO₃", type:"compound"},
  {symbol:"AgBr", name:"Silver Bromide", formula:"AgBr", type:"compound"},
  {symbol:"NH₄Cl", name:"Ammonium Chloride", formula:"NH₄Cl", type:"compound"},
  {symbol:"(NH₄)₂SO₄", name:"Ammonium Sulfate", formula:"(NH₄)₂SO₄", type:"compound"},
  {symbol:"Na₂CO₃", name:"Sodium Carbonate", formula:"Na₂CO₃", type:"compound"},
  {symbol:"Na₂CO₃·10H₂O", name:"Washing Soda", formula:"Na₂CO₃·10H₂O", type:"compound"},
  {symbol:"CuSO₄·5H₂O", name:"Copper Sulfate Pentahydrate", formula:"CuSO₄·5H₂O", type:"compound"},
  {symbol:"Fe₂O₃·nH₂O", name:"Hydrated Iron(III) Oxide", formula:"Fe₂O₃·nH₂O", type:"compound"},
  
  // Gases
  {symbol:"CO", name:"Carbon Monoxide", formula:"CO", type:"compound"},
  {symbol:"NO", name:"Nitric Oxide", formula:"NO", type:"compound"},
  {symbol:"SO₂", name:"Sulfur Dioxide", formula:"SO₂", type:"compound"},
  {symbol:"H₂S", name:"Hydrogen Sulfide", formula:"H₂S", type:"compound"},
  {symbol:"NH₃", name:"Ammonia", formula:"NH₃", type:"compound"},
  {symbol:"H₂", name:"Hydrogen", formula:"H₂", type:"compound"},
  {symbol:"O₂", name:"Oxygen", formula:"O₂", type:"nonmetal"},
  {symbol:"N₂", name:"Nitrogen", formula:"N₂", type:"nonmetal"},
  {symbol:"Cl₂", name:"Chlorine", formula:"Cl₂", type:"nonmetal"},
  {symbol:"F₂", name:"Fluorine", formula:"F₂", type:"nonmetal"},
  {symbol:"Br₂", name:"Bromine", formula:"Br₂", type:"nonmetal"},
  {symbol:"I₂", name:"Iodine", formula:"I₂", type:"nonmetal"},
  
  // Elements
  {symbol:"Fe", name:"Iron", formula:"Fe", type:"metal"},
  {symbol:"Cu", name:"Copper", formula:"Cu", type:"metal"},
  {symbol:"Zn", name:"Zinc", formula:"Zn", type:"metal"},
  {symbol:"Ag", name:"Silver", formula:"Ag", type:"metal"},
  {symbol:"Au", name:"Gold", formula:"Au", type:"metal"},
  {symbol:"Pt", name:"Platinum", formula:"Pt", type:"metal"},
  {symbol:"Hg", name:"Mercury", formula:"Hg", type:"metal"},
  {symbol:"Pb", name:"Lead", formula:"Pb", type:"metal"},
  {symbol:"Sn", name:"Tin", formula:"Sn", type:"metal"},
  {symbol:"Al", name:"Aluminum", formula:"Al", type:"metal"},
  {symbol:"Mg", name:"Magnesium", formula:"Mg", type:"metal"},
  {symbol:"Ca", name:"Calcium", formula:"Ca", type:"metal"},
  {symbol:"Na", name:"Sodium", formula:"Na", type:"metal"},
  {symbol:"K", name:"Potassium", formula:"K", type:"metal"},
  {symbol:"Li", name:"Lithium", formula:"Li", type:"metal"},
  {symbol:"Sr", name:"Strontium", formula:"Sr", type:"metal"},
  {symbol:"Ba", name:"Barium", formula:"Ba", type:"metal"},
  {symbol:"Be", name:"Beryllium", formula:"Be", type:"metal"},
  {symbol:"C", name:"Carbon", formula:"C", type:"nonmetal"},
  {symbol:"S", name:"Sulfur", formula:"S", type:"nonmetal"},
  {symbol:"P", name:"Phosphorus", formula:"P", type:"nonmetal"},
  {symbol:"Si", name:"Silicon", formula:"Si", type:"metalloid"},
  {symbol:"B", name:"Boron", formula:"B", type:"metalloid"},
];

// ============================================================
// Reaction matching logic
// ============================================================
function matchReaction(droppedFormulas) {
  if (!droppedFormulas.length) return {match:null, partial:false};

  const selCount = {};
  droppedFormulas.forEach(f => { selCount[f] = (selCount[f]||0)+1; });
  const selTotal = droppedFormulas.length;

  let bestPartial = null;
  let bestScore = 0;

  for (const rxn of REACTIONS) {
    const rxnReactants = rxn.reactants.split(',').map(s=>s.trim());
    const rxnCount = {};
    rxnReactants.forEach(r => { rxnCount[r] = (rxnCount[r]||0)+1; });
    const rxnTotal = rxnReactants.length;

    // Check if every dropped element is valid in this reaction and count matches
    let valid = true;
    let matchScore = 0;
    for (const [sym, cnt] of Object.entries(selCount)) {
      if (!rxnCount[sym] || cnt > rxnCount[sym]) { valid = false; break; }
      matchScore += cnt;
    }
    if (!valid) continue;

    if (selTotal === rxnTotal) {
      // Exact match — all reactants present in correct quantities
      return {match: rxn, partial: false};
    }
    // Partial — dropped elements are a valid subset
    const score = matchScore / rxnTotal;
    if (score > bestScore) { bestScore = score; bestPartial = rxn; }
  }

  return {match: null, partial: bestPartial !== null, partialRxn: bestPartial};
}

// ============================================================
// ENHANCED NO-REACTION REASONING SYSTEM
// ============================================================

function classifyChemical(formula) {
  const cats = [];
  const f = formula || '';
  
  // Acids
  if (['HCl','H₂SO₄','HNO₃','HBr','HI','HClO₄'].includes(f)) {
    cats.push('acid','strong acid','inorganic');
  } else if (['CH₃COOH','H₂CO₃','H₂SO₃','H₃PO₄','H₂S','HF'].includes(f)) {
    cats.push('acid','weak acid','inorganic');
  } else if (f.includes('COOH') || f.includes('CO₂H')) {
    cats.push('acid','organic acid','organic');
  }
  
  // Bases
  if (['NaOH','KOH','Ca(OH)₂','Ba(OH)₂','LiOH'].includes(f)) {
    cats.push('base','strong base','inorganic');
  } else if (['NH₃','NH₄OH'].includes(f)) {
    cats.push('base','weak base','inorganic');
  } else if (f.includes('NH₂') && f !== 'C₆H₅NH₂') {
    cats.push('base','organic base','organic');
  }
  
  // Special organic amines
  if (f === 'C₆H₅NH₂') cats.push('amine','aromatic amine','base','weak base','organic');
  if (f === 'CH₃NH₂') cats.push('amine','aliphatic amine','base','organic');
  
  // Metals
  if (['Na','K','Ca','Mg','Al','Zn','Fe','Cu','Ag','Pb','Hg','Sn','Li'].includes(f)) {
    cats.push('metal');
    if (['Na','K','Ca','Li'].includes(f)) cats.push('alkali metal','reactive metal');
    if (['Mg','Al','Zn','Fe','Sn','Pb'].includes(f)) cats.push('transition/post-transition metal');
    if (['Cu','Ag','Au','Pt','Hg'].includes(f)) cats.push('noble/less reactive metal');
  }
  
  // Nonmetals
  if (['O₂','Cl₂','Br₂','I₂','S','N₂','H₂','C','P'].includes(f)) {
    cats.push('nonmetal');
  }
  
  // Noble gases
  if (['He','Ne','Ar','Kr','Xe','Rn'].includes(f)) cats.push('noble gas','inert');
  
  // Organic compounds (contain carbon and hydrogen)
  if (/C/.test(f) && /H/.test(f)) {
    cats.push('organic');
    if (f === 'CH₄' || /^C\d*H/.test(f) && !/O|N|Cl|Br|I|S/.test(f)) cats.push('hydrocarbon','alkane');
    if (/C₆H₆/.test(f)) cats.push('aromatic hydrocarbon','benzene derivative');
    if (/OH/.test(f) && !/COOH/.test(f)) cats.push('alcohol','alcohol/phenol');
    if (/CHO/.test(f) || /CH=O/.test(f) || f === 'HCHO') cats.push('aldehyde');
    if (/COCH/.test(f) || /COC/.test(f) || f === 'CH₃COCH₃') cats.push('ketone');
    if (/COOH/.test(f) || /CO₂H/.test(f)) cats.push('carboxylic acid');
    if (/COCl/.test(f)) cats.push('acid chloride');
    if (/NH₂/.test(f)) cats.push('amine');
    if (/NO₂/.test(f)) cats.push('nitro compound');
    if (/SO₃H/.test(f)) cats.push('sulfonic acid');
    if (/CN/.test(f)) cats.push('nitrile');
    if (/Cl/.test(f) || /Br/.test(f) || /I/.test(f)) cats.push('halide','alkyl halide');
  }
  
  // Salts
  if ((/[A-Z][a-z]?/.test(f) && !cats.includes('acid') && !cats.includes('base') && !cats.includes('metal') && !cats.includes('nonmetal') && !cats.includes('organic')) || 
      (/Na|K|Ca|Mg|Al|Zn|Fe|Cu|Ag|Pb|Ba|Li|NH₄/.test(f) && /Cl|Br|I|SO₄|NO₃|CO₃|PO₄|CH₃COO|OH|O/.test(f))) {
    cats.push('salt');
  }
  
  // Oxidizing agents
  if (['KMnO₄','K₂Cr₂O₇','HNO₃','H₂O₂','Cl₂','O₂','O₃','MnO₂'].includes(f)) {
    cats.push('oxidizing agent');
  }
  
  // Reducing agents
  if (['H₂','Na','K','Zn','Fe','Sn','SO₂','H₂S','CO','C'].includes(f)) {
    cats.push('reducing agent');
  }
  
  // Catalysts
  if (['AlCl₃','FeCl₃','AlBr₃','V₂O₅','Pd','Pt','Ni','CuCl','CuCl₂','ZnCl₂','Conc. H₂SO₄'].includes(f)) {
    cats.push('catalyst','Lewis acid');
  }
  
  // Water
  if (f === 'H₂O') cats.push('water','universal solvent');
  
  return [...new Set(cats)];
}

function findClosestReaction(droppedFormulas) {
  const droppedSet = new Set(droppedFormulas);
  let bestMatch = null;
  let bestScore = -Infinity;
  
  for (const rxn of REACTIONS) {
    const rxnReactants = rxn.reactants.split(',').map(s=>s.trim());
    const rxnSet = new Set(rxnReactants);
    
    let matchCount = 0;
    for (const el of droppedSet) {
      if (rxnSet.has(el)) matchCount++;
    }
    
    const extraInDropped = droppedFormulas.filter(el => !rxnSet.has(el)).length;
    const missingInRxn = rxnReactants.filter(r => !droppedSet.has(r)).length;
    
    const score = (matchCount * 3) - (extraInDropped * 2) - (missingInRxn * 1);
    
    if (score > bestScore) {
      bestScore = score;
      bestMatch = { rxn, score, matchCount, extraInDropped, missingInRxn, rxnReactants };
    }
  }
  
  return bestMatch;
}

function generateChemistryReason(droppedFormulas) {
  const dropped = [...new Set(droppedFormulas)];
  const allCats = dropped.map(classifyChemical);
  
  // Helper to check if any dropped has category
  const has = cat => allCats.some(c => c.includes(cat));
  const allHave = cat => allCats.every(c => c.includes(cat));
  const count = cat => allCats.filter(c => c.includes(cat)).length;
  
  const closest = findClosestReaction(droppedFormulas);
  
  // CASE 1: Noble gases are inert
  if (has('noble gas')) {
    const noble = dropped.find(d => classifyChemical(d).includes('noble gas'));
    return {
      title: 'Inert Gas Behavior',
      reason: `${noble} is a noble gas with a complete octet electron configuration. Noble gases are chemically inert under normal conditions and do not form compounds readily.`
    };
  }
  
  // CASE 2: Two strong acids together
  if (count('strong acid') >= 2) {
    return {
      title: 'Acid-Acid Incompatibility',
      reason: 'Both chemicals are acids. Acids cannot react with each other because they both donate H⁺ ions. Acids typically react with bases (neutralization), reactive metals, metal carbonates, or metal oxides.'
    };
  }
  
  // CASE 3: Two strong bases together
  if (count('strong base') >= 2) {
    return {
      title: 'Base-Base Incompatibility',
      reason: 'Both chemicals are bases. Bases cannot react with each other because they both accept H⁺ ions or donate OH⁻ ions. Bases typically react with acids (neutralization), ammonium salts, or certain non-metal oxides.'
    };
  }
  
  // CASE 4: Two salts together - check for precipitation or DD
  if (count('salt') >= 2 && dropped.length === 2) {
    return {
      title: 'Salt-Salt Reaction Conditions',
      reason: 'Two salts generally do not react unless a double displacement reaction produces an insoluble precipitate, a gas, or water. Check solubility rules: a reaction only occurs if one product is insoluble (precipitate) or unstable (gas).'
    };
  }
  
  // CASE 5: Acid + salt without reactivity
  if (has('acid') && has('salt') && dropped.length === 2) {
    return {
      title: 'Acid + Salt Limitations',
      reason: 'An acid reacts with a salt only if the reaction produces a weaker acid, a gas, or an insoluble salt. According to the reactivity series and solubility rules, stronger acids can displace weaker acids from their salts.'
    };
  }
  
  // CASE 6: Metal + nonmetal but wrong conditions or inert metal
  if (has('metal') && has('nonmetal') && !has('acid') && !has('base')) {
    const metals = dropped.filter(d => classifyChemical(d).includes('metal'));
    const nonmetals = dropped.filter(d => classifyChemical(d).includes('nonmetal'));
    const nobleMetals = metals.filter(m => classifyChemical(m).includes('noble/less reactive metal'));
    if (nobleMetals.length > 0) {
      return {
        title: 'Metal Reactivity',
        reason: `${nobleMetals.join(', ')} is a less reactive metal. It does not readily react with nonmetals at room temperature. More reactive metals (Na, K, Ca, Mg, Al, Zn) react directly with nonmetals like O₂, Cl₂, or S.`
      };
    }
    return {
      title: 'Reaction Conditions Required',
      reason: `While ${metals.join(', ')} can react with ${nonmetals.join(', ')}, these reactions typically require specific conditions such as heat, ignition, or moisture. For example, Na reacts vigorously with O₂ only when heated or cut fresh.`
    };
  }
  
  // CASE 7: Metal + metal
  if (allHave('metal')) {
    return {
      title: 'Metal-Metal Incompatibility',
      reason: 'Metals do not react with each other directly. A more reactive metal can displace a less reactive metal from its salt solution (displacement reaction), but two pure metals mixed together remain unchanged.'
    };
  }
  
  // CASE 8: Organic compounds without proper reagents
  if (has('organic') && dropped.length >= 2) {
    const organic = dropped.filter(d => classifyChemical(d).includes('organic'));
    const inorganic = dropped.filter(d => !classifyChemical(d).includes('organic'));
    
    if (inorganic.length === 0) {
      return {
        title: 'Organic-Organic Reactions',
        reason: `Organic compounds like ${organic.join(', ')} generally require specific catalysts, solvents, or temperature conditions to react. Simply mixing them at room temperature without a catalyst (e.g., Lewis acid, base, or heat) rarely causes a reaction.`
      };
    }
    
    // Check for missing catalyst
    const hasCatalyst = dropped.some(d => classifyChemical(d).includes('catalyst'));
    if (!hasCatalyst && organic.some(d => classifyChemical(d).includes('benzene derivative'))) {
      return {
        title: 'Missing Catalyst',
        reason: 'Benzene and its derivatives are very stable due to resonance. Electrophilic substitution reactions on benzene require strong Lewis acid catalysts like AlCl₃ or FeCl₃. Without a catalyst, the aromatic ring does not react.'
      };
    }
  }
  
  // CASE 9: Strong acid + strong base = neutralization but not in DB
  if (has('strong acid') && has('strong base')) {
    return {
      title: 'Neutralization Reaction',
      reason: 'A strong acid and a strong base will undergo neutralization to form salt and water. If this specific pair is not in our reaction database, it is still a valid reaction in real chemistry: H⁺ from the acid combines with OH⁻ from the base to form H₂O.'
    };
  }
  
  // CASE 10: Strong acid + weak base
  if (has('strong acid') && has('weak base') && !has('strong base')) {
    return {
      title: 'Acid-Base Neutralization',
      reason: 'A strong acid will protonate the weak base, forming a salt. The reaction goes to completion because the strong acid completely ionizes. For example, HCl + NH₃ → NH₄Cl.'
    };
  }
  
  // CASE 11: Weak acid + strong base
  if (has('weak acid') && has('strong base')) {
    return {
      title: 'Acid-Base Neutralization',
      reason: 'A strong base will deprotonate the weak acid, forming a salt and water. The equilibrium lies to the right because OH⁻ is a much stronger base than the conjugate base of the weak acid.'
    };
  }
  
  // CASE 12: Metal + acid but noble metal
  if (has('metal') && has('acid')) {
    const metals = dropped.filter(d => classifyChemical(d).includes('metal'));
    const nobleMetals = metals.filter(m => classifyChemical(m).includes('noble/less reactive metal'));
    if (nobleMetals.length > 0) {
      return {
        title: 'Metal Below Hydrogen',
        reason: `${nobleMetals.join(', ')} is below hydrogen in the reactivity series. It cannot displace H⁺ from dilute acids. Only metals above hydrogen (Zn, Fe, Mg, Al, Na, K, Ca) react with dilute HCl or H₂SO₄ to liberate H₂ gas.`
      };
    }
    const diluteAcids = dropped.filter(d => ['HCl','H₂SO₄'].includes(d));
    if (diluteAcids.length > 0) {
      return {
        title: 'Possible Displacement Reaction',
        reason: 'This metal-acid combination should react if the metal is above hydrogen in the reactivity series. The metal displaces hydrogen from the acid, forming a salt and H₂ gas. If no reaction occurs, the acid may be too dilute or the metal surface may be passivated.'
      };
    }
  }
  
  // CASE 13: Metal + water but wrong metal
  if (has('metal') && has('water')) {
    const metals = dropped.filter(d => classifyChemical(d).includes('metal'));
    const unreactive = metals.filter(m => classifyChemical(m).includes('noble/less reactive metal') || ['Fe','Sn','Pb'].includes(m));
    if (unreactive.length > 0) {
      return {
        title: 'Metal-Water Reactivity',
        reason: `${unreactive.join(', ')} does not react with cold water. Only highly reactive metals (Na, K, Ca) react vigorously with cold water. Mg reacts with steam, and Fe reacts only with steam at high temperatures.`
      };
    }
  }
  
  // CASE 14: Oxidizing + reducing agent but wrong conditions
  if (has('oxidizing agent') && has('reducing agent')) {
    return {
      title: 'Redox Reaction Conditions',
      reason: 'This oxidizing agent and reducing agent pair can potentially undergo a redox reaction. However, redox reactions often require specific conditions: proper temperature, aqueous medium, acidic or alkaline pH, and sometimes a catalyst. Ensure all required conditions are met.'
    };
  }
  
  // CASE 15: Closest database match with actionable feedback
  if (closest && closest.score >= 2 && closest.matchCount >= 1) {
    const rxn = closest.rxn;
    const missing = closest.rxnReactants.filter(r => !dropped.includes(r));
    const extra = dropped.filter(d => !closest.rxnReactants.includes(d));
    
    if (missing.length > 0 && extra.length === 0) {
      return {
        title: `Missing Reagents for ${rxn.name}`,
        reason: `You are missing required reagents: ${missing.join(', ')}. ${rxn.name} requires all these reactants together. ${rxn.conditions ? 'Conditions: ' + rxn.conditions + '.' : ''}`
      };
    }
    
    if (extra.length > 0 && closest.matchCount >= 1) {
      return {
        title: `Incompatible with ${rxn.name}`,
        reason: `${extra.join(', ')} does not belong in this reaction. ${rxn.name} only requires: ${closest.rxnReactants.join(', ')}. Adding incorrect reagents can cause side reactions or prevent the desired product from forming.`
      };
    }
    
    if (rxn.not_occur) {
      return {
        title: rxn.name,
        reason: rxn.not_occur
      };
    }
  }
  
  // CASE 16: Completely unrelated combinations
  if (dropped.length >= 2) {
    const types = allCats.map((c,i) => {
      if (c.includes('organic')) return 'organic';
      if (c.includes('metal')) return 'metal';
      if (c.includes('acid')) return 'acid';
      if (c.includes('base')) return 'base';
      if (c.includes('salt')) return 'salt';
      return 'other';
    });
    
    return {
      title: 'No Known Reaction',
      reason: `The combination of ${dropped.join(' + ')} does not correspond to any known reaction in our chemistry database. ${types.includes('organic') && types.includes('inorganic') ? 'Organic and inorganic compounds often require specific catalysts or conditions to react.' : 'These chemical classes do not typically react under normal conditions. Try checking the Reactions page for valid reactant combinations.'}`
    };
  }
  
  return null;
}

function findNoReactionReason(droppedFormulas) {
  return generateChemistryReason(droppedFormulas);
}

// ============================================================
// Helper functions
// ============================================================
const REACTION_CATEGORY_MAP = {
  "Organic_Named_Reactions": ["r1-r20"],
  "Substitution_Reactions": ["r1-r3","r7-r9","r11","r13","r14","r20","r22","r73-r76"],
  "Addition_Reactions": ["r10","r15","r16","r69","r120-r150"],
  "Elimination_Reactions": ["r10","r15","r130-r160"],
  "Rearrangement_Reactions": ["r9","r18","r140-r170"],
  "Oxidation_Reactions": ["r6","r12","r21","r28-r30","r40-r42","r54","r55","r71","r72","r73","r80","r150-r200"],
  "Reduction_Reactions": ["r4","r5","r19","r31-r33","r170-r210"],
  "Condensation_Reactions": ["r10","r15","r16","r200-r220"],
  "Disproportionation_Reactions": ["r17","r74","r75","r78","r210-r225"],
  "Hydrolysis_Reactions": ["r65","r67","r69","r78","r220-r240"],
  "Polymerization_Reactions": ["r69","r240-r255"],
  "Combustion_Reactions": ["r21","r40","r41","r42","r255-r270"],
  "Free_Radical_Reactions": ["r21","r22","r260-r275"],
  "Combination_Reactions": ["r23","r24","r25","r26","r63","r266-r280"],
  "Decomposition_Reactions": ["r27","r28","r29","r30","r280-r295"],
  "Displacement_Reactions": ["r31","r32","r33","r43","r44","r45","r46","r286-r300"],
  "Double_Displacement_Reactions": ["r34","r35","r36","r296-r305"],
  "Neutralization_Reactions": ["r37","r38","r39","r305-r310"],
  "Metal_Acid_Reactions": ["r43-r49","r54","r55","r310-r315"],
  "Metal_Water_Reactions": ["r50","r51","r52","r53","r315-r320"],
  "Oxide_Reactions": ["r56","r57","r58","r59","r60","r61","r62","r200-r230"],
  "Industrial_Processes": ["r26","r64","r70","r71","r72","r320-r322"],
  "s_Block_Reactions": ["r50-r66"],
  "p_Block_Reactions": ["r67-r76"],
  "d_Block_Reactions": ["r79-r100"],
  "Noble_Gas_Reactions": ["r77","r78"]
};

const EXPANDED_CATEGORIES = {};
for (const [cat, ranges] of Object.entries(REACTION_CATEGORY_MAP)) {
    let ids = new Set();
    ranges.forEach(item => {
        if (item.includes('-')) {
            const parts = item.split('-');
            const start = parseInt(parts[0].replace('r', ''));
            const end = parseInt(parts[1].replace('r', ''));
            for(let i = start; i <= end; i++) {
                ids.add('r' + i);
            }
        } else {
            ids.add(item);
        }
    });
    EXPANDED_CATEGORIES[cat] = ids;
}

function getReactionCategories(id) {
    if (!id) return [];
    let cats = [];
    for (const [cat, ids] of Object.entries(EXPANDED_CATEGORIES)) {
        if (ids.has(id)) {
            cats.push(cat);
        }
    }
    return cats;
}

function getReactionType(rOrName) {
  let id = null;
  let nameStr = "";
  if (typeof rOrName === 'object' && rOrName !== null) {
      id = rOrName.id;
      nameStr = (rOrName.name || '').toLowerCase();
  } else if (typeof rOrName === 'string') {
      nameStr = rOrName.toLowerCase();
  }

  if (id) {
      let cats = getReactionCategories(id);
      if (cats.length > 0) return cats[0].replace(/_/g, ' ');
  }

  // Fallback to original string matching logic if no ID matches
  const n = nameStr;
  if (n.includes('combination')||n.includes('formation of')&&(n.includes('oxide')||n.includes('hydroxide')||n.includes('ammonia')||n.includes('water')||n.includes('molecule'))) return 'Combination_Reactions';
  if (n.includes('decomposition')||n.includes('thermal decomposition')||n.includes('photochemical')||n.includes('electrolysis')) return 'Decomposition_Reactions';
  if (n.includes('displacement')||(n.includes('zinc with')||n.includes('iron with')||n.includes('aluminium with')||n.includes('magnesium with')||n.includes('sodium with')||n.includes('displacement of'))) return 'Displacement_Reactions';
  if (n.includes('double displacement')||n.includes('precipitation')||n.includes('barium chloride')||n.includes('silver nitrate')||n.includes('lead nitrate')||n.includes('precipitation of')) return 'Double_Displacement_Reactions';
  if (n.includes('neutralization')||n.includes('hcl with naoh')||n.includes('acid with')||n.includes('acetic acid')||n.includes('sulfuric acid with')||n.includes('base with')) return 'Neutralization_Reactions';
  if (n.includes('oxidation')||n.includes('etard')||n.includes('iodoform')||n.includes('ozonolysis')||n.includes('bleaching action')) return 'Oxidation_Reactions';
  if (n.includes('reduction')||n.includes('clemmensen')||n.includes('rosenmund')||n.includes('mendius')||n.includes('wolff-kishner')||n.includes('meerwein')) return 'Reduction_Reactions';
  if (n.includes('addition')||n.includes('hydroboration')) return 'Addition_Reactions';
  if (n.includes('elimination')||n.includes('dehydration')||n.includes('dehydrohalogenation')) return 'Elimination_Reactions';
  if (n.includes('substitution')||n.includes('finkelstein')||n.includes('balz')||n.includes('swarts')||n.includes('halogenation')) return 'Substitution_Reactions';
  if (n.includes('rearrangement')||n.includes('fries')||n.includes('hofmann')||n.includes('beckmann')||n.includes('pinacol')) return 'Rearrangement_Reactions';
  if (n.includes('condensation')||n.includes('aldol')||n.includes('benzoin')||n.includes('perkin')||n.includes('cannizzaro')) return 'Condensation_Reactions';
  if (n.includes('hydrolysis')||n.includes('saponification')) return 'Hydrolysis_Reactions';
  if (n.includes('polymerization')) return 'Polymerization_Reactions';
  if (n.includes('combustion')) return 'Combustion_Reactions';
  
  return 'Other';
}

function hasReactionBlockingInfo(rxn) {
  return Boolean(rxn.not_occur) || /no reaction/i.test(rxn.equation || '') || /passive layer/i.test(rxn.products || '');
}

function getMechanismLabel(rxn) {
  if (rxn.mechanism) return rxn.mechanism;

  const name = (rxn.name || '').toLowerCase();
  const type = getReactionType(rxn.name);

  if (name.includes('friedel-crafts')) return 'Electrophilic aromatic substitution';
  if (name.includes('sandmeyer')) return 'Diazonium substitution';
  if (name.includes('wurtz')) return 'Sodium-mediated coupling';
  if (name.includes('rosenmund')) return 'Selective catalytic hydrogenation';
  if (name.includes('clemmensen')) return 'Acidic deoxygenation reduction';
  if (name.includes('etard')) return 'Controlled side-chain oxidation';
  if (name.includes('reimer-tiemann')) return 'Carbene electrophilic substitution';
  if (name.includes("kolbe")) return 'Electrophilic carboxylation';
  if (name.includes('fries')) return 'Lewis acid rearrangement';
  if (name.includes('aldol')) return 'Enolate nucleophilic addition';
  if (name.includes('diazotization')) return 'Nitrosation to diazonium formation';
  if (name.includes('iodoform')) return 'Haloform oxidation-cleavage';
  if (name.includes('finkelstein')) return 'SN2 nucleophilic substitution';
  if (name.includes('swarts')) return 'Halogen-exchange substitution';
  if (name.includes('perkin')) return 'Base-promoted condensation';
  if (name.includes('benzoin')) return 'Cyanide-catalysed umpolung condensation';
  if (name.includes('passivation')) return 'Passivation by oxide-film formation';

  const typeMechanisms = {
    Combination: 'Direct bond formation',
    Decomposition: 'Bond cleavage decomposition',
    Displacement: 'Single-displacement redox',
    'Double Displacement': 'Ion-exchange metathesis',
    Neutralization: 'Acid-base proton transfer',
    Combustion: 'Rapid oxidation',
    Oxidation: 'Oxidation',
    Reduction: 'Reduction',
    Addition: 'Addition across a multiple bond',
    Elimination: 'Elimination',
    Condensation: 'Condensation',
    Rearrangement: 'Rearrangement',
    Hydrolysis: 'Hydrolytic bond cleavage',
    Esterification: 'Nucleophilic acyl substitution',
    Coupling: 'Coupling bond formation',
    Diazotization: 'Diazonium-ion formation',
    'Carbon-Carbon Bond Formation': 'Carbon-carbon bond formation'
  };

  return typeMechanisms[type] || 'Reaction pathway analysis';
}

function getBlockingReason(rxn) {
  return rxn.not_occur || rxn.explanation || 'Required chemical conditions for product formation are not satisfied.';
}

function getBadgeClass(type) {
  return 'badge badge-' + type.toLowerCase().replace(/[^a-z]/g,'');
}

function svgArrow(){return `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>`;}

// ============================================================
// Navigation — defined in index.html inline script to allow
// access to renderReactionsPage, renderLabPage, etc.
// This file exposes only the page-rendering helpers:
// renderReactionsPage(), renderLabPage(), renderDetailPage(),
// initTitrationPage(). They are called by navigate() in index.html.
// ============================================================

// ============================================================
// REACTIONS PAGE
// ============================================================
// Search tab state
let currentSearchTab = 'name'; // 'name', 'reactant', 'product'

const CHEMICAL_CHAR_NORMALIZATION = {
  '₀':'0','₁':'1','₂':'2','₃':'3','₄':'4','₅':'5','₆':'6','₇':'7','₈':'8','₉':'9',
  '⁰':'0','¹':'1','²':'2','³':'3','⁴':'4','⁵':'5','⁶':'6','⁷':'7','⁸':'8','⁹':'9',
  '₊':'+','⁺':'+','₋':'-','⁻':'-','₌':'=','⁼':'=',
  '₍':'(','₎':')','⁽':'(','⁾':')',
  '→':'->','⇌':'<->','−':'-','–':'-','·':'.'
};

function normalizeChemicalText(text) {
  return (text || '')
    .split('')
    .map(ch => CHEMICAL_CHAR_NORMALIZATION[ch] || ch)
    .join('')
    .toLowerCase()
    .replace(/\s+/g, '');
}

function buildChemicalSearchRegex(term) {
  if (!term) return null;
  const variants = {
    '0':'[0₀⁰]','1':'[1₁¹]','2':'[2₂²]','3':'[3₃³]','4':'[4₄⁴]','5':'[5₅⁵]',
    '6':'[6₆⁶]','7':'[7₇⁷]','8':'[8₈⁸]','9':'[9₉⁹]',
    '+':'[+₊⁺]','-':'[-−–₋⁻]','=':'[=₌⁼]','(':'[(₍⁽]',')':'[)₎⁾]','.' :'[.·]'
  };

  const pattern = term
    .split('')
    .map(ch => variants[ch] || ch.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))
    .join('\\s*');

  return new RegExp('(' + pattern + ')', 'gi');
}

function setSearchTab(tab) {
  currentSearchTab = tab;
  // Update tab UI
  document.querySelectorAll('.search-tab').forEach(t => t.classList.remove('active'));
  document.getElementById('tab-' + tab).classList.add('active');
  // Update placeholder
  const input = document.getElementById('search-input');
  if (tab === 'name') input.placeholder = '🔍  Search by reaction name...';
  else if (tab === 'reactant') input.placeholder = '🧪  Enter a reactant formula (e.g. C6H6, NaOH, HCl)...';
  else if (tab === 'product') input.placeholder = '✨  Enter a product formula (e.g. C6H5Br, CO2, H2O)...';
  input.value = '';
  input.focus();
  filterReactions();
}

let currentFilterType = 'all';

function setFilterType(type, btn) {
  currentFilterType = type;
  
  // Update UI active state
  document.querySelectorAll('.type-btn').forEach(b => {
    b.classList.remove('bg-primary', 'text-on-primary', 'border-primary', 'shadow-[0_0_15px_rgba(6,182,212,0.3)]');
    b.classList.add('bg-surface-container', 'border-white/5', 'text-slate-400');
  });
  btn.classList.remove('bg-surface-container', 'border-white/5', 'text-slate-400');
  btn.classList.add('bg-primary', 'text-on-primary', 'border-primary', 'shadow-[0_0_15px_rgba(6,182,212,0.3)]');
  
  filterReactions();
}

function filterReactions() {
  const q = document.getElementById('search-input').value.trim();
  const cls = document.getElementById('class-filter').value;
  const type = currentFilterType;

  const normQ = normalizeChemicalText(q);
  const qLower = q.toLowerCase();

  const filtered = REACTIONS.filter(r => {
    let matchQ = false;
    if (!q) {
      matchQ = true;
    } else {
      let rTokens = (r.reactants || '').split(',').map(normalizeChemicalText);
      let pTokens = (r.products || '').split(',').map(normalizeChemicalText);
      
      // Exact token matching prevents "Na" from incorrectly matching "NaOH"
      let isExactChem = rTokens.includes(normQ) || pTokens.includes(normQ);
      
      // Substring text matching for names and explanations
      let isTextMatch = false;
      if (q.length > 2) {
         isTextMatch = r.name.toLowerCase().includes(qLower) || 
                       (r.explanation && r.explanation.toLowerCase().includes(qLower));
      } else {
         // For very short queries, enforce word boundaries so "Na" doesn't match "ElimiNAtion"
         isTextMatch = new RegExp('\\b' + qLower + '\\b').test(r.name.toLowerCase());
      }
      
      matchQ = isExactChem || isTextMatch;
    }

    const matchCls = cls === 'all' || String(r.class_level) === cls;
    
    let matchType = false;
    if (type === 'all') {
      matchType = true;
    } else {
      let cats = getReactionCategories(r.id);
      matchType = cats.includes(type);
    }
    
    return matchQ && matchCls && matchType;
  });

  renderReactionCards(filtered, q);
}

function renderReactionsPage() {
  filterReactions();
}

function getRiskLevel(r) {
  const name = r.name.toLowerCase();
  const cond = (r.conditions || '').toLowerCase();
  
  if (name.includes('combustion') || name.includes('thermite') || name.includes('explosive') || cond.includes('ignit') || cond.includes('conc. hcl') || cond.includes('conc. h2so4')) {
    return { level: 'High Risk', bars: 3, color: 'bg-secondary', icon: 'warning' };
  }
  if (name.includes('decomposition') || name.includes('oxidation') || name.includes('reduction') || cond.includes('heat')) {
    return { level: 'Medium Risk', bars: 2, color: 'bg-secondary', icon: 'science' };
  }
  return { level: 'Low Risk', bars: 1, color: 'bg-secondary', icon: 'check_circle' };
}



function renderReactionCards(list, query) {
  const grid = document.getElementById('reactions-grid');
  if (!list.length) {
    grid.innerHTML = `<div class="col-span-full py-20 text-center border border-dashed border-white/10 rounded-2xl bg-surface-container-low">
      <h3 class="text-3xl font-black uppercase mb-2 text-on-surface">No matching protocols</h3>
      <p class="font-bold text-sm text-slate-500 uppercase tracking-wide">Adjust your search parameters or check laboratory clearance.</p>
    </div>`;
    return;
  }

  if (currentFilterType !== 'all') {
    grid.innerHTML = list.map((r, index) => renderSingleCard(r, index)).join('');
    return;
  }

  const groups = {};
  Object.keys(REACTION_CATEGORY_MAP).forEach(cat => groups[cat] = []);
  groups['Other'] = [];

  list.forEach(r => {
    const types = getReactionCategories(r.id);
    if (types.length === 0) {
      groups['Other'].push(r);
    } else {
      // Put in the primary group to avoid duplicates in the "all" view
      groups[types[0]].push(r);
    }
  });

  let html = '';
  Object.keys(groups).forEach(cat => {
    const items = groups[cat];
    if (items.length > 0) {
      const displayCat = cat.replace(/_/g, ' ');
      html += `
        <div class="col-span-full mt-8 mb-4 border-b border-white/5 pb-3 flex justify-between items-end">
          <h2 class="text-2xl font-black uppercase tracking-tight text-on-surface">${displayCat}</h2>
          <span class="text-xs font-bold uppercase tracking-wider text-slate-500">${items.length} Units Found</span>
        </div>
        ${items.map((r, idx) => renderSingleCard(r, idx)).join('')}
      `;
    }
  });

  grid.innerHTML = html;
}

function renderSingleCard(r, index) {
  const risk = getRiskLevel(r);
  const isFeatured = index === 0; // First in each category is featured
  
  return `
    <div class="${isFeatured ? 'group bg-gradient-to-br from-[#1e4d58]/40 to-[#0e1416] border border-cyan-500/30' : 'group bg-surface-container border border-white/5'} p-5 rounded-xl hover:border-primary/30 hover:-translate-y-1 hover:shadow-xl transition-all duration-300 cursor-pointer flex flex-col justify-between min-h-[250px] shadow-lg" onclick="navigate('detail','${r.id}')">
      <div>
        <div class="flex justify-between items-start mb-4">
          <span class="${isFeatured ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30' : 'bg-surface-container-high text-slate-400'} px-2.5 py-0.5 text-[10px] font-bold uppercase rounded-md">REACTION-${r.id.toUpperCase()}</span>
          <div class="flex gap-2">
            <span class="material-symbols-outlined font-bold text-sm ${isFeatured ? 'text-cyan-400' : 'text-slate-500'}" style="font-variation-settings: 'FILL' 1;">${risk.icon}</span>
            <span class="material-symbols-outlined text-sm ${isFeatured ? 'text-cyan-400' : 'text-slate-500'}">experiment</span>
          </div>
        </div>
        <h3 class="${isFeatured ? 'text-xl leading-tight text-cyan-300' : 'text-lg leading-snug text-on-surface'} font-black uppercase mb-3">${r.name}</h3>
        <div class="${isFeatured ? 'bg-cyan-500/10 text-cyan-200 border border-cyan-500/20' : 'bg-background text-[#acedff] border border-white/5'} p-3.5 mb-3 font-mono font-bold ${isFeatured ? 'text-sm' : 'text-xs'} rounded-lg transition-colors">
          ${r.equation}
        </div>
      </div>
      
      <div class="flex justify-between items-end">
        <div class="space-y-1">
          <p class="text-[9px] font-black uppercase tracking-widest ${isFeatured ? 'text-slate-500' : 'text-slate-600'}">Hazard Level</p>
          <div class="flex gap-1">
            <div class="w-5 h-1.5 ${risk.bars >= 1 ? 'bg-red-400/80 shadow-[0_0_8px_rgba(248,113,113,0.5)]' : 'bg-slate-700'} rounded-sm"></div>
            <div class="w-5 h-1.5 ${risk.bars >= 2 ? 'bg-red-400/80 shadow-[0_0_8px_rgba(248,113,113,0.5)]' : 'bg-slate-700'} rounded-sm"></div>
            <div class="w-5 h-1.5 ${risk.bars >= 3 ? 'bg-red-400/80 shadow-[0_0_8px_rgba(248,113,113,0.5)]' : 'bg-slate-700'} rounded-sm"></div>
          </div>
        </div>
        <div class="${isFeatured ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30' : 'bg-surface-container-high text-slate-400 border border-white/5'} px-3 py-1 font-bold uppercase text-[9px] rounded-lg">${risk.level}</div>
      </div>
    </div>
  `;
}

// ============================================================
// DETAIL PAGE
// ============================================================
function renderDetailPage(rxnId) {
  const rxn = REACTIONS.find(r=>r.id===rxnId);
  if (!rxn) return;
  const type = getReactionType(rxn);
  const badgeClass = getBadgeClass(type);
  const steps = rxn.explanation.split(/(?<=\.)\s+/).filter(s=>s.trim());
  const related = REACTIONS.filter(r=>r.class_level===rxn.class_level && r.id!==rxn.id).slice(0,3);

  document.getElementById('detail-content').innerHTML = `
    <div class="detail-header fade-in">
      <div class="detail-badges">
        <span class="${badgeClass}">${type}</span>
        <span class="badge badge-class">Class ${rxn.class_level}</span>
      </div>
      <h1 class="detail-title">${rxn.name}</h1>
    </div>

    <div class="detail-section fade-in">
      <div style="background:var(--primary-light);border:1.5px solid #bfdbfe;border-radius:14px;padding:18px;margin-bottom:16px">
        <div style="font-size:0.7rem;font-weight:700;color:var(--primary);text-transform:uppercase;letter-spacing:0.07em;margin-bottom:6px">Balanced Equation</div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:1rem;font-weight:700;color:var(--text)">${rxn.equation}</div>
      </div>
    </div>

    <div class="detail-section fade-in">
      <h2><svg viewBox="0 0 24 24"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg> Reaction Mechanism</h2>
      <div class="mechanism-steps">
        ${steps.map((s,i)=>`<div class="step"><div class="step-num">${i+1}</div><div class="step-content">${s}</div></div>`).join('')}
      </div>
    </div>

    ${rxn.applications ? `
    <div class="detail-section fade-in">
      <h2><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg> Real-World Applications</h2>
      <div class="applications-box"><p>${rxn.applications}</p></div>
    </div>` : ''}

    <div class="detail-section fade-in" style="background:var(--card);border:1.5px solid var(--border);border-radius:16px;padding:28px;text-align:center">
      <h3 style="font-size:1.1rem;font-weight:700;margin-bottom:8px">Practice this reaction in the lab</h3>
      <p style="color:var(--muted);font-size:0.875rem;margin-bottom:16px">Try assembling the reactants in the virtual lab</p>
      <button class="btn btn-primary" onclick="navigate('lab')">Open Virtual Lab →</button>
    </div>

    ${related.length ? `
    <div class="detail-section fade-in">
      <h2><svg viewBox="0 0 24 24"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg> Related Reactions</h2>
      <div class="related-grid">
        ${related.map(r=>`<div class="related-card" onclick="navigate('detail','${r.id}')">
          <div class="type">${getReactionType(r.name)}</div>
          <div class="name">${r.name}</div>
          <div style="font-size:0.8rem;color:var(--primary);margin-top:8px;font-weight:600">Read more →</div>
        </div>`).join('')}
      </div>
    </div>` : ''}
  `;
}

// ============================================================
// LAB PAGE — CHEMLAB_V01 VIRTUAL WORKBENCH
// ============================================================

let droppedElements = [];
let instanceCounter = 0;

function filterChemicalShelf() {
  const query = document.getElementById('shelf-search')?.value.trim() || '';
  renderLabPage(query);
}

function renderLabPage(query = '') {
  const grid = document.getElementById('elements-grid');
  if(!grid) return;
  
  const normQuery = normalizeChemicalText(query);
  const qLower = query.toLowerCase();

  const filteredElements = ELEMENTS.map((el, originalIndex) => ({el, originalIndex}))
    .filter(item => {
      if (!query) return true;
      const {el} = item;
      return el.name.toLowerCase().includes(qLower) || 
             el.symbol.toLowerCase().includes(qLower) ||
             normalizeChemicalText(el.symbol).includes(normQuery);
    });

  grid.innerHTML = filteredElements.map(({el, originalIndex}) => {
    let textColor = 'text-slate-300';
    let dot = '';
    
    // Match colors from the image reference
    if (el.symbol === 'CH4') {
        textColor = 'text-yellow-400';
        dot = '<div class="absolute top-3 right-3 w-2 h-2 bg-yellow-400 rounded-full animate-pulse shadow-[0_0_8px_#facc15]"></div>';
    } else if (el.symbol === 'O2') {
        textColor = 'text-blue-400';
    } else if (el.symbol === 'H2SO4') {
        textColor = 'text-red-400';
    } else if (el.symbol === 'NaOH') {
        textColor = 'text-cyan-400';
    } else {
        // General typing if not specifically matching the image
        if (getChemicalType(el.formula || el.symbol) === 'acid') {
            textColor = 'text-red-400';
        } else if (getChemicalType(el.formula || el.symbol) === 'base') {
            textColor = 'text-blue-400';
        }
    }

    return `
    <div class="group bg-surface-container border border-white/5 p-4 rounded-xl flex flex-col gap-1 cursor-grab active:cursor-grabbing hover:border-primary/30 hover:-translate-y-1 hover:shadow-lg transition-all duration-300 relative" 
         draggable="true" 
         id="element-${originalIndex}"
         ondragstart="handleDragStart(event, ${originalIndex})"
         ondragend="handleDragEnd(event)">
        ${dot}
        <span class="text-xl font-bold ${textColor}">${el.symbol}</span>
        <span class="text-[9px] font-bold uppercase tracking-wider opacity-60 ${textColor}">${el.name}</span>
    </div>
  `}).join('');
}

function handleDragStart(e, index) {
  const el = ELEMENTS[index];
  e.dataTransfer.setData('text/plain', JSON.stringify(el));
  e.currentTarget.classList.add('opacity-50');
  addLabLog(`PREPARING_REAGENT: ${el.symbol}`, 'text-zinc-500');
}

function handleDragEnd(e) {
  e.currentTarget.classList.remove('opacity-50');
}

function handleDragEnter(e) {
  e.preventDefault();
  e.currentTarget.classList.add('bg-primary-container/20');
}

function handleDragLeave(e) {
  e.preventDefault();
  e.currentTarget.classList.remove('bg-primary-container/20');
}

function handleDragOver(e) {
  e.preventDefault();
}

function handleDrop(e) {
  e.preventDefault();
  const dropZone = e.currentTarget;
  dropZone.classList.remove('bg-primary-container/20');

  try {
    const el = JSON.parse(e.dataTransfer.getData('text/plain'));
    droppedElements.push(el);
    updateLabUIOnDrop(el);
    
    addLabLog(`MOLECULAR_INJECTION: ${el.symbol} ADDED TO CHAMBER`, 'text-tertiary');
    
    // Update count display
    document.getElementById('el-count').textContent = `${droppedElements.length} CHEMICALS ADDED`;
    
    // Render chips in sequence control
    renderDroppedChips();
    
    // Small shake effect on drop
    dropZone.classList.add('animate-bounce');
    setTimeout(() => dropZone.classList.remove('animate-bounce'), 500);

  } catch (err) {
    console.error('Drop error:', err);
  }
}

function updateLabUIOnDrop(el) {
  const liq = document.getElementById('flask-liquid-0');
  
  // Update liquid color based on the chemical dropped
  const colorType = getChemicalType(el.formula || el.symbol);
  let targetColor = '#3b82f6'; // default blue
  
  if (colorType === 'acid') targetColor = '#e63b2e'; // red
  else if (colorType === 'base') targetColor = '#0055ff'; // deep blue
  else if (el.symbol === 'CH4') targetColor = '#ffcc00'; // yellow
  
  liq.style.fill = targetColor;
  liq.style.fillOpacity = Math.min(0.6 + (droppedElements.length * 0.15), 1);
  liq.classList.remove('opacity-0');
  
  // Update the liquid path to simulate rising level
  const drops = Math.min(droppedElements.length, 5);
  const rise = drops * 12;
  
  const yBase = 150 - rise;
  const yWave = 145 - rise;
  
  // Flask diagonals go from y=90 to y=170
  // Left wall: x = 85 - 45 * ((y - 90) / 80)
  // Right wall: x = 115 + 45 * ((y - 90) / 80)
  const w1 = 85 - 45 * ((yBase - 90) / 80);
  const w2 = 115 + 45 * ((yBase - 90) / 80);
  
  // Generate wave path dynamically by scaling it to the current width
  const step = (w2 - w1) / 8;
  const wavePath = `M ${w1} ${yBase} L ${w1+step} ${yWave} L ${w1+step*2} ${yBase} L ${w1+step*3} ${yWave} L ${w1+step*4} ${yBase} L ${w1+step*5} ${yWave} L ${w1+step*6} ${yBase} L ${w1+step*7} ${yWave} L ${w2} ${yBase} L 160 170 L 40 170 Z`;
  
  liq.setAttribute('d', wavePath);
  
  // Start bubbles if it's the first element
  if (droppedElements.length === 1) {
    startBubbles(0);
  }
  
  updateLiveTelemetry();
}

function updateLiveTelemetry() {
  let temp = 24.5;
  let ph = 7.02;
  let stability = 100.0;
  
  if (droppedElements.length === 0) {
    updateGauges(temp, ph, stability);
    return;
  }
  
  let acidCount = 0;
  let baseCount = 0;
  let metalCount = 0;
  let organicCount = 0;
  
  droppedElements.forEach(el => {
    const type = getChemicalType(el.formula || el.symbol);
    if (type === 'acid') acidCount++;
    else if (type === 'base') baseCount++;
    else if (type === 'metal') metalCount++;
    else if (type === 'organic') organicCount++;
    
    // Slight temperature increase for mixing
    temp += 0.5;
  });
  
  // Exothermic reactions approximate
  const neutralizationPairs = Math.min(acidCount, baseCount);
  temp += neutralizationPairs * 12.5;
  
  const metalAcidPairs = Math.min(metalCount, acidCount);
  temp += metalAcidPairs * 18.0;
  
  // Approximate pH
  const netH = acidCount - baseCount;
  if (netH > 0) {
    ph = Math.max(1.0, 7.0 - (netH * 1.5));
  } else if (netH < 0) {
    ph = Math.min(14.0, 7.0 + (Math.abs(netH) * 1.5));
  }
  
  // Approximate stability
  stability -= (neutralizationPairs * 5);
  stability -= (metalAcidPairs * 15);
  stability -= (droppedElements.length * 1.5);
  stability = Math.max(0, Math.min(100, Math.round(stability * 10) / 10));
  
  updateGauges(temp, ph, stability);
}

function startBubbles(index) {
  const container = document.getElementById(`bubbles-container-${index}`);
  container.innerHTML = '';
  for (let i = 0; i < 15; i++) {
    const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    circle.setAttribute("cx", 80 + Math.random() * 40);
    circle.setAttribute("cy", 140 + Math.random() * 20);
    circle.setAttribute("r", 1 + Math.random() * 3);
    circle.setAttribute("fill", "white");
    circle.setAttribute("fill-opacity", "0.6");
    
    const animY = document.createElementNS("http://www.w3.org/2000/svg", "animate");
    animY.setAttribute("attributeName", "cy");
    animY.setAttribute("from", "160");
    animY.setAttribute("to", "110");
    animY.setAttribute("dur", (1 + Math.random() * 2) + "s");
    animY.setAttribute("repeatCount", "indefinite");
    
    const animO = document.createElementNS("http://www.w3.org/2000/svg", "animate");
    animO.setAttribute("attributeName", "opacity");
    animO.setAttribute("from", "0.6");
    animO.setAttribute("to", "0");
    animO.setAttribute("dur", animY.getAttribute("dur"));
    animO.setAttribute("repeatCount", "indefinite");
    
    circle.appendChild(animY);
    circle.appendChild(animO);
    container.appendChild(circle);
  }
}

function renderDroppedChips() {
  const container = document.getElementById('dropped-elements');
  if(!container) return;
  
  const counts = {};
  droppedElements.forEach(el => {
    if (!counts[el.symbol]) counts[el.symbol] = { count: 0, el: el };
    counts[el.symbol].count++;
  });

  container.innerHTML = Object.values(counts).map((item) => `
    <div class="bg-surface-container border border-white/10 text-slate-300 text-xs font-bold px-3 py-1.5 rounded-xl flex items-center gap-2 shadow-md">
      <span>${item.el.symbol}</span>
      <div class="flex items-center gap-1 bg-[#0e1416] border border-white/5 text-slate-300 px-2 py-0.5 rounded-lg ml-1">
        <button class="hover:text-red-400 font-bold px-1" onclick="changeElementAmount('${item.el.symbol}', -1)">-</button>
        <input type="number" class="w-8 text-center text-slate-300 font-bold bg-transparent outline-none p-0 text-xs m-0 border-none no-spinners" style="appearance: textfield; -moz-appearance: textfield;" value="${item.count}" min="1" onchange="setElementAmount('${item.el.symbol}', this.value)">
        <button class="hover:text-cyan-400 font-bold px-1" onclick="changeElementAmount('${item.el.symbol}', 1)">+</button>
      </div>
      <span class="cursor-pointer text-slate-500 hover:text-red-400 ml-1 text-sm font-light" onclick="removeAllOfElement('${item.el.symbol}')">×</span>
    </div>
  `).join('');
}

function changeElementAmount(symbol, delta) {
  if (delta === 1) {
    const el = ELEMENTS.find(e => e.symbol === symbol) || droppedElements.find(e => e.symbol === symbol);
    if (el) droppedElements.push(el);
  } else if (delta === -1) {
    const index = droppedElements.findIndex(e => e.symbol === symbol);
    if (index !== -1) droppedElements.splice(index, 1);
  }
  
  document.getElementById('el-count').textContent = `${droppedElements.length} CHEMICALS ADDED`;
  renderDroppedChips();
  if (droppedElements.length === 0) {
    resetLab();
  } else {
    updateLabUIOnDrop(droppedElements[droppedElements.length - 1]);
  }
}

function setElementAmount(symbol, amount) {
  amount = parseInt(amount, 10);
  if (isNaN(amount) || amount < 1) amount = 1;
  const currentCount = droppedElements.filter(e => e.symbol === symbol).length;
  const delta = amount - currentCount;
  if (delta > 0) {
    const el = ELEMENTS.find(e => e.symbol === symbol) || droppedElements.find(e => e.symbol === symbol);
    if (el) {
      for (let i = 0; i < delta; i++) droppedElements.push(el);
    }
  } else if (delta < 0) {
    for (let i = 0; i < -delta; i++) {
      const index = droppedElements.findIndex(e => e.symbol === symbol);
      if (index !== -1) droppedElements.splice(index, 1);
    }
  }
  document.getElementById('el-count').textContent = `${droppedElements.length} CHEMICALS ADDED`;
  renderDroppedChips();
  if (droppedElements.length === 0) {
    resetLab();
  } else {
    updateLabUIOnDrop(droppedElements[droppedElements.length - 1]);
  }
}

function removeAllOfElement(symbol) {
  droppedElements = droppedElements.filter(e => e.symbol !== symbol);
  document.getElementById('el-count').textContent = `${droppedElements.length} CHEMICALS ADDED`;
  renderDroppedChips();
  if (droppedElements.length === 0) {
    resetLab();
  } else {
    updateLabUIOnDrop(droppedElements[droppedElements.length - 1]);
  }
}

function removeElement(index) {
  droppedElements.splice(index, 1);
  addLabLog(`REAGENT_REMOVED`, 'text-zinc-500');
  document.getElementById('el-count').textContent = `${droppedElements.length} CHEMICALS ADDED`;
  renderDroppedChips();
  if (droppedElements.length === 0) {
    resetLab();
  } else {
    // Recalculate visual level using the last remaining element
    updateLabUIOnDrop(droppedElements[droppedElements.length - 1]);
  }
}

function resetLab() {
  droppedElements = [];
  document.getElementById('el-count').textContent = `0 CHEMICALS ADDED`;
  document.getElementById('dropped-elements').innerHTML = '';
  document.getElementById('lab-status').textContent = 'READY FOR EXPERIMENT';
  document.getElementById('lab-status').className = 'mt-4 mb-8 border border-cyan-500/30 bg-[#1e4d58] text-[#acedff] px-10 py-4 font-bold text-2xl uppercase text-center rounded-xl shadow-[0_0_20px_rgba(6,182,212,0.2)] z-20';
  
  const liq = document.getElementById('flask-liquid-0');
  liq.style.fillOpacity = 0.3;
  liq.style.fill = '#3b82f6';
  liq.setAttribute('d', 'M 62 130 L 70 125 L 80 130 L 90 125 L 100 130 L 110 125 L 120 130 L 130 125 L 138 130 L 160 170 L 40 170 Z');
  liq.classList.remove('success', 'error', 'partial', 'metal', 'nonmetal', 'acid', 'base', 'organic');
  liq.classList.add('opacity-0');
  
  document.getElementById(`bubbles-container-0`).innerHTML = '';
  document.getElementById(`reaction-glow-0`).classList.add('opacity-0');
  
  const resultArea = document.getElementById('result-area');
  if (resultArea) resultArea.classList.add('hidden');
  
  // Reset Gauges
  updateGauges(24.5, 7.02, 100);
  
  addLabLog(`SYSTEM_FLUSHED: ALL_REAGENTS_CLEARED`, 'text-secondary');
}

function addLabLog(msg, colorClass = 'text-white') {
  const log = document.getElementById('lab-log');
  const time = new Date().toLocaleTimeString([], { hour12: false });
  const entry = document.createElement('div');
  entry.className = `flex gap-2 ${colorClass}`;
  entry.innerHTML = `<span class="font-black">[${time}]</span> <span>${msg}</span>`;
  log.appendChild(entry);
  log.scrollTop = log.scrollHeight;
}

function updateGauges(temp, ph, stability) {
  // Update Values
  document.getElementById('temp-val').textContent = temp.toFixed(1);
  document.getElementById('ph-val').textContent = ph.toFixed(2);
  document.getElementById('stability-val').textContent = stability.toFixed(1) + '%';
  
  // Update Bar/Marker
  document.getElementById('temp-bar').style.width = Math.min(temp * 2, 100) + '%';
  document.getElementById('ph-marker').style.left = (ph / 14 * 100) + '%';
}

function runReactionCheck() {
  if (droppedElements.length < 2) {
    addLabLog('ERROR: INSUFFICIENT_REAGENTS_FOR_TRACE', 'text-secondary');
    return;
  }

  addLabLog('INITIATING_MOLECULAR_ANALYSIS...', 'text-tertiary');
  document.getElementById('lab-status').textContent = 'ANALYZING...';
  document.getElementById('lab-status').classList.add('animate-pulse');

  const formulas = droppedElements.map(e => e.formula);
  const rxn = matchReaction(formulas);

  setTimeout(() => {
    document.getElementById('lab-status').classList.remove('animate-pulse');
    
    if (rxn.match) {
      handleReactionSuccess(rxn.match);
    } else if (rxn.partial) {
      handleReactionPartial(rxn.match);
    } else {
      handleReactionInvalid();
    }
  }, 1500);
}

function handleReactionSuccess(rxn) {
  addLabLog(`REACTION_SUCCESS: ${rxn.name.toUpperCase()}`, 'text-green-400');
  
  // Log reaction success to database
  fetch('/api/log_event', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
          event_type: 'reaction_success',
          event_data: rxn.name
      })
  }).catch(e => console.error('Failed to log event', e));

  document.getElementById('lab-status').textContent = 'REACTION DETECTED';
  document.getElementById('lab-status').className = 'mt-4 mb-8 border border-cyan-400/50 bg-[#004e5c] text-[#acedff] px-10 py-4 font-bold text-2xl uppercase text-center rounded-xl shadow-[0_0_25px_rgba(6,182,212,0.4)] z-20';
  
  // Visual Effects
  document.getElementById('reaction-glow-0').classList.remove('opacity-0');
  const liq = document.getElementById('flask-liquid-0');
  liq.style.fill = '#4cd7f6';
  
  // Update Gauges
  const isExothermic = rxn.explanation.toLowerCase().includes('exothermic') || rxn.explanation.toLowerCase().includes('releases heat');
  const finalTemp = isExothermic ? 45.8 : 22.1;
  const finalPH = rxn.products.includes('HCl') || rxn.products.includes('H2SO4') ? 1.5 : 7.2;
  
  updateGauges(finalTemp, finalPH, 94.5);
  
  const isDangerous = rxn.explanation.toLowerCase().includes('explosive') || 
                      rxn.explanation.toLowerCase().includes('violent') || 
                      rxn.explanation.toLowerCase().includes('combustion') || 
                      rxn.name.toLowerCase().includes('combustion') ||
                      rxn.explanation.toLowerCase().includes('ignites');
                      
  if (isDangerous) {
    triggerBlastEffect();
    updateGauges(finalTemp + 100, finalPH, 5.0); // Override gauges for chaos
  }
  
  // Show Result area with modern dark styling
  const res = document.getElementById('result-area');
  if(!res) return;
  
  const reactantsHtml = rxn.reactants.split(',').map(r => `<div class="bg-[#1e4d58] text-[#acedff] px-6 py-3 border border-cyan-500/20 rounded-xl font-mono">${r.trim()}</div>`).join('<span class="text-tertiary font-black text-3xl">+</span>');
  const productsHtml = rxn.products.split(',').map(p => `<div class="bg-[#640039] text-[#ffd9e4] px-6 py-3 border border-[#ff79b4]/20 rounded-xl font-mono">${p.trim()}</div>`).join('<span class="text-tertiary font-black text-3xl">+</span>');
  const type = getReactionType(rxn.name || rxn.equation);

  res.innerHTML = `
    <div class="mt-8 flex flex-col gap-6 animate-[fadeIn_0.5s_ease-out]">
      <!-- Badges -->
      <div class="flex justify-center gap-4">
        <div class="bg-[#004e5c] text-[#acedff] px-4 py-2 font-bold uppercase border border-cyan-500/30 rounded-xl flex items-center gap-2 shadow-lg">
          <span class="material-symbols-outlined text-sm">check_circle</span> Reaction Successful!
        </div>
        <div class="bg-secondary-container text-secondary-fixed-dim px-4 py-2 font-bold uppercase border border-secondary/20 rounded-xl shadow-lg">
          ${type}
        </div>
      </div>

      <!-- Title & Conditions -->
      <div class="text-center">
        <h2 class="font-black text-3xl md:text-4xl uppercase tracking-tight mb-2 text-on-surface">${rxn.name}</h2>
        <p class="font-bold text-xs md:text-sm uppercase tracking-widest text-slate-500">${rxn.conditions ? 'CONDITIONS: ' + rxn.conditions : 'CONDITIONS: STANDARD AMBIENT'}</p>
      </div>

      <!-- Visual Equation Box -->
      <div class="bg-surface-container border border-white/5 p-6 md:p-8 rounded-2xl flex flex-wrap justify-center items-center gap-4 md:gap-6 text-xl md:text-3xl font-black">
        ${reactantsHtml}
        <span class="text-cyan-400 material-symbols-outlined text-4xl md:text-5xl font-black mx-2">arrow_forward</span>
        ${productsHtml}
      </div>

      <!-- Balanced Equation -->
      <div class="bg-surface-container-high border border-white/10 p-6 rounded-2xl shadow-xl">
        <h4 class="font-bold text-xs uppercase mb-4 text-slate-500 tracking-widest">Balanced Equation</h4>
        <p class="font-mono text-xl md:text-2xl font-bold text-cyan-400">${rxn.equation}</p>
      </div>

      <!-- What Happened -->
      <div class="bg-surface-container-high border border-white/10 p-6 rounded-2xl shadow-xl">
        <h4 class="font-bold text-xs uppercase mb-4 text-slate-500 tracking-widest">What Happened</h4>
        <p class="font-body text-sm md:text-base leading-relaxed text-on-surface-variant">${rxn.explanation}</p>
      </div>
    </div>
  `;
  res.classList.remove('hidden');
}

function triggerBlastEffect() {
  const sandbox = document.getElementById('drop-zone');
  if (!sandbox) return;

  const blast = document.createElement('div');
  blast.className = 'absolute inset-0 z-50 flex items-center justify-center pointer-events-none overflow-hidden';
  blast.innerHTML = `
    <div class="absolute inset-0 bg-red-600 animate-blast-flash mix-blend-multiply"></div>
    <div class="relative w-full h-full flex items-center justify-center">
       <div class="absolute w-20 h-20 bg-yellow-400 rounded-full animate-blast-expand"></div>
       <div class="absolute w-16 h-16 bg-orange-500 rounded-full animate-blast-expand" style="animation-delay: 0.1s"></div>
       <div class="absolute w-12 h-12 bg-red-600 rounded-full animate-blast-expand" style="animation-delay: 0.2s"></div>
       <div class="absolute font-black text-7xl md:text-9xl text-white uppercase italic tracking-tighter drop-shadow-2xl animate-blast-text">BOOM!</div>
    </div>
  `;
  sandbox.appendChild(blast);
  
  const centerArea = sandbox.parentElement;
  centerArea.classList.add('animate-blast-shake');

  const liq = document.getElementById('flask-liquid-0');
  const oldFill = liq ? liq.style.fill : null;
  if (liq) liq.style.fill = '#ff4400';

  setTimeout(() => {
    if (blast.parentNode) blast.remove();
    centerArea.classList.remove('animate-blast-shake');
    if (liq && document.body.contains(liq)) {
        liq.style.fill = oldFill;
    }
  }, 1000);
}

function handleReactionInvalid() {
  addLabLog('ERROR: NO_REACTION_DETECTED_UNDER_CURRENT_STATE', 'text-secondary');
  document.getElementById('lab-status').textContent = 'STABLE MIXTURE';
  document.getElementById('lab-status').className = 'mt-4 mb-8 border border-white/10 bg-surface-container-high text-on-surface-variant px-10 py-4 font-bold text-2xl uppercase text-center rounded-xl z-20';
  
  updateGauges(24.5, 7.02, 100);

  // Show intelligent no-reaction reasoning
  const formulas = droppedElements.map(e => e.formula);
  const reason = findNoReactionReason(formulas);
  const res = document.getElementById('result-area');
  if (res && reason) {
    res.innerHTML = `
      <div class="mt-8 flex flex-col gap-4 animate-[fadeIn_0.5s_ease-out]">
        <div class="flex justify-center">
          <div class="bg-surface-container-high text-on-surface px-4 py-2 font-bold uppercase border border-white/10 rounded-xl flex items-center gap-2 shadow-lg">
            <span class="material-symbols-outlined text-sm">info</span> No Reaction Detected
          </div>
        </div>
        <div class="no-reaction-box">
          <div class="no-reaction-title text-[#ff79b4]">${reason.title}</div>
          <div class="no-reaction-reason text-slate-400">${reason.reason}</div>
        </div>
        <div class="bg-surface-container-high border border-white/10 p-5 rounded-2xl text-center shadow-lg">
          <p class="font-bold text-xs uppercase text-slate-500 mb-3">Try a Known Reaction</p>
          <button class="btn btn-primary text-xs" onclick="navigate('reactions')">Browse Reaction Catalog →</button>
        </div>
      </div>
    `;
    res.classList.remove('hidden');
  }
}

function handleReactionPartial(rxn) {
  addLabLog('WARNING: PARTIAL_REACTION_DETECTED', 'text-yellow-400');
  document.getElementById('lab-status').textContent = 'PARTIAL REACTION';
  document.getElementById('lab-status').className = 'mt-4 mb-8 border border-[#ff79b4]/50 bg-[#640039] text-[#ffd9e4] px-10 py-4 font-bold text-2xl uppercase text-center rounded-xl shadow-[0_0_25px_rgba(255,121,180,0.4)] z-20';
  
  updateGauges(24.5, 7.02, 100);
}
function getChemicalColorType(el) {
  const chemicalType = (el && el.type ? el.type : '').toLowerCase();
  if (['metal', 'nonmetal', 'acid', 'base', 'organic'].includes(chemicalType)) {
    return chemicalType;
  }
  return 'organic';
}

function getChemicalType(formula) {
  const acids = ['HCl', 'H₂SO₄', 'CH₃COOH'];
  const bases = ['NaOH', 'KOH', 'NH₃'];
  if (acids.includes(formula)) return 'acid';
  if (bases.includes(formula)) return 'base';
  return 'neutral';
}

function isStrongAcid(formula) { return ['HCl', 'H₂SO₄'].includes(formula); }
function isWeakAcid(formula) { return ['CH₃COOH'].includes(formula); }
function isStrongBase(formula) { return ['NaOH', 'KOH'].includes(formula); }
function isWeakBase(formula) { return ['NH₃'].includes(formula); }

const TITRATION_DATA = {
  acids: {
    'HCl': { type: 'strong', ka: null },
    'H₂SO₄': { type: 'strong', ka: null },
    'CH₃COOH': { type: 'weak', ka: 1.8e-5 },
    'NH₃': { type: 'weak_base', kb: 1.8e-5 }
  },
  bases: {
    'NaOH': { type: 'strong' },
    'KOH': { type: 'strong' },
    'NH₃': { type: 'weak', kb: 1.8e-5 },
    'CH₃COOH': { type: 'weak_acid', ka: 1.8e-5 }
  },
  indicators: {
    phenolphthalein: { acidColor: '#fff', baseColor: '#ec4899', acidText: 'Colorless', baseText: 'Pink', low: 8.3, high: 10.0 },
    methylorange: { acidColor: '#f97316', baseColor: '#facc15', acidText: 'Red/Orange', baseText: 'Yellow', low: 3.1, high: 4.4 },
    litmus: { acidColor: '#ef4444', baseColor: '#3b82f6', acidText: 'Red', baseText: 'Blue', low: 4.5, high: 8.3 }
  }
};

let titrationState = {
  titrantAdded: 0,
  titrant: 'NaOH',
  titrantConc: 0.1,
  analyte: 'HCl',
  analyteVol: 20,
  analyteConc: 0.1,
  indicator: 'phenolphthalein'
};

function initTitrationPage() {
  generateBuretteGraduations();
  updateTitration();
}

function generateBuretteGraduations() {
  const container = document.getElementById('burette-graduations');
  if (!container) return;
  let html = '';
  for (let i = 0; i <= 10; i++) {
    const major = i % 5 === 0;
    html += `<div class="graduation-mark ${major ? 'major' : ''}" ${major ? `data-val="${50 - i * 5}"` : ''}></div>`;
  }
  container.innerHTML = html;
}

function calculatePH(state) {
  const { titrant, titrantConc, titrantAdded, analyte, analyteVol, analyteConc } = state;
  const Va = analyteVol / 1000; // L
  const Vt = titrantAdded / 1000; // L
  const Ca = analyteConc;
  const Ct = titrantConc;
  const nA = Ca * Va;
  const nT = Ct * Vt;
  const Vtotal = Va + Vt;

  // Determine reaction type
  const analyteIsAcid = isStrongAcid(analyte) || isWeakAcid(analyte);
  const titrantIsBase = isStrongBase(titrant) || isWeakBase(titrant);
  const titrantIsAcid = isStrongAcid(titrant) || isWeakAcid(titrant);

  // If titrant is acid and analyte is base (reverse titration)
  if (titrantIsAcid && !analyteIsAcid) {
    if (isStrongBase(analyte) && isStrongAcid(titrant)) {
      if (nT < nA) return 14 + Math.log10((nA - nT) / Vtotal);
      if (Math.abs(nT - nA) < 1e-9) return 7;
      return -Math.log10((nT - nA) / Vtotal);
    }
    if (isStrongBase(analyte) && isWeakAcid(titrant)) {
      const Ka = 1.8e-5;
      if (nT < nA) return 14 + Math.log10((nA - nT) / Vtotal);
      if (Math.abs(nT - nA) < 1e-9) {
        const Csalt = nA / Vtotal;
        const OH = Math.sqrt((1e-14 / Ka) * Csalt);
        return 14 + Math.log10(OH);
      }
      const excessAcid = nT - nA;
      const Csalt = nA / Vtotal;
      const pH = -Math.log10(Ka) + Math.log10(Csalt / (excessAcid / Vtotal));
      return pH;
    }
    if (isWeakBase(analyte) && isStrongAcid(titrant)) {
      const Kb = 1.8e-5;
      if (nT < nA) {
        const pOH = -Math.log10(Kb) + Math.log10((nA - nT) / nT);
        return 14 - pOH;
      }
      if (Math.abs(nT - nA) < 1e-9) {
        const Csalt = nA / Vtotal;
        const H = Math.sqrt((1e-14 / Kb) * Csalt);
        return -Math.log10(H);
      }
      return -Math.log10((nT - nA) / Vtotal);
    }
  }

  // Standard: titrant is base, analyte is acid
  if (isStrongAcid(analyte) && isStrongBase(titrant)) {
    if (nT < nA) return -Math.log10((nA - nT) / Vtotal);
    if (Math.abs(nT - nA) < 1e-9) return 7;
    return 14 + Math.log10((nT - nA) / Vtotal);
  }

  if (isWeakAcid(analyte) && isStrongBase(titrant)) {
    const Ka = 1.8e-5;
    if (nT < nA) {
      const pH = -Math.log10(Ka) + Math.log10(nT / (nA - nT));
      return pH;
    }
    if (Math.abs(nT - nA) < 1e-9) {
      const Csalt = nA / Vtotal;
      const OH = Math.sqrt((1e-14 / Ka) * Csalt);
      return 14 + Math.log10(OH);
    }
    return 14 + Math.log10((nT - nA) / Vtotal);
  }

  if (isStrongAcid(analyte) && isWeakBase(titrant)) {
    const Kb = 1.8e-5;
    if (nT < nA) {
      const pOH = -Math.log10(Kb) + Math.log10((nA - nT) / nT);
      return 14 - pOH;
    }
    if (Math.abs(nT - nA) < 1e-9) {
      const Csalt = nA / Vtotal;
      const H = Math.sqrt((1e-14 / Kb) * Csalt);
      return -Math.log10(H);
    }
    const pOH = -Math.log10(Kb) + Math.log10((nT - nA) / Vtotal);
    return 14 - pOH;
  }

  if (isWeakAcid(analyte) && isWeakBase(titrant)) {
    const Ka = 1.8e-5;
    if (nT < nA) {
      const pH = -Math.log10(Ka) + Math.log10(nT / (nA - nT));
      return pH;
    }
    if (Math.abs(nT - nA) < 1e-9) {
      const pH = 7 + 0.5 * (-Math.log10(Ka) + Math.log10(1.8e-5));
      return pH;
    }
    const Kb = 1.8e-5;
    const pOH = -Math.log10(Kb) + Math.log10((nT - nA) / Vtotal);
    return 14 - pOH;
  }

  return 7;
}

function calculateEquivalenceVolume(state) {
  const { titrantConc, analyteVol, analyteConc } = state;
  return (analyteConc * analyteVol) / titrantConc;
}

function updateTitration() {
  const titrant = document.getElementById('titrant-select').value;
  const analyte = document.getElementById('analyte-select').value;
  const titrantConc = parseFloat(document.getElementById('titrant-conc')?.value || 0.1);
  const analyteVol = parseFloat(document.getElementById('analyte-vol')?.value || 20);
  const analyteConc = parseFloat(document.getElementById('analyte-conc')?.value || 0.1);
  const indicator = document.getElementById('indicator-select')?.value || 'phenolphthalein';

  if(document.getElementById('titrant-conc-val')) document.getElementById('titrant-conc-val').textContent = titrantConc.toFixed(2) + ' N';
  if(document.getElementById('analyte-vol-val')) document.getElementById('analyte-vol-val').textContent = analyteVol + ' mL';
  if(document.getElementById('analyte-conc-val')) document.getElementById('analyte-conc-val').textContent = analyteConc.toFixed(2) + ' N';

  titrationState = { titrant, titrantConc, analyte, analyteVol, analyteConc, indicator, titrantAdded: titrationState.titrantAdded, hasLoggedCompleted: titrationState.hasLoggedCompleted };

  const Veq = calculateEquivalenceVolume(titrationState);
  const slider = document.getElementById('titrant-added');
  if(slider) slider.max = Math.max(50, Math.ceil(Veq * 2));

  updateTitrationUI();
}

function updateTitrationFromSlider() {
  const slider = document.getElementById('titrant-added');
  if(slider) {
    titrationState.titrantAdded = parseFloat(slider.value);
    updateTitrationUI();
  }
}

function adjustTitrant(delta) {
  const slider = document.getElementById('titrant-added');
  if(slider) {
    let val = parseFloat(slider.value) + delta;
    val = Math.max(0, Math.min(val, parseFloat(slider.max)));
    slider.value = val;
    titrationState.titrantAdded = val;
    updateTitrationUI();
  }
}

function addTitrantDrop() {
  const drop = document.getElementById('drop-falling');
  if (drop) {
    drop.style.animation = 'none';
    drop.offsetHeight;
    drop.style.animation = '';
  }
  adjustTitrant(0.05);
}

function resetTitration() {
  titrationState.titrantAdded = 0;
  titrationState.hasLoggedCompleted = false;
  const slider = document.getElementById('titrant-added');
  if(slider) slider.value = 0;
  updateTitrationUI();
  const res = document.getElementById('titration-result');
  if(res) res.style.display = 'none';
}

function updateTitrationUI() {
  const state = titrationState;
  const pH = calculatePH(state);
  const Veq = calculateEquivalenceVolume(state);

  const phDisp = document.getElementById('ph-display');
  if(phDisp) phDisp.textContent = pH.toFixed(2);
  
  const phBar = document.getElementById('ph-bar');
  if (phBar) phBar.style.width = Math.min(100, Math.max(0, (pH / 14) * 100)) + '%';

  const titrVal = document.getElementById('titrant-added-val');
  if(titrVal) titrVal.textContent = state.titrantAdded.toFixed(2) + ' mL';

  const buretteLiquid = document.getElementById('burette-liquid');
  if (buretteLiquid) {
    const slider = document.getElementById('titrant-added');
    const maxVal = slider ? parseFloat(slider.max) : 50;
    const pct = Math.max(10, 80 - (state.titrantAdded / maxVal) * 70);
    buretteLiquid.style.height = pct + '%';
  }

  const flaskLabel = document.getElementById('flask-label');
  if(flaskLabel) flaskLabel.textContent = state.analyteVol + ' mL ' + state.analyte;

  const flaskLiquid = document.getElementById('flask-liquid');
  const ind = TITRATION_DATA.indicators[state.indicator];
  if (ind && flaskLiquid) {
    if (pH < ind.low) {
      flaskLiquid.style.background = ind.acidColor === '#fff'
        ? 'linear-gradient(to top, rgba(248,250,252,0.15), rgba(248,250,252,0.08))'
        : `linear-gradient(to top, ${ind.acidColor}40, ${ind.acidColor}20)`;
      flaskLiquid.classList.toggle('pink', false);
    } else if (pH > ind.high) {
      flaskLiquid.style.background = `linear-gradient(to top, ${ind.baseColor}66, ${ind.baseColor}33)`;
      flaskLiquid.classList.toggle('pink', ind.baseColor === '#ec4899');
    } else {
      const t = (pH - ind.low) / (ind.high - ind.low);
      flaskLiquid.style.background = 'linear-gradient(to top, rgba(248,250,252,0.15), rgba(248,250,252,0.08))';
      flaskLiquid.classList.toggle('pink', t > 0.5 && ind.baseColor === '#ec4899');
    }
  }

  const nearEndpoint = Math.abs(state.titrantAdded - Veq) < 0.2;
  const resultDiv = document.getElementById('titration-result');
  const resultText = document.getElementById('titration-result-text');
  if (nearEndpoint && state.titrantAdded > 0 && resultDiv && resultText) {
    if (!state.hasLoggedCompleted) {
      state.hasLoggedCompleted = true;
      fetch('/api/log_event', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
              event_type: 'titration_complete',
              event_data: `${state.analyteVol}mL ${state.analyte} with ${state.titrant}`
          })
      }).catch(e => console.error('Failed to log titration', e));
    }
    resultDiv.style.display = 'block';
    const calcConc = (state.titrantConc * state.titrantAdded) / state.analyteVol;
    resultText.innerHTML =
      `Endpoint detected at <span class="result-highlight">${state.titrantAdded.toFixed(2)} mL</span> of titrant.<br>` +
      `Calculated analyte concentration: <span class="result-highlight">${calcConc.toFixed(3)} N</span><br>` +
      `Theoretical equivalence volume: <span class="result-highlight">${Veq.toFixed(2)} mL</span>`;
  } else if(resultDiv) {
    resultDiv.style.display = 'none';
  }

  updateGraph(state, pH, Veq);
}

function updateGraph(state, currentPH, Veq) {
  const svg = document.getElementById('ph-graph');
  if (!svg) return;
  const curvePath = document.getElementById('graph-curve');
  const point = document.getElementById('graph-point');

  const slider = document.getElementById('titrant-added');
  const maxVol = slider ? parseFloat(slider.max) : 50;
  const points = [];
  const steps = 80;
  for (let i = 0; i <= steps; i++) {
    const v = (i / steps) * maxVol;
    const ph = calculatePH({ ...state, titrantAdded: v });
    points.push({ x: 40 + (v / maxVol) * 340, y: 160 - (ph / 14) * 150 });
  }

  if(curvePath) {
    const d = points.map((p, i) => (i === 0 ? 'M' : 'L') + ` ${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join('');
    curvePath.setAttribute('d', d);
  }

  if(point) {
    const cx = 40 + (state.titrantAdded / maxVol) * 340;
    const cy = 160 - (currentPH / 14) * 150;
    point.setAttribute('cx', cx);
    point.setAttribute('cy', cy);
  }
}

