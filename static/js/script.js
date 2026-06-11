
// ============================================================
// DATA: Full reactions database (replaces PocketBase)
// ============================================================
let REACTIONS = [];

// Dynamically fetch reactions from the server database
fetch('/api/reactions')
  .then(res => res.json())
  .then(data => {
    REACTIONS = data.reactions || [];
    console.log("Successfully loaded " + REACTIONS.length + " reactions dynamically.");
    if (typeof updateCategoryDropdown === 'function') {
      updateCategoryDropdown();
    }
    if (typeof filterReactions === 'function') {
      filterReactions();
    } 
  })
  .catch(err => console.error("Error loading reactions from database:", err));
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
  const tabElem = document.getElementById('tab-' + tab);
  if (tabElem) tabElem.classList.add('active');
  // Update placeholder
  const input = document.getElementById('search-input');
  if (input) {
    if (tab === 'name') input.placeholder = '🔍  Search by reaction name...';
    else if (tab === 'reactant') input.placeholder = '🧪  Enter a reactant formula (e.g. C6H6, NaOH, HCl)...';
    else if (tab === 'product') input.placeholder = '✨  Enter a product formula (e.g. C6H5Br, CO2, H2O)...';
    input.value = '';
    input.focus();
  }
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
  if (btn) {
    btn.classList.remove('bg-surface-container', 'border-white/5', 'text-slate-400');
    btn.classList.add('bg-primary', 'text-on-primary', 'border-primary', 'shadow-[0_0_15px_rgba(6,182,212,0.3)]');
  }
  
  filterReactions();
}

