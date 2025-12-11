#ifndef TTDILEPRECO
#define TTDILEPRECO

#include <map>
#include <cmath>
#include <complex>
#include <vector>
#include <random>
#include <numeric>
#include <algorithm>
#include <iostream>
#include <limits>
#include <stdexcept>

#include "ROOT/RVec.hxx"
#include "TH1.h"
#include "TRandom3.h"
#include <TLorentzVector.h>
#include <Math/LorentzVector.h>
#include "Math/Vector3D.h"
#include "Math/PxPyPzE4D.h"

//typedef ROOT::Math::PxPyPzEVector LV;
typedef ROOT::Math::LorentzVector<ROOT::Math::PxPyPzE4D<double> > LV;
typedef ROOT::RVec<LV> VLV;

class TopRecoSolution {
    public:
        bool valid;
        LV top;
        LV Wp;
        LV b;
        LV antilep;
        LV nu;
        LV antitop;
        LV Wm;
        LV antib;
        LV lep;
        LV antinu;
        TopRecoSolution() {
            valid = false;
            top = LV(std::nan(""), std::nan(""), std::nan(""), std::nan(""));
            Wp = LV(std::nan(""), std::nan(""), std::nan(""), std::nan(""));
            b = LV(std::nan(""), std::nan(""), std::nan(""), std::nan(""));
            antilep = LV(std::nan(""), std::nan(""), std::nan(""), std::nan(""));
            nu = LV(std::nan(""), std::nan(""), std::nan(""), std::nan(""));
            antitop = LV(std::nan(""), std::nan(""), std::nan(""), std::nan(""));
            Wm = LV(std::nan(""), std::nan(""), std::nan(""), std::nan(""));
            antib = LV(std::nan(""), std::nan(""), std::nan(""), std::nan(""));
            lep = LV(std::nan(""), std::nan(""), std::nan(""), std::nan(""));
            antinu = LV(std::nan(""), std::nan(""), std::nan(""), std::nan(""));
        }
        TopRecoSolution operator+(TopRecoSolution s) {
            TopRecoSolution news;
            news.top = this->top + s.top;
            news.Wp = this->Wp + s.Wp;
            news.b = this->b + s.b;
            news.antilep = this->antilep + s.antilep;
            news.nu = this->nu + s.nu;
            news.antitop = this->antitop + s.antitop;
            news.Wm = this->Wm + s.Wm;
            news.antib = this->antib + s.antib;
            news.lep = this->lep + s.lep;
            news.antinu = this->antinu + s.antinu;

            return news;
        }

        TopRecoSolution operator/(double f) {
            TopRecoSolution news;
            news.top = this->top / f;
            news.Wp = this->Wp / f;
            news.b = this->b / f;
            news.antilep = this->antilep / f;
            news.nu = this->nu / f;
            news.antitop = this->antitop / f;
            news.Wm = this->Wm / f;
            news.antib = this->antib / f;
            news.lep = this->lep / f;
            news.antinu = this->antinu / f;

            return news;
        }
};

class TTDilepReconstruction {
    public:
        TTDilepReconstruction(int num_smear=0);
        //TTDilepReconstruction(int num_smear=0, TH1D* h_mlb=nullptr, TH1D* h_energyfj=nullptr, TH1D* h_alphaj=nullptr, TH1D* h_energyfl=nullptr, TH1D* h_alphal=nullptr, TRandom3* rng=nullptr);
        ~TTDilepReconstruction();
        void SetH_MLB(TH1D* h_mlb) {h_mlb_ = h_mlb;}
        void SetH_JetEnergy(TH1D* h_energyfj) {h_energyfj_ = h_energyfj;}
        void SetH_JetAngle(TH1D* h_alphaj) {h_alphaj_ = h_alphaj;}
        void SetH_LepEnergy(TH1D* h_energyfl) {h_energyfl_ = h_energyfl;}
        void SetH_LepAngle(TH1D* h_alphal) {h_alphal_ = h_alphal;}
        LV SetPhysicalLV(const LV& lv);
        std::vector<double> solve_quadratic(double a, double b, double c);
        std::vector<double> solve_cubic(double a, double b, double c, double d);
        std::vector<double> solve_quartic(double h0, double h1, double h2, double h3, double h4);
        ROOT::Math::XYZVectorD random_orthogonal(const ROOT::Math::XYZVectorD vec);
        ROOT::Math::XYZVectorD rotate_axis(ROOT::Math::XYZVectorD vec, ROOT::Math::XYZVectorD axis, double angle);
        LV smear(LV vec, TH1* h_energyf, TH1* h_alpha);
        std::pair<size_t, size_t> pick_bs_from_lepton_pair(const LV& lepton, const LV& antilepton, const VLV& jets, const ROOT::RVecB& btags);
        TopRecoSolution sonnenschein(const LV& lep, const LV& antilep, const LV& b, const LV& antib, double met_px, double met_py, double mwp, double mwm, double mt, double mat);
        std::pair<TopRecoSolution, std::pair<size_t, size_t>> reconstruction(const LV& lep, const LV& antilep, const VLV& jets, const ROOT::RVecB& btags, double met_px, double met_py, double mwp=80.3, double mwp_width=2.14, double mwm=80.3, double mwm_width=2.14, double mt=172.5, double mt_width=1.42, double mat=172.5, double mat_width=1.42);

