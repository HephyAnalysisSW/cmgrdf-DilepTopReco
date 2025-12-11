#ifndef CMGRDF_toprecofunctions_h
#define CMGRDF_toprecofunctions_h

#include "Math/GenVector/LorentzVector.h"
#include "Math/GenVector/PtEtaPhiM4D.h"
#include "Math/GenVector/PxPyPzE4D.h"
#include "Math/Vector4D.h"
#include "Math/GenVector/Boost.h"
#include <ROOT/RVec.hxx>

#include "TopReco.h"

ROOT::Math::PxPyPzEVector makeP4_PxPyPzE(const double pt, const double eta, const double phi, const double mass) {
    auto p4_PtEtaPhiM = ROOT::Math::PtEtaPhiMVector(pt, eta, phi, mass);
    return ROOT::Math::PxPyPzEVector(p4_PtEtaPhiM);
}

ROOT::RVec<ROOT::Math::PxPyPzEVector> makeP4_PxPyPzE(const ROOT::RVecF& pt, const ROOT::RVecF& eta, const ROOT::RVecF& phi, const ROOT::RVecF& mass) {
    auto p4_PtEtaPhiM = ROOT::VecOps::Construct<ROOT::Math::PtEtaPhiMVector>(pt, eta, phi, mass);
    return ROOT::VecOps::Construct<ROOT::Math::PxPyPzEVector>(p4_PtEtaPhiM);
}

std::pair<TopRecoSolution,std::pair<size_t,size_t>> topreco_solution(TTDilepReconstruction& r, const ROOT::Math::PxPyPzEVector& lep, const ROOT::Math::PxPyPzEVector& antilep, const ROOT::RVec<ROOT::Math::PxPyPzEVector>& jets, const ROOT::RVecB& btags, double met_pt, double met_phi, double mwp=80.3, double mwp_width=2.14, double mwm=80.3, double mwm_width=2.14, double mt=172.5, double mt_width=1.42, double mat=172.5, double mat_width=1.42) {
    double met_px = met_pt*std::cos(met_phi);
    double met_py = met_pt*std::sin(met_phi);
    std::pair<TopRecoSolution,std::pair<size_t,size_t>> sol = r.reconstruction(lep, antilep, jets, btags, met_px, met_py, mwp, mwp_width, mwm, mwm_width, mt, mt_width, mat, mat_width);
    return sol;
}

#endif