function filterReactions() {
  const searchInput = document.getElementById('search-input');
  const classFilter = document.getElementById('class-filter');
  if (!searchInput || !classFilter) return;

  const q = searchInput.value.trim();
  const cls = classFilter.value;
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
  const liqMobile = document.getElementById('flask-liquid-mobile');
  
  // Update liquid color based on the chemical dropped
  const colorType = getChemicalType(el.formula || el.symbol);
  let targetColor = '#3b82f6'; // default blue
  
  if (colorType === 'acid') targetColor = '#e63b2e'; // red
  else if (colorType === 'base') targetColor = '#0055ff'; // deep blue
  else if (el.symbol === 'CH4') targetColor = '#ffcc00'; // yellow
  
  if (liq) {
    liq.style.fill = targetColor;
    liq.style.fillOpacity = Math.min(0.6 + (droppedElements.length * 0.15), 1);
    liq.classList.remove('opacity-0');
  }
  if (liqMobile) {
    liqMobile.style.fill = targetColor;
    liqMobile.style.fillOpacity = Math.min(0.6 + (droppedElements.length * 0.15), 1);
    liqMobile.classList.remove('opacity-0');
  }
  
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
  
  if (liq) liq.setAttribute('d', wavePath);
  if (liqMobile) liqMobile.setAttribute('d', wavePath);
  
  // Update meniscus position dynamically
  const rx = (w2 - w1) / 2;
  const meniscus = document.getElementById('liquid-meniscus');
  const meniscusMobile = document.getElementById('liquid-meniscus-mobile');
  if (meniscus) {
    meniscus.setAttribute('cy', yBase);
    meniscus.setAttribute('rx', rx);
  }
  if (meniscusMobile) {
    meniscusMobile.setAttribute('cy', yBase);
    meniscusMobile.setAttribute('rx', rx);
  }
  
  // Start bubbles if it's the first element
  if (droppedElements.length === 1) {
    startBubbles(0);
    startBubbles('mobile');
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
  if (liq) {
    liq.style.fillOpacity = 0.3;
    liq.style.fill = '#3b82f6';
    liq.setAttribute('d', 'M 62 130 L 70 125 L 80 130 L 90 125 L 100 130 L 110 125 L 120 130 L 130 125 L 138 130 L 160 170 L 40 170 Z');
    liq.classList.remove('success', 'error', 'partial', 'metal', 'nonmetal', 'acid', 'base', 'organic');
    liq.classList.add('opacity-0');
  }
  
  const liqMobile = document.getElementById('flask-liquid-mobile');
  if (liqMobile) {
    liqMobile.style.fillOpacity = 0.3;
    liqMobile.style.fill = '#3b82f6';
    liqMobile.setAttribute('d', 'M 62 130 L 70 125 L 80 130 L 90 125 L 100 130 L 110 125 L 120 130 L 130 125 L 138 130 L 160 170 L 40 170 Z');
    liqMobile.classList.remove('success', 'error', 'partial', 'metal', 'nonmetal', 'acid', 'base', 'organic');
    liqMobile.classList.add('opacity-0');
  }
  
  const b0 = document.getElementById(`bubbles-container-0`);
  if (b0) b0.innerHTML = '';
  const bm = document.getElementById(`bubbles-container-mobile`);
  if (bm) bm.innerHTML = '';
  
  const g0 = document.getElementById(`reaction-glow-0`);
  if (g0) g0.classList.add('opacity-0');
  const gm = document.getElementById(`reaction-glow-mobile`);
  if (gm) gm.classList.add('opacity-0');
  
  // Reset meniscus
  const meniscus = document.getElementById('liquid-meniscus');
  const meniscusMobile = document.getElementById('liquid-meniscus-mobile');
  if (meniscus) {
    meniscus.setAttribute('cy', 130);
    meniscus.setAttribute('rx', 38);
  }
  if (meniscusMobile) {
    meniscusMobile.setAttribute('cy', 130);
    meniscusMobile.setAttribute('rx', 38);
  }
  
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
  const g0 = document.getElementById('reaction-glow-0');
  if (g0) g0.classList.remove('opacity-0');
  const gm = document.getElementById('reaction-glow-mobile');
  if (gm) gm.classList.remove('opacity-0');
  
  const liq = document.getElementById('flask-liquid-0');
  if (liq) liq.style.fill = '#4cd7f6';
  const liqMobile = document.getElementById('flask-liquid-mobile');
  if (liqMobile) liqMobile.style.fill = '#4cd7f6';
  
  // Update Gauges
  const isExothermic = rxn.explanation.toLowerCase().includes('exothermic') || rxn.explanation.toLowerCase().includes('releases heat');
  const finalTemp = isExothermic ? 45.8 : 22.1;
  const finalPH = rxn.products.includes('HCl') || rxn.products.includes('H2SO4') ? 1.5 : 7.2;
  
  updateGauges(finalTemp, finalPH, 94.5);
  
  if (typeof window.render3D === 'function') {
      const primaryProduct = rxn.products.split(',')[0].trim();
      window.render3D(primaryProduct);
  }
  
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
  const liqMobile = document.getElementById('flask-liquid-mobile');
  const oldFill = liq ? liq.style.fill : null;
  const oldFillMobile = liqMobile ? liqMobile.style.fill : null;
  if (liq) liq.style.fill = '#ff4400';
  if (liqMobile) liqMobile.style.fill = '#ff4400';

  setTimeout(() => {
    if (blast.parentNode) blast.remove();
    centerArea.classList.remove('animate-blast-shake');
    if (liq && document.body.contains(liq)) {
        liq.style.fill = oldFill;
    }
    if (liqMobile && document.body.contains(liqMobile)) {
        liqMobile.style.fill = oldFillMobile;
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


// ============================================================
// AUDIO SYNTHESIS ENGINE (Web Audio API)
// ============================================================
let audioCtx = null;
function playLabSound(type) {
  try {
    if (!audioCtx) {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (audioCtx.state === 'suspended') {
      audioCtx.resume();
    }
    const osc = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();
    osc.connect(gainNode);
    gainNode.connect(audioCtx.destination);
    
    if (type === 'pour') {
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(800, audioCtx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(150, audioCtx.currentTime + 0.5);
      gainNode.gain.setValueAtTime(0.15, audioCtx.currentTime);
      gainNode.gain.linearRampToValueAtTime(0, audioCtx.currentTime + 0.5);
      osc.start();
      osc.stop(audioCtx.currentTime + 0.5);
    } else if (type === 'bubble') {
      osc.type = 'sine';
      osc.frequency.setValueAtTime(Math.random() * 500 + 400, audioCtx.currentTime);
      gainNode.gain.setValueAtTime(0.08, audioCtx.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.1);
      osc.start();
      osc.stop(audioCtx.currentTime + 0.1);
    } else if (type === 'explosion') {
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(180, audioCtx.currentTime);
      osc.frequency.linearRampToValueAtTime(40, audioCtx.currentTime + 0.4);
      gainNode.gain.setValueAtTime(0.25, audioCtx.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.45);
      osc.start();
      osc.stop(audioCtx.currentTime + 0.45);
    }
  } catch (e) {
    console.log("Audio not supported or interaction deferred:", e);
  }
}

// Modify existing drop to play sounds
const originalHandleDrop = window.handleDrop;
window.handleDrop = function(e) {
  playLabSound('pour');
  setTimeout(() => playLabSound('bubble'), 300);
  if (originalHandleDrop) {
    originalHandleDrop(e);
  }
};


// ============================================================
// EQUIPMENT ASSEMBLY & SWAPPING
// ============================================================
let currentEquipment = 'flask';
window.setEquipment = function(type) {
  currentEquipment = type;
  document.querySelectorAll('.equip-btn').forEach(btn => {
    if (btn.id === `equip-btn-${type}`) {
      btn.classList.add('active', 'bg-primary', 'text-on-primary');
      btn.classList.remove('text-slate-400');
    } else {
      btn.classList.remove('active', 'bg-primary', 'text-on-primary');
      btn.classList.add('text-slate-400');
    }
  });
  
  const status = document.getElementById('lab-status');
  if (status) status.textContent = `EQUIPMENT MIGRATED TO: ${type.toUpperCase()}`;
  playLabSound('pour');
};


// ============================================================
// SIDEBAR TOGGLE & AI SCIENTIST ENGINE
// ============================================================
window.setRightTab = function(tab) {
  const viewTelemetry = document.getElementById('right-view-telemetry');
  const viewAI = document.getElementById('right-view-ai');
  const tabTelemetry = document.getElementById('right-tab-telemetry');
  const tabAI = document.getElementById('right-tab-ai');
  
  if (tab === 'telemetry') {
    if(viewTelemetry) viewTelemetry.classList.remove('hidden');
    if(viewAI) viewAI.classList.add('hidden');
    if(tabTelemetry) tabTelemetry.className = "flex-1 text-center py-1.5 rounded-lg text-[10px] font-black uppercase tracking-wider bg-cyan-950/40 text-cyan-400";
    if(tabAI) tabAI.className = "flex-1 text-center py-1.5 rounded-lg text-[10px] font-black uppercase tracking-wider text-slate-400 hover:text-white";
  } else {
    if(viewTelemetry) viewTelemetry.classList.add('hidden');
    if(viewAI) viewAI.classList.remove('hidden');
    if(tabTelemetry) tabTelemetry.className = "flex-1 text-center py-1.5 rounded-lg text-[10px] font-black uppercase tracking-wider text-slate-400 hover:text-white";
    if(tabAI) tabAI.className = "flex-1 text-center py-1.5 rounded-lg text-[10px] font-black uppercase tracking-wider bg-cyan-950/40 text-cyan-400";
  }
};

function appendChatMessage(sender, text) {
  const log = document.getElementById('ai-chat-log');
  if(!log) return;
  const div = document.createElement('div');
  div.className = `p-2 rounded-xl text-[10px] leading-relaxed max-w-[90%] ${sender === 'AI' ? 'bg-cyan-950/40 text-cyan-300 border border-cyan-500/10 mr-auto' : 'bg-slate-800 text-slate-100 ml-auto'}`;
  div.innerHTML = `<strong>${sender}:</strong> ${text}`;
  log.appendChild(div);
  log.scrollTop = log.scrollHeight;
}

let currentAIReport = null;

window.triggerAIQuickAction = async function(action) {
  const log = document.getElementById('ai-chat-log');
  if(log && log.querySelector('.italic')) log.innerHTML = '';
  
  appendChatMessage('System', `Requesting AI analysis: ${action}...`);
  
  const formulas = droppedElements.map(el => el.symbol || el.formula);
  const temp = parseFloat(document.getElementById('temp-val')?.textContent || '24.5');
  const ph = parseFloat(document.getElementById('ph-val')?.textContent || '7.00');
  const stability = parseFloat(document.getElementById('stability-val')?.textContent || '100');

  try {
    const res = await fetch('/api/ai/scientist', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_query: action,
        experiment_name: activeGuidedExp || 'Sandbox',
        chemicals_in_flask: formulas,
        telemetry: { ph, temp, stability }
      })
    });
    if(!res.ok) throw new Error("API call failed");
    const data = await res.json();
    
    if (action === 'Report') {
      currentAIReport = data.lab_report;
      appendChatMessage('AI', 'Experiment report successfully generated! Initiating PDF download...');
      downloadPDFReport(data.lab_report);
    } else if (action === 'Viva') {
      appendChatMessage('AI', `Generated Laboratory Viva Questions:<br>${data.viva_questions.map((q, i) => `${i+1}. ${q}`).join('<br>')}`);
    } else if (action === 'Predict') {
      appendChatMessage('AI', `Predicted reaction output products: <strong>${data.predicted_product}</strong>`);
    } else if (action === 'Suggest') {
      appendChatMessage('AI', `AI Chemist Suggestion: ${data.suggested_next}`);
    } else {
      appendChatMessage('AI', data.response);
    }
  } catch (e) {
    console.error("AI Error:", e);
    appendChatMessage('AI', 'Sorry, I encountered an error checking telemetry logs. Please try again.');
  }
};

window.submitAIChat = async function() {
  const input = document.getElementById('ai-chat-input');
  if(!input || !input.value.trim()) return;
  const query = input.value.trim();
  input.value = '';
  
  const log = document.getElementById('ai-chat-log');
  if(log && log.querySelector('.italic')) log.innerHTML = '';
  
  appendChatMessage('Student', query);
  
  const formulas = droppedElements.map(el => el.symbol || el.formula);
  const temp = parseFloat(document.getElementById('temp-val')?.textContent || '24.5');
  const ph = parseFloat(document.getElementById('ph-val')?.textContent || '7.00');
  const stability = parseFloat(document.getElementById('stability-val')?.textContent || '100');

  try {
    const res = await fetch('/api/ai/scientist', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_query: query,
        experiment_name: activeGuidedExp || 'Sandbox',
        chemicals_in_flask: formulas,
        telemetry: { ph, temp, stability }
      })
    });
    if(!res.ok) throw new Error("API call failed");
    const data = await res.json();
    appendChatMessage('AI', data.response);
  } catch (e) {
    appendChatMessage('AI', 'Sorry, I lost contact with my core knowledge base. Please try again.');
  }
};


// ============================================================
// PDF LAB REPORT GENERATOR
// ============================================================
function downloadPDFReport(report) {
  if(!report || !window.jspdf) {
    alert("No report generated yet. Click 'Generate Lab Report' first.");
    return;
  }
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF();
  
  doc.setFont("helvetica", "bold");
  doc.setFontSize(22);
  doc.setTextColor(6, 182, 212);
  doc.text("ChemLove Laboratory Report", 20, 25);
  
  doc.setFontSize(10);
  doc.setTextColor(100);
  doc.text(`Generated on: ${new Date().toLocaleString()}`, 20, 32);
  doc.line(20, 35, 190, 35);
  
  let y = 45;
  const sections = [
    { title: "OBJECTIVE", content: report.objective },
    { title: "PROCEDURE", content: report.procedure },
    { title: "OBSERVATIONS", content: report.observations },
    { title: "CALCULATIONS", content: report.calculations },
    { title: "RESULT", content: report.result },
    { title: "CONCLUSION", content: report.conclusion }
  ];
  
  sections.forEach(sec => {
    doc.setFont("helvetica", "bold");
    doc.setFontSize(12);
    doc.setTextColor(14, 20, 22);
    doc.text(sec.title, 20, y);
    y += 6;
    
    doc.setFont("helvetica", "normal");
    doc.setFontSize(10);
    doc.setTextColor(80);
    const splitText = doc.splitTextToSize(sec.content || "N/A", 170);
    doc.text(splitText, 20, y);
    y += (splitText.length * 5) + 8;
  });
  
  doc.save("laboratory_report.pdf");
}


// ============================================================
// GUIDED EXPERIMENTS WORKBENCH
// ============================================================
let activeGuidedExp = null;
let guidedStepIndex = 0;
let guidedExperiments = {
  oxygen: {
    title: "Preparation of Oxygen",
    steps: [
      { desc: "Add solid KClO3 reagent into the flask", check: () => droppedElements.some(el => el.symbol === 'KClO3') },
      { desc: "Assemble Bunsen Burner heating device", check: () => currentEquipment === 'burner' },
      { desc: "Apply heat to trigger chemical decomposition", check: () => {
          const flame = document.getElementById('burner-flame');
          return flame && document.getElementById('burner-setup').classList.contains('opacity-100');
        }
      },
      { desc: "Observe oxygen bubbles forming in displacement", check: () => true }
    ],
    xp: 50
  },
  neutralization: {
    title: "Acid-Base Synthesis",
    steps: [
      { desc: "Dispense hydrochloric acid (HCl) into simulator", check: () => droppedElements.some(el => el.symbol === 'HCl') },
      { desc: "Slowly add neutralizing base Sodium Hydroxide (NaOH)", check: () => droppedElements.some(el => el.symbol === 'NaOH') },
      { desc: "Equilibrate solution pH exactly to 7.00", check: () => {
          const ph = parseFloat(document.getElementById('ph-val')?.textContent || '7.00');
          return Math.abs(ph - 7.00) <= 0.1;
        }
      }
    ],
    xp: 50
  },
  displacement: {
    title: "Displacement Reaction",
    steps: [
      { desc: "Dispense blue Copper Sulfate (CuSO4) solution", check: () => droppedElements.some(el => el.symbol === 'CuSO4') },
      { desc: "Add reactive metallic Iron (Fe) strips", check: () => droppedElements.some(el => el.symbol === 'Fe') },
      { desc: "Observe red metallic copper forming and color displacement", check: () => true }
    ],
    xp: 50
  }
};

window.startGuidedExperiment = function(id) {
  activeGuidedExp = id;
  guidedStepIndex = 0;
  const exp = guidedExperiments[id];
  document.getElementById('guided-title').textContent = exp.title;
  
  document.querySelectorAll('.guided-exp-btn').forEach(btn => {
    if (btn.getAttribute('onclick').includes(`'${id}'`)) {
      btn.className = "guided-exp-btn w-full text-left p-3 rounded-xl border border-cyan-500/20 bg-cyan-950/20 text-cyan-400 transition-all hover:bg-cyan-950/30";
    } else {
      btn.className = "guided-exp-btn w-full text-left p-3 rounded-xl border border-white/5 bg-surface-container text-slate-300 transition-all hover:bg-white/5";
    }
  });

  window.renderGuidedSteps();
  window.resetGuidedApparatus();
};

window.renderGuidedSteps = function() {
  const exp = guidedExperiments[activeGuidedExp];
  const list = document.getElementById('guided-steps-list');
  if(!list) return;
  list.innerHTML = exp.steps.map((step, idx) => {
    const isCompleted = idx < guidedStepIndex;
    const isActive = idx === guidedStepIndex;
    return `
      <div class="flex items-start gap-3 p-3 rounded-xl border ${isCompleted ? 'border-emerald-500/20 bg-emerald-950/10 text-emerald-300' : isActive ? 'border-cyan-500/20 bg-cyan-950/10 text-cyan-300' : 'border-white/5 bg-surface-container text-slate-500'}">
        <span class="material-symbols-outlined text-sm mt-0.5">${isCompleted ? 'check_circle' : 'circle'}</span>
        <div class="text-[10px] font-bold uppercase tracking-wider">${step.desc}</div>
      </div>
    `;
  }).join('');

  const pct = Math.round((guidedStepIndex / exp.steps.length) * 100);
  document.getElementById('guided-progress-val').textContent = `${pct}%`;
  document.getElementById('guided-progress-bar').style.width = `${pct}%`;
  
  const nextBtn = document.getElementById('guided-next-step-btn');
  const claimBtn = document.getElementById('guided-claim-reward-btn');
  
  if (guidedStepIndex >= exp.steps.length) {
    if(nextBtn) nextBtn.disabled = true;
    if(claimBtn) {
      claimBtn.disabled = false;
      claimBtn.className = "w-full py-3 bg-cyan-500 text-[#001f26] font-black text-xs uppercase tracking-widest rounded-xl transition-all border border-cyan-400/20 flex items-center justify-center gap-1.5 cursor-pointer shadow-lg active:scale-95";
    }
  } else {
    if(nextBtn) nextBtn.disabled = false;
    if(claimBtn) {
      claimBtn.disabled = true;
      claimBtn.className = "w-full py-3 bg-slate-800 text-slate-500 font-black text-xs uppercase tracking-widest rounded-xl transition-all border border-white/5 flex items-center justify-center gap-1.5 cursor-not-allowed";
    }
  }
};

window.guidedNextStep = function() {
  const exp = guidedExperiments[activeGuidedExp];
  const step = exp.steps[guidedStepIndex];
  
  if (step.check()) {
    guidedStepIndex++;
    window.renderGuidedSteps();
    playLabSound('pour');
    
    if (activeGuidedExp === 'oxygen' && guidedStepIndex === 3) {
      document.getElementById('burner-setup').classList.remove('opacity-0');
      document.getElementById('burner-setup').classList.add('opacity-100');
      document.getElementById('guided-liquid').classList.remove('opacity-0');
      document.getElementById('guided-status-badge').textContent = "HEATING ACTIVE - OXYGEN EVOLUTION";
      playLabSound('explosion');
    }
  } else {
    alert(`Please complete step requirements: "${step.desc}"`);
  }
};

window.guidedPrevStep = function() {
  if(guidedStepIndex > 0) {
    guidedStepIndex--;
    window.renderGuidedSteps();
  }
};

window.resetGuidedApparatus = function() {
  droppedElements = [];
  currentEquipment = 'flask';
  const flameSetup = document.getElementById('burner-setup');
  if(flameSetup) flameSetup.className = "opacity-0 transition-opacity";
  const guidedLiq = document.getElementById('guided-liquid');
  if(guidedLiq) guidedLiq.classList.add('opacity-0');
  const badge = document.getElementById('guided-status-badge');
  if(badge) badge.textContent = "Awaiting Setup";
};

window.claimGuidedReward = async function() {
  const exp = guidedExperiments[activeGuidedExp];
  try {
    const res = await fetch('/api/student/lab/reward', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ xp: exp.xp, mission: exp.title })
    });
    const data = await res.json();
    if(data.ok) {
      if(typeof confetti === 'function') {
        confetti({ particleCount: 100, spread: 70, origin: { y: 0.6 } });
      }
      alert(`Congratulations! You completed ${exp.title} and earned +${exp.xp} XP!`);
      
      await fetch('/api/student/lab/attempt', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          experiment_name: exp.title,
          mode: 'guided',
          duration_seconds: 180,
          mistakes_count: 0,
          accuracy_percentage: 100
        })
      });
      
      switchLabTab('lab');
    }
  } catch (e) {
    console.error(e);
  }
};