    private:
        int num_smear_;
        TRandom3* rng_;
        TH1D* h_mlb_;
        TH1D* h_energyfj_;
        TH1D* h_alphaj_;
        TH1D* h_energyfl_;
        TH1D* h_alphal_;


        double get_mlb_weight(double m) {
            if (h_mlb_)
                return h_mlb_->GetBinContent(h_mlb_->GetXaxis()->FindBin(m));
            else
                return 1;
        }
};

TTDilepReconstruction::TTDilepReconstruction(int num_smear)
{
    num_smear_ = num_smear;
    h_mlb_ = nullptr;
    h_energyfj_ = nullptr;
    h_alphaj_ = nullptr;
    h_energyfl_ = nullptr;
    h_alphal_ = nullptr;
    rng_ = new TRandom3();
}

//TTDilepReconstruction::TTDilepReconstruction(int num_smear, TH1D* h_mlb, TH1D* h_energyfj, TH1D* h_alphaj, TH1D* h_energyfl, TH1D* h_alphal, TRandom3* rng)
//{
//    num_smear_ = num_smear;
//    h_mlb_ = h_mlb;
//    h_energyfj_ = h_energyfj;
//    h_alphaj_ = h_alphaj;
//    h_energyfl_ = h_energyfl;
//    h_alphal_ = h_alphal;
//    if (rng) {
//        rng_ = rng;
//    }
//    else {
//        rng_ = new TRandom3();
//    }
//}

TTDilepReconstruction::~TTDilepReconstruction(){
    delete rng_;
    delete h_mlb_;
    delete h_energyfj_;
    delete h_alphaj_;
    delete h_energyfl_;
    delete h_alphal_;
}

std::pair<size_t, size_t> TTDilepReconstruction::pick_bs_from_lepton_pair(const LV& lep, const LV& antilep, const VLV& jets, const ROOT::RVecB& btags) {
    // Pick a bottom quark and a bottom antiquark that fit best to a pair
    // of leptons assuming they come from a top pair decay. This is using
    // the mlb histogram method
    
    // Separate jets into b-tagged and non-btagged
    std::vector<size_t> jetsb, jetsnob;
    for (size_t ij=0; ij<jets.size(); ++ij) {
        if (btags[ij])
            jetsb.push_back(ij);
        else
            jetsnob.push_back(ij);
    }

    // Build jet pairs: (b0, b1)
    std::vector<std::pair<size_t, size_t>> b_pairs;
    if (jetsb.size() > 1) {
        for (size_t i = 0; i < jetsb.size(); ++i)
            for (size_t j = i + 1; j < jetsb.size(); ++j)
                b_pairs.emplace_back(jetsb[i], jetsb[j]);
    } else if (jetsb.size() == 1) {
        for (const auto& j : jetsnob)
            b_pairs.emplace_back(jetsb[0], j);
    } else { // no b-tags
        for (size_t i = 0; i < jetsnob.size(); ++i)
            for (size_t j = i + 1; j < jetsnob.size(); ++j)
                b_pairs.emplace_back(jetsnob[i], jetsnob[j]);
    }

    // Keep track of best-scoring pair
    double best_score = -1.0;
    std::pair<size_t, size_t> best_pair;

    // Loop through all possible jet pairs
    for (const auto& [b0, b1] : b_pairs) {
        LV b0_p4 = jets[b0];
        LV b1_p4 = jets[b1];
        // Compute invariant masses for both configurations
        double mass_alb = (b0_p4 + antilep).M();
        double mass_lb  = (b1_p4 + lep).M();
        double mass_alb_rev = (b1_p4 + antilep).M();
        double mass_lb_rev  = (b0_p4 + lep).M();

        // Get probabilities from histogram
        double p_m_alb      = TTDilepReconstruction::get_mlb_weight(mass_alb);
        double p_m_lb       = TTDilepReconstruction::get_mlb_weight(mass_lb);
        double p_m_alb_rev  = TTDilepReconstruction::get_mlb_weight(mass_alb_rev);
        double p_m_lb_rev   = TTDilepReconstruction::get_mlb_weight(mass_lb_rev);

        // Evaluate both configurations
        double score_normal   = p_m_alb * p_m_lb;
        double score_reversed = p_m_alb_rev * p_m_lb_rev;

        if (score_normal > best_score) {
            best_score = score_normal;
            best_pair = {b0, b1};
        }
        if (score_reversed > best_score) {
            best_score = score_reversed;
            best_pair = {b1, b0};
        }
    }

    return best_pair;
}

