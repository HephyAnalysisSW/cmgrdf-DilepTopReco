from CMGRDF import Cut, AddWeight, Data, DataSample, MCSample, DataDrivenSample, Process, Define, Flow, ReDefine
from CMGRDF.cms.jmeUncertainties import JMEUncertaintiesDefine, JetVetoMapCut, JetPuIDSF
from CMGRDF.cms.eras import run2eras, run3eras, suberas_perera

jetAlgoPerEra = dict( [(era, "AK4PFchs") for era in run2eras] + [(era, "AK4PFPuppi") for era in run3eras])
metNamePerEra = dict( [(era, "MET") for era in run2eras] + [(era, "PuppiMET") for era in run3eras])


# first we hardcode some variable to zero (as done in nanoaodtools, until these inputs are added to nano)

jme_sequences = [ Define( f'CorrT1METJet_{var}', '0.0*CorrT1METJet_rawPt') for var in ['neEmEF', 'chEmEF']] 

# then, data needs dummy variables to prevent the thing from crashing
jme_sequences.extend( [Define(f"GenJet_{var}", "0*Jet_pt-99.", onMC=False) for var in [ 'pt', 'eta', 'phi', 'mass']])
jme_sequences.extend( [Define( f"Jet_{var}", "0*Jet_pt -99.", onMC=False) for var in ['partonFlavour', 'genJetIdx']])

# run2 samples have a different name
jme_sequences.append( Define("Rho_fixedGridRhoFastjetAll", "fixedGridRhoFastjetAll", eras=run2eras) )

# run3 samples have uncl variations stored differently :)
met_run3=metNamePerEra["2022"] # we assume we wont have different met in 2023. it should crash if we did anyway
jme_sequences.append( Define(f"{met_run3}_MetUnclustEnUpDeltaX", f"{met_run3}_ptUnclusteredUp*TMath::Cos({met_run3}_phiUnclusteredUp)-{met_run3}_pt*TMath::Cos({met_run3}_phi)", eras=run3eras))
jme_sequences.append( Define(f"{met_run3}_MetUnclustEnUpDeltaY", f"{met_run3}_ptUnclusteredUp*TMath::Sin({met_run3}_phiUnclusteredUp)-{met_run3}_pt*TMath::Sin({met_run3}_phi)", eras=run3eras))
                             
# storing dict of names of jes and jer variations per era
# applied to jets and MET (from Type-1 corrections)
# used to propagate result of original Vary automatically
jme_variation_names_data = {}
jme_variation_names_MC = {}

# same as above, but for variations that apply only to MET
met_variation_names_data = {}
met_variation_names_MC = {}

# now we go into the meat
for era in run2eras+run3eras:
    for subera in suberas_perera[era]:
        # adding a sequence per era,subera for data. first met and then jets
        jme_sequences.append(JMEUncertaintiesDefine(doMET=True,jetAlgo=jetAlgoPerEra[era] , suffix="data_%s_%s"%(era,subera)     , eras=[era], suberas=[subera], onMC=False, onData=True, onDataDriven=True, metcollection=metNamePerEra[era]))
        jme_sequences.append(JMEUncertaintiesDefine(doMET=False,jetAlgo=jetAlgoPerEra[era], suffix="data_jets_%s_%s"%(era,subera), eras=[era], suberas=[subera], onMC=False, onData=True, onDataDriven=True, metcollection=metNamePerEra[era]))

    #  in data, only considering total JES uncertainty and a single JER uncertainty (defaults)
    # subera information used to get the correction but correlated across suberas
    jme_variation_names_data[era] = ["CMS_scale_j_Total"]
    jme_variation_names_data[era] += [f"CMS_res_j_0_{era}"]

    met_variation_names_data[era] = ["Uncl"]
    # TODO: add deltaphi MET uncertainty

    # adding a sequence per era for MC. first met and then jets
    # adding both era-correlated and era-decorrelated components (the ones with _{theera})
    # same corrections for both 2016 eras
    theera="2016" if era == "2016APV" else era
    uncSources=["Regrouped_HF", f"Regrouped_BBEC1_{theera}", "FlavorPureGluon", "FlavorPureQuark", "FlavorPureCharm", "FlavorPureBottom", f"Regrouped_RelativeSample_{theera}", "Regrouped_EC2", f"Regrouped_HF_{theera}", "Regrouped_RelativeBal", f"Regrouped_Absolute_{theera}", "Regrouped_BBEC1", f"Regrouped_EC2_{theera}", "Regrouped_Absolute"] if era in run2eras else ["Total"]
    jme_sequences.append( JMEUncertaintiesDefine(doMET=True ,jetAlgo=jetAlgoPerEra[era],suffix="mc_%s"%era     , doSyst=True, onMC=True, onData=False, onDataDriven=False, eras=[era], metcollection=metNamePerEra[era], splitJER=True, uncSources=uncSources ))
    jme_sequences.append( JMEUncertaintiesDefine(doMET=False,jetAlgo=jetAlgoPerEra[era],suffix="mc_jets_%s"%era, doSyst=True, onMC=True, onData=False, onDataDriven=False, eras=[era], metcollection=metNamePerEra[era], splitJER=True, uncSources=uncSources))

    jme_variation_names_MC[era] = [f"CMS_scale_j_{source}" for source in uncSources]
    # for JER, always separated by era
    jme_variation_names_MC[era] += [f"CMS_res_j_{ijer}_{era}" for ijer in range(6)]
    
    met_variation_names_MC[era] = ["Uncl"]

# now we add jet veto maps for run3. no PU ID SF for run 3
for era in run3eras:
    jme_sequences.append( JetVetoMapCut( "jetVetoMapCut", eras=[era] ) )

# pu ID weight for run 2. nothing for run 3
# these are applied after all selection cuts
jme_sequences_after=[]
for era in run2eras:
    jme_sequences_after.append( JetPuIDSF( eras=[era], jetCol="SelJet" ) )
for era in run3eras:
    jme_sequences_after.append( Define( "JetPUID_SF", "1", eras=[era] ) )