// ============================================================
// CHEMISTRY MISSIONS ENGINE
// ============================================================
let activeMission = null;
let missionStartTime = 0;
let missionMistakes = 0;

window.startMission = function(id) {
  activeMission = id;
  missionStartTime = Date.now();
  missionMistakes = 0;
  
  const container = document.getElementById('mission-exec-container');
  const title = document.getElementById('mission-exec-title');
  const content = document.getElementById('mission-exec-content');
  
  container.classList.remove('hidden');
  
  if (id === 'neutralize') {
    title.textContent = "Neutralization Mission";
    content.innerHTML = `
      <p>Setup: The flask contains 10 mL of HCl Acid. Add NaOH base from the shelf drop-zone until the pH reaches exactly 7.00 &plusmn; 0.1.</p>
      <button onclick="launchNeutralizeMission()" class="bg-primary hover:bg-cyan-300 text-[#001f26] font-bold text-[10px] uppercase px-4 py-2 rounded-xl transition-all">Begin Simulation</button>
    `;
  } else if (id === 'identify') {
    title.textContent = "Unknown Compound Identifier";
    content.innerHTML = `
      <p>Setup: A mystery chemical tag 'X' is in the flask. It exhibits pH 12.0 and reacts with acid releasing significant heat.</p>
      <p class="font-bold">What is compound X?</p>
      <div class="grid grid-cols-2 gap-2 mt-2">
        <button onclick="submitIdentifyAnswer('HCl')" class="bg-slate-800 text-xs text-white p-2.5 rounded-lg border border-white/5 hover:bg-slate-700">HCl</button>
        <button onclick="submitIdentifyAnswer('NaOH')" class="bg-slate-800 text-xs text-white p-2.5 rounded-lg border border-white/5 hover:bg-slate-700">NaOH</button>
        <button onclick="submitIdentifyAnswer('CH4')" class="bg-slate-800 text-xs text-white p-2.5 rounded-lg border border-white/5 hover:bg-slate-700">CH4</button>
        <button onclick="submitIdentifyAnswer('KClO3')" class="bg-slate-800 text-xs text-white p-2.5 rounded-lg border border-white/5 hover:bg-slate-700">KClO3</button>
      </div>
    `;
  } else if (id === 'titrate_mission') {
    title.textContent = "Precision Titration Mission";
    content.innerHTML = `
      <p>Setup: Adjust the Titration burette setup to dispense NaOH into 20 mL HCl. Tap on burette or use the slider, and stop EXACTLY at the Phenolphthalein color endpoint (pH 8.3).</p>
      <button onclick="launchTitrationMission()" class="bg-primary hover:bg-cyan-300 text-[#001f26] font-bold text-[10px] uppercase px-4 py-2 rounded-xl transition-all">Begin Titration</button>
    `;
  }
};