LV TTDilepReconstruction::SetPhysicalLV(const LV& lv) {
    LV lv_new(lv);
    if (lv_new.E() < lv_new.P()) {
        lv_new.SetE(lv_new.P());
    }
    return lv_new;
}

TopRecoSolution TTDilepReconstruction::sonnenschein(const LV& lep, const LV& antilep, const LV& b, const LV& antib, double met_px, double met_py, double mwp, double mwm, double mt, double mat) {
    /*
     * Full kinematic reconstruction for dileptonic ttbar using Sonnenschein's
     * method https://arxiv.org/pdf/hep-ph/0603011.pdf

     * Parameters
     * ----------
     * lep
     *     Lorentz vector of the negatively charged lepton
     * antilep
     *     Lorentz vector of the positively charged lepton
     * b
     *     Lorentz vector of the negativly charged bottom quark
     * antib
     *     Lorentz vector of the positively changed bottom quark
     * met_px
     *     X component of missing transverse energy
     * met_py
     *     Y component of missing transverse energy
     * mwp
     *     Mass of the W+ boson.
     * mwm
     *     Same as ``mwp`` for the W- boson
     * mt
     *     Same as ``mwp`` for the top quark
     * mat
     *     Same as ``mwp`` for the top antiquark
     * num_smear
     *     Number of times an event is smeared. If None, smearing is off
     * energyfl
     *     Histogram in form of an uproot TH1 or numpy array giving Ereco/Egen
     *     for the leptons. If None, lepton energy won't be smeared
     * energyfj
     *     Same as energyfl for bottom quarks
     * alphal
     *     Histogram in form of an uproot TH1 or numpy array giving the angle
     *      between reco and gen leptons. If None, lepton angles won't be smeared
     * alphaj
     *     Same as ``alphal`` for bottom quarks
     * hist_mlb
     *     uproot TH1 of the lepton-bottom-quark-mass distribution.
     *     Is needed, if num_smear is not None
     * rng
     *     A numpy.random.BitGenerator, if None a new one will be used
     *
     */

    TopRecoSolution best_sol;
    best_sol.valid = false;

    LV lep_phy = TTDilepReconstruction::SetPhysicalLV(lep);
    LV antilep_phy = TTDilepReconstruction::SetPhysicalLV(antilep);
    LV b_phy = TTDilepReconstruction::SetPhysicalLV(b);
    LV antib_phy = TTDilepReconstruction::SetPhysicalLV(antib);

    double lx = lep_phy.Px();
    double ly = lep_phy.Py();
    double lz = lep_phy.Pz();
    double lE = lep_phy.E();
    double lp = lep_phy.P();
    double ml = lep_phy.M();

    double alx = antilep_phy.Px();
    double aly = antilep_phy.Py();
    double alz = antilep_phy.Pz();
    double alE = antilep_phy.E();
    double alp = antilep_phy.P();
    double mal = antilep_phy.M();

    double bx = b_phy.Px();
    double by = b_phy.Py();
    double bz = b_phy.Pz();
    double bE = b_phy.E();
    double bp = b_phy.P();
    double mb = b_phy.M();

    double abx = antib_phy.Px();
    double aby = antib_phy.Py();
    double abz = antib_phy.Pz();
    double abE = antib_phy.E();
    double abp = antib_phy.P();
    double mab = antib_phy.M();

    // Compute terms a*, b*
    double a1 = ((bE + alE) * (mwp*mwp - mal*mal)
                - alE * (mt*mt - mb*mb - mal*mal) + 2.0 * bE * alE * alE
                - 2.0 * alE * (bx * alx + by * aly + bz * alz));
    double a2 = 2.0 * (bE * alx - alE * bx);
    double a3 = 2.0 * (bE * aly - alE * by);
    double a4 = 2.0 * (bE * alz - alE * bz);

    double b1 = ((abE + lE) * (mwm*mwm - ml*ml)
                - lE * (mat*mat - mab*mab - ml*ml) + 2.0 * abE * lE * lE
                - 2.0 * lE * (abx * lx + aby * ly + abz * lz));
    double b2 = 2.0 * (abE * lx - lE * abx);
    double b3 = 2.0 * (abE * ly - lE * aby);
    double b4 = 2.0 * (abE * lz - lE * abz);

    // ignore the case when a4 or b4 are 0
    const double eps = 1e-12;
    if (std::abs(a4) < eps || std::abs(b4) < eps) {
        // degenerate geometry, cannot proceed robustly
        return best_sol;
    }

    // terms c*
    double c00 = (-4.0 * (alE*alE - aly*aly) - 4.0 * (alE*alE - alz*alz) * (a3/a4)*(a3/a4)
                  - 8.0 * aly * alz * a3 / a4);
    double c10 = (-8.0 * (alE*alE - alz*alz) * a2 * a3 / (a4*a4) + 8.0 * alx * aly
                  - 8.0 * alx * alz * a3 / a4 - 8.0 * aly * alz * a2 / a4);
    double c11 = (4.0 * (mwp*mwp - mal*mal) * (aly - alz * a3 / a4)
                  - 8.0 * (alE*alE - alz*alz) * a1 * a3 / (a4*a4)
                  - 8.0 * aly * alz * a1 / a4);
    double c20 = (-4.0 * (alE*alE - alx*alx) - 4.0 * (alE*alE - alz*alz) * (a2/a4)*(a2/a4)
                  - 8.0 * alx * alz * a2 / a4);
    double c21 = (4.0 * (mwp*mwp - mal*mal) * (alx - alz * a2 / a4)
                  - 8.0 * (alE*alE - alz*alz) * a1 * a2 / (a4*a4)
                  - 8.0 * alx * alz * a1 / a4);
    // FIXME: the pepper implemetation is different with the paper! Need to understand 
    double c22 = ((mwp*mwp - mal*mal) * (mwp*mwp - mal*mal) - 4.0 * (alE*alE - alz*alz) * (a1/a4)*(a1/a4)
                  - 4.0 * (mwp*mwp - mal*mal) * alz * a1 / a4);

    // terms d*
    double d00 = (-4.0 * (lE*lE - ly*ly) - 4.0 * (lE*lE - lz*lz) * (b3/b4)*(b3/b4)
                  - 8.0 * ly * lz * b3 / b4);
    double d10 = (-8.0 * (lE*lE - lz*lz) * b2 * b3 / (b4*b4)
                  + 8.0 * lx * ly - 8.0 * lx * lz * b3 / b4 - 8.0 * ly * lz * b2 / b4);
    double d11p = (4.0 * (mwm*mwm - ml*ml) * (ly - lz * b3 / b4)
                   - 8.0 * (lE*lE - lz*lz) * b1 * b3 / (b4*b4)
                   - 8.0 * ly * lz * b1 / b4);
    double d20 = (-4.0 * (lE*lE - lx*lx) - 4.0 * (lE*lE - lz*lz) * (b2/b4)*(b2/b4)
                  - 8.0 * lx * lz * b2 / b4);
    double d21p = (4.0 * (mwm*mwm - ml*ml) * (lx - lz * b2 / b4)
                   - 8.0 * (lE*lE - lz*lz) * b1 * b2 / (b4*b4)
                   - 8.0 * lx * lz * b1 / b4);
    // FIXME: the pepper implemetation is different with the paper! Need to understand 
    double d22p = ((mwm*mwm - ml*ml) * (mwm*mwm - ml*ml) - 4.0 * (lE*lE - lz*lz) * (b1/b4)*(b1/b4)
                   - 4.0 * (mwm*mwm - ml*ml) * lz * b1 / b4);

    double d11 = - d11p - 2.0 * met_py * d00 - met_px * d10;
    double d21 = - d21p - 2.0 * met_px * d20 - met_py * d10;
    double d22 = (d22p + met_px * met_px * d20 + met_py * met_py * d00
                  + met_px * met_py * d10 + met_px * d21p + met_py * d11p);

    // h polynomial coefficients (note ordering: Python had h0...h4 where polynomial is h0 + h1*x + ... + h4*x^4)
    double h0 = (c00*c00 * d20*d20 + c10 * d20 * (c10 * d00 - c00 * d10)
                 + c20 * d10 * (c00 * d10 - c10 * d00)
                 + c20 * d00 * (c20 * d00 - 2.0 * c00 * d20));
    double h1 = (c00 * d21 * (2.0 * c00 * d20 - c10 * d10)
                 - c00 * d20 * (c11 * d10 + c10 * d11)
                 + c00 * d10 * (2.0 * c20 * d11 + c21 * d10)
                 - 2.0 * c00 * d00 * (c21 * d20 + c20 * d21)
                 + c10 * d00 * (2.0 * c11 * d20 + c10 * d21)
                 + c20 * d00 * (2.0 * c21 * d00 - c10 * d11)
                 - d00 * d10 * (c11 * c20 + c10 * c21));
    double h2 = (c00*c00 * (2.0 * d22 * d20 + d21*d21)
                 - c00 * d21 * (c11 * d10 + c10 * d11)
                 + c11 * d20 * (c11 * d00 - c00 * d11)
                 + c00 * d10 * (c22 * d10 - c10 * d22)
                 + c00 * d11 * (2.0 * c21 * d10 + c20 * d11)
                 + (2.0 * c22 * c20 + c21*c21) * d00*d00
                 - 2.0 * c00 * d00 * (c22 * d20 + c21 * d21 + c20 * d22)
                 + c10 * d00 * (2.0 * c11 * d21 + c10 * d22)
                 - d00 * d10 * (c11 * c21 + c10 * c22)
                 - d00 * d11 * (c11 * c20 + c10 * c21));
    double h3 = (c00 * d21 * (2.0 * c00 * d22 - c11 * d11)
                 + c00 * d11 * (2.0 * c22 * d10 + c21 * d11)
                 + c22 * d00 * (2.0 * c21 * d00 - c11 * d10)
                 - c00 * d22 * (c11 * d10 + c10 * d11)
                 - 2.0 * c00 * d00 * (c22 * d21 + c21 * d22)
                 - d00 * d11 * (c11 * c21 + c10 * c22)
                 + c11 * d00 * (c11 * d21 + 2.0 * c10 * d22));
    double h4 = (c00*c00 * d22*d22 + c11 * d22 * (c11 * d00 - c00 * d11)
                 + c00 * c22 * (d11*d11 - 2.0 * d00 * d22)
                 + c22 * d00 * (c22 * d00 - c11 * d11));

    // Solve quartic
    auto roots = TTDilepReconstruction::solve_quartic(h0, h1, h2, h3, h4);

    if (roots.empty()) {
        // no real root -> no physical solution
        return best_sol;
    }

    // For each real root evaluate vpy, vpz, vbarpx/vbarpy/vbarpz and build t, at.
    double best_mtt = std::numeric_limits<double>::infinity();

    for (double vpx : roots) {
        double c0 = c00;
        double c1 = c10 * vpx + c11;
        double c2 = c20 * vpx*vpx + c21 * vpx + c22;
        double d0 = d00;
        double d1 = d10 * vpx + d11;
        double d2 = d20 * vpx*vpx + d21 * vpx + d22;

        // denominator for vpy
        double denom = (c1 * d0 - c0 * d1);
        //if (std::abs(denom) < 1e-15) continue; // avoid divide by zero
        if (denom == 0) continue; // avoid divide by zero

        double vpy = (c0 * d2 - c2 * d0) / denom;
        double vpz = ((-a1 - a2 * vpx - a3 * vpy) / a4);

        double vbarpx = met_px - vpx;
        double vbarpy = met_py - vpy;
        double vbarpz = ((-b1 - b2 * vbarpx - b3 * vbarpy) / b4);

        // Neutrino energies (assume neutrino mass to be 0)
        double vE = std::sqrt(std::max(0.0, vpx*vpx + vpy*vpy + vpz*vpz));
        double vbarE = std::sqrt(std::max(0.0, vbarpx*vbarpx + vbarpy*vbarpy + vbarpz*vbarpz));

        // Build LorentzVectors for neutrinos
        LV v(vpx, vpy, vpz, vE);
        LV vbar(vbarpx, vbarpy, vbarpz, vbarE);

        TopRecoSolution sol;
        sol.nu = LV(v);
        sol.antinu = LV(vbar);
        sol.Wp = LV(v + antilep_phy);
        sol.Wm = LV(vbar + lep_phy);
        sol.top = LV(sol.Wp + b_phy);
        sol.antitop = LV(sol.Wm + antib_phy);
        sol.b = LV(b_phy);
        sol.antib = LV(antib_phy);
        sol.lep = LV(lep_phy);
        sol.antilep = LV(antilep_phy);
        sol.valid = true;

        LV sum = sol.top + sol.antitop;
        double mtt = sum.M();

        // choose smallest mtt
        if (mtt < best_mtt) {
            best_mtt = mtt;
            best_sol = sol;
        }
    }

    return best_sol;
}