window.launchNeutralizeMission = function() {
  switchLabTab('lab');
  resetLab();
  // Simulate drop
  droppedElements.push({symbol: "HCl", name: "Hydrochloric Acid", formula: "HCl"});
  updateLabUIOnDrop({symbol: "HCl", name: "Hydrochloric Acid", formula: "HCl"});
  addLabLog("MISSION START: REACH pH 7.00", "text-cyan-400 font-bold");
};

window.launchTitrationMission = function() {
  switchLabTab('titration');
  resetTitration();
  addLabLog("MISSION START: REACH ENDPOINT pH 8.3", "text-cyan-400 font-bold");
};

window.submitIdentifyAnswer = async function(ans) {
  if (ans === 'NaOH') {
    alert("Correct! Compound X is NaOH (a strong base).");
    await completeMission('Identify Unknown', 60);
  } else {
    missionMistakes++;
    alert("Incorrect! Try analyzing the chemical properties again.");
  }
};

async function completeMission(name, xp) {
  const duration = Math.round((Date.now() - missionStartTime) / 1000);
  const accuracy = Math.max(0, 100 - (missionMistakes * 20));
  
  try {
    const res = await fetch('/api/student/lab/reward', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ xp: xp, mission: name })
    });
    const data = await res.json();
    if(data.ok) {
      if(typeof confetti === 'function') confetti({ particleCount: 120, spread: 80 });
      
      await fetch('/api/student/lab/attempt', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          experiment_name: name,
          mode: 'mission',
          duration_seconds: duration,
          mistakes_count: missionMistakes,
          accuracy_percentage: accuracy
        })
      });
      
      window.abortMission();
      switchLabTab('missions');
    }
  } catch (e) {
    console.error(e);
  }
}

window.abortMission = function() {
  activeMission = null;
  const container = document.getElementById('mission-exec-container');
  if(container) container.classList.add('hidden');
};


// ============================================================
// SPECTROSCOPY LAB GRAPH ENGINE
// ============================================================
let specData = {
  Methane: {
    ir: [
      { x: 50, y: 10 }, { x: 100, y: 10 }, { x: 150, y: 80 }, { x: 170, y: 10 },
      { x: 250, y: 10 }, { x: 300, y: 90 }, { x: 320, y: 10 }, { x: 400, y: 10 }
    ],
    nmr: [
      { x: 350, y: 120, label: "Singlet (CH4, 0.9 ppm)" }
    ]
  },
  Benzene: {
    ir: [
      { x: 50, y: 15 }, { x: 120, y: 15 }, { x: 180, y: 95 }, { x: 200, y: 15 },
      { x: 280, y: 15 }, { x: 330, y: 85 }, { x: 350, y: 15 }, { x: 400, y: 15 }
    ],
    nmr: [
      { x: 100, y: 130, label: "Aromatic Singlet (C6H6, 7.27 ppm)" }
    ]
  },
  Ethanol: {
    ir: [
      { x: 50, y: 10 }, { x: 80, y: 90 }, { x: 120, y: 10 }, { x: 200, y: 10 },
      { x: 280, y: 85 }, { x: 310, y: 10 }, { x: 400, y: 10 }
    ],
    nmr: [
      { x: 300, y: 120, label: "Triplet (CH3, 1.2 ppm)" },
      { x: 200, y: 90, label: "Quartet (CH2, 3.7 ppm)" },
      { x: 100, y: 50, label: "Singlet (OH, 5.0 ppm)" }
    ]
  },
  Water: {
    ir: [
      { x: 50, y: 20 }, { x: 100, y: 98 }, { x: 180, y: 20 },
      { x: 300, y: 90 }, { x: 330, y: 20 }, { x: 400, y: 20 }
    ],
    nmr: [
      { x: 250, y: 130, label: "Liquid peak (H2O, 4.7 ppm)" }
    ]
  }
};