std::vector<double> TTDilepReconstruction::solve_quadratic(double a, double b, double c) {
    if (std::abs(a) < 1e-18) {
        if (std::abs(b) < 1e-18) return {};
        return { -c / b };
    }
    double disc = b*b - 4.0*a*c;
    if (disc<0)
        return {};
    else if (disc==0)
        return { (-b) / (2.0*a)};
    else {
        double s = std::sqrt(disc);
        return { (-b + s) / (2.0*a), (-b - s) / (2.0*a) };
    }
}

std::vector<double> TTDilepReconstruction::solve_cubic(double a, double b, double c, double d) {
    // Solve for ax^3+bx^2+cx+d=0
    
    // If a == 0 fallback to quadratic
    if (std::abs(a) < 1e-18) {
        return solve_quadratic(b, c, d); // note order: ax^2 + bx + c -> (b,c,d) mapping
    }
    // Normalize
    double A = b / a;
    double B = c / a;
    double C = d / a;

    // Depressed cubic x = y - A/3
    // equation becomes: y^3+3*p*y+2*q = 0
    double sqA = A*A;
    double p = (1.0/3.0) * (-1.0/3.0 * sqA + B);
    double q = 0.5 * (2.0/27.0 * A*sqA - A*B/3.0 + C);

    // Solutions based on Cardano's formula
    // https://en.wikipedia.org/wiki/Cubic_equation#Cardano's_formula
    double D = q*q + p*p*p;

    std::vector<double> roots;
    if (D >= 0.0) {
        double sqrtD = std::sqrt(D);
        double u = std::cbrt(-q + sqrtD);
        double v = std::cbrt(-q - sqrtD);
        roots.push_back(u + v - A/3.0);
    } else {
        // three real roots: https://en.wikipedia.org/wiki/Cubic_equation#Trigonometric_and_hyperbolic_solutions
        // under the depression y^3+3*p*y+2*q = 0
        double phi = std::acos(q / std::sqrt(-(p*p*p)));
        double t = -2.0 * std::sqrt(-p);
        roots.push_back(t * std::cos(phi/3.0) - A/3.0);
        roots.push_back(t * std::cos((phi + 2*M_PI)/3.0) - A/3.0);
        roots.push_back(t * std::cos((phi - 2*M_PI)/3.0) - A/3.0);
    }
    return roots;
}