window.showSpectra = function(compound) {
  document.querySelectorAll('.spec-compound-btn').forEach(btn => {
    if (btn.textContent.includes(compound)) {
      btn.className = "spec-compound-btn active w-full p-3 rounded-lg border border-cyan-500/20 bg-cyan-950/20 text-cyan-400 font-bold text-xs text-left uppercase";
    } else {
      btn.className = "spec-compound-btn w-full p-3 rounded-lg border border-white/5 bg-surface text-slate-300 font-bold text-xs text-left uppercase hover:bg-white/5";
    }
  });

  const data = specData[compound];
  const irContainer = document.getElementById('ir-spectra-container');
  const nmrContainer = document.getElementById('nmr-spectra-container');
  
  if (irContainer && data) {
    irContainer.innerHTML = `
      <svg class="w-full h-full" viewBox="0 0 450 120">
        <line x1="30" y1="10" x2="30" y2="100" stroke="rgba(255,255,255,0.2)" stroke-width="1.5"/>
        <line x1="30" y1="100" x2="430" y2="100" stroke="rgba(255,255,255,0.2)" stroke-width="1.5"/>
        <text x="5" y="15" fill="#a0aec0" font-size="8">100%T</text>
        <text x="5" y="98" fill="#a0aec0" font-size="8">0%T</text>
        <polyline fill="none" stroke="#4cd7f6" stroke-width="2" points="${data.ir.map(p => `${p.x + 30},${100 - p.y}`).join(' ')}" />
      </svg>
    `;
  }

  if (nmrContainer && data) {
    let nmrBars = '';
    data.nmr.forEach(bar => {
      nmrBars += `
        <line x1="${bar.x}" y1="100" x2="${bar.x}" y2="${100 - bar.y}" stroke="#ffb0cd" stroke-width="3.5" />
        <text x="${bar.x - 10}" y="${80 - bar.y}" fill="#ffb0cd" font-size="7" font-weight="bold">${bar.label}</text>
      `;
    });
    nmrContainer.innerHTML = `
      <svg class="w-full h-full" viewBox="0 0 450 120">
        <line x1="30" y1="10" x2="30" y2="100" stroke="rgba(255,255,255,0.2)" stroke-width="1.5"/>
        <line x1="30" y1="100" x2="430" y2="100" stroke="rgba(255,255,255,0.2)" stroke-width="1.5"/>
        <text x="360" y="112" fill="#a0aec0" font-size="7">TMS (0 ppm)</text>
        ${nmrBars}
      </svg>
    `;
  }
};


// ============================================================
// ORGANIC REACTION SIMULATOR ANIMATOR
// ============================================================
let currentMechanism = 'SN2';

window.playOrganicSim = function(mechanism) {
  currentMechanism = mechanism;
  document.querySelectorAll('.org-btn').forEach(btn => {
    if (btn.getAttribute('onclick').includes(`'${mechanism}'`)) {
      btn.className = "org-btn active w-full p-3 rounded-lg border border-cyan-500/20 bg-cyan-950/20 text-cyan-400 font-bold text-xs text-left uppercase";
    } else {
      btn.className = "org-btn w-full p-3 rounded-lg border border-white/5 bg-surface text-slate-300 font-bold text-xs text-left uppercase hover:bg-white/5";
    }
  });
  
  const title = document.getElementById('organic-title');
  const desc = document.getElementById('organic-desc');
  
  if (mechanism === 'SN2') {
    title.textContent = "SN2 Reaction Pathway";
    desc.textContent = "In an SN2 mechanism, the nucleophile attacks the substrate from the backside, exactly 180 degrees away from the leaving group, causing a transition state with five-coordinate carbon and inversion of configuration.";
  } else if (mechanism === 'SN1') {
    title.textContent = "SN1 Substitution Mechanism";
    desc.textContent = "SN1 is a two-step nucleophilic substitution. First, the leaving group departs, forming a carbocation intermediate. Then, the nucleophile attacks from either side, resulting in racemization.";
  } else if (mechanism === 'E2') {
    title.textContent = "E2 Elimination Mechanism";
    desc.textContent = "E2 is a concerted elimination reaction where a strong base pulls a proton from the beta-carbon while the leaving group departs, forming a double bond.";
  } else if (mechanism === 'Esterification') {
    title.textContent = "Fischer Esterification Mechanism";
    desc.textContent = "Reaction of carboxylic acid and alcohol in acid catalyst to form ester and water. The acid protonates the carbonyl carbon, activating it to nucleophilic attack by alcohol.";
  }
  
  window.triggerOrganicAnimation();
};

window.triggerOrganicAnimation = function() {
  const stage = document.getElementById('organic-stage');
  if(!stage) return;
  
  if (currentMechanism === 'SN2') {
    stage.innerHTML = `
      <svg class="w-full h-full" viewBox="0 0 400 160">
        <circle cx="200" cy="80" r="16" fill="#4a5568" />
        <text x="196" y="84" fill="white" font-size="10" font-weight="bold">C</text>
        <g id="leaving-group">
          <line x1="200" y1="80" x2="260" y2="80" stroke="white" stroke-width="2" />
          <circle cx="260" cy="80" r="14" fill="#e53e3e" />
          <text x="254" y="84" fill="white" font-size="10" font-weight="bold">Cl</text>
          <animateTransform attributeName="transform" type="translate" from="0,0" to="100,0" dur="2s" fill="freeze" begin="1s" />
          <animate attributeName="opacity" from="1" to="0" dur="2s" fill="freeze" begin="1.5s" />
        </g>
        <g id="nucleophile">
          <circle cx="60" cy="80" r="14" fill="#3182ce" />
          <text x="50" y="84" fill="white" font-size="10" font-weight="bold">OH-</text>
          <animateTransform attributeName="transform" type="translate" from="0,0" to="124,0" dur="1.2s" fill="freeze" />
        </g>
      </svg>
    `;
  } else {
    stage.innerHTML = `
      <svg class="w-full h-full" viewBox="0 0 400 160">
        <g id="carbocation">
          <circle cx="200" cy="80" r="18" fill="#4cd7f6" />
          <text x="194" y="84" fill="#001f26" font-size="11" font-weight="black">C+</text>
          <circle cx="120" cy="80" r="12" fill="#3182ce" />
          <text x="110" y="84" fill="white" font-size="8" font-weight="bold">Nu-</text>
          <animateTransform attributeName="transform" type="translate" from="-200,0" to="0,0" dur="1s" fill="freeze" />
        </g>
      </svg>
    `;
  }
};