std::vector<double> TTDilepReconstruction::solve_quartic(double h0, double h1, double h2, double h3, double h4) {
    // polynomial: h0 x^4 + h1 x^3 + h2 x^2 + h3 x + h4 = 0
    // handle lower-degree cases first
    if (std::abs(h0) < 1e-18) {
        // cubic
        return solve_cubic(h1, h2, h3, h4);
    }

    std::vector<double> solutions;
    // normalize
    double h1p = h1 / h0;
    double h2p = h2 / h0;
    double h3p = h3 / h0;
    double h4p = h4 / h0;

    // depressed quartic substitution: x = y - h1p/4
    // equation: y^4+k1y^2+k2y+k3=0
    double k1 = h2p - 3.0/8.0*h1p*h1p;
    double k2 = h3p + h1p*h1p*h1p/8.0 - h1p*h2p/2.0;
    double k3 = h4p - 3.0*h1p*h1p*h1p*h1p/256.0 + h1p*h1p*h2p/16.0 - h1p*h3p/4.0;
    if (k3==0) {
        std::vector<double> roots = solve_cubic(1,0,k1,k2);
        for (auto& ir : roots) {
            solutions.push_back(ir-h1p/4);
        }
        solutions.push_back(-h1p/4);
    }
    else {
        std::vector<double> t12s = solve_cubic(1,2*k1,(k1*k1-4*k3),-k2*k2);
        std::vector<double> t1s, t2s;
        // One solution of t1 and t2 is sufficient to get all roots of the quartic euqation
        for (auto& t12 : t12s) {
            if ( t12>=0 ) {
                t1s.push_back(std::sqrt(t12));
                t2s.push_back(0.5*(k1+t12-k2/std::sqrt(t12)));
                //t1s.push_back((-1)*std::sqrt(t12.real()));
                //t2s.push_back(0.5*(k1+t12.real()+k2/std::sqrt(t12.real())));
                break;
            }
        }
        if (t1s.size()<1) {
            return solutions;
        }
        std::vector<double> roots1 = solve_quadratic(1,t1s[0],t2s[0]);
        std::vector<double> roots2 = solve_quadratic(1,(-1)*t1s[0],k3/t2s[0]);
        
        for (auto& ir1 : roots1) {
            solutions.push_back(ir1-h1p/4);
        }
        for (auto& ir2 : roots2) {
            solutions.push_back(ir2-h1p/4);
        }
    }
    return solutions;
}