// ============================================================
// INTERACTIVE PERIODIC TABLE
// ============================================================
let elementsData = {
  1: { name: "Hydrogen", symbol: "H", num: 1, mass: 1.008, conf: "1s1", uses: "Rocket fuel, ammonia synthesis", rxn: "2H2 + O2 -> 2H2O" },
  2: { name: "Helium", symbol: "He", num: 2, mass: 4.003, conf: "1s2", uses: "Balloons, cooling superconducting magnets", rxn: "Noble gas (inert)" },
  3: { name: "Lithium", symbol: "Li", num: 3, mass: 6.94, conf: "[He] 2s1", uses: "Batteries, glass, psychiatric meds", rxn: "2Li + 2H2O -> 2LiOH + H2" },
  4: { name: "Beryllium", symbol: "Be", num: 4, mass: 9.012, conf: "[He] 2s2", uses: "Aerospace parts, X-ray tubes", rxn: "2Be + O2 -> 2BeO" },
  5: { name: "Boron", symbol: "B", num: 5, mass: 10.81, conf: "[He] 2s2 2p1", uses: "Fiberglass, borosilicate glass", rxn: "4B + 3O2 -> 2B2O3" },
  6: { name: "Carbon", symbol: "C", num: 6, mass: 12.011, conf: "[He] 2s2 2p2", uses: "Steel alloy, organic compounds", rxn: "C + O2 -> CO2" },
  7: { name: "Nitrogen", symbol: "N", num: 7, mass: 14.007, conf: "[He] 2s2 2p3", uses: "Fertilizers, liquid coolant", rxn: "N2 + 3H2 -> 2NH3" },
  8: { name: "Oxygen", symbol: "O", num: 8, mass: 15.999, conf: "[He] 2s2 2p4", uses: "Respiration, steel manufacture", rxn: "Combustion agent" },
  9: { name: "Fluorine", symbol: "F", num: 9, mass: 18.998, conf: "[He] 2s2 2p5", uses: "Uranium processing, toothpaste", rxn: "H2 + F2 -> 2HF" },
  10: { name: "Neon", symbol: "Ne", num: 10, mass: 20.180, conf: "[He] 2s2 2p6", uses: "Neon signs, advertising lights", rxn: "Noble gas (inert)" },
  11: { name: "Sodium", symbol: "Na", num: 11, mass: 22.990, conf: "[Ne] 3s1", uses: "Street lights, heat exchanger", rxn: "2Na + Cl2 -> 2NaCl" },
  12: { name: "Magnesium", symbol: "Mg", num: 12, mass: 24.305, conf: "[Ne] 3s2", uses: "Aircraft alloys, flares, medicine", rxn: "Mg + 2HCl -> MgCl2 + H2" },
  13: { name: "Aluminium", symbol: "Al", num: 13, mass: 26.982, conf: "[Ne] 3s2 3p1", uses: "Cans, foil, kitchen utensils", rxn: "4Al + 3O2 -> 2Al2O3" },
  14: { name: "Silicon", symbol: "Si", num: 14, mass: 28.085, conf: "[Ne] 3s2 3p2", uses: "Microchips, solar cells, glass", rxn: "Si + O2 -> SiO2" },
  15: { name: "Phosphorus", symbol: "P", num: 15, mass: 30.974, conf: "[Ne] 3s2 3p3", uses: "Matches, fertilizers, detergents", rxn: "P4 + 5O2 -> P4O10" },
  16: { name: "Sulfur", symbol: "S", num: 16, mass: 32.06, conf: "[Ne] 3s2 3p4", uses: "Sulfuric acid, gunpowder", rxn: "S + O2 -> SO2" },
  17: { name: "Chlorine", symbol: "Cl", num: 17, mass: 35.45, conf: "[Ne] 3s2 3p5", uses: "Water purification, disinfectants", rxn: "2Na + Cl2 -> 2NaCl" },
  18: { name: "Argon", symbol: "Ar", num: 18, mass: 39.948, conf: "[Ne] 3s2 3p6", uses: "Incandescent lamps, welding shields", rxn: "Noble gas (inert)" },
  19: { name: "Potassium", symbol: "K", num: 19, mass: 39.098, conf: "[Ar] 4s1", uses: "Potash fertilizers, liquid soaps", rxn: "2K + 2H2O -> 2KOH + H2" },
  20: { name: "Calcium", symbol: "Ca", num: 20, mass: 40.078, conf: "[Ar] 4s2", uses: "Cement, plaster, calcium alloys", rxn: "Ca + 2H2O -> Ca(OH)2 + H2" }
};

window.initPeriodicTable = function() {
  const grid = document.getElementById('ptable-grid');
  if(!grid) return;
  grid.innerHTML = '';
  
  for (let num = 1; num <= 20; num++) {
    const el = elementsData[num];
    const card = document.createElement('button');
    card.onclick = () => window.showElementDetails(num);
    card.className = "bg-surface-container border border-white/5 p-2 rounded-xl flex flex-col items-center hover:border-cyan-400/35 hover:-translate-y-1 transition-all";
    card.innerHTML = `
      <span class="text-[8px] font-bold text-slate-500 self-start">${el.num}</span>
      <span class="text-base font-black text-cyan-400">${el.symbol}</span>
      <span class="text-[8px] text-slate-400 truncate w-full text-center">${el.name}</span>
    `;
    grid.appendChild(card);
  }
};

window.showElementDetails = function(num) {
  const el = elementsData[num];
  const details = document.getElementById('ptable-details');
  if(!details) return;
  
  details.innerHTML = `
    <div class="flex justify-between items-center border-b border-white/5 pb-2">
      <h3 class="text-sm font-black uppercase text-cyan-400">${el.name}</h3>
      <span class="px-2 py-0.5 rounded text-[9px] font-bold bg-cyan-950/20 text-cyan-300 border border-cyan-500/10">No. ${el.num}</span>
    </div>
    <div class="space-y-3 text-xs">
      <div>
        <div class="text-[9px] font-bold uppercase text-slate-500">Atomic Symbol</div>
        <div class="font-black text-xl text-white mt-0.5">${el.symbol}</div>
      </div>
      <div>
        <div class="text-[9px] font-bold uppercase text-slate-500">Atomic Mass</div>
        <div class="font-mono text-white mt-0.5">${el.mass} u</div>
      </div>
      <div>
        <div class="text-[9px] font-bold uppercase text-slate-500">Electron Configuration</div>
        <div class="font-mono text-white mt-0.5">${el.conf}</div>
      </div>
      <div>
        <div class="text-[9px] font-bold uppercase text-slate-500">Typical Uses</div>
        <div class="text-slate-300 mt-0.5 leading-relaxed">${el.uses}</div>
      </div>
      <div>
        <div class="text-[9px] font-bold uppercase text-slate-500">Characteristic Reaction</div>
        <div class="font-mono text-cyan-300 mt-0.5">${el.rxn}</div>
      </div>
    </div>
  `;
};