LV  TTDilepReconstruction::smear(LV vec, TH1* h_energyf, TH1* h_alpha) {
    LV newvec;

    // smear the energy
    double E_smear = vec.E();
    if (h_energyf) {
        E_smear = h_energyf->GetRandom()*vec.E();
    }
    double m = vec.M();
    if (E_smear < 1.01*m)
        E_smear = 1.01*m;

    // smear the axis 
    ROOT::Math::XYZVectorD p3d(vec.Px(),vec.Py(),vec.Pz());
    ROOT::Math::XYZVectorD p3d_rotate = p3d;
    if (h_alpha) {
        double alpha = h_alpha->GetRandom();
        ROOT::Math::XYZVectorD rotating_axis = TTDilepReconstruction::random_orthogonal(p3d);
        p3d_rotate = TTDilepReconstruction::rotate_axis(p3d,rotating_axis,alpha);
    }

    // Ensure mass remain unchanged after smearing: E^2 = p^2 + m^2
    double p2_smear = E_smear*E_smear - m*m;
    double p_scale = std::sqrt(p2_smear/p3d_rotate.mag2());
    newvec.SetPxPyPzE(p3d_rotate.x()*p_scale,p3d_rotate.y()*p_scale,p3d_rotate.z()*p_scale,E_smear);

    return newvec;
}


ROOT::Math::XYZVectorD TTDilepReconstruction::random_orthogonal(const ROOT::Math::XYZVectorD vec) {
    ROOT::Math::XYZVectorD random_vec(this->rng_->Uniform(), this->rng_->Uniform(), this->rng_->Uniform());
    random_vec = random_vec.Unit();

    ROOT::Math::XYZVectorD vnorm = vec.Unit();
    ROOT::Math::XYZVectorD u = random_vec - (random_vec.Dot(vnorm))*vnorm;

    return u.Unit();
}

ROOT::Math::XYZVectorD TTDilepReconstruction::rotate_axis(ROOT::Math::XYZVectorD vec, ROOT::Math::XYZVectorD axis, double angle) {
    axis = axis.Unit();
    ROOT::Math::XYZVectorD newvec = vec*std::cos(angle) + (axis.Cross(vec))*std::sin(angle) + axis*(axis.Dot(axis))*(1-std::cos(angle));
    return newvec;
}

std::pair<TopRecoSolution, std::pair<size_t, size_t>> TTDilepReconstruction::reconstruction(const LV& lep, const LV& antilep, const VLV& jets, const ROOT::RVecB& btags, double met_px, double met_py, double mwp, double mwp_width, double mwm, double mwm_width, double mt, double mt_width, double mat, double mat_width) {
    std::pair<size_t,size_t> jet_indices = TTDilepReconstruction::pick_bs_from_lepton_pair(lep, antilep, jets, btags);
    const LV b = jets[jet_indices.first];
    const LV antib = jets[jet_indices.second];
    // run reconstruction if no smear is not requested
    if (this->num_smear_==0) {
        TopRecoSolution sol = TTDilepReconstruction::sonnenschein(lep, antilep, b, antib, met_px, met_py, mwp, mwm, mt, mat);
        return {sol,jet_indices};
    }

    // run reconstruction for num_smear_ times with different random smearing
    std::vector<std::pair<TopRecoSolution,double>> sols;
    double mwp_sample = mwp;
    double mwm_sample = mwm;
    double mt_sample = mt;
    double mat_sample = mat;
    for (size_t i=0; i<(size_t)this->num_smear_; ++i) {
        if (mwp_width>0) {
            mwp_sample = this->rng_->BreitWigner(mwp,mwp_width);
        }
        if (mwm_width>0) {
            mwm_sample = this->rng_->BreitWigner(mwm,mwm_width);
        }
        if (mt_width>0) {
            mt_sample = this->rng_->BreitWigner(mt,mt_width);
        }
        if (mat_width>0) {
            mat_sample = this->rng_->BreitWigner(mat,mat_width);
        }

        LV lep_smear = TTDilepReconstruction::smear(lep, this->h_energyfl_, this->h_alphal_);
        LV antilep_smear = TTDilepReconstruction::smear(antilep, this->h_energyfl_, this->h_alphal_);
        LV b_smear = TTDilepReconstruction::smear(b, this->h_energyfj_, this->h_alphaj_);
        LV antib_smear = TTDilepReconstruction::smear(antib, this->h_energyfj_, this->h_alphaj_);

        LV met_changes = lep + antilep + b + antib - lep_smear - antilep_smear - b_smear - antib_smear;
        double met_px_smear = met_px + met_changes.Px();
        double met_py_smear = met_py + met_changes.Py();

        TopRecoSolution sol = TTDilepReconstruction::sonnenschein(lep_smear, antilep_smear, b_smear, antib_smear, met_px_smear, met_py_smear, mwp_sample, mwm_sample, mt_sample, mat_sample);
        if (sol.valid){
            double mlepantib = (sol.antib + sol.lep).M();
            double mantilepb = (sol.b + sol.antilep).M();
            double weight = TTDilepReconstruction::get_mlb_weight(mlepantib) * TTDilepReconstruction::get_mlb_weight(mantilepb);
            sols.push_back(std::pair<TopRecoSolution,double>(sol,weight));
            //std::cout << "met_px_smear " << met_px_smear << " met_py_smear " << met_py_smear << " mwp_sample " << mwp_sample << " mwm_sample " << mwm_sample << " mt_sample " << mt_sample << " mat_sample " << mat_sample << std::endl;
            //std::cout << "sol met_px " << sol.nu.Px()+sol.antinu.Px() << " met_py " << sol.nu.Py()+sol.antinu.Py() << " mwp " << sol.Wp.M() << " mwm " << sol.Wm.M() << " t " << sol.top.M() << " at " << sol.antitop.M() << " nu " << sol.nu.M() <<" anu " << sol.antinu.M() << std::endl; 
        }

    }
    TopRecoSolution sum_sol;
    double sum_weight = 0;
    for (size_t isol=0; isol<sols.size(); ++isol) {
        double wi = sols[isol].second;
        if ( !(sols[isol].first.valid) || (wi==0) ) continue; // skip invalid solutions or with 0 weight

        // avoid starting from NaN-initialized sum_sol object, which would just give NaN for the sum
        if (!sum_sol.valid){
            sum_sol = (sols[isol].first)/(1.0/wi);
        }else{
            sum_sol = sum_sol + (sols[isol].first)/(1.0/wi);
        }
        sum_weight += wi;
        sum_sol.valid = true;
    }

    TopRecoSolution sol;
    if (sum_sol.valid) {
        sol = sum_sol/sum_weight;
        // FIXME: top masses are ensured to be on shell after the weighted sum, but what about W and v?
        //sol.top.SetE(std::sqrt(mt*mt+sol.top.P2()));
        //sol.antitop.SetE(std::sqrt(mat*mat+sol.antitop.P2()));
        sol.valid = true;
        //std::cout << "final sol met_px " << sol.nu.Px()+sol.antinu.Px() << " met_py " << sol.nu.Py()+sol.antinu.Py() << " mwp " << sol.Wp.M() << " mwm " << sol.Wm.M() << " t " << sol.top.M() << " at " << sol.antitop.M() << " nu " << sol.nu.M() <<" anu " << sol.antinu.M() << std::endl; 
    }

    return {sol,jet_indices}; 
}

#endif
